#!/usr/bin/env python3
"""
optimize.py — constraint-checked greedy compression optimizer.

Hill-climbs on token count. A move (deleting one word/punctuation occurrence)
is accepted ONLY if the full isomorphism constraint set still holds:

  C1 every source content stem remains present in the document
  C2 every directive atom keeps local-window coverage >= its tier threshold
     (W4/W5 >= 0.85, else >= 0.70) with local core >= 0.50 or global hoisting
  C3 every required literal string survives
  C4 structure survives (14 section headers, 11 gate lines, markers)
  C5 polarity/logic words are never deletable (hard protected list)

Runs repeated passes until a fixed point (no accepted move in a full pass).
Every accepted and rejected move is logged for audit.
"""
from __future__ import annotations
import json, os, re, sys, time
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forensic_core import (atomize, stem, stem_set, tokens, content_stems,
                            STEMMED_STOPWORDS, _init_stopwords, expand_with_lexicon)
import tiktoken

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENC = tiktoken.get_encoding("o200k_base")

# ---------------------------------------------------------------- protections
OPERATOR_CHARS = set("+→|↔—/=§·•")
POLARITY = {
    "where", "when", "wherever", "whenever", "most", "least", "more", "less",
    "inside", "within", "between", "across", "per", "including", "incl",
    "safe", "unsafe", "first", "last", "own", "other", "otherwise", "via",

    "not", "no", "never", "without", "unless", "only", "cannot", "can", "must",
    "before", "after", "outside", "beyond", "non", "nothing", "none", "any",
    "all", "every", "each", "both", "and", "or", "if", "else", "otherwise",
    "instead", "rather", "than", "versus", "vs", "except", "but", "while",
    "independent", "independently", "separate", "separately", "same", "one",
    "single", "merely", "silently", "explicitly", "explicit", "implicit",
    "actual", "actually", "genuine", "authentic", "real", "additional",
    "additionally", "minimal", "maximally", "complete", "incomplete", "partial",
    "do", "does", "is", "are", "was", "were", "be",
}
MARKERS = {"x", "g", "a", "b", "c", "§"}
HARD_LITERALS = [
    "PASS", "FAIL", "BLOCKED", "SKIP", "INCOMPLETE", "CONFIRMED", "MATCH",
    "MISMATCH", "UNRESOLVED", "ANALYZED", "IMPLEMENTED", "VERIFIED",
    "PARTIALLY_VERIFIED", "NOT_IMPLEMENTED", "NOT_APPLICABLE", "SHA-256",
    "GitHub", "Actions", "CodeQL", "SARIF", "SBOM", "SCA", "IDOR", "a11y",
    "ZIP", "AST", "IR", "NUL", "JSON", "Markdown", "JavaScript", "TypeScript",
    "Python", "Go", "Rust", "ChatGPT", "Interpreter", "HTTP", "API", "CI",
    "ONE", "ALL", "NEVER", "THREE", "omni-audit", "seven", "28",
]
REQUIRED_LITERAL_PHRASES = [
    "CONFIRMED MATCH", "CONFIRMED MISMATCH", "NOT ANALYZED",
    "IMPLEMENTED+VERIFIED", "IMPLEMENTED+PARTIALLY_VERIFIED",
    "NOT_IMPLEMENTED", "NOT_APPLICABLE", "GitHub Actions", "Code Interpreter",
    "execution law", "response law", "output contract", "hard stop",
]
PIPELINES = [
    ["source-first", "forensic reconciliation", "architectural integration",
     "executable implementation", "adversarial verification", "repair", "verified delivery"],
    ["repository discovery", "source/manifest analysis", "static verification",
     "language/dependency gates", "API/security/integration analysis",
     "applicable runtime verification", "gate reconciliation", "forensic reporting",
     "CI disposition/artifact delivery"],
    ["coverage", "correctness", "precision", "security", "resource efficiency",
     "integration depth", "reproducibility", "evidence integrity", "usability"],
    ["diagnose", "repair", "rerun affected tests", "run integration/regression checks",
     "record actual evidence"],
]

TOKEN_RE = re.compile(r"\s+|[^\s]+")


class Doc:
    """Mutable token-level view of the compressed document."""

    def __init__(self, text: str):
        self.lines: List[List[str]] = []
        for raw in text.split("\n"):
            self.lines.append(TOKEN_RE.findall(raw) if raw.strip() else [])
        self.raw_blank = [not bool(l) for l in self.lines]

    def render(self) -> str:
        out = []
        for toks in self.lines:
            s = "".join(toks)
            s = re.sub(r"[ \t]{2,}", " ", s)
            s = re.sub(r"\s+([,;.])", r"\1", s)
            s = re.sub(r"([,;])\1+", r"\1", s)
            s = re.sub(r"[,;]\s*([,;])", r"\1", s)
            s = re.sub(r"\s+$", "", s)
            out.append(s)
        txt = "\n".join(out)
        txt = re.sub(r"\n{3,}", "\n\n", txt)
        return txt

    def word_positions(self) -> List[Tuple[int, int, str]]:
        res = []
        for i, toks in enumerate(self.lines):
            for j, t in enumerate(toks):
                if t.strip():
                    res.append((i, j, t))
        return res


class Checker:
    """Incremental constraint checker.

    Fast path: a deletion that removes no content stem from its line cannot
    reduce any coverage, so only the literal/structure guard must re-run.
    Slow path: only atoms indexed by the removed stems are re-evaluated.
    """

    def __init__(self, src_path: str, lexicon: Dict[str, List[str]], doc: "Doc", n_global: int):
        self.atoms = atomize(open(src_path, encoding="utf-8").read())
        self.lex = lexicon
        self.atom_stems = [set(a.stems) for a in self.atoms]
        self.weights = [a.weight for a in self.atoms]
        self.required: Set[str] = set()
        for s in self.atom_stems:
            self.required |= s
        self.index: Dict[str, List[int]] = defaultdict(list)
        for k, st in enumerate(self.atom_stems):
            for s in st:
                self.index[s].append(k)
        self.doc = doc
        self.n_global = n_global
        self.rebuild()
        self.sections = self._sections()
        self.anchor: List[Tuple[int, int]] = []     # (start,end) indices into self.idx
        self.base_cov: List[float] = []
        self.base_core: List[float] = []
        self.freeze_anchors()

    def line_stems(self, line_text: str) -> Set[str]:
        e, _ = expand_with_lexicon(stem_set(line_text), self.lex)
        return e

    def line_counts(self, line_text: str) -> Counter:
        """Multiset of content stems on a line (lexicon-expanded forms count 1)."""
        c = Counter(content_stems(line_text))
        e, _ = expand_with_lexicon(set(c), self.lex)
        for x in e:
            if x not in c:
                c[x] = 1
        return c

    def rebuild(self):
        d = self.doc
        self.rendered = [("".join(t)).strip() for t in d.lines]
        self.lstems_all = [self.line_stems(r) if r else set() for r in self.rendered]
        self.lcounts_all = [self.line_counts(r) if r else Counter() for r in self.rendered]
        self.idx = [i for i, r in enumerate(self.rendered) if r]
        self.lstems = [self.lstems_all[i] for i in self.idx]
        self.lcounts = [self.lcounts_all[i] for i in self.idx]
        self.gstems = set()
        for i in self.idx:
            if i < self.n_global:
                self.gstems |= self.lstems_all[i]
        self.doc_count = Counter()
        for s in self.lstems:
            for x in s:
                self.doc_count[x] += 1

    def _sections(self) -> List[str]:
        secs, cur = [], "0"
        for i in self.idx:
            m = re.match(r"^§(\d+)\b", self.rendered[i])
            if m:
                cur = m.group(1)
            secs.append(cur)
        return secs

    def freeze_anchors(self, window: int = 1):
        """Bind every source atom to the compressed span that carries it NOW.

        The binding plus monotone non-degradation is the isomorphism contract:
        no later edit may reduce any atom's coverage at its own anchor, so
        meaning can never silently migrate to another part of the document.
        """
        self.anchor, self.base_cov, self.base_core = [], [], []
        self.anchor_mode: List[str] = []
        L, g, n = self.lstems, self.gstems, len(self.lstems)
        pre = [i for i in range(n) if self.idx[i] < self.n_global]
        for k, s in enumerate(self.atom_stems):
            if not s:
                self.anchor.append((0, 0)); self.base_cov.append(0.0)
                self.base_core.append(0.0); self.anchor_mode.append("EMPTY")
                continue
            sec = self.atoms[k].section
            cand = [i for i in range(n) if self.sections[i] == sec]
            thresh = 0.85 if self.weights[k] >= 4 else 0.70
            best = (-1.0, -1.0, 0, 0)
            for i in cand:
                acc: Set[str] = set()
                for w in range(window):
                    if i + w >= n or self.sections[i + w] != sec:
                        break
                    acc |= L[i + w]
                    core = len(s & acc) / len(s)
                    tot = len(s & (acc | g)) / len(s)
                    score = (round(tot, 6), round(core, 6))
                    if score > (round(best[0], 6), round(best[1], 6)):
                        best = (tot, core, i, i + w)
            mode = "LOCAL"
            if best[0] < thresh or best[1] < 0.50:
                # not carried in its own section -> must be hoisted into the
                # globally-binding preamble, and anchored THERE (so the
                # preamble text that discharges it is itself protected).
                bestg = (-1.0, -1.0, 0, 0)
                for i in pre:
                    acc = set()
                    for w in range(3):
                        if i + w >= n or self.idx[i + w] >= self.n_global:
                            break
                        acc |= L[i + w]
                        core = len(s & acc) / len(s)
                        tot = core
                        if (round(tot, 6), round(core, 6)) > (round(bestg[0], 6), round(bestg[1], 6)):
                            bestg = (tot, core, i, i + w)
                if bestg[0] >= best[0]:
                    best, mode = bestg, "HOISTED"
            self.anchor.append((best[2], best[3]))
            self.base_cov.append(best[0])
            self.base_core.append(best[1])
            self.anchor_mode.append(mode)
        self.base_counts: List[Counter] = []
        for k, s_ in enumerate(self.atom_stems):
            i0, i1 = self.anchor[k]
            acc = Counter()
            for i in range(i0, min(i1 + 1, len(self.lcounts))):
                acc += self.lcounts[i]
            self.base_counts.append(Counter({x: acc[x] for x in s_ if acc[x] > 0}))

    def anchor_cov(self, k: int) -> Tuple[float, float]:
        s = self.atom_stems[k]
        if not s:
            return 1.0, 1.0
        i0, i1 = self.anchor[k]
        acc: Set[str] = set()
        for i in range(i0, min(i1 + 1, len(self.lstems))):
            acc |= self.lstems[i]
        core = len(s & acc) / len(s)
        tot = len(s & (acc | self.gstems)) / len(s)
        return tot, core

    def atom_ok(self, k: int, window=1) -> bool:
        if os.environ.get("OMNI_ABLATION") == "1":
            return self.atom_ok_free(k, window=3)
        """Monotone rule: the multiset of this atom's stems present at its own
        anchor may never shrink. Set-coverage monotonicity is implied, and
        within-line duplicate cannibalisation becomes impossible."""
        base = self.base_counts[k]
        if not base:
            tot, core = self.anchor_cov(k)
            eps = 1e-9
            return (tot >= self.base_cov[k] - eps) and (core >= self.base_core[k] - eps)
        i0, i1 = self.anchor[k]
        acc = Counter()
        for i in range(i0, min(i1 + 1, len(self.lcounts))):
            acc += self.lcounts[i]
        for x, n in base.items():
            if acc[x] < n:
                return False
        return True

    def atom_ok_free(self, k: int, window=3) -> bool:
        s = self.atom_stems[k]
        if not s:
            return True
        thresh = 0.85 if self.weights[k] >= 4 else 0.70
        g = self.gstems
        if len(s & g) / len(s) >= 1.0:
            return True
        L = self.lstems
        n = len(L)
        for i in range(n):
            acc: Set[str] = set()
            for w in range(window):
                if i + w >= n:
                    break
                acc |= L[i + w]
                inter = s & acc
                if (len(s & (inter | g)) / len(s)) >= thresh and len(inter) / len(s) >= 0.50:
                    return True
        return False

    def all_atoms_ok(self) -> bool:
        return all(self.atom_ok(k) for k in range(len(self.atoms)))

    def try_delete(self, i: int, j: int) -> bool:
        """Attempt deletion of token j on line i; returns True if accepted."""
        d = self.doc
        saved = d.lines[i][j]
        d.lines[i][j] = ""
        new_line = ("".join(d.lines[i])).strip()
        old_stems = self.lstems_all[i]
        new_stems = self.line_stems(new_line) if new_line else set()
        new_counts = self.line_counts(new_line) if new_line else Counter()
        old_counts = self.lcounts_all[i]
        count_changed = (new_counts != old_counts)
        removed = old_stems - new_stems
        blankness_changed = bool(new_line) != bool(self.rendered[i])

        if not removed and not blankness_changed and not count_changed:
            if self.literals_ok():
                self.rendered[i] = new_line
                return True
            d.lines[i][j] = saved
            return False

        # slow path: apply, then validate
        prev_rendered, prev_lstems_all = self.rendered[i], self.lstems_all[i]
        prev_counts = self.lcounts_all[i]
        self.rendered[i] = new_line
        self.lstems_all[i] = new_stems
        self.lcounts_all[i] = new_counts
        if blankness_changed:
            self.rebuild_light()
        else:
            k = self.idx.index(i)
            self.lstems[k] = new_stems
            self.lcounts[k] = new_counts
            for x in removed:
                self.doc_count[x] -= 1
            if i < self.n_global:
                self.gstems = set()
                for ii in self.idx:
                    if ii < self.n_global:
                        self.gstems |= self.lstems_all[ii]

        ok = True
        for x in removed:
            if x in self.required and self.doc_count.get(x, 0) <= 0:
                ok = False
                break
        if ok:
            affected = set()
            for x in set(old_counts) - set(new_counts) | {y for y in old_counts if new_counts[y] < old_counts[y]}:
                affected.update(self.index.get(x, ()))
            for x in removed:
                affected.update(self.index.get(x, ()))
            try:
                li = self.idx.index(i)
                for k, (a0, a1) in enumerate(self.anchor):
                    if a0 <= li <= a1:
                        affected.add(k)
            except ValueError:
                affected = set(range(len(self.atoms)))
            if i < self.n_global:
                affected = set(range(len(self.atoms)))
            ok = all(self.atom_ok(k) for k in affected)
        if ok:
            ok = self.literals_ok()
        if ok:
            return True
        # revert
        d.lines[i][j] = saved
        self.rendered[i] = prev_rendered
        self.lstems_all[i] = prev_lstems_all
        self.lcounts_all[i] = prev_counts
        self.rebuild()
        return False

    def rebuild_light(self):
        self.idx = [i for i, r in enumerate(self.rendered) if r]
        self.lstems = [self.lstems_all[i] for i in self.idx]
        self.lcounts = [self.lcounts_all[i] for i in self.idx]
        self.lcounts = [self.lcounts_all[i] for i in self.idx]
        self.gstems = set()
        for i in self.idx:
            if i < self.n_global:
                self.gstems |= self.lstems_all[i]
        self.doc_count = Counter()
        for s in self.lstems:
            for x in s:
                self.doc_count[x] += 1

    def literals_ok(self) -> bool:
        txt = self.doc.render()
        low = txt.lower()
        for lit in REQUIRED_LITERAL_PHRASES:
            if lit.lower() not in low:
                return False
        for lit in HARD_LITERALS:
            if lit.lower() not in low:
                return False
        for pipe in PIPELINES:
            pos = -1
            for seg in pipe:
                i = low.find(seg.lower(), pos + 1)
                if i < 0:
                    return False
                pos = i
        if len(re.findall(r"^§\d+ ", txt, re.M)) < 14:
            return False
        if len(re.findall(r"^G ", txt, re.M)) < 11:
            return False
        return True


def token_count(text: str) -> int:
    return len(ENC.encode(text))


def protected(tok: str, line_text: str) -> bool:
    raw = tok.strip()
    if os.environ.get("OMNI_ABLATION") == "1":
        return not raw
    w = raw.strip(".,;:|").lower()
    if not w:
        return True
    if any(ch in OPERATOR_CHARS for ch in raw):      # separators/operators
        return True
    if any(ch.isdigit() for ch in raw):              # ordinals, 28, SHA-256
        return True
    if sum(1 for ch in raw if ch.isupper()) >= 2:    # status labels/acronyms
        return True
    # GLUE-ONLY RULE: a token carrying any content stem is never deletable;
    # semantic compression is done by verified rewriting, not by deletion.
    if content_stems(raw):
        return True
    parts = set(re.split(r"[^a-z0-9]+", w)) | {w}
    for h in HARD_LITERALS:
        hl = h.lower()
        if hl in parts or (len(hl) >= 4 and hl in w):
            return True
    if w in POLARITY or w in MARKERS:
        return True
    if any(w == h.lower() or w in h.lower().split() for h in HARD_LITERALS):
        return True
    # legend + globally-binding invariant block are DECODER metadata:
    # they are what makes the compressed form self-interpreting, so no word
    # in them may be removed even when stem-redundant elsewhere.
    if line_text.startswith("key:") or line_text.startswith("global"):
        return True
    # W5 behavioural laws must read exactly; they are the response contract.
    if line_text.startswith("execution law:") or line_text.startswith("response law:"):
        return True
    if re.match(r"^§\d+", line_text) and line_text.index(" ") > len(line_text) - 1:
        return True
    return False


def optimize(comp_path: str, out_path: str, max_passes: int = 8):
    _init_stopwords()
    lexpath = os.path.join(ROOT, "tools", "lexicon.json")
    lex = {k: v for k, v in json.load(open(lexpath)).items() if not k.startswith("_")}

    text = open(comp_path, encoding="utf-8").read()
    doc = Doc(text)
    rendered = [("".join(t)).strip() for t in doc.lines]
    n_global = next(i for i, r in enumerate(rendered) if r.startswith("\u00a71 "))
    chk = Checker(os.path.join(ROOT, "source", "SOURCE_VERBATIM.md"), lex, doc, n_global)

    missing = chk.required - set().union(*chk.lstems) if chk.lstems else chk.required
    if missing or not chk.all_atoms_ok() or not chk.literals_ok():
        print("!! baseline violates constraints; refusing to optimize. missing:", sorted(missing)[:20])
        return None

    log = {"accepted": [], "rejected": [], "passes": []}
    start_tokens = token_count(doc.render())
    for p in range(max_passes):
        t0 = time.time()
        accepted = 0
        positions = doc.word_positions()
        positions.sort(key=lambda x: -len(ENC.encode(" " + x[2])))
        for (i, j, tok) in positions:
            if j >= len(doc.lines[i]) or doc.lines[i][j] != tok:
                continue
            # never delete the leading word of a line (clause head)
            if not any(t.strip() for t in doc.lines[i][:j]):
                continue
            line_text = "".join(doc.lines[i]).strip()
            if protected(tok, line_text):
                continue
            if chk.try_delete(i, j):
                accepted += 1
                log["accepted"].append({"pass": p, "line": i + 1, "token": tok})
            else:
                log["rejected"].append({"pass": p, "line": i + 1, "token": tok})
        cur = token_count(doc.render())
        log["passes"].append({"pass": p, "accepted": accepted, "tokens": cur,
                              "seconds": round(time.time() - t0, 1)})
        print(f"  pass {p}: accepted={accepted} tokens={cur} ({time.time()-t0:.1f}s)", flush=True)
        if accepted == 0:
            break

    final = doc.render()
    open(out_path, "w", encoding="utf-8").write(final if final.endswith("\n") else final + "\n")
    log["start_tokens"] = start_tokens
    log["final_tokens"] = token_count(final)
    log["rejected_count"] = len(log["rejected"])
    log["rejected"] = log["rejected"][:500]
    os.makedirs(os.path.join(ROOT, "evidence"), exist_ok=True)
    json.dump(log, open(os.path.join(ROOT, "evidence", "optimizer_log.json"), "w"), indent=1)
    print(f"optimizer: {start_tokens} -> {log['final_tokens']} tokens, "
          f"{len(log['accepted'])} deletions accepted, {log['rejected_count']} rejected")
    return out_path


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "compressed_v3.md")
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "build", "compressed_v4_opt.md")
    optimize(src, dst)

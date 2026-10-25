"""
forensic_core.py — Deterministic lexical/semantic instrumentation for the
OMNI-AUDIT prompt-compression mandate.

Provides:
  * normalization + conservative stemming (no aggressive conflation)
  * atomization of the source mandate into directive units
  * deterministic urgency/importance weighting (W1..W5) with cue provenance
  * content-stem extraction (the semantic invariant set)
  * explicit, auditable equivalence LEXICON (abbrev/synonym discharge)
  * coverage verification engine (source -> compressed isomorphism check)
  * token/char metrics (tiktoken o200k_base + cl100k_base)

Design law: a stem is only ever considered "covered" by (a) literal presence,
or (b) an explicitly declared LEXICON equivalence whose discharging token is
literally present in the compressed text. No fuzzy/probabilistic matching.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Dict, Iterable, List, Set, Tuple

# ----------------------------------------------------------------------------
# 0. Hashing / IO helpers
# ----------------------------------------------------------------------------

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------------
# 1. Tokenization + conservative stemming
# ----------------------------------------------------------------------------

STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "that", "this",
    "these", "those", "of", "to", "in", "on", "for", "from", "by", "with",
    "without", "as", "at", "into", "its", "it", "is", "are", "was", "were",
    "be", "been", "being", "can", "cannot", "could", "may", "might", "shall",
    "should", "will", "would", "must", "do", "does", "did", "done", "not",
    "no", "every", "each", "all", "any", "some", "only", "also", "such",
    "other", "others", "their", "there", "where", "when", "which", "who",
    "whom", "while", "both", "between", "across", "within", "during", "after",
    "before", "until", "unless", "upon", "about", "above", "below", "under",
    "over", "out", "up", "down", "per", "via", "etc", "e", "g", "i", "we",
    "you", "they", "them", "he", "she", "him", "her", "his", "one", "two",
    "three", "more", "most", "less", "least", "own", "same", "so", "too",
    "very", "just", "even", "ever", "never_stop",  # sentinel, 'never' is content
    "has", "have", "having", "had", "s", "t", "re", "ve", "ll", "d", "m",
    "wherever", "whenever", "however", "therefore", "thus", "hence",
}

IRREGULAR: Dict[str, str] = {
    "analyses": "analysis", "analyzes": "analysis", "analyze": "analysis",
    "analyzed": "analysis", "analyzing": "analysis", "analyzer": "analyzer",
    "analyzers": "analyzer", "analytic": "analysis",
    "indices": "index", "matrices": "matrix", "vertices": "vertex",
    "children": "child", "people": "person", "criteria": "criterion",
    "running": "run", "ran": "run", "runs": "run",
    "given": "give", "gave": "give", "taken": "take", "took": "take",
    "written": "write", "wrote": "write", "proven": "prove", "proved": "prove",
    "built": "build", "builds": "build", "building": "build",
    "made": "make", "making": "make", "makes": "make",
    "kept": "keep", "keeps": "keep", "keeping": "keep",
    "left": "leave", "lost": "lose", "met": "meet",
    "chosen": "choose", "chose": "choose",
}

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9+/_.\-]*|\d+")


def _strip_edges(tok: str) -> str:
    return tok.strip(".-_/+")


def stem(word: str) -> str:
    """Conservative symmetric normalizer.

    Symmetry law: inflected and base forms of the SAME lemma must collapse to
    one key (executed/execute -> execut), while distinct lemmas stay apart.
    Verified by tools/test_stemmer.py against the full corpus vocabulary.
    """
    w = unicodedata.normalize("NFKD", word).lower()
    w = _strip_edges(w)
    if not w:
        return ""
    w = IRREGULAR.get(w, w)

    def dedouble(b: str) -> str:
        if len(b) > 2 and b[-1] == b[-2] and b[-1] not in "sz":
            return b[:-1]
        return b

    # plurals
    if len(w) > 4:
        if w.endswith("ies"):
            w = w[:-3] + "y"
        elif w.endswith("sses"):
            w = w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is", "as", "os")):
        w = w[:-1]
    # verb forms
    if len(w) > 5 and w.endswith("ing"):
        w = dedouble(w[:-3]) or w
    elif len(w) > 4 and w.endswith("ed") and not w.endswith(("eed",)):
        w = dedouble(w[:-2]) or w
    if len(w) > 5 and w.endswith("ly"):
        w = w[:-2]
    # silent-e collapse (makes execute/executed, cache/caching symmetric)
    if len(w) > 4 and w.endswith("e"):
        w = w[:-1]
    return w


def tokens(text: str) -> List[str]:
    return [t for t in (_strip_edges(m.group(0)) for m in _WORD_RE.finditer(text)) if t]


STEMMED_STOPWORDS: Set[str] = set()


def _init_stopwords() -> None:
    STEMMED_STOPWORDS.update(STOPWORDS)
    for w in list(STOPWORDS):
        STEMMED_STOPWORDS.add(stem(w))


def content_stems(text: str) -> List[str]:
    if not STEMMED_STOPWORDS:
        _init_stopwords()
    out: List[str] = []
    for t in tokens(text):
        if t.lower() in STEMMED_STOPWORDS:
            continue
        s = stem(t)
        if not s or s in STEMMED_STOPWORDS:
            continue
        if len(s) == 1 and not s.isdigit():
            continue
        out.append(s)
        # hyphen/slash compounds also contribute their parts
        for part in re.split(r"[-/+_.]", s):
            p = stem(part)
            if p and p not in STEMMED_STOPWORDS and (len(p) > 1 or p.isdigit()):
                out.append(p)
    return out


def stem_set(text: str) -> Set[str]:
    return set(content_stems(text))


# ----------------------------------------------------------------------------
# 2. Atomization
# ----------------------------------------------------------------------------

SECTION_RE = re.compile(r"^(\d{1,2})\.\s+([A-Z][A-Z0-9 ,&/\u2194\u2192\-—]+)$")
BULLET_RE = re.compile(r"^-\s+(.*)$")
NUMITEM_RE = re.compile(r"^(\d{1,2})\.\s+(.*)$")
LABEL_RE = re.compile(r"^\*\*([A-Z][A-Z \-/]+):\*\*\s*(.*)$")
SENT_SPLIT_RE = re.compile(r"(?<=[.;])\s+(?=[A-Z\*\u2014])")


@dataclass
class Atom:
    aid: str
    section: str
    section_title: str
    kind: str            # label | directive | bullet | numitem | gate | pipeline | definition
    text: str
    weight: int
    weight_label: str
    cues: List[str] = field(default_factory=list)
    stems: List[str] = field(default_factory=list)
    anchors: List[str] = field(default_factory=list)   # compressed-line ids
    coverage: float = 0.0


WEIGHT_LABELS = {
    5: "W5/LAW-ABSOLUTE",
    4: "W4/PROHIBITION-OR-GATE",
    3: "W3/MANDATORY-BUILD",
    2: "W2/CONDITIONAL-APPLICABLE",
    1: "W1/ENUMERATED-DETAIL",
}

# Deterministic urgency cues, highest precedence first.
W5_CUES = [
    "execution law", "response law", "output contract", "hard stop",
    "do not declare", "never substitute", "cannot satisfy", "do not fabricate",
    "hard-stop", "final acceptance", "nothing conversational",
    "declare completion", "deliver functioning",
]
W4_CUES = [
    "gate:", "never", "do not", "must not", "cannot", "no unrelated",
    "no browser-key", "eliminate all", "prevent", "exclude", "reject",
    "not fabricated", "remain visible", "remain distinct", "fail verification",
    "without verification", "unless", "only",
]
W3_CUES = [
    "implement", "produce", "preserve", "execute", "maintain", "enforce",
    "establish", "generate", "validate", "resolve", "identify", "map ",
    "reconcile", "add ", "include", "measure", "treat ", "distinguish",
    "use ", "support", "ensure", "make ", "keep ", "provide", "investigate",
    "evaluate", "research", "inventory", "retain", "consolidate", "replace",
    "deliver", "integrate", "install", "configure", "mark ", "state-changing",
    "required classification", "both environments", "for every gate record",
]
W2_CUES = [
    "applicable", "where ", "when ", "if ", "wherever", "as applicable",
    "where available", "where required", "where supported", "where analyzable",
    "optional", "appropriate", "relevant", "supported",
]


def classify_weight(text: str, inherited: int = 0) -> Tuple[int, List[str]]:
    low = " " + text.lower().strip() + " "
    cues: List[str] = []
    w = 0
    for cue in W5_CUES:
        if cue in low:
            cues.append(f"W5:{cue.strip()}")
            w = max(w, 5)
    for cue in W4_CUES:
        if cue in low:
            cues.append(f"W4:{cue.strip()}")
            w = max(w, 4)
    for cue in W3_CUES:
        if cue in low:
            cues.append(f"W3:{cue.strip()}")
            w = max(w, 3)
    for cue in W2_CUES:
        if cue in low:
            cues.append(f"W2:{cue.strip()}")
            w = max(w, min(2, w) if w else 2)
    if w == 0:
        w = 1
        cues.append("W1:default-enumeration")
    w = max(w, inherited)
    if inherited:
        cues.append(f"INHERIT:{inherited}")
    return w, cues


def atomize(src: str) -> List[Atom]:
    atoms: List[Atom] = []
    section, title = "0", "PREAMBLE"
    lead_weight = 0
    counter = 0
    for raw in src.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        stripped = line.strip()
        plain = stripped.replace("**", "").strip()

        m = NUMITEM_RE.match(plain)
        if m and len(plain) < 90 and not plain.endswith("."):
            body = m.group(2).strip()
            letters = [c for c in body if c.isalpha()]
            if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.85:
                section, title = m.group(1), body
                lead_weight = 0
                atoms.append(_mk(section, title, "section", plain, 3,
                                 ["STRUCTURAL:section-header"], counter))
                counter += 1
                continue
        if re.match(r"^OMNI-AUDIT", plain):
            section, title = "0", "TITLE"

        kind = "directive"
        text = plain
        if plain.startswith("GATE:"):
            kind = "gate"
        elif LABEL_RE.match(stripped):
            kind = "label"
        elif BULLET_RE.match(stripped):
            kind = "bullet"
            text = BULLET_RE.match(stripped).group(1).replace("**", "").strip()
        elif NUMITEM_RE.match(plain):
            kind = "numitem"
            text = plain
        elif "→" in plain and plain.count("→") >= 2:
            kind = "pipeline"

        # lead-in weight inheritance: "Implement:", "Add applicable:", "Produce ONE ... containing:"
        if plain.endswith(":") and kind in ("directive", "label"):
            lead_weight, _ = classify_weight(plain)
            atoms.append(_mk(section, title, kind, text, lead_weight, ["LEAD-IN"], counter))
            counter += 1
            continue

        units = ([text] if kind in ("bullet", "gate", "pipeline", "label")
                 else SENT_SPLIT_RE.split(text))
        for u in units:
            u = u.strip()
            if len(u) < 3:
                continue
            inherit = lead_weight if kind in ("bullet", "numitem") else 0
            w, cues = classify_weight(u, inherit)
            atoms.append(_mk(section, title, kind, u, w, cues, counter))
            counter += 1
        if kind not in ("bullet", "numitem"):
            lead_weight = 0
    return atoms


def _mk(section, title, kind, text, w, cues, counter) -> Atom:
    return Atom(
        aid=f"A{counter:03d}.S{section}",
        section=section,
        section_title=title,
        kind=kind,
        text=text,
        weight=w,
        weight_label=WEIGHT_LABELS[w],
        cues=cues,
        stems=sorted(stem_set(text)),
    )


# ----------------------------------------------------------------------------
# 3. Equivalence LEXICON (explicit, auditable discharge of compressed forms)
#    compressed_token -> source stems it legitimately represents
# ----------------------------------------------------------------------------

LEXICON: Dict[str, List[str]] = {}


def load_lexicon(path: str) -> Dict[str, List[str]]:
    global LEXICON
    with open(path, "r", encoding="utf-8") as fh:
        LEXICON = json.load(fh)
    return LEXICON


# ----------------------------------------------------------------------------
# 4. Coverage verification engine
# ----------------------------------------------------------------------------

@dataclass
class CoverageReport:
    source_stems: int
    compressed_stems: int
    literal_hits: int
    lexicon_hits: int
    uncovered: List[str]
    stem_coverage: float
    atom_rows: List[dict]
    weak_atoms: List[dict]
    atom_coverage_min: float
    atom_coverage_mean: float
    weight_mass_preserved: Dict[str, float]


def expand_with_lexicon(comp_stems: Set[str], lexicon: Dict[str, List[str]]) -> Tuple[Set[str], Dict[str, str]]:
    """Return (expanded stem set, discharge provenance map)."""
    expanded = set(comp_stems)
    provenance: Dict[str, str] = {}
    for token, targets in lexicon.items():
        tstem = stem(token)
        present = tstem in comp_stems or token.lower() in comp_stems
        if present:
            for tgt in targets:
                ts = stem(tgt)
                if ts not in comp_stems:
                    provenance[ts] = token
                expanded.add(ts)
    return expanded, provenance


def verify(atoms: List[Atom], compressed: str, lexicon: Dict[str, List[str]],
           comp_lines: List[Tuple[str, str]], min_atom_cov: float = 0.70,
           global_line_ids: Set[str] | None = None,
           min_local_core: float = 0.50, window: int = 3,
           line_sections: List[str] | None = None) -> CoverageReport:
    comp_stems = stem_set(compressed)
    expanded, prov = expand_with_lexicon(comp_stems, lexicon)

    src_stems: Set[str] = set()
    for a in atoms:
        src_stems |= set(a.stems)

    uncovered = sorted(s for s in src_stems if s not in expanded)
    literal = sum(1 for s in src_stems if s in comp_stems)
    lexhits = sum(1 for s in src_stems if s not in comp_stems and s in expanded)

    line_expanded = []
    for lid, ltext in comp_lines:
        le, _ = expand_with_lexicon(stem_set(ltext), lexicon)
        line_expanded.append((lid, le))
    gids = global_line_ids or set()
    global_stems: Set[str] = set()
    for lid, le in line_expanded:
        if lid in gids:
            global_stems |= le

    rows, weak, covs = [], [], []
    n = len(line_expanded)
    for a in atoms:
        s = set(a.stems)
        if not s:
            continue
        glob_cov = len(s & expanded) / len(s)
        g_only = len(s & global_stems) / len(s)
        best_total, best_core, best_span = 0.0, 0.0, []
        allowed = None
        if line_sections is not None:
            allowed = [i for i in range(n) if line_sections[i] == a.section]
        for i in (allowed if allowed is not None else range(n)):
            acc: Set[str] = set()
            for w in range(window):
                if i + w >= n:
                    break
                if allowed is not None and (i + w) not in allowed:
                    break
                acc |= line_expanded[i + w][1]
                tot = len((s & (acc | global_stems))) / len(s)
                if tot > best_total:
                    best_total = tot
                    best_core = len(s & acc) / len(s)
                    best_span = [line_expanded[i][0], line_expanded[i + w][0]]
                elif tot == best_total and best_span:
                    core = len(s & acc) / len(s)
                    if core > best_core:
                        best_core = core
                        best_span = [line_expanded[i][0], line_expanded[i + w][0]]
            if best_total == 1.0 and best_core == 1.0:
                break
        hoisted = (g_only >= 1.0)
        if not best_span and hoisted:
            best_total, best_core = g_only, 0.0
        thresh = 0.85 if a.weight >= 4 else min_atom_cov
        ok = (best_total >= thresh) and (best_core >= min_local_core or hoisted) and not (s - expanded)
        a.anchors = best_span
        a.coverage = round(best_total, 4)
        covs.append(best_total)
        row = {"atom_id": a.aid, "section": a.section, "kind": a.kind,
               "weight": a.weight, "weight_label": a.weight_label,
               "coverage": round(best_total, 4), "local_core": round(best_core, 4),
               "global_only": round(g_only, 4), "hoisted": hoisted,
               "doc_coverage": round(glob_cov, 4), "anchors": best_span,
               "missing_global": sorted(s - expanded), "text": a.text}
        rows.append(row)
        if not ok:
            weak.append(row)

    mass: Dict[str, float] = {}
    for w in range(1, 6):
        tier = [r for r in rows if r["weight"] == w]
        if tier:
            th = 0.85 if w >= 4 else min_atom_cov
            okc = sum(1 for r in tier
                      if r["coverage"] >= th and (r["local_core"] >= min_local_core or r["hoisted"])
                      and not r["missing_global"])
            mass[WEIGHT_LABELS[w]] = round(okc / len(tier), 4)
    return CoverageReport(
        source_stems=len(src_stems), compressed_stems=len(comp_stems),
        literal_hits=literal, lexicon_hits=lexhits, uncovered=uncovered,
        stem_coverage=round((literal + lexhits) / max(1, len(src_stems)), 6),
        atom_rows=rows, weak_atoms=weak,
        atom_coverage_min=round(min(covs), 4) if covs else 0.0,
        atom_coverage_mean=round(sum(covs) / len(covs), 4) if covs else 0.0,
        weight_mass_preserved=mass)


# ----------------------------------------------------------------------------
# 5. Metrics
# ----------------------------------------------------------------------------

def token_counts(text: str) -> Dict[str, int]:
    out = {"chars": len(text), "words": len(text.split()), "lines": len(text.splitlines())}
    try:
        import tiktoken
        for name in ("o200k_base", "cl100k_base"):
            out[name] = len(tiktoken.get_encoding(name).encode(text))
    except Exception as exc:  # pragma: no cover
        out["tiktoken_error"] = str(exc)
    return out


def ratio_block(src: str, comp: str) -> Dict[str, object]:
    s, c = token_counts(src), token_counts(comp)
    r = {}
    for k in s:
        if isinstance(s[k], int) and isinstance(c.get(k), int) and s[k]:
            r[k] = {"source": s[k], "compressed": c[k],
                    "retained_pct": round(100 * c[k] / s[k], 2),
                    "reduction_pct": round(100 * (1 - c[k] / s[k]), 2)}
    return r


def to_jsonable(atoms: List[Atom]) -> List[dict]:
    return [asdict(a) for a in atoms]

#!/usr/bin/env python3
"""
verify_isomorphism.py — adversarial coverage verifier for the compressed mandate.

Checks, in order:
  V1 stem coverage      : every source content stem present literally or via LEXICON
  V2 atom coverage      : every directive atom anchored to >=1 compressed line
  V3 weight mass        : urgency tiers W1..W5 fully represented
  V4 invariant literals : numbers, status labels, named tools, pipelines, laws
  V5 structure          : all 14 sections + gates present
  V6 metrics            : char/token compression ratios

Exit status 0 only when V1..V5 are all clean.
"""
from __future__ import annotations
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forensic_core import (atomize, verify, load_lexicon, token_counts, ratio_block,
                           stem, stem_set, sha256_file, to_jsonable)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- V4 invariant literals that MUST survive compression verbatim -----------
REQUIRED_LITERALS = [
    "seven", "28", "SHA-256", "PASS", "FAIL", "BLOCKED", "SKIP", "INCOMPLETE",
    "CONFIRMED MATCH", "CONFIRMED MISMATCH", "UNRESOLVED", "NOT ANALYZED",
    "IMPLEMENTED+VERIFIED", "IMPLEMENTED+PARTIALLY_VERIFIED", "NOT_IMPLEMENTED",
    "NOT_APPLICABLE", "GitHub Actions", "CodeQL", "SARIF", "SBOM", "SCA",
    "IDOR", "a11y", "ZIP", "AST", "NUL", "JSON", "Markdown", "JavaScript",
    "TypeScript", "Python", "Go", "Rust", "ChatGPT", "Code Interpreter",
    "ONE", "ALL", "NEVER", "THREE", "execution law", "response law",
    "output contract", "hard stop",
]
REQUIRED_PIPELINES = [
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


def comp_line_index(text: str):
    out = []
    n = 0
    for raw in text.splitlines():
        if not raw.strip():
            continue
        n += 1
        out.append((f"L{n:03d}", raw.strip()))
    return out


def main(comp_path: str, emit: bool = True):
    src_path = os.path.join(ROOT, "source", "SOURCE_VERBATIM.md")
    src = open(src_path, encoding="utf-8").read()
    comp = open(comp_path, encoding="utf-8").read()
    lex = load_lexicon(os.path.join(ROOT, "tools", "lexicon.json"))
    lex = {k: v for k, v in lex.items() if not k.startswith("_")}

    atoms = atomize(src)
    lines = comp_line_index(comp)
    # globally-binding preamble = every line before the first section marker
    gids = set()
    for lid, txt in lines:
        if txt.startswith("§1 "):
            break
        gids.add(lid)
    secs, cur = [], "0"
    for lid, txt in lines:
        m = re.match(r"^§(\d+)\b", txt)
        if m:
            cur = m.group(1)
        secs.append(cur)
    rep = verify(atoms, comp, lex, lines, global_line_ids=gids, line_sections=secs)

    # V4 literals
    low = comp.lower()
    missing_lit = [l for l in REQUIRED_LITERALS if l.lower() not in low]
    # V4b pipelines in order
    broken_pipes = []
    for pipe in REQUIRED_PIPELINES:
        pos, ok = -1, True
        for seg in pipe:
            i = low.find(seg.lower(), pos + 1)
            if i < 0 or i < pos:
                ok = False
                broken_pipes.append({"pipeline": " -> ".join(pipe), "failed_at": seg})
                break
            pos = i
        _ = ok
    # V5 structure
    missing_sections = [f"§{i}" for i in range(1, 15) if f"§{i} " not in comp and f"§{i}\n" not in comp]
    gate_lines = [l for _, l in lines if l.startswith("G ") or l.startswith("G:")]
    src_gates = len(re.findall(r"\*\*GATE:\*\*", src))

    metrics = ratio_block(src, comp)
    verdict = {
        "V1_stem_coverage": {
            "source_stems": rep.source_stems, "literal": rep.literal_hits,
            "lexicon": rep.lexicon_hits, "coverage": rep.stem_coverage,
            "uncovered_count": len(rep.uncovered), "uncovered": rep.uncovered,
            "status": "PASS" if not rep.uncovered else "FAIL"},
        "V2_atom_coverage": {
            "atoms": len(rep.atom_rows), "mean": rep.atom_coverage_mean,
            "min": rep.atom_coverage_min, "weak_count": len(rep.weak_atoms),
            "global_scope_lines": sorted(gids),
            "hoisted_atoms": sum(1 for r in rep.atom_rows if r["hoisted"]),
            "status": "PASS" if not rep.weak_atoms else "FAIL"},
        "V3_weight_mass": {"fully_covered_by_tier": rep.weight_mass_preserved,
                           "status": "PASS" if all(v == 1.0 for v in rep.weight_mass_preserved.values()) else "FAIL"},
        "V4_literals": {"missing": missing_lit, "broken_pipelines": broken_pipes,
                        "status": "PASS" if not missing_lit and not broken_pipes else "FAIL"},
        "V5_structure": {"missing_sections": missing_sections,
                         "gates_source": src_gates, "gates_compressed": len(gate_lines),
                         "status": "PASS" if not missing_sections and len(gate_lines) >= src_gates else "FAIL"},
        "V6_metrics": metrics,
    }
    overall = all(verdict[k]["status"] == "PASS" for k in list(verdict)[:5])
    verdict["OVERALL"] = "PASS" if overall else "FAIL"

    if emit:
        os.makedirs(os.path.join(ROOT, "evidence"), exist_ok=True)
        tag = os.path.basename(comp_path).replace(".md", "")
        json.dump(verdict, open(os.path.join(ROOT, "evidence", f"verdict_{tag}.json"), "w"), indent=1)
        json.dump(rep.atom_rows, open(os.path.join(ROOT, "evidence", f"atom_ledger_{tag}.json"), "w"), indent=1)
        print(json.dumps({k: (v if k != "V1_stem_coverage" else
                              {**v, "uncovered": v["uncovered"][:400]}) for k, v in verdict.items()}, indent=1))
        if rep.weak_atoms:
            print("\n--- WEAK ATOMS (coverage below threshold) ---")
            for w in rep.weak_atoms[:60]:
                print(f"  {w['atom_id']} W{w['weight']} total={w['coverage']} core={w['local_core']} glob_only={w['global_only']} span={w['anchors']}\n     missing={w['missing_global']}\n     {w['text'][:150]}")
    return 0 if overall else 1


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "compressed_v1.md")
    sys.exit(main(path))

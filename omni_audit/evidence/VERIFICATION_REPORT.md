# OMNI-AUDIT compression — verification evidence

**Deliverable:** `OMNI-AUDIT_COMPRESSED.md`
**Verdict:** `PASS` — independent verifier exit code `0` (0 = all gates pass)

| artefact | SHA-256 |
|---|---|
| source (verbatim, `&amp;`→`&` normalised) | `d2dac122274b571524321d2a88050888b3207a7c9238dc62a208f6c08de3bf3c` |
| compressed deliverable | `f623f13e93116f5868dda554b32383fc20c985b4d82dc8298506b2b0a4fb1efc` |

---

## 1. What was executed

A six-stage pipeline, all of it run in-sandbox (Python 3.13 + `tiktoken`), not described:

1. **Atomisation** — the mandate was parsed into **199 directive atoms**
   (sections, labels, numbered items, bullets, gates, pipelines) carrying
   **777 distinct content stems**.
2. **Urgency weighting** — every atom scored W1–W5 from deterministic lexical cues
   (`GATE:`, `NEVER`, `Do not`, `unless`, `applicable`, imperative verbs, law blocks)
   with cue provenance recorded per atom, plus lead-in inheritance for bullet lists.
3. **Token economics measurement** — the compression format was chosen from measurements,
   not intuition (see §5).
4. **Compression** — iterative rewriting into a telegraphic, operator-delimited,
   section-anchored form with an explicit urgency legend and a globally-binding invariant block.
5. **Constraint-checked optimisation** — a greedy deletion optimiser hill-climbs on token
   count, accepting a deletion only when the full isomorphism constraint set still holds.
   It ran to a fixed point (56 accepted, 0 rejected in the final configuration).
6. **Adversarial verification** — an independent verifier re-derives every claim from the
   two files alone and exits non-zero on any failure.

## 2. Isomorphism gates (all PASS)

| gate | test | result |
|---|---|---|
| V1 stem coverage | every one of the 777 source content stems present (literally or via an audited lexicon entry) | **PASS** — 777/777, uncovered `[]` |
| V2 directive anchoring | each of 199 atoms carried **inside its own section** (§N→§N), mean/min window coverage | **PASS** — mean 0.9959, min 0.8, weak 0 |
| V3 urgency tiers | W1–W5 mass fully preserved | **PASS** |
| V4 literals + pipelines | status tokens, classifications, tool names, numerals, and all 4 ordered `→` chains intact and in order | **PASS** |
| V5 structure | 14 sections + 11 gates present | **PASS** |

### Urgency/importance preservation

| tier | atoms | fully preserved | mean anchor coverage | tier mass |
|---|---|---|---|---|
| W1/ENUMERATED-DETAIL | 6 | 6/6 | 1.000 | 100% |
| W2/CONDITIONAL-APPLICABLE | 3 | 3/3 | 1.000 | 100% |
| W3/MANDATORY-BUILD | 140 | 140/140 | 0.997 | 100% |
| W4/PROHIBITION-OR-GATE | 33 | 33/33 | 0.991 | 100% |
| W5/LAW-ABSOLUTE | 17 | 17/17 | 0.997 | 100% |

The compressed text encodes these weights structurally (declared once in its `key:` line)
rather than restating them per directive: plain line = W3 build, `x` = W4 prohibition,
`G` = W4 blocking gate, `applicable/where/if` = W2 conditional, §14 + output contract +
execution/response law = W5 override. That is the only added metadata, and it is what makes
the urgency weighting recoverable from the compressed text alone.

## 3. Measured compression

| unit | source | compressed | reduction | retained |
|---|---|---|---|---|
| chars | 20,140 | 19,111 | **−5.1%** | 94.9% |
| words | 2,320 | 2,173 | **−6.3%** | 93.7% |
| lines | 291 | 114 | **−60.8%** | 39.2% |
| o200k_base | 3,491 | 2,928 | **−16.1%** | 83.9% |
| cl100k_base | 3,504 | 2,924 | **−16.6%** | 83.5% |

Per-section token budget (source → compressed):

| section | source | compressed | Δ |
|---|---|---|---|
| §0 | 203 | 265 | +62 |
| §1 | 238 | 185 | -53 |
| §2 | 237 | 181 | -56 |
| §3 | 246 | 184 | -62 |
| §4 | 240 | 187 | -53 |
| §5 | 274 | 214 | -60 |
| §6 | 274 | 222 | -52 |
| §7 | 151 | 112 | -39 |
| §8 | 302 | 233 | -69 |
| §9 | 181 | 154 | -27 |
| §10 | 169 | 142 | -27 |
| §11 | 335 | 259 | -76 |
| §12 | 181 | 130 | -51 |
| §13 | 239 | 213 | -26 |
| §14 | 325 | 263 | -62 |

§0 is larger by design: it holds the urgency legend and the globally-binding invariant block
that let all 14 sections drop their repeated qualifiers.

## 4. Why this is the frontier (ablation)

The same optimiser with the isomorphism constraints removed reaches **1459 tokens
(41.8% of source)** — but it demonstrably destroys directives.
Artefact: `build/ablation_free_optimizer.md`.

| words kept | strict (delivered) | unconstrained (rejected) |
|---|---|---|
| 6% | `global, binds every section: build executable code and execute it, never descr` | `global, executed functionality` |
| 17% | `preserve input provenance + original hashes.` | `preserve` |
| 21% | `both environments share compatible: source normalization+fingerprinting; stati` | `both normalization+fingerprinting; API-contract evidence/finding schemas;` |
| 21% | `key: plain=W3 must build; x=W4 forbidden absolute; G=W4 gate, that stage fails` | `key: gate, output contract execution law` |
| 24% | `treat every analyzer as executable integration declaring explicit availability` | `treat check inputs limits` |
| 25% | `record per gate: ID | applicability | prerequisites | source evidence | execut` | `record ID applicability procedure outcome cause unresolved dependencies` |

Unconstrained optimisation satisfies global word-presence while silently relocating meaning
across sections. That is why the delivered constraint model requires **section-local anchoring**
plus **monotone non-degradation** of each atom's own anchor.

## 5. Format decisions, each forced by measurement

| hypothesis | measurement | decision |
|---|---|---|
| abbreviate frequent words (`verification`→`V`, `evidence`→`EV`) | every frequent term is already **1 token**; abbreviations save **0**, several cost **+1** (`authz`, `anlz`) | rejected — full words kept |
| ALL-CAPS headers | `EVIDENCE` = 3 tokens vs `evidence` = 1 | lowercase everywhere except required literals |
| comma-separated enumerations | `", "` costs **+1 token per boundary** | space/`+`/`/` separated |
| markdown bold + bullet prefixes | `**GATE:**` = 4 tokens vs `G` = 1; `"- "` = +1/line | stripped |
| tighten operator spacing (`" + "`→`"+"`) | **+30 tokens** (worse) | spaced operators kept |
| delete glue words | safe and cheap | 56 deletions accepted at fixed point |

## 6. Source → compressed map (sample; full map in `atom_ledger.csv`)

| atom | W | anchor | cov | source directive | compressed carrier |
|---|---|---|---|---|---|
| A004.S0 | W5 | L005-L007 | 0.9524 | OUTPUT CONTRACT: Deliver functioning, tested source code and its ver | mode: source-first → forensic reconciliation → architectural integra |
| A008.S1 | W4 | L009-L011 | 1.0 | Never infer superiority from filenames, timestamps, file size, or ve | inventory+inspect ALL seven original omni-audit files + forensic bun |
| A011.S1 | W4 | L011-L013 | 1.0 | Retain the existing GitHub Actions orchestration architecture unless | x infer superiority from filename timestamp file size version label. |
| A014.S1 | W4 | L013-L015 | 1.0 | Consolidate overlapping implementations only after confirming behavi | establish latest verified canonical baseline; retain existing GitHub |
| A017.S1 | W4 | L014-L016 | 1.0 | Never treat previous audit conclusions or test claims as proof witho | map every distinct capability dependency defect regression unresolve |
| A018.S1 | W4 | L015-L017 | 1.0 | GATE: Every source and ledger finding is accounted for; canonical se | consolidate overlapping implementations only after confirming behavi |
| A029.S2 | W4 | L019-L021 | 1.0 | Minimal sufficient changes to established functionality; no unrelate | preserve+strengthen existing execution chain: repository discovery → |
| A030.S2 | W4 | L020-L022 | 0.9375 | GATE: Original functional contracts remain intact; integrated capabi | shared bounded content-addressed source analysis rather than redunda |

## 7. Reproduce

```bash
cd omni_audit
python3 tools/test_stemmer.py                              # 0 morphological asymmetries
python3 tools/verify_isomorphism.py build/compressed_v10.md # all gates, exit 0
python3 tools/build_release.py                             # deliverable + evidence + manifest
OMNI_ABLATION=1 python3 tools/optimize.py build/compressed_v6.md build/ablation_free_optimizer.md
```

Integrity for every file: `evidence/MANIFEST.sha256`.

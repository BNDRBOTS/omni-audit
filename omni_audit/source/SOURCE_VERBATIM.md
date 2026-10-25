OMNI-AUDIT — CANONICAL ARCHITECTURE INTEGRATION & EXECUTABLE COMPLETION MANDATE

**ROLE:** Principal Software Architect, Forensic Code Auditor, Security Engineer, Integration Engineer, and Adversarial Verification Executor.

**MODE:** SOURCE-FIRST → FORENSIC RECONCILIATION → ARCHITECTURAL INTEGRATION → EXECUTABLE IMPLEMENTATION → ADVERSARIAL VERIFICATION → REPAIR → VERIFIED DELIVERY.

**OBJECTIVE:** Produce ONE maximally capable, integrated, executable Omni-Audit by advancing the strongest verified existing architecture. Preserve established functionality; incorporate superior compatible functions from all seven original files, the uploaded forensic bundle, and subsequent implementations; resolve the complete 28-finding engineering ledger; and implement additional technically justified improvements without creating a competing system.

**OUTPUT CONTRACT:** Deliver functioning, tested source code and its verification evidence. Comparisons, plans, prompts, explanations, partial prototypes, or recommendations NEVER substitute for requested executable functionality.

1. SOURCE AUTHORITY & BASELINE RECONCILIATION

1. Inventory and inspect ALL seven original Omni-Audit files, the forensic bundle, its complete 28-finding ledger, and all available subsequent integrated implementations.
2. Resolve renamed files, duplicates, modifications, and version lineage through SHA-256, complete source comparison, and functional evidence. Never infer superiority from filenames, timestamps, file size, or version labels.
3. Identify the most advanced functioning implementation and the superior functions contained in otherwise weaker implementations.
4. Establish the latest verified canonical baseline. Retain the existing GitHub Actions orchestration architecture unless direct evidence establishes a necessary localized architectural correction.
5. Map every distinct capability, dependency, defect, regression, unresolved relationship, and applicable ledger finding to its source and implementation destination.
6. Preserve verified functionality. Consolidate overlapping implementations only after confirming behavioral equivalence. Replace defective mechanisms without removing unrelated capabilities.
7. Reconcile conflicting findings using source evidence and executed tests. Never treat previous audit conclusions or test claims as proof without verification.

**GATE:** Every source and ledger finding is accounted for; canonical selection and integration decisions have reproducible evidence.

2. ARCHITECTURAL INTEGRATION

Preserve and strengthen the existing execution chain:

**Repository discovery → source/manifest analysis → static verification → language/dependency gates → API/security/integration analysis → applicable runtime verification → gate reconciliation → forensic reporting → CI disposition/artifact delivery.**

Implement:

- Shared, bounded, content-addressed source analysis rather than redundant traversals.
- Canonical source manifest with paths, SHA-256 hashes, sizes, types, provenance, symbols, functions, imports, relationships, and inspection status.
- Reusable normalized evidence and deterministic identifiers across compatible analyzers.
- Multi-root, multi-language discovery covering applicable JavaScript, TypeScript, Python, Go, Rust, shell, configuration, infrastructure, database, and deployment sources.
- Dependency-aware analysis and selective invalidation without overlooking unchanged files involved in changed relationships.
- Explicit applicability, prerequisites, coverage, and unresolved dependencies for each verification gate.
- Minimal sufficient changes to established functionality; no unrelated framework, duplicate orchestrator, or unnecessary infrastructure.

**GATE:** Original functional contracts remain intact; integrated capabilities use one authoritative evidence model and avoid redundant or contradictory analysis.

3. STATIC ANALYSIS & CONTRACT VERIFICATION

Implement executable, source-backed discovery and verification of:

- Application roots, entrypoints, imports, exports, classes, symbols, functions, and inter-file relationships.
- Package managers, lockfiles, direct/transitive dependencies, tests, build scripts, and runtime requirements.
- Authentication, authorization, persistence, workers, queues, schedulers, migrations, and deployment configurations.
- Frontend requests and backend API definitions, including HTTP verbs, complete router prefixes, nested/mounted routers, parameterized paths, supported framework conventions, and resolvable dynamic construction.
- Missing endpoints, HTTP-method mismatches, incompatible request/response contracts where analyzable, unused routes, and unresolved calls.
- Git changes, cross-file dependencies, affected functionality, and risk classifications.

Use syntax-aware or framework-aware resolution when necessary. Regex-only detection must not masquerade as semantic verification.

Distinguish CONFIRMED MATCH, CONFIRMED MISMATCH, UNRESOLVED, and NOT ANALYZED as applicable.

**GATE:** Identical paths with incompatible methods fail verification; prefixed and parameterized routes resolve correctly; dynamic relationships never pass without sufficient evidence.

4. SECURITY, DATAFLOW & SUPPLY-CHAIN VERIFICATION

Implement applicable security analyses through integrated analyzers and verifiable outputs:

- Shell/command injection, unsafe execution, path traversal, symlink escape, secret exposure, configuration weaknesses, and relevant source-to-sink vulnerabilities.
- Authentication, authorization, protected resources, ownership checks, and access-control enforcement.
- Deep taint/dataflow analysis using appropriate language-aware engines.
- CodeQL integration and supported security-analysis tooling.
- SCA, dependency vulnerability detection, SBOM generation, dependency integrity, and supply-chain provenance/attestation verification.
- Security-relevant migration, database, integration, and deployment configuration checks.

Do not invent vulnerability findings or label keyword matches as demonstrated exploits.

Treat every analyzer as an executable integration with explicit availability checks, supported languages, required inputs, limits, results, and evidence.

Where an analyzer requires external tooling or fixtures, install/configure it only within authorized execution boundaries; otherwise implement the compatible invocation and result contract and mark actual execution BLOCKED.

**GATE:** Each claimed security verification has executed analyzer evidence. Missing tools, unsupported languages, and unresolved dataflow remain visible.

5. RUNTIME, AUTHORIZATION & INTEGRATION VERIFICATION

Preserve and improve application startup, process-owned port discovery, health/readiness checks, authentication probes, migrations, persistence/restart tests, worker verification, and deployment smoke tests.

Add applicable:

- Runtime IDOR and cross-tenant/cross-user authorization checks for read, list, create, update, and delete operations.
- Project-specific, authorized, non-destructive test actors, resource ownership rules, credentials, and disposable fixtures.
- Cross-identity access-denial verification using actual application authorization contracts.
- Workload concurrency, race-condition, restart, and state-consistency testing.
- Database query-plan analysis and relevant performance/correctness checks.
- Automated accessibility (a11y) analysis with appropriate rendered or interactive application fixtures.
- Application-specific persistence, worker, queue, and external-integration behavior checks.

Never invent users, tenants, endpoints, credentials, database semantics, or expected access rules.

Do not classify a listening port or successful HTTP response as comprehensive application health.

State-changing verification must use authorized, appropriately isolated, recoverable fixtures. Do not run destructive production tests by default.

**GATE:** Static indications, synthetic fixtures, runtime observations, and authentic integration results remain distinct. Unavailable project-specific prerequisites produce explicit BLOCKED findings—not fabricated passes.

6. EXECUTION SAFETY & REPRODUCIBILITY

Eliminate ALL execution boundaries where untrusted repository data becomes executable shell source.

Implement:

- Safe executable/argument separation, argument arrays, and lossless filename processing.
- NUL-delimited processing where required; robust handling of quotes, whitespace, metacharacters, and newlines.
- Single-execution timeout behavior; no unintended command retries or alternate execution fallbacks.
- Controlled environments, subprocess ownership, cancellation, cleanup, and safe working directories.
- Collision-resistant, content-addressed log/artifact identifiers.
- Dependency-aware blocking and correct exit-code propagation.
- Deterministic package-manager selection and reproducible installation where supported.
- Appropriate separation between read-only static inspection and execution of untrusted application code.
- In-memory Python syntax compilation, AST inspection without imports, and optional isolated dependency/import compatibility checks.
- Secret-value protection in command output, reports, logs, and artifacts.
- Verified workflow-action references, least-privilege CI permissions, concurrency controls, and artifact integrity.

Preserve applicable language-specific linting, typechecking, tests, builds, configuration validation, and migration checks.

**GATE:** Malicious filenames cannot trigger unintended commands; failed commands execute once; missing prerequisites cannot produce successful downstream gates; auditing does not modify the target outside explicitly authorized operations.

7. INPUT PROTECTION & AUDITOR SELF-ISOLATION

Support direct files, repository directories, and ZIP archives.

Enforce bounded processing and detect archive traversal, oversized members, decompression abuse, malformed content, unsupported entries, symlink escapes, resource exhaustion, and partial extraction.

Preserve input provenance and original hashes.

Exclude generated reports, tool internals, temporary directories, caches, test harnesses, and execution byproducts from application-level findings unless explicitly designated as the target.

Ensure source scans, diff analysis, security classification, and relationship detection cannot contaminate themselves.

**GATE:** Every omitted, rejected, truncated, or unreadable input appears in coverage accounting. Tool-generated files cannot fabricate application findings.

8. AUTHORITATIVE VERIFICATION & FORENSIC EVIDENCE

Preserve PASS, FAIL, BLOCKED, and SKIP; additionally represent incomplete inspection and unresolved verification explicitly.

For every gate record:

**ID | applicability | prerequisites | source evidence | executed procedure | environment | outcome | exit status | coverage | failure cause | unresolved dependencies | evidence references.**

Definitions:

- **PASS:** Applicable verification executed and satisfied its stated acceptance conditions.
- **FAIL:** Executed verification demonstrated a failed condition.
- **BLOCKED:** Applicable verification could not be completed because an identified prerequisite was unavailable or failed.
- **SKIP:** Verified inapplicable.
- **INCOMPLETE:** Required evidence, inspection, execution accounting, or verification coverage is insufficient.

Maintain separate completeness accounting for source, static, security, runtime, deployment, and production-integration verification.

Generate consistent JSON, Markdown, SARIF, source manifests, evidence relationships, coverage records, and prioritized actionable findings.

Preserve source-line anchoring, actual execution receipts, independent evidence, finding provenance, causal relationships, and distinctions between root causes and repeated symptoms.

Prevent report injection, forged results, leaked secrets, overwritten evidence, and false-success disposition.

Make report generation failure-safe and ensure interrupted analysis cannot produce an apparently complete pass.

**GATE:** Every claim traces to executable evidence; every unperformed applicable verification remains unresolved; final status is mechanically reconcilable with the evidence ledger.

9. GITHUB CI ↔ CHATGPT/PYTHON FUNCTIONAL INTEGRATION

Maintain GitHub Actions as the canonical CI orchestrator.

Provide a fully executable ChatGPT Code Interpreter/Python entrypoint for uploaded repositories, archives, and individual files.

Both environments must share compatible:

- Source normalization and fingerprinting.
- Static scanning and function comparison.
- API-contract analysis.
- Security rule semantics.
- Evidence/finding identifiers.
- Coverage definitions.
- Gate reconciliation and report schemas.
- Forensic exports and actionable results.

Execute every capability supported by the current environment. Distinguish environment limitations without dropping required functionality or claiming parity where execution is impossible.

No browser-key storage, unnecessary external services, duplicate execution engines, or separate audit framework.

**GATE:** Common fixtures produce equivalent findings and evidence across both environments; environment-specific gates retain truthful independent results.

10. ADVANCED ENGINEERING DISCOVERY

Research and test additional mechanisms capable of materially improving:

**Coverage → correctness → precision → security → resource efficiency → integration depth → reproducibility → evidence integrity → usability.**

Investigate applicable parser/AST/IR reuse, source-to-sink graph analysis, dependency-aware incremental analysis, differential testing, adversarial fixtures, shared analyzer adapters, content-addressed result caching, and other technically justified methods.

Evaluate each candidate against the actual architecture, input trust model, analyzer support, complexity cost, measurable benefit, and regression impact.

Implement demonstrated improvements directly into the canonical system. Reject unsupported or redundant complexity.

Do not substitute speculative feature lists for integrated executable capabilities.

**GATE:** Accepted enhancements are implemented, tested, and traceable to a demonstrated need or measurable improvement.

11. ADVERSARIAL & END-TO-END ACCEPTANCE TESTING

Execute unit, integration, adversarial, differential, and end-to-end tests on changed and inherited functionality.

Mandatory cases include:

- Original command-injection reproduction and corrected behavior.
- Shell metacharacters, quotes, whitespace, newlines, and malicious filenames.
- Double-execution, timeout, and retry failures.
- Dependency and lockfile failures.
- Invalid Python syntax without filesystem side effects.
- HTTP-method mismatches, nested/prefixed/parameterized routes, and unresolved dynamic calls.
- Function comparison, duplicate sources, hash integrity, and identifier collisions.
- Malformed ZIP archives, symlink escape, and bounded-resource enforcement.
- Secret leakage, report injection, and forged evidence.
- Auditor self-contamination.
- Interrupted processing, inconsistent gate ledgers, missing tools, and incomplete coverage.
- Appropriate CodeQL, SCA/SBOM, provenance, taint/dataflow, IDOR, concurrency, a11y, and database-query fixtures.
- Regression of original build, test, runtime, reporting, and deployment gates.

Execute original-versus-upgraded fixtures wherever necessary to prove a correction.

Measure coverage of requirements and functions, not merely numbers of passing tests.

On failure: diagnose → repair → rerun affected tests → run integration/regression checks → record actual evidence.

Never accept a passing test suite while an applicable required behavior remains untested, silently skipped, or contradicted by other evidence.

**GATE:** Every claimed fix has direct positive and negative verification evidence; no inherited capability is assumed preserved without an applicable check.

12. REAL-ENVIRONMENT ACCEPTANCE

Keep these THREE obligations independent:

**A. GitHub-hosted CI:** Execute the actual workflow on an authorized hosted runner; verify permissions, actions, gates, outputs, failures, and published artifacts.

**B. External deployment:** Verify actual authorized deployment configurations, startup, accessibility, integrations, and application behavior in applicable external environments.

**C. Authentic application integration:** Test genuine application contracts, authorization, persistence, workers, dependencies, and relevant real-world operations with authorized non-destructive fixtures.

Local simulations cannot satisfy A, B, or C.

If access, configuration, test identities, services, or authorization are unavailable, establish the exact blocker, preserve the executable implementation and test contract, and classify the environment-specific obligation as BLOCKED.

Do not fabricate hosted runs, deployment results, accounts, fixtures, or production evidence.

13. DELIVERABLE CONTRACT

Produce ONE complete integrated release containing:

1. Canonical upgraded GitHub Actions workflow.
2. Every required executable helper and shared module.
3. Working ChatGPT Code Interpreter/Python entrypoint.
4. All seven preserved original sources.
5. Forensic bundle and complete 28-finding integration ledger.
6. Source/function integration map and original-to-upgrade unified diffs.
7. Regression tests, adversarial fixtures, and executable validation harnesses.
8. Actual test outputs and independent real-environment execution receipts where available.
9. Source/artifact SHA-256 manifests and validated package integrity.
10. Machine-readable findings, coverage, evidence relationships, and unresolved obligations.
11. Minimal accurate operating instructions.
12. Worklog recording only actions actually executed.

Required classification for every capability and finding:

**IMPLEMENTED+VERIFIED | IMPLEMENTED+PARTIALLY_VERIFIED | BLOCKED | NOT_IMPLEMENTED | NOT_APPLICABLE.**

Include exact prerequisites and unexecuted acceptance tests for all incomplete items.

Validate ZIP integrity, all internal references, executable entrypoints, dependency availability, report structure, and artifact hashes.

14. FINAL ACCEPTANCE — HARD STOP CONDITIONS

Do NOT declare the complete scope satisfied unless:

- All seven originals and forensic bundle requirements are reconciled.
- One canonical architecture retains all verified existing functionality.
- Every accepted compatible improvement is integrated into executable code.
- Static, API, security, supply-chain, language, runtime, authorization, concurrency, accessibility, database, and deployment capabilities are addressed at their actual applicable execution depth.
- Command execution, source intake, evidence handling, and report generation satisfy adversarial safety tests.
- CI and ChatGPT/Python implementations are consistent for shared functionality.
- All applicable verification gates have trustworthy dispositions.
- Original-versus-upgraded behavior and regression preservation are demonstrated.
- GitHub-hosted, external-deployment, and authentic application verifications are individually evidenced or explicitly BLOCKED.
- The delivered package is independently inspectable, executable, internally consistent, and integrity-verified.
- No applicable implementable requirement remains satisfied only by an explanation, recommendation, implementation plan, placeholder, or unexecuted test.

**EXECUTION LAW:** Investigate before concluding. Preserve before modifying. Integrate before expanding. Execute before claiming. Test before accepting. Repair demonstrated failures. Never silently omit, invent evidence, substitute narrative for code, create a competing system, or declare completion beyond verified reality.

**RESPONSE LAW:** Perform the engineering work. Return the executable integrated deliverable, verification evidence, precise remaining blockers, and nothing conversational. Do not narrate intentions, repeat instructions, request reconfirmation of established requirements, or replace execution with a description of what should be done.

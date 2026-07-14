# ECL: Closure-Aware Event Certification Framework

> **Release status:** version 1.0.0 public-interface release candidate. Keep the repository private until the release checklist, GitHub Actions matrix, and final legal/IP review are complete.
>
> **Rights boundary:** public visibility is intended for technical inspection, non-commercial evaluation, scholarly discussion, and citation. It grants no patent licence or unrestricted software rights. See `LICENSE`, `PATENT_NOTICE.md`, and `PUBLIC_RELEASE_BOUNDARY.md`.

ECL is an experimental framework for deterministic event certification, closure-aware transition control, append-only records, and residue-aware ledger prototypes.

Version 1.0.0 stabilizes the public Python package, command-line interface, output structures, and documented closure-before-commit decision model. It does not convert the research model into independently validated physics, audited cryptography, legal timestamping, or production infrastructure.

The public layer is governed by one rule:

```text
closure before commit
```

A transition is not marked commit-ready merely because a hash exists or an average error looks small. The closure engine separately checks normalized defect, seam rupture, phase locking, winding consistency, and orientation consistency before issuing a deterministic certificate.

## Public components

- **Closure engine:** five-component error vector with `COMMIT`, `HOLD`, and `REJECT` classifications.
- **Topological diagnostics:** winding mismatch and orientation mismatch are measured separately.
- **Native-ledger experiment:** deterministic paired comparison with canonical certificate hashes.
- **PRTP event certificate:** Root-Template-Phase event adapter with an explicit closure tolerance.
- **Machine-readable schema:** JSON Schema for closure certificates.
- **Tests and CI:** deterministic, bounded, hold-band, rupture, orientation, winding, command-surface, and release-boundary checks.

## Scientific levels

| Level | Meaning in this repository |
|---|---|
| Definition | A state, defect, residue, threshold, invariant, or certificate field is explicitly introduced. |
| Derivation | A result follows from declared definitions and assumptions. |
| Computational verification | Code and tests confirm behavior for declared fixtures and thresholds. |
| External observation | Data originate from a separately identified external system or experiment. |
| Independent validation | Independent evidence supports a broader mechanism or claim within stated uncertainty. |

The current ECL public package contains definitions, derivations, and computational verification. It does not convert a passing software certificate into independent physical, cryptographic, legal, or engineering validation. Computers remain tragically unable to confer truth by printing JSON.

## Event grammar

```text
LOAD Root -> MAP Template -> LINK Context -> RUN Phase -> AUDIT Closure -> COMMIT/HOLD/REJECT
```

## Quick start

Requirements: Python 3.10 or newer.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python tools/verify_public_release.py
```

Run the closure audit:

```bash
ecl-closure-audit --fixture bounded --output outputs/closure-certificate.json
```

Adversarial fixtures return exit code `2`, indicating a correctly generated non-commit certificate:

```bash
ecl-closure-audit --fixture rupture
ecl-closure-audit --fixture orientation
```

Run the additional public prototypes:

```bash
ecl-native-ledger --events 512 --seed 117 --out-dir outputs/native-ledger
ecl-prtp-demo --output outputs/prtp-demo.json
```

## Repository layout

```text
src/ecl/closure_engine.py              Closure-before-commit engine
src/ecl/native_ledger.py               Deterministic residue-ledger experiment
src/ecl/prtp.py                        Root-Template-Phase certificate prototype
tests/                                 Positive, boundary, and adversarial tests
schemas/ecl-closure-certificate-v1.schema.json
docs/CLOSURE_ENGINE.md                 Metrics and classification rule
docs/ARCHITECTURE.md                   Public model architecture
PUBLIC_RELEASE_BOUNDARY.md             Included and excluded publication layers
PATENT_NOTICE.md                       Patent-rights boundary
RELEASE_CHECKLIST.md                   Pre-public gates
RELEASE_NOTES_v1.0.0.md                Version 1.0.0 release summary
```

## Reproducibility

Certificates use SHA-256 over compact, sorted JSON. Identical samples, thresholds, and software versions produce identical certificate hashes. Each result should be cited by immutable release tag or exact commit.

## Publication author

Monty Dabas, Independent Researcher  
ORCID: 0009-0005-6948-209X

## Citation and licence

Citation metadata is provided in `CITATION.cff`. The controlled public-inspection terms are in `LICENSE`.

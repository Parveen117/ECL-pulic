# ECL: Public Research Preview

ECL is an experimental framework for deterministic event certification, append-only transition records, and residue-aware ledger prototypes.

This repository is a **source-available research preview**. It presents a compact, reproducible public surface without publishing the private provisional vault, patent drafts, internal proof chains, credentials, device designs, financial systems, or unpublished implementation material.

## What is included

- A deterministic native-ledger simulation with reproducible certificate hashes.
- A compact Root-Template-Phase (PRTP) event-certificate adapter.
- Unit tests and continuous-integration checks.
- Architecture and public-release scope notes.

## Research status

ECL is an exploratory model. Terms such as `Root`, `Template`, `Phase`, `Seam`, `Ledger`, and `G_UGD` are defined within this repository's model. Results produced by the code demonstrate the behavior of those definitions; they are not, by themselves, proof of a physical law, production-grade cryptographic security, legal timestamping, or independent scientific validation.

## Event grammar

```text
LOAD Root -> MAP Template -> LINK Context -> RUN Phase -> HALT Seam
```

The public prototype studies whether a transition can be represented by:

1. a preserved event identity (`Root`),
2. an allowed transition rule (`Template`),
3. contextual state (`Phase`),
4. a boundary correction (`Seam`), and
5. recorded residual memory (`Ledger`).

The model-defined closure ratio is:

```text
G_UGD = open_residue / raw_residue
```

## Quick start

Requirements: Python 3.10 or newer.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Run the native-ledger simulation:

```bash
ecl-native-ledger --events 512 --seed 117 --out-dir outputs/native-ledger
```

Run the PRTP certificate demo:

```bash
ecl-prtp-demo --output outputs/prtp-demo.json
```

The commands write machine-readable JSON and CSV artifacts with SHA-256 certificate hashes derived from canonical JSON payloads.

## Repository layout

```text
src/ecl/                 Core public implementation
examples/                Minimal runnable examples
tests/                   Reproducibility and policy tests
docs/ARCHITECTURE.md     Model and data-flow description
docs/PUBLIC_RELEASE_SCOPE.md
.github/workflows/ci.yml Python validation workflow
```

## Reproducibility

The native-ledger experiment uses a fixed pseudorandom seed by default. Identical code, configuration, and Python behavior should produce identical report content and certificate hashes. Generated output folders are intentionally ignored by Git.

## Security and interpretation

This repository is not a replacement for audited cryptographic libraries, digital-signature infrastructure, official filing receipts, or legal advice. See `SECURITY.md` and `docs/ARCHITECTURE.md` before adapting it to another system.

## Citation

Citation metadata is provided in `CITATION.cff`.

## License

Copyright © 2026 Parveen. All rights reserved. Public visibility does not grant an open-source or patent license. See `LICENSE`.

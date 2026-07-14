# ECL v1.0.0: Closure-Aware Event Certification Framework

ECL v1.0.0 is the first stable release of the bounded public software interface for closure-aware event certification.

The release stabilizes the public Python package, command-line tools, deterministic output structures, and the documented **closure-before-commit** decision rule. It is intended for technical inspection, reproducibility review, non-commercial evaluation, scholarly discussion, and citation under the repository's controlled public-inspection licence.

## Highlights

- Five-component closure error vector covering normalized closure defect, seam-rupture supremum, seam-rupture RMS, phase-lock residual, and topology mismatch.
- Explicit `COMMIT`, `HOLD`, and `REJECT` classifications.
- Separate winding-number and orientation-consistency diagnostics.
- Deterministic SHA-256 certificate and report fingerprints over canonical JSON.
- Closure-audit, native-ledger, and Root-Template-Phase command-line tools.
- Positive, bounded, hold-band, rupture, orientation, winding, zero-tolerance, and determinism tests.
- Complete public-command smoke testing across Python 3.10, 3.11, and 3.12.
- Public JSON Schema, claim-scope map, patent notice, transfer manifest, release boundary, and reproducibility verifier.

## Supported public commands

```bash
ecl-closure-audit --fixture bounded --output outputs/closure-certificate.json
ecl-native-ledger --events 512 --seed 117 --out-dir outputs/native-ledger
ecl-prtp-demo --output outputs/prtp-demo.json
```

The adversarial closure fixtures intentionally return exit code `2` after generating a valid `REJECT` certificate:

```bash
ecl-closure-audit --fixture rupture
ecl-closure-audit --fixture orientation
```

## Interpretation boundary

Version 1.0.0 stabilizes the public software interface. It does not establish a universal mathematical law, independently validated physical mechanism, audited cryptographic protocol, trusted timestamp, legal priority, production safety, or commercial readiness.

The certificate hash is a deterministic content fingerprint. It is not a digital signature or trusted timestamp.

## Rights boundary

The release is governed by the repository's controlled public-inspection licence and patent notice. Public access does not grant a patent licence, unrestricted redistribution right, commercial-use permission, device-development right, or permission to create derivative products.

## Citation

Publication author: **Monty Dabas, Independent Researcher**  
ORCID: **0009-0005-6948-209X**

Cite the immutable `v1.0.0` tag and its exact commit. Citation metadata is provided in `CITATION.cff`.

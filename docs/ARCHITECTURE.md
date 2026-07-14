# ECL Public Architecture

## 1. Purpose

The public ECL preview provides two small, auditable prototypes:

1. a deterministic comparison experiment for residue processing, and
2. an event certificate that separates exact hash agreement from policy-defined transition closure.

The code is intentionally dependency-free so that the model can be inspected without a framework hiding the arithmetic.

## 2. Core vocabulary

| Term | Public-model meaning |
|---|---|
| Root | Stable event identity and payload invariant |
| Template | Permitted transition rule |
| Phase | Context, timestamp, nonce, and optional memory state |
| Seam | Boundary between expected and observed states |
| Ledger | Recorded portion of residue after seam compensation |
| Open residue | Residue remaining after compensation and ledgering |
| `G_UGD` | `open_residue / raw_residue`, or zero when raw residue is zero |

These are repository-local definitions. They should not be silently substituted for established terms in physics, cryptography, or formal verification.

## 3. Native-ledger experiment

`src/ecl/native_ledger.py` generates paired conditions from the same pseudorandom seed:

```text
Root bits -> Template map -> Phase perturbation -> Observed state
```

The `native_on` condition applies configurable compensation and ledger fractions. The `native_off` condition retains the raw perturbation. The report stores every event row, aggregate values, configuration, an interpretation note, and a SHA-256 certificate hash.

The comparison is internal to this model. A positive result means the configured transformation behaved as defined; it does not establish superiority over external algorithms.

## 4. PRTP event certificate

`src/ecl/prtp.py` constructs an expected transition hash from Root, Template, and Phase data. It then records:

- exact hash agreement,
- normalized hash-character distance,
- seam compensation,
- ledger memory,
- open residue,
- closure ratio, and
- the explicit closure tolerance used to decide `native_pass`.

A mismatch is never accepted merely because `G_UGD < 1`. Acceptance requires the remaining open residue to be at or below the explicit tolerance carried in the policy. This keeps the decision visible and testable.

## 5. Certificate hashing

Certificate hashes use SHA-256 over canonical JSON with sorted keys and compact separators. They provide deterministic content fingerprints. They are not digital signatures and do not establish authorship, trusted time, or legal priority without an external signing and timestamping system.

## 6. Trust boundaries

The public preview does not include:

- key management,
- digital signatures,
- network consensus,
- adversarial validation,
- tamper-resistant storage,
- official timestamp authority integration,
- private vault logic, or
- patent-claim implementation details.

Any production adaptation must define those boundaries independently and undergo security review.

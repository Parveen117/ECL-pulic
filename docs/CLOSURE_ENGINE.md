# Advanced Closure Engine

## Purpose

The ECL closure engine evaluates a declared expected trajectory against an observed trajectory before a state transition is committed. Its governing rule is:

```text
closure before commit
```

The engine produces a deterministic certificate with an explicit five-component error vector, separate topological diagnostics, component-level pass flags, and a final `COMMIT`, `HOLD`, or `REJECT` classification.

## Declared measurements

For expected complex state `z_k` and observed state `y_k`, the pointwise closure defect is:

```text
D_k = y_k - z_k
```

The normalized defect is:

```text
N_k = |D_k| / max(|z_k|, epsilon)
```

The seam-rupture increment is:

```text
R_k = |D_k - D_(k-1)|
```

The engine reports the supremum and RMS of `R_k`. It also reports the RMS principal-angle residual between expected and observed phase trajectories.

## Five-component error vector

```text
E_closure = (
  max normalized closure defect,
  seam-rupture supremum,
  seam-rupture RMS,
  phase-lock residual,
  topology mismatch
)
```

`topology mismatch` is the maximum of:

- absolute winding-number mismatch; and
- orientation mismatch rate.

Winding mismatch and orientation mismatch are also retained separately in the certificate so the combined component does not conceal its cause.

## Decision rule

- `COMMIT`: every component is at or below its declared threshold.
- `HOLD`: topology is intact and every failing continuous component is within the declared hold band.
- `REJECT`: topology fails or at least one continuous component exceeds the hold band.

Only `COMMIT` sets `closure_before_commit = true`.

## Certificate integrity

The sample list and complete certificate payload are hashed using SHA-256 over compact, sorted JSON. These hashes are deterministic content fingerprints. They are not digital signatures, trusted timestamps, proof of authorship, or proof of legal priority.

## Scientific boundary

The engine establishes whether data pass this repository's declared definitions, metrics, and thresholds. Broader mathematical, physical, cryptographic, engineering, or legal conclusions require independent arguments and validation.

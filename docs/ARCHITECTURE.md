# ECL Public Architecture

## 1. Purpose

The advanced ECL public candidate contains three bounded prototypes:

1. a closure-before-commit trajectory auditor;
2. a deterministic residue-ledger comparison experiment; and
3. a Root-Template-Phase event certificate with explicit closure tolerance.

The implementation is dependency-free so the declared arithmetic and decision rules remain directly inspectable.

## 2. Closure-before-commit path

```text
Expected trajectory
        +
Observed trajectory
        |
        v
Pointwise closure defect
        |
        +--> normalized defect
        +--> seam-rupture increments
        +--> phase-lock residual
        +--> winding mismatch
        +--> orientation mismatch
        |
        v
Five-component error vector
        |
        v
COMMIT / HOLD / REJECT
        |
        v
Canonical JSON certificate + SHA-256 fingerprint
```

The five-component vector combines winding and orientation diagnostics into a topology-mismatch component while preserving both underlying values separately in the certificate.

## 3. Native-ledger experiment

The native-ledger module generates paired conditions from the same pseudorandom seed:

```text
Root bits -> Template map -> Phase perturbation -> Observed state
```

The native-on condition applies configurable compensation and ledger fractions. The native-off condition retains raw perturbation. The comparison is internal to the declared model and does not establish superiority over external algorithms.

## 4. PRTP event certificate

The PRTP module constructs an expected transition hash from Root, Template, and Phase data. It records exact hash agreement, normalized hash-character distance, seam compensation, ledger memory, open residue, closure ratio, and the explicit tolerance used for acceptance.

## 5. Certificate hashing

Certificate hashes use SHA-256 over compact JSON with sorted keys. They provide deterministic content fingerprints. They are not digital signatures and do not establish authorship, trusted time, consensus, non-repudiation, or legal priority.

## 6. Trust boundaries

The public candidate does not include key management, digital signatures, network consensus, hostile-input hardening, trusted timestamp authorities, private vault logic, complete patent-claim implementations, device fabrication details, or production safety assurance.

Any external adaptation must define those boundaries independently and undergo appropriate mathematical, scientific, security, engineering, and legal review.

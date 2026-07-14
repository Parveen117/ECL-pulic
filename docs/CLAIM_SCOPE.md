# Claim Scope and Falsification Map

## Public claim 1: deterministic certification

**Statement:** identical ordered samples, thresholds, and software version produce the same ECL certificate hash.

**Evidence:** `tests/test_closure_engine.py::test_certificate_is_deterministic`.

**Falsification condition:** two executions with identical inputs produce unequal certificate payloads or hashes.

**Boundary:** deterministic hashing does not establish trusted time, authorship, consensus, non-repudiation, or legal priority.

## Public claim 2: closure-before-commit classification

**Statement:** the closure engine emits `COMMIT` only when all five declared error-vector components pass their thresholds.

**Evidence:** `src/ecl/closure_engine.py`, exact and bounded positive fixtures, and boundary/adversarial unit tests.

**Falsification condition:** a certificate is marked commit-ready while any component-level pass flag is false.

**Boundary:** passing repository thresholds means only that the declared computational rule passed.

## Public claim 3: seam-rupture detection

**Statement:** a discontinuous change in the defect trajectory can exceed the rupture supremum or RMS threshold and block commit.

**Evidence:** `test_seam_rupture_rejects`.

**Falsification condition:** the declared rupture fixture remains commit-ready under the default thresholds.

## Public claim 4: topological consistency checks

**Statement:** winding mismatch or orientation mismatch contributes to topology mismatch and blocks commit when the topology threshold is zero.

**Evidence:** `test_winding_mismatch_rejects` and `test_orientation_mismatch_rejects`.

**Falsification condition:** a nonzero declared topology mismatch is classified `COMMIT` under a zero topology threshold.

## Claims not made by this release

This repository does not, by itself, establish:

- a universal mathematical law;
- a new physical interaction or material mechanism;
- production cryptographic security;
- legal timestamping or patent priority;
- safety, commercial readiness, or device validation;
- superiority to external event, consensus, control, or formal-verification systems.

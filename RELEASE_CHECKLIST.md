# ECL Advanced Public Release Checklist

The repository should remain private until every required pre-public gate is closed. A longer README is not a validation method, despite several centuries of institutional optimism.

## Scope and claims

- [x] Advanced public target is limited to closure-aware event certification and the existing bounded public prototypes.
- [x] Definition, derivation, computational verification, external observation, and independent validation are distinguished.
- [x] Public language avoids converting software output into universal mathematical, physical, cryptographic, or legal proof.
- [x] Technical naming is neutral; author attribution remains separate from framework terminology.

## Code and reproducibility

- [x] Closure engine provides normalized defect, rupture supremum, rupture RMS, phase-lock residual, winding mismatch, and orientation mismatch.
- [x] Five-component error vector and component-level thresholds are explicit.
- [x] `COMMIT`, `HOLD`, and `REJECT` decision paths have deterministic tests.
- [x] Certificate hashes are deterministic for identical inputs and thresholds.
- [x] Adversarial rupture, orientation, and winding fixtures are included.
- [ ] Run CI on the exact final `main` commit.

## Intellectual property and identity

- [x] Controlled public-inspection licence identifies Monty Dabas.
- [x] Citation metadata identifies Monty Dabas, Independent Researcher, ORCID `0009-0005-6948-209X`.
- [x] Patent notice exists.
- [x] Public/private release boundary exists.
- [ ] Complete final human legal/IP comparison against active filings and unpublished claim strategy.

## Repository hygiene

- [x] Public files contain no intended credentials, local paths, private legal identity, or private-vault material.
- [x] Generated outputs are ignored by Git.
- [ ] Confirm repository-local Markdown links and schema references in CI.
- [ ] Apply final repository description and topics in GitHub settings.
- [ ] Rename repository from `ECL-pulic` to `ECL-public`.

## Release

- [ ] Confirm exact final commit after CI.
- [ ] Change repository visibility to public.
- [ ] Create an immutable `v0.2.0-rc1` prerelease from the verified commit.
- [ ] Archive the exact release and record its DOI if an external archival service is used.

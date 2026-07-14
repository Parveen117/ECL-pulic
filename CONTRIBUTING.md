# Contributing

Contributions should keep the public surface small, reproducible, and explicit about assumptions.

## Before submitting a change

1. Do not add private-vault material, provisional drafts, credentials, local absolute paths, personal data, trading integrations, or unpublished device details.
2. Add or update unit tests for behavioral changes.
3. Run:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m compileall -q src tests examples
```

4. Describe whether the change modifies a definition, an implementation, an output format, or an interpretation claim.

## Research claims

Code output should be described as evidence about the included model. Broader scientific, cryptographic, legal, or engineering claims require clearly identified external validation.

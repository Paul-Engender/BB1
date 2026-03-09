# Test Suite Notes

This folder contains both core tests (always runnable in this repo) and optional integration tests that depend on modules not currently present in this workspace.

## Run Tests

- Core + optional (with auto-skips):
  - `python -m unittest discover -s tests -v`

- Core-only (no optional groups):
  - `python -m unittest tests.test_cid tests.test_evaluator tests.test_issuer_proof tests.test_ledger tests.test_loader -v`

## Optional Test Groups

These tests are designed to skip automatically if dependencies are missing.

- `tests/test_negative_shacl.py`
  - Requires: `runtime.kernel_gate`

- `tests/test_ontology.py`
  - Requires: `runtime.kernel_gate`, `rdflib`

- `tests/test_packager.py`
  - Requires: `tools.packager`

- `tests/test_uuidv7.py`
  - Requires: `src.uuidv7`

## Current Workspace Status

From the latest run in this workspace:

- Test discovery passes with skips:
  - `OK (skipped=15)`

This means all runnable tests pass, and skipped tests are waiting on optional modules/dependencies.

# Unified Operating Ontology Kernel

This project implements the core components of the ENG Unified Operating Ontology Kernel, including the TBox (ontology), SHACL shapes for validation, and a FastAPI-based Kernel Gate service.

## Environment Setup

This project uses Python 3.9+ and Poetry for dependency management. A virtual environment is recommended:

```bash
python3 -m venv .venv
.venv/bin/pip install poetry
.venv/bin/poetry install --no-root
```

## Known Issues

### `rdflib` Parsing Incompatibility with Language Tags

**Issue:** The `rdflib` library (version 7.5.0) used for parsing Turtle (`.ttl`) files exhibits a `BadSyntax` error when encountering language tags (e.g., `@en`) within string literals, particularly in multi-property declarations for ontology objects. This issue was consistently observed with `rdflib.plugins.parsers.notation3.BadSyntax` pointing to constructs like `"...'^b'@en ;..."`. Downgrading to `rdflib==6.3.2` did not resolve the issue.

**Workaround:** To unblock development and allow `rdflib` to parse the `kernel.ttl` file successfully, all `@en` language tags have been **temporarily removed** from string literals in `ontology/kernel.ttl`.

**Impact:** This results in a degradation of multilingual labels/definitions within the TBox.

**Future Resolution:**
*   Monitor `rdflib` releases for fixes to this parsing behavior.
*   Investigate alternative RDF parsing libraries for Python.
*   If the issue persists, a custom parsing/loading mechanism may be required, or the absence of language tags will need to be formally accepted for the kernel's internal representation.

## Running Tests

To run the project's tests:

```bash
.venv/bin/poetry run pytest tests/
```

## Running the Kernel Gate Service

To start the FastAPI service:

```bash
.venv/bin/poetry run uvicorn runtime.main:app --host 0.0.0.0 --port 8000
```

---

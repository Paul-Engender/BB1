# Architecture Overview

This repository is organized as a small monorepo with clearly bounded components. The primary goal is to keep reusable services (like the LLM transport gateway) intentionally "dumb" and stable, while allowing the ontology work to evolve quickly until it is mature enough to move into a governed space.

## Boundary Map
These components are top-level directories within the repository root.

### Core Ontology Kernel (TBox + SHACL)
- **Location:** `ontology/`
- **Purpose:** Canonical ontology artifacts (TBox and SHACL shapes).
- **Stability:** Intended to be governed and stable once mature.

### Kernel Gate Service (FastAPI)
- **Location:** `runtime/`
- **Purpose:** Validation and ingestion API over the ontology kernel.
- **Dependencies:** Python/Poetry service that consumes the kernel artifacts.

### Reusable Gateways
- **Location:** `gateways/`
- **Purpose:** Provider-agnostic, reusable services.
- **Design Principle:** These services should remain intentionally "dumb" and enforce their service contracts.

### Ontology Workspace (Temporary)
- **Location:** `ontology_workspace/`
- **Purpose:** Temporary tools and scripts for building and reviewing the ontology.
- **Stability:** Intentionally flexible and expected to migrate to a governed system once mature.

## Guiding Principles
- Keep transport/gateway services reusable and contract-driven.
- Keep ontology evolution tooling separate from production kernel artifacts.
- Prefer explicit module boundaries over implicit coupling.

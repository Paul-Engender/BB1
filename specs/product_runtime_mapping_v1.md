# Product Runtime Mapping v1

Status: IS
Owner: paul
Plan Item: P1-011
Task: TASK-11.1
Date: 2026-03-06

## Purpose

Map the directional product architecture in `specs/ontoForge_03_Product-Spec_V1.1.md`
onto the current repository structure and identify the concrete implementation gaps.

This artifact is a runtime/module map. It does not collapse:
- runtime-internal lifecycle candidates
- runtime lifecycle instances
- boundary objects
- Runtime 3 operational instantiation

## Runtime Map

| Product Runtime | Product-Spec Role | Current Repo Assets | Current State | Primary Gap |
| --- | --- | --- | --- | --- |
| Runtime 1: Support Ontology Engine | Global semantic kernel and release engine | `ontology/`, `runtime/kernel_gate.py`, `runtime/main.py`, `runtime/runtime1_engine.py`, `dist/SupportOntologyRelease-v0.2.0/` | Partial | Release engine and evidence model exist; canonical payload membership still needs alignment to the approved support-release composition |
| Runtime 2: SCR TBox Engine | Tenant-scoped compiler/runtime for workflow control logic | No dedicated compiler module; partial packaging substrate only | Missing | No compiler pipeline from tenant workflow definitions to tenant-scoped `SCR_TBox_Release` |
| Runtime 3: SCR Customer Runtime | Tenant-scoped enforcement runtime and operational truth | `src/ledger.py`, `src/evaluator.py`, `src/issuer_proof.py`, `src/loader.py` | Bootstrap-only | No tenant service boundary, no product event model, and load binding is not yet isolated from generic package verification |

## Module Mapping

### Runtime 1
[text](app://-/index.html?initialRoute%3D%2Fthread-overlay%2F019cc334-7555-7622-a97b-ee2783fdddd4%26hostId%3Dlocal)
- Product intent:
  - validate ontology/kernel artifacts
  - produce global release objects
  - emit promotion evidence
- Internal lifecycle candidate:
  - support-layer semantic component or coherent semantic change set
- Boundary object:
  - `SupportOntologyRelease`
- Current repo mapping:
  - ontology source: `ontology/`
  - validation service: `runtime/kernel_gate.py`
  - API shell: `runtime/main.py`
  - release engine: `runtime/runtime1_engine.py`
  - packaging substrate: `tools/packager.py`, `src/loader.py`
- Required implementation direction:
  - align Runtime 1 build output to the canonical support-release payload contract without treating individual semantic components as boundary artifacts

### Runtime 2

- Product intent:
  - compile tenant workflow definitions under global doctrine and kernel constraints
  - fail closed on invalid or incomplete semantics
  - emit tenant-scoped `SCR_TBox_Release`
- Internal lifecycle candidate:
  - tenant workflow/process/control definition with compile-time semantics
- Boundary object:
  - `SCR_TBox_Release`
- Current repo mapping:
  - none as a dedicated compiler/runtime
  - partial downstream package format exists
- Required implementation direction:
  - create a compiler module that consumes `SupportOntologyRelease` as an upstream boundary object rather than treating Runtime 1 internals as Runtime 2 candidate state

### Runtime 3

- Product intent:
  - append-only tenant ledger
  - authority derivation and execution commitment
  - deterministic authorization, eligibility, and control events
- Internal lifecycle candidate:
  - live tenant proposal, transition, or requested action
- Load boundary objects:
  - `SCR_TBox_Release`
  - `SCR_Runtime_LoadManifest`
- Current repo mapping:
  - ledger primitive: `src/ledger.py`
  - evaluator primitive: `src/evaluator.py`
  - proof primitive: `src/issuer_proof.py`
  - package loader: `src/loader.py`
- Required implementation direction:
  - build a tenant-scoped runtime service around these primitives and keep Runtime 3 operational instantiation separate from load-binding/package-verification concerns

## Boundary Object Mapping

| Boundary Object | Product-Spec Expectation | Current Repo State | Gap |
| --- | --- | --- | --- |
| `SupportOntologyRelease` | Global release with evidence-bound promotion discipline | Runtime 1 engine plus `dist/SupportOntologyRelease-v0.2.0/` exist | Canonical payload membership still needs implementation alignment |
| `SCR_TBox_Release` | Tenant-scoped compiled release referencing exact support-ontology dependencies | Minimal packaged artifact exists in `dist/SCR_TBox_Release-v0.1.0/`; schema/loader contract support exists | Missing Runtime 2 compiler provenance and production path |
| `SCR_Runtime_LoadManifest` | Tenant-aware declaration of what the runtime may load | Schema plus loader checks exist | Missing strict isolation of Runtime 3 load binding from generic package verification flow |

## Architectural Conclusions

1. The repo already contains a viable Runtime 1 substrate.
2. Runtime 2 is the largest missing architectural component.
3. Runtime 3 should be built by wrapping and hardening existing primitives, not replacing them wholesale.
4. Internal lifecycle candidates, boundary objects, and Runtime 3 operational truth must remain distinct in implementation planning.
5. The immediate architectural hinge is boundary-object discipline, because Runtime 2 and Runtime 3 both depend on it.

## Next Inputs

This document is the input to:
- `TASK-11.2` for product event modeling
- `TASK-11.3` for boundary object definition

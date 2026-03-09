# Runtime 2 Ingest Admissibility Contract v1

Status: APPROVED
Owner: paul
Plan Item: P2-003
Task: TASK-29.3
Date: 2026-03-08

## Purpose

Translate the approved Runtime 2 tenant input contract and admissibility matrix
into implementation-facing ingest and fail-closed gate controls.

This artifact defines the compiler front-door contract. It does not define
compiled primitive emission or Runtime 3 load behavior.

## Baseline Inputs

- `specs/runtime2_tenant_workflow_input_contract_v1.md`
- `specs/runtime2_support_admissibility_matrix_v1.md`
- `specs/runtime2_compiler_module_boundary_v1.md`
- `specs/product_tenant_scope_rules_v1.md`
- `specs/product_boundary_objects_v1.md`

## Compiler Front-Door Boundary

The first Runtime 2 implementation should expose a single compile request
boundary through `runtime/runtime2/compiler_service.py`.

A compile request is admissible for processing only when it includes all of the
following explicit inputs:
- `tenant_input_path`
- `support_release_manifest_path`
- `support_release_archive_path`
- `requested_release_version`
- `deterministic` flag

Interpretation rules:
- `tenant_input_path` is the canonical serialized tenant workflow input payload
  for first compile
- `support_release_manifest_path` and `support_release_archive_path` together
  bind Runtime 2 to an exact `SupportOntologyRelease`
- omitted fields are non-permissive
- no implicit path discovery or fallback resolution is allowed

## Ingest Preconditions

Before semantic admissibility checks begin, Runtime 2 must confirm:
1. the compile request envelope is structurally complete
2. the upstream support release package is present and exact
3. the tenant input payload is readable and parseable
4. the request carries an explicit deterministic mode choice

Failure at this boundary is `ABORT`.

## Ordered Gate Sequence

Runtime 2 ingest and admissibility processing must follow this fixed order.

### Stage 1) Request-envelope checks

Checks:
- all compile request fields are present
- referenced files exist
- no duplicate or conflicting support-release references are provided

Fail outcome:
- `ABORT`

Primary reason-code pattern:
- `RC:S1:REQUEST:<DETAIL>`

### Stage 2) Upstream support-release dependency checks

Checks:
- verify manifest structure and archive integrity for the referenced
  `SupportOntologyRelease`
- confirm `artifact_type = SupportOntologyRelease`
- confirm `tenant_scope = global`
- confirm dependency reference is exact and resolvable for this compile request

Implementation note:
- generic package verification may reuse existing shared verification substrate
  for support-release validation
- Runtime 3 load-manifest logic is not part of this stage

Fail outcome:
- `ABORT`

Primary reason-code patterns:
- `RC:S2:I7:UNBOUND_REFERENCE`
- `RC:S2:DEPENDENCY:INVALID_SUPPORT_RELEASE`

### Stage 3) Tenant input parse and envelope checks

Checks:
- tenant input payload parses successfully
- first-compile input envelope families are present
- required canonical fields are explicit
- hidden or renamed constraint-like fields are absent

Fail outcome:
- `ABORT` for malformed or incomplete request structure
- `QUARANTINE` or `ABORT` for unsupported constraint boundary violations

Primary reason-code patterns:
- `RC:S2:I8:MISSING_IDENTITY`
- `RC:S2:DD-001:INVALID_IDENTIFIER`
- `RC:S2:DD-004:UNSUPPORTED_CONSTRAINT`

### Stage 4) Deterministic semantic admissibility checks

Checks follow the approved matrix row order:
1. tenant context
2. upstream dependency binding
3. target-set declaration
4. scope declaration
5. action/effect declaration
6. authority references
7. authorization semantics
8. eligibility semantics
9. denial semantics
10. control-state semantics
11. AI-operable declaration
12. constraint boundary
13. identifier hygiene
14. evidence-linkage readiness

Rules:
- row order is fixed
- stage outcome is fail-closed
- the first failing row emits the primary reason code
- secondary failures may be recorded but must not replace the primary cause

Fail outcomes:
- `ABORT`
- `DENY`
- `QUARANTINE`

Primary reason-code patterns remain those defined in
`specs/runtime2_support_admissibility_matrix_v1.md`.

## Successful Output of Ingest/Admissibility

A successful front-door pass produces an admitted compile candidate for
`normalize.py` containing, at minimum:
- exact `tenant_id`
- exact admitted workflow identifiers
- exact support-release artifact identity and version
- explicit target, scope, action, effect, authorization, eligibility, denial,
  control-state, and AI-operable references
- stable primary reason-code policy reference
- source input lineage references needed for later primitive emission

This is an internal admitted candidate only. It is not yet a boundary object.

## Failure Handling Contract

Runtime 2 must expose failure surfaces with all of the following:
- outcome class (`ABORT`, `DENY`, `QUARANTINE`)
- primary reason code
- stage identifier
- concise machine-readable detail
- source reference back to the triggering input surface where available

Rules:
- unknown required semantics are non-permissive
- failure responses must not imply fallback compilation
- no partial primitive emission may occur after admissibility failure

## Explicit Exclusions

This front-door contract does not authorize Runtime 2 to:
- infer missing target, scope, authority, or control semantics
- treat prose notes as executable compile meaning
- emit `SCR_TBox_Release` on partial admission
- generate Runtime 3 authority or execution events
- bypass support-release dependency validation

## Acceptance Checklist (TASK-29.3)

- compile request boundary is explicit
- support-release dependency validation is explicit
- ordered ingest/admissibility stages are explicit
- fail outcomes and reason-code handling are explicit
- successful admitted-candidate handoff is explicit
- Runtime 3 behavior is explicitly excluded



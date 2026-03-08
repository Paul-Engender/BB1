# Support to TBox Dependency Provenance v1

Status: APPROVED
Owner: paul
Plan Item: P1-022
Task: TASK-22.4
Date: 2026-03-07

## Purpose

Define exact dependency provenance rules by which Runtime 2 `SCR_TBox_Release`
records and proves reliance on upstream `SupportOntologyRelease`.

## Inputs

- `specs/runtime2_compiled_control_primitives_v1.md`
- `specs/support_release_provenance_model_v1.md`
- `specs/product_runtime_mapping_v1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

## Dependency Provenance Record

Each `SCR_TBox_Release` MUST include dependency provenance with:

- `tenant_id`: tenant scope identifier
- `tbox_release_id`: CID for `SCR_TBox_Release`
- `support_release_id`: exact upstream `SupportOntologyRelease` CID
- `support_release_version`: referenced support release version
- `support_manifest_digest`: digest of referenced support manifest
- `support_evidence_digest`: digest of referenced support evidence bundle
- `compile_profile`: Runtime 2 compile profile id/version
- `compile_input_digest`: digest of tenant workflow input set
- `compile_output_digest`: digest of compiled primitive set
- `compile_reasoncode_digest`: digest of compile reason-code/evidence outputs
- `dependency_check_results_digest`: digest of dependency validation outputs

## Binding Rules

1. Exact dependency identity.
- `support_release_id` must reference one exact released support package.
- Range references or "latest" references are invalid.

2. Tenant scope binding.
- `tenant_id` in dependency provenance must match tenant id declared by `SCR_Runtime_LoadManifest`.

3. Evidence continuity.
- Runtime 2 provenance must include digests proving upstream support evidence was present and verified.

4. Compile lineage completeness.
- compile input, output, and reason-code digests must all be present.

5. Non-permissive dependency failure.
- missing/mismatched support dependency provenance yields compile reject.

## Runtime 3 Load-Facing Implications

Runtime 3 load checks must be able to verify from `SCR_TBox_Release`:
- exact support release dependency identity
- dependency evidence digest presence
- tenant scope match

If these conditions are not met, load is rejected.

## Prohibited Patterns

- support dependency by filename/path only
- support dependency by mutable tag
- implicit tenant id defaults
- acceptance when support evidence digest is absent

## Validation Checks

Dependency provenance validation fails if:
- `support_release_id` missing or unresolved
- support manifest/evidence digests missing
- compile lineage digests missing
- tenant id mismatch with load manifest

## Runtime Boundary Note

This artifact defines cross-runtime dependency semantics for boundary objects.
It does not define Runtime 3 operational event semantics.

## Done Test

This artifact is complete only if all are true:
- `SCR_TBox_Release` dependency fields are explicit and exact
- upstream support evidence lineage is machine-checkable
- tenant-binding rule is explicit for Runtime 3 load verification
- no implicit/mutable dependency pattern is permitted

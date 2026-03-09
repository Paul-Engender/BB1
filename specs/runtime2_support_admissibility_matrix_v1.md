# Runtime 2 Support Admissibility Matrix v1

Status: APPROVED
Owner: paul
Plan Item: P1-020
Task: TASK-20.4
Date: 2026-03-07

## Purpose

Define the deterministic admissibility matrix mapping tenant input features to
support-layer checks and compile outcomes for Runtime 2.

This matrix is the canonical accept/reject surface for first compile and is
fail-closed by default.

## Source Anchors

Primary canonical anchors:
- `specs/ontoForge_02_Lifecycle-Specification_v1.1.md`
- `specs/ontoForge_03_Product-Spec_V1.1.md`
- `specs/ontoForge_04_Decisions-Register_v1.1.md`
- `specs/product_runtime_instantiation_clarification_addendum_2026-03-07.md`

Contract anchors:
- `specs/runtime2_tenant_workflow_input_contract_v1.md`
- `specs/runtime2_compiled_control_primitives_v1.md`
- `specs/support_ontology_machine_contract_map_v1.md`
- `specs/support_ontology_invariant_model_v1.md`
- `specs/support_ontology_identifier_and_mvp_boundary_v1.md`

## Canonical Rule

For every admitted feature family, Runtime 2 must evaluate explicit checks with
deterministic non-permissive outcomes on failure.

Unknown or missing required semantics are non-permissive.

## Matrix

| Feature Family | Input Surface | Support Check | Invariant / Decision Anchor | Pass Condition | Fail Outcome | Primary Reason-Code Pattern |
| --- | --- | --- | --- | --- | --- | --- |
| Tenant context | `tenant_id`, workflow envelope | tenant identity explicit and identifier-clean | `I8`, `I10`, `DD-001` | tenant and workflow identity present and valid | ABORT | `RC:S2:I8:MISSING_IDENTITY` |
| Upstream dependency binding | support release reference | exact `SupportOntologyRelease` dependency present | `I7`, `DD-002` | dependency id/version present and resolvable | ABORT | `RC:S2:I7:UNBOUND_REFERENCE` |
| Target-set declaration | `target_set_id`, selection basis | target identity and boundary explicit | `I16`, `I17` | explicit bounded target semantics | DENY | `RC:S4:I17:IMPLICIT_TARGET` |
| Scope declaration | `scope_id`, scope boundary | scope explicit and non-implicit | `I16`, `I10` | scope present where required | ABORT or DENY | `RC:S4:I16:MISSING_SCOPE` |
| Action/effect declaration | `action_id`, `effect_id`, linkage | explicit action-effect map exists | `I23`, `I10` | each executable action has explicit effect mapping | ABORT at admission / DENY at operation | `RC:S2:I23:MISSING_EFFECT_SEMANTICS` |
| Authority references | authority semantic refs | no inferred authority, explicit joins only | `I14`, `I15` | authority references explicit and typed | DENY | `RC:S5:I14:IMPLICIT_AUTHORITY` |
| Authorization semantics | authorization refs | authorization decision path explicit | `I4`, `I10` | explicit allow/deny surfaces defined | DENY | `RC:S6:I4:MISSING_AUTHORIZATION` |
| Eligibility semantics | eligibility refs | `eligible|ineligible|unknown` semantics explicit | `I11`, `DD-005` | unknown remains non-permissive | DENY | `RC:S6:DD-005:UNKNOWN_ELIGIBILITY` |
| Denial semantics | denial refs | denial class and reason-code policy explicit | `I10`, `DD-004` | denial categories declared | ABORT | `RC:S6:I10:MISSING_DENIAL_CLASS` |
| Control-state semantics | hard-stop/resume/mode refs | control-state compile surfaces explicit | `I10`, `I23` | control semantics explicit when required | DENY | `RC:S6:I10:MISSING_CONTROL_STATE` |
| AI-operable declaration | `ai_operable` | AI-operable semantics explicit | `I10`, `I11` | declared and non-ambiguous | DENY | `RC:S3:I11:UNKNOWN_AI_OPERABLE` |
| Constraint boundary | any constraint-like field | MVP constraint exclusion check | `DD-004` | no unsupported constraints in binding input | QUARANTINE or ABORT | `RC:S2:DD-004:UNSUPPORTED_CONSTRAINT` |
| Identifier hygiene | all ids/refs | identifier format and binding checks | `DD-001` | references are identifier-clean | ABORT | `RC:S2:DD-001:INVALID_IDENTIFIER` |
| Evidence linkage surface | compile evidence refs | output must carry compile evidence requirements | `I20`, `I21`, `DD-002` | evidence obligations defined in output contract | ABORT | `RC:S6:I20:MISSING_EVIDENCE_LINK` |

## Stage Allocation Summary

- `S2` admission checks dominate identity, dependency, and structural fields.
- `S4` alignment checks dominate target/scope explicitness.
- `S5` attribution checks dominate authority reference integrity.
- `S6` operation checks dominate authorization/eligibility/denial/control
  semantics.

## Determinism Rules

- Check order is fixed by stage and then matrix row order.
- First emitted reason code identifies the primary cause.
- Secondary causes may be appended but may not replace the primary cause.

## Out-of-Scope

This matrix does not define Runtime 3 event execution behavior.
It only defines Runtime 2 compile admissibility checks and outcomes.

## Addendum Consideration

This matrix preserves non-conflation between Runtime 2 compile admissibility and
Runtime 3 operational instantiation.

## Acceptance Checklist (TASK-20.4)

- feature-to-check mapping is explicit and deterministic
- each feature row has pass condition and non-permissive fail outcome
- invariant/decision anchors are explicit per row
- reason-code patterns are explicit
- Runtime 3 operational behavior is not pulled into Runtime 2 matrix scope

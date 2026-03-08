# P2 Contract Baseline and Delta Resolution Policy v1

Status: ACTIVE_FOR_P2
Date: 2026-03-08
Owner: paul

## Purpose

Control how P2 uses the existing implementation-facing contract surfaces without implying a blanket v2 rewrite program.

## Scope

Applies to the current baseline documents:

- `specs/product_runtime_mapping_v1.md`
- `specs/product_event_model_v1.md`
- `specs/product_boundary_objects_v1.md`

And to any narrow P2 follow-on surfaces such as:

- `specs/p2_contract_translation_review_v1.md`
- `specs/p2_contract_delta_register_v1.md`
- `specs/product_tenant_scope_rules_v1.md`
- targeted addenda or replacement documents if the approved delta register requires them

## Rules

1. The existing v1 runtime, event, and boundary documents remain the executable baseline at P2 start.
2. `P2-001` must first produce a contract translation review and delta register before any replacement surface is planned.
3. Prefer targeted addenda or narrow new contract surfaces over blanket `v2` rewrites.
4. A full replacement document is allowed only when the approved delta register states that the existing surface cannot safely absorb the required change.
5. Boundary/load enforcement deltas needed for strict cross-runtime loading belong to `P2-005`, not `P2-001`.
6. Task ledgers and evidence rows must reference one active execution baseline per functional contract surface.

## Activation condition

This policy is active with successor workstream `P2-001` and gates milestone `M1` closure through `EP-27`.

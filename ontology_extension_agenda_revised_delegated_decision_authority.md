# Ontology Extension Agenda (Revised)

**Status:** Updated to reflect delegated decision execution under accountable human mandate

---

## Framing Update (Normative)

This extension agenda reflects an explicit correction to the earlier interpretation that *only humans may perform Decision acts*. That interpretation is **no longer valid**.

The governing position is now:

> **Only accountable mandate holders may bear authority and liability for Decisions.**  
> **Decision acts may be executed by agents, provided accountability, mandate, and revocability remain human‑anchored and explicit.**

This change is driven by operational necessity in a small, high‑leverage team and does **not** weaken Kernel safety. It clarifies the distinction between **authority bearer** and **decision executor**.

The ontology must therefore enforce *accountability anchoring*, not *anthropocentric execution*.

---

## I. Cross‑Cutting Requirements (Unchanged except where noted)

### 1. Semantic Plane Separation
(unchanged)

Governance, mechanism, strategy narrative, and sensemaking remain strictly separated.

---

### 2. Artefact Kind Primitives
(unchanged)

Evidence, Proposal, Decision, Accepted Construct, Sensemaking Artefact, Novelty Signal, Mandate, Claim Scope remain mandatory and disjoint where required.

---

### 3. Identity Continuity
(unchanged)

IdentityBearer remains first‑class. Promotion requires continuity.

---

### 3A. Separation of Duties (Producer ≠ Approver)
(unchanged)

No agent (human or automated) that produces artefacts may approve them.

---

### 4. Negative Capability and Forbidden Inference
(unchanged)

Execution, confidence, completeness, or success never imply authority.

---

## II. Updated Kernel‑Derived Requirements

The following sections **replace** the earlier “human‑only decision” interpretation.

---

## Charter §5 — Authority, Accountability, and Delegated Decision Execution (Revised)

### Semantic Commitment (Updated)

Authority is inseparable from accountability and mandate. However, **execution of a Decision act does not require the authority bearer to be the executor**.

The kernel distinguishes between:

* **Authority Bearer** — the entity that holds mandate, bears downside exposure, and is accountable for the Decision.
* **Decision Executor** — the entity that performs the Decision act as a bounded, auditable action.

Only the former is restricted to humans (or legally accountable organisational roles). The latter **may be an automation agent**.

---

### Ontology Obligations (Revised)

Introduce or confirm the following distinctions:

#### Agent Types

* **AccountableAgent**  
  A human or legally accountable organisational role capable of holding mandate and bearing downside exposure.

* **AutomationAgent**  
  A non‑accountable execution entity incapable of holding mandate or bearing liability.

#### Decision Model (Revised)

A Decision MUST include all of the following:

* **hasAuthorityBearer → AccountableAgent**  
  (mandatory; exactly one)

* **exercisedUnderMandate → Mandate**  
  (mandatory; mandate holder must equal authority bearer)

* **executedBy → Agent**  
  (may be AccountableAgent or AutomationAgent)

* **enactsTransition → GovernanceStateTransition**

Authority is derived **only** from the authority bearer + mandate combination.

Execution confers no authority.

---

### Explicit Prohibitions (Revised)

The ontology MUST enforce that:

* AutomationAgent **MUST NOT** be a Mandate holder.
* AutomationAgent **MUST NOT** be an Authority Bearer.
* Decisions **without** an Authority Bearer are invalid.
* Decisions **without** a Mandate are invalid.
* The presence of an AutomationAgent as executor **does not** relax any kernel constraints.

---

### Validation Obligations (Kernel‑Critical)

SHACL or equivalent constraints MUST ensure:

* `Decision.hasAuthorityBearer` is present and is an AccountableAgent.
* `Decision.executedBy` may reference AutomationAgent **only if** `hasAuthorityBearer` is present.
* `Mandate.holder` equals `Decision.hasAuthorityBearer`.
* No Decision is valid if the executor is also a producer of artefacts under decision.

---

### Audit and Revocation Requirements

Every Decision must be auditable such that it is possible to answer:

* Who bore authority?
* Under which mandate?
* Who executed the act?
* What transition occurred?
* What evidence and proposal were referenced?

Revocation and supersession always apply to the **Decision**, not to the executor.

---

## Implications for Other Sections

### Sensemaking (§7)
(unchanged)

Agents may freely operate in sensemaking space. No authority.

---

### Decision Patterns (§9)
(clarified)

Decision Patterns may be **executed by agents**, but:

* Pattern approval remains a governed Decision.
* Pattern adoption records must still identify an Authority Bearer.
* Automated application of patterns does not remove accountability.

---

### Strategy Alignment

This update does **not** change the Strategy Positioning.

It strengthens feasibility while preserving:

* Explicit governance
* Defensible eligibility
* Mandate‑bound claims
* Liability containment

---

## Summary of Change (Non‑Synthetic)

The extension agenda no longer encodes a “humans perform all decisions” rule.

It now encodes:

* **Human accountability is mandatory.**
* **Decision execution may be automated.**
* **Authority, mandate, and liability remain non‑delegable.**

This resolves the four‑person team constraint without violating any Kernel axiom.

---

**End of Revised Extension Agenda**


# Evaluator Boundary v1 Specification

*Status: DRAFT*

## 1. Abstract

This document specifies the interface for the Evaluator, a critical component that enforces commit-boundary semantics. The Evaluator's primary role is to validate a proposed state transition (a "commit") against a set of rules and produce a deterministic outcome: either an approval (`IssuerProof`) or a rejection.

## 2. Core Concepts

*   **Commit**: A proposed state transition, packaged as a collection of artifacts and claims.
*   **Ruleset**: A collection of stipulations, requirements, and policies that govern the validity of a commit. This ruleset is itself an information artifact identified by a `cid:`.
*   **Evaluation**: The process of applying a Ruleset to a Commit.
*   **Commit-Boundary Enforcement**: The principle that no state transition is accepted into the system's official history (i.e., recorded on the ledger) without a successful evaluation.

## 3. Evaluator Interface

The Evaluator is conceptualized as a function that takes a commit and returns a result.

`evaluate(commit_cid: str, ruleset_cid: str) -> result_cid: str`

### 3.1 Inputs

*   **`commit_cid`**: A `cid:` pointing to the root artifact of the proposed commit. The commit artifact is expected to be a manifest that references all other artifacts included in the state transition.
*   **`ruleset_cid`**: A `cid:` pointing to the ruleset against which the commit should be evaluated.

### 3.2 Output

*   **`result_cid`**: A `cid:` pointing to an `IssuerProof` artifact that contains the outcome of the evaluation.

## 4. Evaluation Process

The `evaluate` function MUST perform the following high-level steps:

1.  **Dereference Inputs**: Securely retrieve the content of the `commit_cid` and the `ruleset_cid`.
2.  **Parse Commit**: Interpret the commit manifest to understand the proposed changes and referenced artifacts.
3.  **Apply Rules**: Systematically apply each rule from the ruleset to the commit. This may involve:
    *   Schema validation of artifacts.
    *   Integrity checks of dependencies.
    *   Validation of `IssuerProof` chains.
    *   Checking for required attestations or evidence.
4.  **Formulate Outcome**: Based on the results of the rule application, formulate a final claim.
    *   **On Success**: The claim asserts that the commit is valid with respect to the given ruleset.
    *   **On Failure**: The claim asserts that the commit is invalid and MUST include data on which rules failed.
5.  **Mint Result Proof**: Create a new `IssuerProof` containing the outcome claim.
    *   The `iss` of this proof is the Evaluator itself (e.g., `did:evaluator:v1`).
    *   The `sub` is the `commit_cid` that was evaluated.
    *   The `evidence` array SHOULD include the `ruleset_cid`.
6.  **Return Result CID**: Return the `cid:` of the newly minted result proof.

## 5. Commit Enforcement Logic

The enforcement of the commit boundary happens *outside* the Evaluator. A separate component, the **Commit Authority**, is responsible for the following workflow:

1.  Receive a proposed `commit_cid`.
2.  Select the appropriate `ruleset_cid` to apply.
3.  Invoke the `evaluate(commit_cid, ruleset_cid)` function.
4.  Inspect the resulting `IssuerProof`.
5.  **If and only if** the proof asserts successful validation, the Commit Authority will append the original `commit_cid` and the `result_cid` to the main system ledger. Otherwise, the commit is rejected.

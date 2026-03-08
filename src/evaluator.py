"""
Simplified Evaluator stub.

This is a bootstrap-phase, simplified implementation of the Evaluator.
It does not perform any real rule evaluation. It simply returns a
pre-determined successful `IssuerProof`.
"""

import time
from typing import Any, Dict

try:
    from .cid import mint_cid
    from .issuer_proof import canonicalize_for_signing
except ImportError:
    from cid import mint_cid
    from issuer_proof import canonicalize_for_signing

# The Evaluator's own identity
EVALUATOR_DID = "did:evaluator:v1"


def evaluate(commit_cid: str, ruleset_cid: str) -> Dict[str, Any]:
    """
    A stub implementation of the evaluate function.

    This function simulates the evaluation process and always returns a
    successful `IssuerProof`.

    Args:
        commit_cid: The CID of the commit to be evaluated.
        ruleset_cid: The CID of the ruleset to use.

    Returns:
        A dictionary representing the resulting IssuerProof.
    """
    proof_claim = {
        "type": "EvaluationResult",
        "statement": f"Commit {commit_cid} validated successfully against ruleset {ruleset_cid}.",
        "outcome": "SUCCESS",
    }

    proof_to_be_signed = {
        "iss": EVALUATOR_DID,
        "sub": commit_cid,
        "iat": int(time.time()),
        "claim": proof_claim,
        "evidence": [ruleset_cid],
    }

    # Stub-only signature simulation using canonical proof bytes.
    canonical_bytes = canonicalize_for_signing(proof_to_be_signed)
    dummy_signature = mint_cid(canonical_bytes)

    final_proof = proof_to_be_signed.copy()
    final_proof["signature"] = dummy_signature
    return final_proof


class CommitAuthority:
    """A simplified stub for the Commit Authority logic."""

    def __init__(self, ledger_module, evaluator_module):
        self.ledger = ledger_module
        self.evaluator = evaluator_module
        self.writer_id = "COMMIT_AUTHORITY"
        self.ledger.configure_ledger(self.writer_id)

    def process_commit(self, commit_cid: str, ruleset_cid: str) -> bool:
        """
        Simulates the commit-boundary enforcement workflow.

        1. Calls the evaluator.
        2. Inspects the result.
        3. Appends to the ledger on success.
        """
        result_proof = self.evaluator.evaluate(commit_cid, ruleset_cid)

        if result_proof.get("claim", {}).get("outcome") == "SUCCESS":
            result_proof_bytes = canonicalize_for_signing(result_proof)
            result_cid = mint_cid(result_proof_bytes)

            success1, _ = self.ledger.append_event(commit_cid, self.writer_id)
            success2, _ = self.ledger.append_event(result_cid, self.writer_id)
            return success1 and success2

        return False

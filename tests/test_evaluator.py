"""
Tests for the simplified Evaluator and Commit Authority.

Focuses on 'enforcement_tests' to ensure the commit-boundary
logic is working as specified.
"""

import unittest
from src import evaluator, ledger, cid

class TestEvaluatorAndCommitAuthority(unittest.TestCase):

    def setUp(self):
        """Reset the ledger before each test."""
        ledger._reset_ledger_for_testing()
    
    def test_evaluate_stub_returns_valid_proof_structure(self):
        """Tests that the evaluator stub produces a proof with the correct structure."""
        commit_cid = "cid:commit-1"
        ruleset_cid = "cid:rules-1"
        
        proof = evaluator.evaluate(commit_cid, ruleset_cid)
        
        self.assertEqual(proof["iss"], evaluator.EVALUATOR_DID)
        self.assertEqual(proof["sub"], commit_cid)
        self.assertEqual(proof["claim"]["outcome"], "SUCCESS")
        self.assertIn(ruleset_cid, proof["evidence"])

    def test_commit_authority_enforcement_success(self):
        """
        Enforcement Test: A successful evaluation results in events
        being written to the ledger.
        """
        authority = evaluator.CommitAuthority(ledger, evaluator)
        commit_cid = "cid:a-good-commit"
        ruleset_cid = "cid:ruleset-v1"

        # Process the commit
        was_committed = authority.process_commit(commit_cid, ruleset_cid)

        # Check that the commit was successful
        self.assertTrue(was_committed)
        
        # Check that two events were written to the ledger
        # (the commit itself and the evaluation proof)
        self.assertEqual(ledger.get_log_size(), 2)
        
        # Verify the events in the ledger
        log_events = ledger.get_events(limit=2)
        self.assertEqual(log_events[0]["event_cid"], commit_cid)
        self.assertTrue(log_events[1]["event_cid"].startswith("cid:"))

    def test_commit_authority_enforcement_failure(self):
        """
        Enforcement Test: A failed evaluation does NOT write to the ledger.
        """
        
        # Create a mock evaluator that always fails
        class FailingEvaluator:
            def evaluate(self, commit_cid, ruleset_cid):
                return {
                    "iss": "did:evaluator:v1",
                    "sub": commit_cid,
                    "claim": { "outcome": "FAILURE" },
                    "signature": "dummy-sig"
                }

        failing_evaluator_module = FailingEvaluator()
        authority = evaluator.CommitAuthority(ledger, failing_evaluator_module)
        
        commit_cid = "cid:a-bad-commit"
        ruleset_cid = "cid:ruleset-v1"

        # Process the commit
        was_committed = authority.process_commit(commit_cid, ruleset_cid)
        
        # Check that the commit failed
        self.assertFalse(was_committed)
        
        # Check that NOTHING was written to the ledger
        self.assertEqual(ledger.get_log_size(), 0)

if __name__ == '__main__':
    unittest.main()

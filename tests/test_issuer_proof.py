"""
Tests for the simplified IssuerProof verifier.

Focuses on negative tests to ensure structural and logical validation
is working as expected.
"""

import unittest
import time
from src.issuer_proof import verify_issuer_proof, canonicalize_for_signing

class TestIssuerProof(unittest.TestCase):

    def setUp(self):
        """Create a base valid proof object for each test."""
        self.base_proof = {
          "iss": "did:example:123456",
          "sub": "cid:subject-hash",
          "iat": int(time.time()) - 60,
          "exp": int(time.time()) + 3600,
          "claim": {
            "type": "TruthAssertion",
            "statement": "This is a valid claim."
          },
          "evidence": ["cid:evidence-hash-1"],
          "signature": "a-valid-looking-signature"
        }

    def test_verify_valid_proof(self):
        """Tests that a structurally valid proof passes verification."""
        is_valid, message = verify_issuer_proof(self.base_proof)
        self.assertTrue(is_valid, message)

    def test_missing_required_field(self):
        """Negative Test: A required field is missing."""
        for field in ["iss", "sub", "iat", "claim", "signature"]:
            with self.subTest(missing_field=field):
                invalid_proof = self.base_proof.copy()
                del invalid_proof[field]
                is_valid, message = verify_issuer_proof(invalid_proof)
                self.assertFalse(is_valid)
                self.assertEqual(message, f"Missing required field: {field}")

    def test_invalid_claim_structure(self):
        """Negative Test: The 'claim' object is malformed."""
        invalid_proof = self.base_proof.copy()
        invalid_proof["claim"] = "just a string" # not an object
        is_valid, message = verify_issuer_proof(invalid_proof)
        self.assertFalse(is_valid)
        self.assertEqual(message, "Invalid 'claim' object structure.")

    def test_proof_expired(self):
        """Negative Test: The proof's expiration date is in the past."""
        expired_proof = self.base_proof.copy()
        expired_proof["exp"] = int(time.time()) - 1
        is_valid, message = verify_issuer_proof(expired_proof)
        self.assertFalse(is_valid)
        self.assertEqual(message, "Proof has expired.")

    def test_proof_issued_in_future(self):
        """Negative Test: The proof's issued-at date is in the future."""
        future_proof = self.base_proof.copy()
        future_proof["iat"] = int(time.time()) + 3600
        is_valid, message = verify_issuer_proof(future_proof)
        self.assertFalse(is_valid)
        self.assertEqual(message, "Proof 'iat' is in the future.")
        
    def test_invalid_signature(self):
        """Negative Test: Signature is missing or not a string."""
        invalid_proof = self.base_proof.copy()
        invalid_proof["signature"] = ""
        is_valid, message = verify_issuer_proof(invalid_proof)
        self.assertFalse(is_valid)
        self.assertEqual(message, "Signature is missing or invalid.")

    def test_invalid_subject_cid(self):
        """Negative Test: Subject is not a valid CID format."""
        invalid_proof = self.base_proof.copy()
        invalid_proof["sub"] = "not-a-cid"
        is_valid, message = verify_issuer_proof(invalid_proof)
        self.assertFalse(is_valid)
        self.assertEqual(message, "Subject 'sub' is not a valid CID.")

    def test_invalid_evidence_cid(self):
        """Negative Test: An item in the evidence array is not a valid CID."""
        invalid_proof = self.base_proof.copy()
        invalid_proof["evidence"] = ["cid:valid-cid", "not-a-cid"]
        is_valid, message = verify_issuer_proof(invalid_proof)
        self.assertFalse(is_valid)
        self.assertTrue(message.startswith("Invalid CID format in 'evidence'"))

    def test_canonicalize_for_signing(self):
        """Tests that canonicalization produces a deterministic, sorted string."""
        proof1 = {"b": 2, "a": 1, "signature": "xxx"}
        proof2 = {"a": 1, "b": 2, "signature": "yyy"} # same data, different order
        
        canonical1 = canonicalize_for_signing(proof1)
        canonical2 = canonicalize_for_signing(proof2)
        
        self.assertEqual(canonical1, canonical2)
        # The canonical form should not include the signature
        self.assertNotIn(b"signature", canonical1)
        # It should be compact (no spaces)
        self.assertEqual(canonical1, b'{"a":1,"b":2}')

if __name__ == '__main__':
    unittest.main()

"""
Tests for the CID library.
"""

import hashlib
import unittest
import uuid

from src.cid import get_hash_from_cid, mint_cid, validate_cid


class TestCID(unittest.TestCase):
    def test_mint_cid_format(self):
        """Tests if mint_cid produces a CID with the correct format."""
        content = b"hello world"
        cid = mint_cid(content)
        self.assertTrue(cid.startswith("cid:"))

        parts = cid[4:].rsplit("-", 1)
        self.assertEqual(len(parts), 2)

        uuid_part, hash_part = parts

        try:
            parsed = uuid.UUID(uuid_part)
        except ValueError:
            self.fail("UUID part of CID is not a valid UUID.")

        self.assertEqual(parsed.version, 7)
        self.assertEqual(len(hash_part), 64)

    def test_validate_cid_success(self):
        """Tests that a correctly minted CID validates successfully."""
        content = b"this is a test"
        cid = mint_cid(content)
        self.assertTrue(validate_cid(cid, content))

    def test_validate_cid_tampered_content(self):
        """Tests that validation fails for tampered content."""
        content = b"original content"
        cid = mint_cid(content)
        tampered_content = b"tampered content"
        self.assertFalse(validate_cid(cid, tampered_content))

    def test_validate_cid_invalid_format(self):
        """Tests that validation fails for invalid CID formats."""
        content = b"some content"
        self.assertFalse(validate_cid("invalid-cid", content))
        self.assertFalse(validate_cid("cid:justonepart", content))
        self.assertFalse(validate_cid("cid:too-many-parts-in-the-end-foo-bar", content))
        self.assertFalse(validate_cid("cid:notauuid-invalidhash", content))

    def test_type_behavior(self):
        """Tests current type behavior of the hardened CID API."""
        with self.assertRaises(TypeError):
            mint_cid("a string, not bytes")

        # Hardened behavior returns False for non-bytes-like validation input.
        self.assertFalse(validate_cid("cid:some-cid", "a string, not bytes"))

    def test_get_hash_from_cid(self):
        """Tests extraction of the hash from a valid minted CID."""
        content = b"some test content for hashing"
        sha256_hash = hashlib.sha256(content).hexdigest()
        cid = mint_cid(content)

        extracted_hash = get_hash_from_cid(cid)
        self.assertEqual(extracted_hash, sha256_hash)

    def test_get_hash_from_invalid_cid(self):
        """Tests that get_hash_from_cid returns None for invalid CIDs."""
        self.assertIsNone(get_hash_from_cid("invalid-cid"))
        self.assertIsNone(get_hash_from_cid("cid:no_hash_part"))


if __name__ == "__main__":
    unittest.main()

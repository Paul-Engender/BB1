# IssuerProof v1 Specification

*Status: DRAFT*

## 1. Abstract

This specification defines the `IssuerProof`, a verifiable, self-contained data structure that binds an assertion to a specific issuer and context. It serves as a foundational element for creating chains of authority and evidence.

## 2. Data Structure

An `IssuerProof` is a JSON object with a mandatory structure. The object MUST be serialized into a canonical byte string (alphabetized keys, no insignificant whitespace) for the purposes of hashing and inclusion in a `cid:`.

```json
{
  "iss": "did:example:123456",
  "sub": "cid:...",
  "iat": 1678886400,
  "exp": 1678972800,
  "claim": {
    "type": "TruthAssertion",
    "statement": "The artifact identified by 'sub' conforms to specification X."
  },
  "evidence": [
    "cid:..."
  ],
  "signature": "..."
}
```

### 2.1 Fields

*   **`iss` (Issuer)**: REQUIRED. A Decentralized Identifier (DID) URI identifying the entity that issued the proof.
*   **`sub` (Subject)**: REQUIRED. A `cid:` identifying the subject of the assertion (e.g., a piece of code, a document, another proof).
*   **`iat` (Issued At)**: REQUIRED. A Unix timestamp (integer seconds) indicating when the proof was issued.
*   **`exp` (Expiration)**: OPTIONAL. A Unix timestamp indicating when the proof expires.
*   **`claim`**: REQUIRED. A JSON object containing the specific assertion being made.
    *   **`type`**: The semantic type of the claim (e.g., `TruthAssertion`, `Stipulation`).
    *   **`statement`**: A human-readable description of the claim.
    *   Additional fields may be present depending on the `type`.
*   **`evidence`**: OPTIONAL. An array of `cid:`s pointing to other artifacts or proofs that support the claim.
*   **`signature`**: REQUIRED. A digital signature of the canonicalized proof object (excluding the `signature` field itself). The algorithm used should be determinable from the issuer's DID document.

## 3. Verification Algorithm

To verify an `IssuerProof`, a verifier MUST perform the following steps:

1.  **Integrity Check**: The `IssuerProof` object itself must be identified by a `cid:`. The verifier must re-calculate the hash of the canonicalized proof content and ensure it matches the hash in the `cid:` it was retrieved by.
2.  **Deconstruct**: Parse the JSON object and validate the presence of all REQUIRED fields.
3.  **Check Timestamps**:
    *   Verify that the current time is after `iat`.
    *   If `exp` is present, verify that the current time is before `exp`.
4.  **Resolve Issuer DID**: Dereference the `iss` DID to retrieve the issuer's public key(s).
5.  **Verify Signature**:
    *   Create a canonical representation of the `IssuerProof` object, ensuring the `signature` field is excluded.
    *   Using the issuer's public key, verify that the `signature` is a valid digital signature of the canonicalized proof.
6.  **Verify Subject and Evidence**: The verifier may recursively check the validity and integrity of the `cid:`s referenced in the `sub` and `evidence` fields.

If all steps pass, the `IssuerProof` is considered valid.

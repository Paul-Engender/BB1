# Identity CID Specification (cid:)

*Status: DRAFT*

## 1. Abstract

This specification defines a deterministic, content-addressable identifier scheme (`cid:`) for all versioned information content within the system. The `cid:` is built upon UUIDv7 to ensure chronological sortability and embeds a SHA-256 hash of the canonical content for integrity verification.

## 2. Identifier Format

The `cid:` has the following structure:

`cid:<uuidv7>-<sha256_hash_of_canonical_content>`

- **`<uuidv7>`**: A 36-character UUID version 7 string, providing a time-ordered, globally unique identifier.
- **`<sha256_hash_of_canonical_content>`**: A 64-character hexadecimal representation of the SHA-256 digest of the content's canonical form.

## 3. Minting Process

A new `cid:` is minted for an information asset through the following deterministic process:

1.  **Canonicalization**: The information content is serialized into its canonical byte representation. For structured data (e.g., JSON), keys must be sorted alphabetically, and whitespace must be normalized.
2.  **Hashing**: A SHA-256 hash is computed from the canonical byte stream.
3.  **UUID Generation**: A new UUIDv7 is generated.
4.  **Concatenation**: The components are concatenated according to the format specified in Section 2.

## 4. Validation Algorithm

An existing `cid:` is validated against its associated content using the following steps:

1.  **Deconstruction**: Parse the `cid:` string to separate the `<uuidv7>` and `<sha256_hash_of_canonical_content>` components.
2.  **Canonicalization & Hashing**: Repeat steps 1 and 2 of the Minting Process on the content being validated.
3.  **Comparison**: Compare the newly computed SHA-256 hash with the hash extracted from the `cid:`. If they match, the content is considered authentic and integral with respect to the identifier. If they do not match, the content is considered tampered or mismatched.
4.  **Format Check**: The UUID component should be validated as a legitimate UUIDv7 string.

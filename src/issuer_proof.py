"""
Simplified IssuerProof verifier.

This is a bootstrap-phase, simplified implementation that focuses on
structural and logical validation of an IssuerProof object. It does
not perform cryptographic signature validation or DID resolution.
"""

import json
import time
from typing import Dict, Any, Tuple

def verify_issuer_proof(proof_obj: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Verifies the structural and logical integrity of an IssuerProof object.
    
    This function performs all verification steps short of cryptographic checks.
    
    Args:
        proof_obj: The IssuerProof as a Python dictionary.
        
    Returns:
        A tuple of (is_valid, message).
    """
    
    # 2. Deconstruct: Validate presence of required fields
    required_fields = ["iss", "sub", "iat", "claim", "signature"]
    for field in required_fields:
        if field not in proof_obj:
            return (False, f"Missing required field: {field}")
            
    if not isinstance(proof_obj["claim"], dict) or "type" not in proof_obj["claim"]:
        return (False, "Invalid 'claim' object structure.")

    # 3. Check Timestamps
    current_time = int(time.time())
    
    iat = proof_obj.get("iat")
    if not isinstance(iat, int):
        return (False, "'iat' must be an integer timestamp.")
    if iat > current_time:
        return (False, "Proof 'iat' is in the future.")
        
    exp = proof_obj.get("exp")
    if exp is not None:
        if not isinstance(exp, int):
            return (False, "'exp' must be an integer timestamp.")
        if current_time >= exp:
            return (False, "Proof has expired.")

    # 4. Resolve Issuer DID (Placeholder)
    # In a real implementation, we would resolve the DID in 'iss'
    # to fetch the issuer's public key.
    # For now, we just check that the 'iss' field is a non-empty string.
    if not isinstance(proof_obj.get("iss"), str) or not proof_obj.get("iss"):
        return (False, "Issuer 'iss' is invalid.")
    
    # 5. Verify Signature (Placeholder)
    # This is where cryptographic signature verification would occur.
    # We would canonicalize the JSON (excluding the 'signature' field),
    # and use the issuer's public key to verify the signature.
    # We will simulate this by checking if the signature is a non-empty string.
    if not isinstance(proof_obj.get("signature"), str) or not proof_obj.get("signature"):
        return (False, "Signature is missing or invalid.")
        
    # 6. Verify Subject and Evidence (Format check)
    if not isinstance(proof_obj.get("sub"), str) or not proof_obj.get("sub").startswith("cid:"):
        return (False, "Subject 'sub' is not a valid CID.")
        
    evidence = proof_obj.get("evidence", [])
    if not isinstance(evidence, list):
        return (False, "'evidence' field must be a list.")
    for ev_cid in evidence:
        if not isinstance(ev_cid, str) or not ev_cid.startswith("cid:"):
            return (False, f"Invalid CID format in 'evidence': {ev_cid}")

    return (True, "Proof is structurally and logically valid (cryptographic checks pending).")

def canonicalize_for_signing(proof_obj: Dict[str, Any]) -> bytes:
    """
    Creates a canonical byte representation of the proof for signing.
    
    The process involves removing the 'signature' field and then creating a
    compact, sorted JSON string.
    
    Args:
        proof_obj: The IssuerProof dictionary.
        
    Returns:
        A UTF-8 encoded byte string of the canonical JSON.
    """
    if "signature" in proof_obj:
        # Create a copy to avoid modifying the original dict
        signable_obj = proof_obj.copy()
        del signable_obj["signature"]
    else:
        signable_obj = proof_obj
        
    # Create a compact, sorted JSON string
    canonical_json = json.dumps(
        signable_obj, 
        sort_keys=True, 
        separators=(',', ':')
    )
    
    return canonical_json.encode('utf-8')

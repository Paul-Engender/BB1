"""
In-memory, append-only ledger service.

This is a bootstrap-phase, simplified implementation of the ledger API
and ordering rules. It is not thread-safe and does not persist data.
"""

from typing import Dict, List, Tuple, Optional

# In-memory storage for events
# The list stores tuples of (sequence_num, event_cid)
_event_log: List[Tuple[int, str]] = []
# A dictionary to quickly look up events by CID
_event_cid_map: Dict[str, int] = {}
# The ordering authority, represented as a simple string for now
_ordering_authority = "SYSTEM_WRITER"


def configure_ledger(authority: str):
    """Sets the designated ordering authority."""
    global _ordering_authority
    _ordering_authority = authority

def append_event(event_cid: str, caller_id: str) -> Tuple[bool, str]:
    """
    Appends a new event CID to the ledger if the caller is authorized.
    
    Args:
        event_cid: The Content-Addressable Identifier of the event.
        caller_id: The identifier of the entity attempting the write.
        
    Returns:
        A tuple of (success, message_or_transaction_id).
        If successful, (True, "transaction_id").
        If failed, (False, "error_message").
    """
    if caller_id != _ordering_authority:
        return (False, "Caller is not the designated ordering authority.")
    
    if not isinstance(event_cid, str) or not event_cid.startswith("cid:"):
        return (False, "Invalid event_cid format.")
        
    if event_cid in _event_cid_map:
        return (False, "Event with this CID has already been committed.")

    # Assign the next sequence number
    next_seq_num = len(_event_log) + 1
    
    # Append to log
    _event_log.append((next_seq_num, event_cid))
    _event_cid_map[event_cid] = next_seq_num
    
    # In this simple implementation, the transaction is instantly "committed".
    # We return a dummy transaction ID.
    return (True, f"txn_{next_seq_num}")

def get_event_by_cid(event_cid: str) -> Optional[Tuple[int, str]]:
    """
    Retrieves an event from the ledger by its CID.
    
    Args:
        event_cid: The CID of the event to retrieve.
        
    Returns:
        A tuple of (sequence_num, event_cid) if found, otherwise None.
    """
    if event_cid in _event_cid_map:
        seq_num = _event_cid_map[event_cid]
        # The sequence number is 1-based, list index is 0-based
        return _event_log[seq_num - 1]
    return None

def get_events(after_seq_num: int = 0, limit: int = 100) -> List[Dict]:
    """
    Replays the event log from a given sequence number.
    
    Args:
        after_seq_num: The sequence number after which to start returning events.
        limit: The maximum number of events to return.
        
    Returns:
        A list of event dictionaries, each containing 'sequence_num' and 'event_cid'.
    """
    start_index = after_seq_num
    end_index = start_index + limit
    
    # Retrieve the slice of the log
    log_slice = _event_log[start_index:end_index]
    
    return [
        {"sequence_num": seq, "event_cid": cid}
        for seq, cid in log_slice
    ]

def get_log_size() -> int:
    """Returns the total number of events in the log."""
    return len(_event_log)
    
def _reset_ledger_for_testing():
    """A private function to reset the ledger state during tests."""
    global _event_log, _event_cid_map
    _event_log = []
    _event_cid_map = {}

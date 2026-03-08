"""
Tests for the in-memory, append-only ledger service.
"""

import unittest
from src import ledger

class TestLedger(unittest.TestCase):

    def setUp(self):
        """Reset the ledger before each test."""
        ledger._reset_ledger_for_testing()
        ledger.configure_ledger("SYSTEM_WRITER") # Default writer

    def test_append_event_success(self):
        """Tests successful event appending by the authority."""
        caller = "SYSTEM_WRITER"
        cid = "cid:uuid1-hash1"
        success, tx_id = ledger.append_event(cid, caller)
        self.assertTrue(success)
        self.assertEqual(tx_id, "txn_1")
        self.assertEqual(ledger.get_log_size(), 1)

    def test_append_event_unauthorized(self):
        """Tests that an unauthorized caller cannot append."""
        caller = "SOMEONE_ELSE"
        cid = "cid:uuid1-hash1"
        success, message = ledger.append_event(cid, caller)
        self.assertFalse(success)
        self.assertEqual(message, "Caller is not the designated ordering authority.")
        self.assertEqual(ledger.get_log_size(), 0)

    def test_append_duplicate_event(self):
        """Tests that the same event cannot be appended twice."""
        caller = "SYSTEM_WRITER"
        cid = "cid:uuid1-hash1"
        ledger.append_event(cid, caller)
        success, message = ledger.append_event(cid, caller)
        self.assertFalse(success)
        self.assertEqual(message, "Event with this CID has already been committed.")
        self.assertEqual(ledger.get_log_size(), 1)

    def test_get_event_by_cid(self):
        """Tests retrieving a committed event by its CID."""
        caller = "SYSTEM_WRITER"
        cid = "cid:uuid1-hash1"
        ledger.append_event(cid, caller)
        
        event = ledger.get_event_by_cid(cid)
        self.assertIsNotNone(event)
        self.assertEqual(event, (1, cid))

    def test_get_nonexistent_event(self):
        """Tests that retrieving a non-existent event returns None."""
        event = ledger.get_event_by_cid("cid:nonexistent-hash")
        self.assertIsNone(event)

    def test_deterministic_replay(self):
        """
        Validates the 'deterministic_replay_test' requirement.
        It appends a series of events and then replays them to ensure
        the order and content are perfectly preserved.
        """
        caller = "SYSTEM_WRITER"
        original_events = [f"cid:uuid{i}-hash{i}" for i in range(1, 6)]
        
        # Append events
        for cid in original_events:
            ledger.append_event(cid, caller)
            
        self.assertEqual(ledger.get_log_size(), 5)
        
        # Replay the full log
        replayed_log = ledger.get_events(limit=10)
        
        # Check that the replayed log matches the original events in order
        self.assertEqual(len(replayed_log), len(original_events))
        for i, event_data in enumerate(replayed_log):
            self.assertEqual(event_data["sequence_num"], i + 1)
            self.assertEqual(event_data["event_cid"], original_events[i])

    def test_get_events_with_pagination(self):
        """Tests the 'after_seq_num' and 'limit' parameters."""
        caller = "SYSTEM_WRITER"
        for i in range(1, 11):
            ledger.append_event(f"cid:uuid{i}-hash{i}", caller)
            
        # Get first 3 events
        events_page1 = ledger.get_events(limit=3)
        self.assertEqual(len(events_page1), 3)
        self.assertEqual(events_page1[0]["sequence_num"], 1)
        self.assertEqual(events_page1[2]["sequence_num"], 3)
        
        # Get next 3 events
        events_page2 = ledger.get_events(after_seq_num=3, limit=3)
        self.assertEqual(len(events_page2), 3)
        self.assertEqual(events_page2[0]["sequence_num"], 4)
        
        # Get remaining events
        events_page3 = ledger.get_events(after_seq_num=6, limit=5)
        self.assertEqual(len(events_page3), 4)

if __name__ == '__main__':
    unittest.main()

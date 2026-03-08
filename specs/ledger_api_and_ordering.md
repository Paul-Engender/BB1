# Ledger API and Ordering Rules

*Status: DRAFT*

## 1. Abstract

This document specifies the API contract for the append-only Ledger Service and the rules governing event ordering. The ledger provides a verifiable, deterministic, and tamper-evident log of system events, serving as a foundational layer for authority and execution.

## 2. Operating Principle

The ledger operates on a **single-writer, append-only** model. A designated ordering authority is the only entity permitted to commit new events to the log. All events are represented as `cid:`-identified information content.

## 3. API Contract

The Ledger Service exposes a minimal surface for interaction.

### Endpoint: `POST /events`

This is the sole endpoint for submitting a new event to be appended to the ledger.

**Request Body:**

The request body must be a JSON object containing the `cid:` of the event to be appended.

```json
{
  "event_cid": "cid:..."
}
```

**Responses:**

*   **`202 Accepted`**: The request has been accepted for processing. The response includes a transaction ID for tracking. The event is not yet committed.

    ```json
    {
      "transaction_id": "<uuid>",
      "status": "PENDING"
    }
    ```

*   **`400 Bad Request`**: The request body is malformed or the `event_cid` is invalid.

*   **`403 Forbidden`**: The caller is not the designated ordering authority.

### Endpoint: `GET /events/<event_cid>`

Retrieves a previously committed event by its CID.

**Responses:**

*   **`200 OK`**: The event is found. The response body will contain the full event content (dereferenced from the CID).

*   **`4NotFound`**: No event with the given CID exists in the ledger.

### Endpoint: `GET /events`

Allows for replaying or querying the event log. Supports pagination.

**Query Parameters:**

*   `after_seq_num` (integer): Returns events committed after the given sequence number.
*   `limit` (integer, default: 100): The maximum number of events to return.

**Responses:**

*   **`200 OK`**: Returns a list of event objects, ordered by sequence number. Each object contains the sequence number and the event's CID.

    ```json
    {
      "events": [
        { "sequence_num": 1, "event_cid": "cid:..." },
        { "sequence_num": 2, "event_cid": "cid:..." }
      ]
    }
    ```

## 4. Ordering and Determinism

*   **Strict Sequential Ordering**: The ordering authority assigns a monotonically increasing sequence number to every event it commits. This sequence number is the final source of truth for event order.
*   **Deterministic Replay**: Given the same initial state and the same sequence of events from the ledger, all higher-level system states must be fully reproducible. Any process that replays the events in their committed sequence order must arrive at the exact same final state.
*   **No Parallel Writes**: Only the single designated writer can commit events. This prevents race conditions and ambiguous ordering.

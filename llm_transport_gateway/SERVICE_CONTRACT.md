# SERVICE_CONTRACT.md
## LLM Transport Gateway — LLM Transport & Stability Layer

---

## 1. Purpose

The **LLM Transport Gateway** is an infrastructure service that provides **reliable, secure, and provider-agnostic access to Large Language Models (LLMs)**.

It is **plumbing**, not intelligence.

The service exists to:
- accept a fully-formed prompt
- invoke an LLM supplier
- return the model’s output **unchanged**
- manage operational, security, and supplier complexity

This service may be used by DecisionExecutor agents, including those executing delegated Decisions. AuthorityBearer and Mandate semantics are out of scope here and must be carried/enforced by the Decision boundary service.

---

## 2. Explicit Non-Goals (Hard Boundary)
The LLM Transport Gateway **MUST NOT**:

- interpret prompts
- interpret outputs
- validate or enforce schemas (e.g. JSON)
- correct or “repair” model responses
- apply workflow logic
- encode domain knowledge
- make decisions
- understand ontology, governance, or semantics
- modify prompts or outputs in any way

All meaning, validation, and governance live **outside** this service.

---

## 3. Input Contract

### Required
- `prompt: str`  
  A fully-formed prompt supplied by the caller.

### Optional (transport-level only)
- `provider` (e.g. gemini, openai, offline)
- `model`
- `timeout_seconds`
- `temperature`
- `max_tokens`

The LLM Transport Gateway **does not inspect, parse, or alter** the prompt.

---

## 4. Output Contract

### Success
- Returns **exactly the text produced by the model**, unchanged.

### Failure
- Raises a transport-level error or returns an explicit failure.
- Failures are limited to operational concerns:
  - timeouts
  - authentication errors
  - rate limits
  - supplier availability
  - network failures

The service **never rewrites, truncates, or restructures** model output.

---

## 5. Operational Guarantees

### 5.1 Stability
- Enforced request timeouts
- Bounded retries
- Exponential backoff
- Retries only on transient failures:
  - timeouts
  - HTTP 429
  - HTTP 5xx

### 5.2 Determinism
- Low default temperature unless overridden
- No hidden prompt augmentation
- No stateful behavior across calls

---

## 6. Security Guarantees

- API keys loaded only from environment variables
- No prompt logging by default
- No output logging by default
- No secrets written to disk or stdout
- Debug logging must be explicitly enabled and opt-in

---

## 7. Logging & Observability (Operational Only)

The service MAY log:
- timestamp
- provider
- model
- latency
- retry count
- success / failure
- **prompt hash (never prompt text)**

The service MUST NOT log:
- prompt contents
- model outputs
- domain or customer data

---

## 8. Provider & Model Abstraction

The LLM Transport Gateway:
- abstracts supplier-specific APIs
- isolates model naming and version churn
- normalizes transport-level errors

Callers must not rely on supplier-specific behavior.

---

## 9. Change Control Rule (Non-Negotiable)

Any change that introduces:
- semantic interpretation
- output validation
- schema enforcement
- task logic
- workflow behavior
- domain awareness

**violates this contract and must be rejected.**

---

## 10. Design Principle (Canonical)

> **This service is dumb on purpose.**  
> **Intelligence lives in the prompt and the caller.**

---

## 11. Intended Longevity

This contract is designed to remain valid across:
- LLM provider changes
- model evolution
- prompt strategies
- ontology workflows
- governance processes

If this contract no longer fits, a **new service** must be created.

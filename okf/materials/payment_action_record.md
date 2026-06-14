---
title: Agent Payment Action Record
step: 9
type: free_builder
service: ai-agent-payment-safety-stack
endpoint: POST /api/payment-action-record/build
pricing: free
x402_required: false
feeds_into:
  - Payment Control Evidence Packet
---

# Agent Payment Action Record

## What it is

A free stateless builder that combines payment intent, pre-payment checks, post-payment evidence, context state, decision, and Agent Action Atom into one external control record.

It is the first outward-facing use case of Agent Action Atom for AI-agent payment decisions.

## When to use

Use this after a payment decision to create a structured external record.

Call this when:
- a payment was allowed, denied, or sent to review
- you need to explain why a payment was allowed or rejected
- you want to combine pre-payment checks and post-payment evidence into one record
- an audit-ready external control record is required

## Endpoint

POST /api/payment-action-record/build

Free. Stateless. No DB storage.

## Input summary

- agent_id
- payment_intent (amount, currency, counterparty, purpose)
- pre_payment_checks (budget_status, counterparty_status, injection_risk)
- post_payment_checks (service_response, delivery_status)
- context_state
- decision (allowed / denied / review_required)
- evidence_ids

## Output summary

- record_id
- record_type (agent_payment_action_record)
- payment_flow (intent → checks → decision → evidence)
- audit_ready (true if all required fields present)
- evidence_id
- agent_action_atom (Atom-compatible reference)

## Non-goals

- does not execute payments
- does not hold funds
- not a wallet
- not a settlement layer
- not a legal compliance system
- not an official standard

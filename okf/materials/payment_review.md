---
title: Payment Review
step: 7
type: approval_gate
service: ai-agent-payment-safety-stack
endpoint: POST /api/payment-review/check
pricing: free
x402_required: false
feeds_into:
  - Budget Check
  - Agent Payment Action Record
  - Payment Control Evidence Packet
---

# Payment Review

## What it is

A free stateless runtime approval gate that returns allow, deny, or review_required before an AI agent makes a paid API call or crypto payment.

It checks budget status, counterparty status, injection risk, tool permission, and memory context before returning a decision.

## When to use

Call this before any paid API call or crypto payment.

Call this when:
- an AI agent is about to make a USDC, JPYC, or x402 payment
- you need a review decision before a paid API call
- injection risk from external data sources needs to be assessed
- budget and counterparty status need to be checked before payment

## Endpoint

POST /api/payment-review/check

Free. Stateless. Not in x402 manifest.

## Input summary

- agent_id
- amount
- currency (USDC / JPYC / JPY)
- counterparty
- payment_purpose
- source_text (the text that triggered the payment)
- requested_tool
- context_state
- policy

## Related materials

- [Search Result Trust Check](./search_result_trust_check.md)

## Output summary

- review_id
- decision (allow / deny / review_required)
- risk_level (low / medium / high / critical)
- reason
- recommended_action
- budget_status (within_limit / over_limit / unknown)
- counterparty_status (trusted / untrusted / unknown)
- injection_risk (none / low / medium / high)
- evidence_id
- agent_action_atom (Atom-compatible reference)

## Non-goals

- does not execute payments
- does not handle private keys
- does not check real on-chain budget
- not a wallet
- not a payment protocol
- not a settlement layer
- not a legal compliance system
- not an official standard

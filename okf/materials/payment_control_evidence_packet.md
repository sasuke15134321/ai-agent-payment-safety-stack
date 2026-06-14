---
title: Payment Control Evidence Packet
step: 10
type: free_builder
service: ai-agent-payment-safety-stack
endpoint: POST /api/payment-evidence-packet/build
pricing: free
x402_required: false
feeds_into:
  - Payment Evidence Check
  - Audit
---

# Payment Control Evidence Packet

## What it is

A free stateless builder that packages payment intent, checks, evidence, Agent Action Atom, and Agent Payment Action Record into one external evidence packet.

It is the top-level container for all payment control materials before audit or dispute review.

## When to use

Use this after payment execution to bundle all evidence into one reviewable packet.

Call this when:
- a payment has been executed and all checks are complete
- you need a single packet for reviewing the payment decision, counterparty checks, evidence, and action record
- an audit-ready evidence bundle is required
- a dispute review or human review needs all evidence in one place

## Endpoint

POST /api/payment-evidence-packet/build

Free. Stateless. No DB storage.

## Input summary

- agent_id
- payment_intent
- pre_payment_checks (budget, counterparty, injection_risk)
- post_payment_evidence (service response, delivery status)
- action_atom_id
- payment_action_record_id
- evidence_ids

## Output summary

- packet_id
- packet_type (payment_control_evidence_packet)
- audit_ready (true if all required components present)
- components (list of included evidence items)
- packet_hash
- evidence_id

## Non-goals

- does not execute payments
- does not store evidence permanently
- not a wallet
- not a settlement layer
- not a legal compliance system
- not an official standard

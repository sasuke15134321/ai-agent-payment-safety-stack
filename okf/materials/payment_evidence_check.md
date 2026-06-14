---
title: Payment Evidence Check
step: 11
type: paid_check
service: ai-agent-payment-safety-stack
endpoint: POST /api/payment-evidence/check
pricing: x402
x402_required: true
feeds_into:
  - Audit
  - Dispute Resolution
---

# Payment Evidence Check

## What it is

A paid check (0.03 USDC via x402) that verifies payment evidence after a payment has been executed.

It checks whether the payment and service response correspond, detects mismatches, and returns an audit-ready status.

## When to use

Use this after payment execution when audit-ready verification is required.

Call this when:
- a payment via x402, USDC, or JPYC has been executed
- you need to confirm the payment and service response correspond
- Japanese compliance audit trail is required
- a dispute review requires verified payment evidence

## Endpoint

POST /api/payment-evidence/check

Paid. 0.03 USDC per call via x402 on Base (eip155:8453).

## Input summary

- payment_reference
- payment_asset (USDC / JPYC / JPY)
- amount
- paid_endpoint
- transaction_reference
- service_response_received (boolean)
- actual_service_response
- expected_service_response (optional)

## Output summary

- payment_evidence_status (ok / incomplete / mismatch / requires_review)
- payment_response_matched (true / false)
- missing_items (list)
- mismatch_items (list)
- audit_ready (true only when status is ok)
- requires_human_review (true for incomplete / mismatch / requires_review)
- recommended_next_step

## Non-goals

- does not execute payments
- does not guarantee service output quality
- not a legal compliance guarantee
- not a tax decision system
- not a wallet
- not a settlement layer
- not an official standard

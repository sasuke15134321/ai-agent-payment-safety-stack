---
title: Budget Check
step: 8
type: paid_check
service: agent-budget-guard
endpoint: POST /api/budget/check
pricing: x402
x402_required: true
feeds_into:
  - Agent Payment Action Record
  - Payment Control Evidence Packet
---

# Budget Check

## What it is

A paid real-time check (0.03 USDC via x402) that verifies whether a payment is within the AI agent's budget before execution.

It checks per-request limits, daily limits, currency allowance, and service allowance, and returns allow or deny with an audit log.

## When to use

Use this after Payment Review returns allow, before executing the actual payment.

Call this when:
- Payment Review has returned allow
- you need real budget validation before executing a paid API call
- daily or per-request limits need to be verified against actual spend
- an audit log entry is required for the payment decision

## Endpoint

POST /api/budget/check

Paid. 0.03 USDC per call via x402 on Base (eip155:8453).

## Input summary

- agent_id
- amount_usdc
- currency
- service
- payment_purpose

## Output summary

- decision (allow / deny)
- reason
- remaining_daily_budget_usdc
- per_request_limit_usdc
- daily_limit_usdc
- audit_log_id
- evidence_id

## Non-goals

- does not execute payments
- does not hold funds
- not a wallet
- not a settlement layer
- not a legal compliance system
- not an official standard

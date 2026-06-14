---
title: Agent Spending Policy
step: 6
type: free_builder
service: agent-budget-guard
endpoint: POST /api/spending-policy/build
pricing: free
x402_required: false
feeds_into:
  - Payment Review
  - Budget Check
  - Agent Action Atom
---

# Agent Spending Policy

## What it is

A free stateless builder that creates structured AI-agent spending policies with limits, allowed currencies, allowed services, approval rules, token budget, and memory scope policy.

It is the policy layer before Payment Review and Budget Check.

## When to use

Use this before paid API calls to define the spending boundary for an AI agent.

Call this when:
- an AI agent session begins and spending limits need to be declared
- you need a structured policy record before payment decisions
- token budget and reasoning cost boundaries need to be defined
- you want to set human review triggers for high-cost actions

## Endpoint

POST /api/spending-policy/build

Free. Stateless. No DB storage.

## Input summary

- agent_id
- per_request_limit_usdc
- daily_limit_usdc
- allowed_currencies (USDC / JPYC / JPY)
- allowed_services (list)
- approval_required_above_usdc
- token_budget (max tokens per session)
- memory_scope_policy
- human_review_triggers

## Output summary

- policy_id
- per_request_limit_usdc
- daily_limit_usdc
- allowed_currencies
- allowed_services
- approval_required_above_usdc
- token_budget
- policy_hash
- evidence_id
- agent_action_atom (Atom-compatible reference)

## Non-goals

- does not execute payments
- does not check budget against real spend data
- does not handle private keys
- not a wallet
- not a payment protocol
- not a legal compliance system
- not an official standard

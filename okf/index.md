---
title: External Control Materials Bundle
version: "0.1"
type: okf_compatible_experimental_bundle
status: experimental
pricing: free
x402_required: false
map_endpoint: /.well-known/external-control-materials.json
map_version: "0.3"
---

# External Control Materials Bundle v0.1

OKF-compatible experimental bundle for AI-agent external control materials.

This bundle describes the 11 external control materials used before and after AI-agent tool use and paid API usage.

## What this bundle is

This is a Markdown knowledge bundle inspired by Open Knowledge Format (OKF).

It is not an official OKF implementation, not Google-certified, not a compliance standard.

It is an experimental AI-readable description of external control materials for AI agents.

## What is included

- 11 materials in okf/materials/
- 1 flow description in okf/flows/
- This index

## Central map

JSON map: /.well-known/external-control-materials.json

## Materials

| Step | Name | Type | Service |
|---|---|---|---|
| 1 | Memory Provenance Context Record | free_builder | agent-memory-api |
| 2 | Tool Permission Policy | free_builder | agent-security-gateway |
| 3 | Tool Approval Check | approval_gate | agent-security-gateway |
| 4 | Observability Data Boundary | conceptual_boundary | agent-security-gateway |
| 5 | Command Execution Gate | free_builder | agent-security-gateway |
| 6 | Agent Spending Policy | free_builder | agent-budget-guard |
| 7 | Payment Review | approval_gate | ai-agent-payment-safety-stack |
| 8 | Budget Check | paid_check | agent-budget-guard |
| 9 | Agent Payment Action Record | free_builder | ai-agent-payment-safety-stack |
| 10 | Payment Control Evidence Packet | free_builder | ai-agent-payment-safety-stack |
| 11 | Payment Evidence Check | paid_check | ai-agent-payment-safety-stack |

## Non-goals

- not an API
- not a payment protocol
- not a wallet
- not a legal compliance system
- not an official standard
- not affiliated with Arc, Circle, JPYC, Coinbase, or any payment network

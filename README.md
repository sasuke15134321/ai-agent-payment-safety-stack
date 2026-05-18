# AI Agent Payment Safety Stack

Not a wallet.
Not a facilitator.
Not a payment processor.
Not a marketplace.

A Japan-built x402-ready safety and audit layer for AI agent payment workflows.

---

AI agents are starting to discover APIs, make payments, and execute workflows.

Payment alone is not enough.

They also need:
- security checks before calling external APIs
- budget control before making payments
- audit-ready records after payments
- workflow orchestration across all steps

AI Agent Payment Safety Stack provides these layers.

All 4 APIs are indexed in CDP Bazaar as of 2026-05-18.

---

## Disclaimer

This is an independent experimental project.
It is not officially affiliated with JPYC, Circle, Arc, Kaia, or OpenAI.
The goal is to explore control layers for AI agents that may use paid APIs, x402 payments, stablecoin rails, and long-term memory.
This project references JPYC, x402, Arc, Kaia, and USDC as technical contexts.
It does not imply official partnership, endorsement, or integration unless explicitly stated.

---

## Why this stack exists

AI agents are beginning to call paid APIs, execute x402 micropayments, and operate across multiple sessions autonomously.
Without structured guardrails, agents can:

- overspend or exceed budgets
- process malicious or injected inputs
- store unverified or conflicting information into long-term memory
- fail to create audit-ready records for compliance or accounting
- execute multi-step workflows without governance checkpoints

This stack provides a set of composable, pre/post-execution control layer APIs designed to run alongside any AI agent that handles real money, real data, or real decisions.

---

## Stack overview

| API | Role | Layer | URL |
|-----|------|-------|-----|
| Agent Security Gateway | Scan inputs for prompt injection, PII, and suspicious metadata before execution | L4 | https://agent-security-gateway.onrender.com |
| Agent Budget Guard | Check budget limits, approval requirements, and audit readiness before payment | L4 | https://agent-budget-guard.onrender.com |
| Agent Memory API | Store payment policy, audit context, and decision history encrypted across sessions | L5 | https://agent-memory-api-bix5.onrender.com |
| Agent Evolution Engine | Orchestrate the full security → budget → memory → payment → invoice flow | L4/L5/L6 | https://agent-evolution-engine.onrender.com |
| Agent Memory Consensus | (Experimental) Govern whether a proposed memory should be stored by multi-agent quorum | L5 | https://github.com/sasuke15134321/agent-memory-consensus |

---

## AI agent execution flow

```
User or task trigger
        │
        ▼
[1] Agent Security Gateway   ← scan input for threats, PII, injection
        │ safe
        ▼
[2] Agent Budget Guard       ← check budget, approval, audit readiness
        │ allow
        ▼
[3] Execute paid API call or x402 payment
        │
        ▼
[4] Agent Memory API         ← store audit context, payment record, decision log
        │
        ▼
[5] Agent Budget Guard       ← record completed payment, classify invoice
        │
        ▼
[6] (Optional) Agent Memory Consensus  ← governance check before long-term memory write
```

Agent Evolution Engine can orchestrate steps 1–5 as a single API call.

---

## Payment rail compatibility

| Rail | Supported | Notes |
|------|-----------|-------|
| x402 | ✅ | All paid endpoints return HTTP 402 with x402 v2 manifest |
| USDC (Base) | ✅ | Primary settlement currency, eip155:8453 |
| JPYC | ✅ | Japan yen-pegged stablecoin, invoice classification supported |
| Arc (ERC-8183) | Planned | Pre-execution control layer before job funding |
| Kaia | Planned | Compatible payment rail for future integration |

---

## next_recommended pattern

Every API in this stack returns a `next_recommended` field in its response.
This allows AI agents to chain API calls without hardcoded logic.

Example flow guided by `next_recommended`:

```json
// Step 1: Security Gateway response
{ "result": "safe", "next_recommended": "proceed_to_budget_check" }

// Step 2: Budget Guard response
{ "result": "allow", "next_recommended": "proceed_to_payment" }

// Step 3: Memory API response (after payment)
{ "memory_id": "mem_001", "next_recommended": "proceed_to_invoice_classification" }
```

An agent can follow this chain autonomously without knowing the full stack in advance.

---

## API endpoints

| API | Endpoint | Method | Price | Description |
|-----|----------|--------|-------|-------------|
| Agent Security Gateway | /api/security/scan | POST | 0.03 USDC | Scan for threats, PII, injection |
| Agent Security Gateway | /api/trust/check | POST | 0.05 USDC | Check API trust score (L6 scanner) |
| Agent Budget Guard | /api/budget/check | POST | 0.03 USDC | Check budget and approval status |
| Agent Budget Guard | /api/budget/record | POST | 0.02 USDC | Record a spending decision |
| Agent Budget Guard | /api/record-payment | POST | 0.02 USDC | Log a completed x402 payment |
| Agent Budget Guard | /api/classify-invoice | POST | 0.03 USDC | Japan invoice classification |
| Agent Budget Guard | /api/budget/report/{id} | GET | 0.02 USDC | Audit-ready budget report |
| Agent Memory API | /api/memory/store | POST | 0.05 USDC | Store encrypted memory |
| Agent Memory API | /api/memory/recall | POST | 0.03 USDC | Recall stored memory |
| Agent Memory API | /api/memory/audit | GET | 0.02 USDC | Retrieve audit log |
| Agent Evolution Engine | /api/evolution/analyze | POST | 0.20 USDC | Analyze agent ecosystem |
| Agent Evolution Engine | /api/evolution/execute | POST | 0.30 USDC | Execute evolution strategy |
| Agent Memory Consensus | /api/memory/consensus | POST | 0.05 USDC | Memory governance decision (experimental) |

---

## Arc / ERC-8183 relevance

Arc and ERC-8183 may enable AI agents to receive jobs, use escrow, and settle payments on-chain autonomously.

This stack fits as a pre/post-execution control layer:

- **Before ERC-8183 job funding**: run Agent Security Gateway + Agent Budget Guard
- **After job execution**: run Agent Memory API to store the audit record
- **Before long-term memory write**: run Agent Memory Consensus (experimental)

The stack does not replace Arc infrastructure.
It provides the safety, budget, and audit layer that runs alongside it.

---

## JPYC relevance

Agent Budget Guard is specifically designed for Japan-grade compliance workflows:

- **Invoice classification**: determines whether a JPYC or USDC payment qualifies for Japan's small-amount invoice exemption (少額特例)
- **Audit log**: generates Japanese-language audit records compatible with bookkeeping requirements
- **Monthly ledger**: aggregates payment records into monthly summaries for accounting
- **JPYC support**: treat JPYC payments identically to USDC in all budget and audit flows

As JPYC expands on Kaia and other rails, Agent Budget Guard provides the accounting and compliance layer between on-chain transactions and Japanese tax/invoice requirements.

---

## What is working now

The following APIs are deployed and accepting requests:

| API | URL | Status |
|-----|-----|--------|
| Agent Security Gateway | https://agent-security-gateway.onrender.com | Working prototype |
| Agent Budget Guard | https://agent-budget-guard.onrender.com | Working prototype |
| Agent Memory API | https://agent-memory-api-bix5.onrender.com | Working prototype |
| Agent Evolution Engine | https://agent-evolution-engine.onrender.com | Working prototype |

All four APIs support x402 payment headers, return `next_recommended` in responses, and have Trust Scores of 9/10 (A) as measured by `/api/trust/check`.

---

## Experimental / Planned

| Component | Status | Description |
|-----------|--------|-------------|
| Agent Memory Consensus | Experimental | README and OpenAPI contract only. No backend implementation yet. |
| Agent Abuse Guard | Planned | Not implemented yet. Intended to detect API abuse patterns across agent sessions. |
| Arc / ERC-8183 integration | Planned | Pre-execution layer before ERC-8183 job funding on Arc testnet. |
| Kaia payment rail | Planned | JPYC on Kaia compatibility layer. |

---

## Repositories

| API / Project | Status | Repository | Demo |
|---|---|---|---|
| Agent Budget Guard | Working prototype | https://github.com/sasuke15134321/agent-budget-guard | https://agent-budget-guard.onrender.com |
| Agent Security Gateway | Working prototype | https://github.com/sasuke15134321/agent-security-gateway | https://agent-security-gateway.onrender.com |
| Agent Memory API | Working prototype | https://github.com/sasuke15134321/agent-memory-api | https://agent-memory-api-bix5.onrender.com |
| Agent Evolution Engine | Working prototype | https://github.com/sasuke15134321/agent-evolution-engine | https://agent-evolution-engine.onrender.com |
| Agent Memory Consensus | Experimental contract | https://github.com/sasuke15134321/agent-memory-consensus | Not deployed |

Demo URLs will be added only when each API has meaningful runtime behavior.
Experimental contracts may remain repository-only until implementation is ready.

---

## Agent flow

```
Security Gateway → Budget Guard → x402 Payment → Memory Consensus → Receipt / Invoice
```

---

## Related repositories

| Repository | Description |
|------------|-------------|
| [agent-security-gateway](https://github.com/sasuke15134321/agent-security-gateway) | L4 security scan API |
| [agent-budget-guard](https://github.com/sasuke15134321/agent-budget-guard) | L4/L5 budget and invoice API |
| [agent-memory-api](https://github.com/sasuke15134321/agent-memory-api) | L5 encrypted memory API |
| [agent-evolution-engine](https://github.com/sasuke15134321/agent-evolution-engine) | L4/L5/L6 orchestrator API |
| [agent-memory-consensus](https://github.com/sasuke15134321/agent-memory-consensus) | Experimental memory governance API |
| [ai-agent-payment-safety-stack](https://github.com/sasuke15134321/ai-agent-payment-safety-stack) | This repository — stack overview and documentation |

---

## Status

| API | x402 | Trust Score | AEO-ready | Implementation |
|-----|------|-------------|-----------|----------------|
| Agent Security Gateway | ✅ | 9/10 (A) | ✅ | Working prototype |
| Agent Budget Guard | ✅ | 9/10 (A) | ✅ | Working prototype |
| Agent Memory API | ✅ | 9/10 (A) | ✅ | Working prototype |
| Agent Evolution Engine | ✅ | 9/10 (A) | ✅ | Working prototype |
| Agent Memory Consensus | — | — | ✅ | Experimental contract (README and OpenAPI only) |
| Agent Abuse Guard | — | — | — | Planned (not implemented yet) |

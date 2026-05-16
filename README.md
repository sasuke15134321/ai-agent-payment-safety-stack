# AI Agent Payment Safety Stack

A stack of APIs for AI agents that call paid APIs, make x402 payments, store memory, and create audit-ready logs.

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

## Related repositories

| Repository | Description |
|------------|-------------|
| [agent-security-gateway](https://github.com/sasuke15134321/agent-security-gateway) | L4 security scan API |
| [agent-budget-guard](https://github.com/sasuke15134321/agent-budget-guard) | L4/L5 budget and invoice API |
| [agent-memory-api](https://github.com/sasuke15134321/agent-memory-api) | L5 encrypted memory API |
| [agent-evolution-engine](https://github.com/sasuke15134321/agent-evolution-engine) | L4/L5/L6 orchestrator API |
| [agent-memory-consensus](https://github.com/sasuke15134321/agent-memory-consensus) | Experimental memory governance API |

---

## Status

| API | x402 | Trust Score | AEO-ready | Arc compatibility |
|-----|------|-------------|-----------|-------------------|
| Agent Security Gateway | ✅ | 9/10 (A) | ✅ | ✅ |
| Agent Budget Guard | ✅ | 9/10 (A) | ✅ | ✅ |
| Agent Memory API | ✅ | 9/10 (A) | ✅ | ✅ |
| Agent Evolution Engine | ✅ | 9/10 (A) | ✅ | ✅ |
| Agent Memory Consensus | Planned | — | ✅ | ✅ |

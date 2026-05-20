# Agent Control Primitives

Small APIs for controlling AI agent security, budget, memory, and workflow quality.

CDP Bazaar already has strong market data, search, and token risk APIs.
But agent-control primitives are still missing:
- Prompt risk before tool calls
- Budget approval before API payment
- Audit-ready memory after decisions
- Workflow analysis across Security, Budget, Payment, and Memory

These 4 APIs fill that gap.

## Current Primitives

Security Primitive — agent-security-gateway
Scan prompts before an AI agent calls tools or paid APIs.
POST /api/security/scan
0.05 USDC per call

Budget Primitive — agent-budget-guard
Check budget before an AI agent pays for an API.
POST /api/budget/check
0.03 USDC per call

Memory Primitive — agent-memory-api
Store audit-ready memory after an AI agent makes a decision.
POST /api/memory/store
0.05 USDC per call

Workflow Primitive — agent-evolution-engine
Analyze Security, Budget, Payment, Memory workflow traces.
POST /api/evolution/analyze
0.20 USDC per call

## Observed Bazaar Gap

As of May 2026, CDP Bazaar has 48,000+ registered APIs.
The dominant categories are market data and search.

Gaps observed:
- security/risk: token rug detection only, no AI agent input security
- budget/payment: wallet transfers only, no agent spend control
- audit/memory/logging: empty
- agent workflow control: empty

## Recommended First Call

Start with agent-security-gateway.

Before an AI agent calls a tool, stores memory, or makes a paid API request,
scan the input first.

POST https://agent-security-gateway.onrender.com/api/security/scan

## All APIs are indexed in CDP Bazaar

Discovery:
https://api.cdp.coinbase.com/platform/v2/x402/discovery/merchant?payTo=0x60c402878EfcEcAe5733A88075328Aa2320C39BE

## Disclaimer

Not a wallet. Not a payment processor. Not a marketplace.
Small control APIs for AI agent workflows.
Not officially affiliated with Coinbase, Circle, CDP, Arc, JPYC, or any related foundation.

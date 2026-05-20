# Agent Control Primitives

Small composable APIs for controlling AI agent actions at external boundaries.

As AI agents connect to tools, MCP servers, sandboxes, memory, payments, and external APIs,
the critical boundary shifts from the model to the execution and access layer.

Agent Control Primitives are small APIs placed at those boundaries —
before tool calls, memory writes, payments, sandbox execution, and MCP access.

## Why now

CDP Bazaar (May 2026, 48,000+ APIs):
- market data / search: dominant
- audit / memory / logging: 0 entries
- agent input security: near zero
- agent spend control: near zero

Anthropic announced Claude Managed Agents with self-hosted sandboxes and MCP tunnels (May 19, 2026).
This separates agent reasoning from tool execution.
New boundaries need new checks.

## Current Primitives

agent-security-gateway
Scan prompts before an AI agent calls tools, stores memory, or makes paid API requests.
POST /api/security/scan — 0.05 USDC

agent-budget-guard
Check budget limits before an AI agent pays for APIs or executes x402 requests.
POST /api/budget/check — 0.03 USDC

agent-memory-api
Store audit-ready memory after an AI agent makes a decision or completes a workflow step.
POST /api/memory/store — 0.05 USDC

agent-evolution-engine
Analyze Security, Budget, Payment, Memory workflow traces and recommend improvements.
POST /api/evolution/analyze — 0.20 USDC

All 4 APIs are indexed in CDP Bazaar.
Discovery: https://api.cdp.coinbase.com/platform/v2/x402/discovery/merchant?payTo=0x60c402878EfcEcAe5733A88075328Aa2320C39BE

## Seven Integrity Layers for AI Agents

Core control layers needed before agents act:

1. Time Integrity — when did it happen, in what order
2. Gate Integrity — where to stop, what threshold to enforce
3. Schema Integrity — what shape the data must be in
4. Identity Integrity — who is executing and with what authority
5. Quota Integrity — how much is allowed to be used or spent
6. Context Integrity — is this action within the intended scope
7. Kill Switch Integrity — how to evaluate, correct, and stop

## Planned Primitive Packs

Agent Core Integrity Pack
Timestamp Integrity Checker / Gate Decision Auditor / Schema Compliance Checker /
Identity Scope Checker / Quota Limit Checker / Context Boundary Checker / Kill Switch Policy Checker

Sandbox and MCP Boundary Pack
Sandbox Boundary Checker / MCP Tunnel Policy Checker / Private Tool Schema Validator /
Egress Risk Checker / Sandbox Event Ledger

RAG-CAG Governance Pack
Hot/Cold Knowledge Classifier / Cache Eligibility Checker / RAG-CAG Router /
Cache Freshness Checker / Cache Poisoning Detector

Agent Update Integrity Pack
Skill Regression Checker / Update Conflict Checker / Forgetting Risk Estimator /
GEPA Candidate Gate / Prompt Policy Regression Checker

CI/CD Boundary Pack
GitHub Actions Permission Auditor / Token Scope Validator /
Package Publish Gate / Secret Exposure Checker

## Recommended First Call

Start with agent-security-gateway.

Before an AI agent calls a tool, stores memory, or makes a paid API request,
scan the input first.

POST https://agent-security-gateway.onrender.com/api/security/scan

## Disclaimer

Not a wallet. Not a payment processor. Not a marketplace.
Small control APIs for AI agent boundaries.
Not officially affiliated with Anthropic, Coinbase, Circle, CDP, Arc, JPYC, or any related foundation.
References to Claude Managed Agents and CDP Bazaar are for context only.

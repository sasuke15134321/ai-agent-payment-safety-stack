# Agent Control Primitives Catalog

## Current Primitives

name: agent-security-gateway
category: Security / Input Risk
purpose: Scan prompts before tool calls, memory writes, or payments
when_to_use: Before any external action involving user or agent input
cost_tier: medium
status: current
endpoint: POST /api/security/scan
price: 0.05 USDC

name: agent-budget-guard
category: Budget / Payment Control
purpose: Check budget limits before API payments or x402 requests
when_to_use: Before any paid API call or x402 payment
cost_tier: low
status: current
endpoint: POST /api/budget/check
price: 0.03 USDC

name: agent-memory-api
category: Audit Memory
purpose: Store audit-ready memory after agent decisions
when_to_use: After decisions, workflow steps, or payment events
cost_tier: medium
status: current
endpoint: POST /api/memory/store
price: 0.05 USDC

name: agent-evolution-engine
category: Workflow Analysis
purpose: Analyze Security-Budget-Payment-Memory workflow traces
when_to_use: For workflow audit and improvement analysis
cost_tier: high
status: current
endpoint: POST /api/evolution/analyze
price: 0.20 USDC

## Planned Primitives — Agent Core Integrity Pack

name: Timestamp Integrity Checker
category: Time Integrity
purpose: Verify event ordering and detect temporal conflicts
cost_tier: low
status: planned

name: Gate Decision Auditor
category: Gate Integrity
purpose: Audit gate decisions and threshold consistency
cost_tier: low
status: planned

name: Schema Compliance Checker
category: Schema Integrity
purpose: Validate tool arguments and structured outputs
cost_tier: low
status: planned

name: Identity Scope Checker
category: Identity Integrity
purpose: Verify agent identity and token scope
cost_tier: low
status: planned

name: Quota Limit Checker
category: Quota Integrity
purpose: Enforce spending, call, and resource limits
cost_tier: low
status: planned

name: LLM Call Necessity Checker
category: Quota Integrity
purpose: Determine if LLM call is necessary or rule-based is sufficient
cost_tier: low
status: planned

name: Irreversible Action Gate
category: Gate Integrity
purpose: Flag actions that cannot be undone before execution
cost_tier: low
status: planned

## Planned Primitives — Sandbox and MCP Boundary Pack

name: Sandbox Boundary Checker
category: Sandbox Integrity
purpose: Check what is allowed inside self-hosted sandboxes
cost_tier: low
status: planned

name: MCP Tunnel Policy Checker
category: MCP Boundary
purpose: Verify which private MCP servers and tools can be called
cost_tier: low
status: planned

name: Private Tool Schema Validator
category: Schema Integrity
purpose: Validate arguments for private MCP tools
cost_tier: low
status: planned

name: Egress Risk Checker
category: Network Boundary
purpose: Check outbound communications from sandboxes
cost_tier: low
status: planned

name: Sandbox Event Ledger
category: Audit
purpose: Record all events inside sandbox execution
cost_tier: low
status: planned

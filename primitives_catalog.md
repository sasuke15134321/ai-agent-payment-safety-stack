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

## Beta Primitives — Agent Insulation Primitives v0.1

name: Tool Call Dry-run Validator
category: Tool Boundary / Insulation
purpose: Detect destructive tool calls before execution. Checks tool name and arguments for payment, file deletion, deploy, secret access, memory write, and destructive action patterns.
when_to_use: Before any tool call that could have irreversible or high-impact effects
cost_tier: low
status: beta
endpoint: POST /api/tool/dry-run-validate
price: free (beta)

name: Tool Response Sanitizer
category: Tool Boundary / Insulation
purpose: Scan tool responses for injected instructions before the agent processes them. Detects prompt injection, system prompt reveal, API key exposure, suspicious URLs, and hidden instructions.
when_to_use: After receiving a tool response, before the agent acts on the content
cost_tier: low
status: beta
endpoint: POST /api/tool/response-sanitize
price: free (beta)

name: Schema Drift Checker
category: Schema Integrity / Insulation
purpose: Detect unexpected changes in tool schemas before accepting updates. Flags new required fields, dangerous field names, suspicious descriptions, and permission expansions.
when_to_use: Before accepting an updated tool or MCP schema from an external source
cost_tier: low
status: beta
endpoint: POST /api/schema/drift-check
price: free (beta)

name: Identity Scope Checker
category: Identity Integrity / Insulation
purpose: Verify agent scopes and role before privileged actions. Detects missing scopes, role mismatch, privilege escalation, and excessive scope grants.
when_to_use: Before any privileged operation such as delete, deploy, admin access, or payment
cost_tier: low
status: beta
endpoint: POST /api/identity/scope-check
price: free (beta)

name: Quota Limit Checker
category: Quota Integrity / Insulation
purpose: Enforce usage limits before the agent calls tools, LLMs, or makes payments. Tracks tool_calls, llm_calls, payment_amount, and subagent_count against configured limits.
when_to_use: Before each tool call, LLM call, or payment to prevent runaway agent loops
cost_tier: low
status: beta
endpoint: POST /api/quota/check
price: free (beta)

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

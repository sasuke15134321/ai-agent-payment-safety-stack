# Agent Approval Unit Builder - Project Context

## Project Overview
Agent Approval Unit Builder API v0.1 converts AI-generated findings, patches, payment requests, deployment proposals, memory writes, tool execution requests, or decision-support outputs into minimal human decision contracts (Approval Units).

Core concept: **Approval Unit = Human Decision Contract**

## Implementation Status

### x402 & CDP Bazaar Integration
**Dynamic routes実装完了（2026-05-25）**
- `/.well-known/x402` を CDP Bazaar 標準の dynamic routes 形式に更新
- `/api/approval-unit/build` エンドポイントを含む（0.05 USDC）
- resources 配列内に各エンドポイントをフル仕様で記載
  - `accepts`: 支払い要件（scheme, network, amount, asset, payTo）
  - `extensions.bazaar.info`: input/output schemas
  - `type`: "http"
  - `x402Version`: 2
- CDP Bazaar クローラー検出待ち

## Architecture Notes
- **Payment Middleware**: x402 exact payment scheme on Base mainnet (eip155:8453)
- **Endpoints**: 
  - `POST /api/approval-unit/build` (0.05 USDC) - Paid endpoint
  - `POST /api/remediation/verify` (Free) - Verification gate
- **Bazaar Discovery**: Automatic discovery via /.well-known/x402 for CDP Bazaar facilitators

## Dependencies
- FastAPI
- Pydantic
- x402 payment infrastructure (Coinbase Commerce)

## Design Specs (13 confirmed)

**Updated 2026-05-27**: agent_decision_provenance_spec.md (2026-05-27 revision) is part of the 13 confirmed design specs.

Core principle: Decision ≠ provenance (plausibility is not traceability).

## Experimental Agent Payment Action Record Builder v0.1

- Endpoint: `POST /api/payment-action-record/build`
- Type: experimental, stateless, free (no x402)
- Purpose: Combines payment_intent + pre_payment_checks + post_payment_checks + agent_action_atom + context_state + decision into one external control record
- audit_ready: rule-based (true if payment_intent + decision + checks + atom_or_evidence all present)
- Output fields: record_id, record_type, experimental, stateless, payment_flow, can_be_combined_into, non_goals
- Not a payment protocol, settlement layer, wallet, legal audit system, or official standard
- commit: "Add experimental Agent Payment Action Record builder" / 2026-06-13

## Experimental Payment Control Evidence Packet Builder v0.1

- Repository: ai-agent-payment-safety-stack
- Endpoint: POST /api/payment-evidence-packet/build
- Purpose: Add a minimal stateless builder that packages payment intent, checks, evidence, Agent Action Atom, and Agent Payment Action Record into one external evidence packet.
- Positioning: Experimental external evidence packet builder for AI-agent payment control and evidence workflows.
- Relation: Works with Agent Payment Control Evidence Pack, Agent Action Atom Builder, and Agent Payment Action Record Builder.
- Scope: Free/stateless builder. No DB storage, no pricing change, no x402 manifest change, no existing endpoint changes.
- Notes: Not a payment protocol, not a settlement layer, not a wallet, not a legal audit system, not an official standard.
- commit: "Add experimental Payment Control Evidence Packet builder" / 2026-06-13

## Experimental Agent Spending Policy Builder v0.1

- Repository: agent-budget-guard
- Endpoint: POST /api/spending-policy/build
- Purpose: Add a free stateless builder that creates structured AI-agent spending policies with limits, allowed currencies, allowed services, approval rules, context state, and Atom-compatible reference.
- Positioning: Free builder / glue layer for AI-agent spending control. Actual budget checks and records remain paid x402 endpoints.
- Relation: Feeds into Budget Check, Agent Action Atom, Agent Payment Action Record, and Payment Control Evidence Packet workflows.
- Scope: Free/stateless builder. No DB storage, no pricing change, no x402 manifest change, no existing endpoint changes.
- Notes: Not a payment protocol, not a settlement layer, not a wallet, not a legal compliance system, not an official standard.
- commit: "Add experimental Agent Spending Policy builder" / 2026-06-13

## Agent Reasoning Cost & Memory Boundary Extension v0.1

- Repository: agent-budget-guard
- Endpoint: POST /api/spending-policy/build
- Purpose: Extend the free Agent Spending Policy Builder with token budget, memory scope policy, reasoning cost boundary, and human review triggers.
- Positioning: External control material for AI-agent token, memory, spending, and payment decisions.
- Relation: Feeds into Budget Check, Agent Action Atom, Agent Payment Action Record, Payment Control Evidence Packet, Decision Cost Trace, Memory Provenance Graph, and Token Placement Governance.
- Scope: Extension of existing free/stateless builder. No new endpoint, no DB storage, no pricing change, no x402 manifest change, no existing paid endpoint changes.
- Notes: Not a model provider, not a memory store, not a payment protocol, not a settlement layer, not a wallet, not a legal compliance system, not an official standard.
- commit: "Extend spending policy with token and memory boundaries" / 2026-06-13

## Experimental Tool Permission Policy Builder v0.1

- Repository: agent-security-gateway
- Endpoint: POST /api/tool-permission-policy/build
- Purpose: Add a free stateless builder that creates external policy material for AI-agent tool and API permission decisions, including allowed tools, blocked tools, approval rules, risk boundaries, context state, and Atom-compatible reference.
- Positioning: External control material for AI-agent tool permission, memory access, network access, paid API use, and sensitive action boundaries.
- Relation: Feeds into Agent Spending Policy, Budget Check, Agent Action Atom, Agent Payment Action Record, Payment Control Evidence Packet, Decision Cost Trace, and Tool Permission Boundary.
- Scope: Free/stateless builder. No DB storage, no pricing change, no x402 manifest change, no existing paid endpoint changes.
- Notes: Not a sandbox, not a model provider, not a wallet, not a payment protocol, not a settlement layer, not a legal compliance system, not an official standard.
- commit: "Add experimental Tool Permission Policy builder" / 2026-06-13

## Experimental Memory Provenance Context Record Builder v0.1

- Repository: agent-memory-api
- Endpoint: POST /api/memory-provenance-record/build
- Purpose: Add a free stateless builder that creates external control material for AI-agent memory and context usage, including raw sources, extracted facts, profile or context summary, state, use rule, evidence, last_checked, risk flags, context usage, and Atom-compatible reference.
- Positioning: External control material for AI-agent memory provenance, context state, stale memory prevention, and source-of-truth usage before tool, spending, token, or payment decisions.
- Relation: Feeds into Tool Permission Policy, Agent Spending Policy, Budget Check, Agent Action Atom, Agent Payment Action Record, Payment Control Evidence Packet, Decision Cost Trace, Memory Provenance Graph, and Token Placement Governance.
- Scope: Free/stateless builder. No DB storage, no pricing change, no x402 manifest change, no existing paid endpoint changes.
- Notes: Not a memory store, not a vector database, not a model provider, not a payment protocol, not a wallet, not a settlement layer, not a legal compliance system, not an official standard.
- commit: "Add experimental Memory Provenance Context Record builder" / 2026-06-13

## External Control Materials Map v0.1

- Repository: ai-agent-payment-safety-stack
- Endpoint: GET /.well-known/external-control-materials.json
- Purpose: Add an AI-readable map showing how external control materials fit together before and after AI-agent paid API usage.
- Flow: Memory Provenance Context Record → Tool Permission Policy → Agent Spending Policy → Budget Check → Agent Payment Action Record → Payment Control Evidence Packet → Payment Evidence Check.
- Positioning: External control materials for AI-agent memory, tool permission, token budget, spending, payment decisions, and evidence workflows.
- Pricing: Free static map. Not included in x402 manifest.
- Relation: Connects agent-memory-api, agent-security-gateway, agent-budget-guard, and ai-agent-payment-safety-stack into a recommended AI-readable flow.
- Scope: Static map / discovery material only. No DB storage, no pricing change, no x402 manifest change, no existing paid endpoint changes.
- Notes: Not an AI OS, not a model provider, not a memory store, not a sandbox, not a wallet, not a payment protocol, not a settlement layer, not a legal compliance system, not an official standard.
- commit: "Add External Control Materials Map" / 2026-06-13

## Experimental Command Execution Gate Builder v0.1

- Repository: agent-security-gateway
- Endpoint: POST /api/command-execution-gate/build
- Purpose: Add a free stateless builder that creates external control records for AI-agent shell command execution decisions. Detects dangerous patterns (npx, curl | bash, credential access, etc.), assesses risk level (high/medium/low), and returns action recommendation (deny / require_human_approval_or_sandbox / allow_with_monitoring).
- Positioning: Experimental external control record builder for AI-agent command execution safety. Does NOT execute shell commands.
- Relation: Feeds into Tool Permission Policy, Agent Spending Policy, Agent Action Atom, Execution Provenance Trace, Payment Control Evidence Packet, and External Control Materials Map.
- Scope: Free/stateless builder. No DB storage, no pricing change, no x402 manifest change, no existing endpoint changes.
- Notes: Not a sandbox, not a shell executor, not a model provider, not a payment protocol, not a settlement layer, not a legal compliance system, not an official standard.
- commit: "Add Command Execution Gate Builder" / 2026-06-13

## External Control Materials Map v0.2

- Repository: ai-agent-payment-safety-stack
- Endpoint: GET /.well-known/external-control-materials.json
- Purpose: Update the AI-readable external control materials map to include Observability Data Boundary and Command Execution Gate.
- Flow: Memory Provenance Context Record → Tool Permission Policy → Observability Data Boundary → Command Execution Gate → Agent Spending Policy → Budget Check → Agent Payment Action Record → Payment Control Evidence Packet → Payment Evidence Check.
- Positioning: External control materials for AI-agent memory, tool permission, observability data, command execution, token budget, spending, payment decisions, and evidence workflows.
- Pricing: Free static map. Not included in x402 manifest.
- Scope: Static map / discovery material only. No DB storage, no pricing change, no x402 manifest change, no existing paid endpoint changes.
- Notes: Not an AI OS, not a model provider, not a memory store, not a sandbox, not a shell executor, not a wallet, not a payment protocol, not a settlement layer, not a legal compliance system, not an official standard.
- commit: "Update External Control Materials Map to v0.2" / 2026-06-13

## OKF-style External Control Materials Bundle v0.2

- Repository: ai-agent-payment-safety-stack
- Index: /okf/index.md
- Version: 0.2 (updated from v0.1's 11 materials to v0.2's 12 materials)
- Type: OKF-compatible experimental Markdown bundle
- Purpose: Provides Markdown-based documentation of 12 external control materials organized according to the 12-step recommended flow in External Control Materials Map v0.4. Introduces Search Result Trust Check as the trust gate before tool execution and payment decisions.
- 12 Materials:
  1. Memory Provenance Context Record
  2. Search Result Trust Check
  3. Tool Permission Policy
  4. Tool Approval Check
  5. Observability Data Boundary
  6. Command Execution Gate
  7. Agent Spending Policy
  8. Payment Review (Payment Gate)
  9. Budget Check
  10. Agent Payment Action Record
  11. Payment Control Evidence Packet
  12. Payment Evidence Check
- Three Core Judgment Gates: Search Result Trust Check (Step 2, trust), Tool Approval Check (Step 4, execution), Payment Review (Step 8, payment)
- Positioning: OKF-compatible external control materials knowledge base for AI-agent memory provenance, search result trust, tool permission, tool approval, observability boundaries, command execution, spending, payment decisions, and evidence workflows. Inspired by Open Knowledge Format (not an official OKF implementation).
- Pricing: Free (Markdown documentation only)
- Scope: Documentation update only. No new API endpoints, no DB storage, no pricing changes, no x402 manifest changes, no existing endpoint changes.
- Notes: Experimental OKF-compatible bundle. Not a model provider, not a memory store, not a sandbox, not a shell executor, not a wallet, not a payment protocol, not a settlement layer, not a legal compliance system, not an official standard.
- Related: Mirrors External Control Materials Map v0.4 endpoint structure and decision gates
- commit: "Update OKF-style bundle to v0.2" / 2026-06-14

## External Control Materials Cross-Link v0.2

- Purpose: Update cross-links across related repositories so agents can discover the central External Control Materials Map v0.4 and OKF-style Bundle v0.2 from any service.
- Target repositories: agent-memory-api / agent-security-gateway / agent-budget-guard / arc_agent_payment_boundary_demo
- Central map: https://ai-agent-payment-safety-stack.onrender.com/.well-known/external-control-materials.json
- OKF-style bundle: https://ai-agent-payment-safety-stack.onrender.com/okf/index.md
- Core gates: trust（Search Result Trust Check）/ execution（Tool Approval Check）/ payment（Payment Review）
- Overall flow: Trust → Execution → Payment → Evidence
- Scope: Documentation and agent-readable discovery links only. No new API, no endpoint change, no pricing change, no x402 manifest change, no DB change, no Render setting change, no existing paid endpoint change.
- Notes: Do not imply official Google / OKF / Arc / Circle / Coinbase / Anthropic / OpenAI / Cursor / MCP partnership, certification, or standard compliance.
- Implementation: README.md sections added to all 4 repositories with External Control Materials descriptions and cross-links
- Status: ✅ Completed 2026-06-14

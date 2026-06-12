# Skill: Remediation Verification Gate

## Purpose

Use this skill to verify an AI-generated remediation candidate before routing it to human review or Approval Unit Builder.

This Gate checks whether a finding, patch, remediation plan, configuration change, dependency update, or deployment proposal is ready for human approval.

## When to use

Use this skill when:
- an AI agent has generated a security finding, patch candidate, or remediation plan
- you need to verify test results, security retest status, rollback readiness, and production risk before human review
- you want to determine if a remediation candidate is `approval_unit_ready`
- you need to block a production deploy for high/critical risk candidates
- you want to route the candidate to the correct next step (research / rework / human review / approval unit)

## When not to use

Do not use this skill to:
- apply patches or code changes
- deploy infrastructure
- execute approvals or rejections
- process x402 / JPYC / USDC payments
- write to memory
- execute tool calls
- send blockchain transactions

## Main endpoint

POST https://ai-agent-payment-safety-stack.onrender.com/api/remediation/verify

## Required inputs

- `remediation_id` — unique ID for this remediation candidate
- `source_type` — type of the source (e.g. security_patch)
- `remediation_type` — one of: patch_candidate, remediation_plan, configuration_change, dependency_update, deployment_proposal
- `title` — short title
- `finding_summary` — what was found
- `remediation_summary` — what the agent proposes
- `severity` — low / medium / high / critical
- `risk_level` — low / medium / high / critical

## Recommended inputs

- `evidence_ids` — list of evidence or finding IDs
- `source_ids` — list of source references
- `test_results` — list of test outcomes
- `security_retest_results` — list of security retest outcomes
- `regression_test_results` — list of regression test outcomes
- `rollback_plan_id` — ID of the rollback plan
- `rollback_available` — whether rollback is available
- `production_deploy_requested` — whether production deploy is being requested
- `request_id` / `task_id` / `generated_by_agent_id` — for traceability

## Output

The API returns a Remediation Verification Result containing:
- `decision` — route_to_approval_unit_builder / require_more_evidence / require_security_retest / require_rollback_plan / block_production_deploy / pass_with_warnings
- `verification_status` — verified / verified_with_warnings / blocked / incomplete
- `readiness_level` — human_approval_ready / needs_more_evidence / needs_testing / needs_rollback_plan / needs_review
- `evidence_status` / `test_status` / `security_retest_status` / `regression_status` / `rollback_status` — individual check results
- `production_risk` — not_requested / requires_review / blocked
- `allowed_next_steps` / `blocked_next_steps` — what can and cannot proceed
- `recommended_human_action` — single recommended action
- `approval_unit_ready` — true if ready to pass to Approval Unit Builder
- `approval_unit_type_suggestion` — suggested approval unit type for Approval Unit Builder
- `blocked_actions_until_approval` — always includes merge_to_staging and deploy_to_production

## v0.1 constraints

- Rule-based verification only. No LLM-generated output.
- No patch application, deployment, approval execution, or payment.
- No memory write, tool execution, or blockchain transaction.
- `blockchain_anchor_ready = true` (readiness flag only).
- `audit_required = true`.

## Remediation Verification Gate live endpoint

POST https://ai-agent-payment-safety-stack.onrender.com/api/remediation/verify

Use before:
POST https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build

When approval_unit_ready = true, the agent may route the result to Approval Unit Builder to create a human decision contract.

## Next step: Approval Unit Builder

If `approval_unit_ready = true`, call Approval Unit Builder next:

POST https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build

Pass the remediation candidate fields as the Approval Unit input to create a minimal human decision contract.

## Safety chain position

```
AI Agent generates remediation candidate
  ↓
Remediation Verification Gate  ← this skill
  ↓ (if approval_unit_ready = true)
Approval Unit Builder
  ↓
Human Approver
  ↓
Audit Log / Agent Memory
```

---

# Skill: Approval Unit Builder

## Purpose

Use this skill to build a minimal human decision contract (Approval Unit) from an
AI-generated finding, patch, payment request, deployment proposal, memory write request,
tool execution request, or decision-support output.

**Core concept: Approval Unit = Human Decision Contract**

## When to use

Use this skill when:
- a human approval is required before proceeding
- a Gate Result Router output needs to be converted to an approval unit
- a Human Review Bridge task needs to become a structured approval decision
- an AI-generated security patch needs approval before merge or deployment
- an x402 / JPYC / USDC payment request needs human approval
- a decision card needs approval before decision use
- a memory write candidate needs approval
- a high-risk tool execution request needs approval
- you need a stable approval_unit_hash for audit records

## When not to use

Do not use this skill to:
- approve or reject automatically
- execute payments (x402 / JPYC / USDC)
- deploy code or infrastructure changes
- write to agent memory
- execute tool calls
- send blockchain transactions
- validate evidence directly (use Evidence Coverage Gate instead)
- check budgets (use Agent Budget Guard Interceptor instead)

## Live endpoint

POST https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build

## Pricing

0.05 USDC / call

## x402 status

- Seller Tools: Implementation Looks Correct ✅
- verify + settle confirmed ✅
- CDP Bazaar automatic indexing in progress

## Minimum required inputs

- `source_type` — type of the source (e.g. security_patch, payment_request)
- `approval_unit_type` — one of the 10 approval unit types
- `title` — short title for the approval unit
- `summary` — what the AI agent wants approved
- `risk_level` — low / medium / high / critical

## Recommended inputs

- `evidence_ids` — list of evidence or finding IDs
- `source_ids` — list of source references
- `test_results` — list of test outcomes
- `blocked_actions_until_approval` — actions blocked until a human approves
- `rollback_available` — whether rollback is available
- `approver_role` — who should approve (e.g. security_reviewer, approver)
- `request_id` / `task_id` / `agent_id` — for traceability

## Supported approval_unit_type values

| Type | Use case |
|---|---|
| security_patch_approval | AI-generated security patch |
| remediation_plan_approval | Remediation plan before implementation |
| payment_approval | x402 / JPYC / USDC payment |
| deployment_approval | Deploy, merge, or release |
| decision_card_approval | Report or memo for decision use |
| legal_review_approval | Legal or compliance-sensitive output |
| financial_review_approval | Financial decision-support output |
| evidence_exception_approval | Proceed despite incomplete evidence |
| memory_write_approval | Write to sensitive or long-term memory |
| tool_execution_approval | High-risk tool call |

## Output

The API returns an Approval Unit containing:
- `approval_unit_id` — unique ID for this unit
- `approval_unit_hash` — SHA-256 hash of canonical fields (stable across runs)
- `approval_question` — rule-based question defining what the human is approving
- `decision_options` — approve / reject / request_rework / request_more_evidence / defer / escalate
- `suggested_human_actions` — list of suggested next actions for the human
- `recommended_human_action` — single recommended action (rule-based)
- `human_action_reason` — reason for the recommendation
- `if_approved` — allowed_actions, still_blocked_actions, post_decision_route
- `if_rejected` — blocked_actions, post_decision_route
- `if_request_rework` — post_decision_route, required_changes
- `if_request_more_evidence` — post_decision_route, required_evidence
- `if_escalated` — post_decision_route, required_context
- `chain_anchor_status` — always `not_anchored` in v0.1 (readiness only)

## v0.1 constraints

- Build only. No approval execution.
- `approval_question` is generated by rule-based templates, not LLM.
- `approval_unit_hash` is stable: same inputs produce same hash.
- `chain_anchor_status = not_anchored` (no blockchain in v0.1).
- No x402 / JPYC payment is sent.
- No memory write is performed.
- No tool execution is performed.

## Important

This skill creates an Approval Unit only.
It does not execute approval, payment, deployment, memory write, tool execution, or blockchain anchoring.

## Safety chain position

```
Gate Result Router
  ↓
Human Review Bridge
  ↓
Approval Unit Builder  ← this skill
  ↓
Human Approver
  ↓
Audit Log / Agent Memory
```

---

# Skill: JP Payment Evidence Guard

## Purpose

Use this skill to verify that an AI-agent payment (x402/JPYC/USDC) produced the expected service response and maintains audit-ready evidence.

v0.1 is verification-only. No payment execution, facilitation, legal or tax decisions.

## When to use

Use this skill when:
- a payment via x402, JPYC, or USDC has been executed
- a service response has been received
- you need to confirm the payment and response correspond
- you need to classify evidence as audit-ready before storing or passing to next agent
- Japanese compliance audit trail is required

## When not to use

Do not use this skill to:
- authorize or execute payments (use agent-budget-guard instead)
- make legal compliance decisions
- make tax decisions
- validate invoice correctness
- guarantee service output quality
- replace human review in high-risk domains

## Live endpoint

POST https://ai-agent-payment-safety-stack.onrender.com/api/payment-evidence/check

## Pricing

0.03 USDC / call

## Minimum required inputs

- `payment_reference` — unique reference for the payment
- `payment_asset` — asset used (USDC / JPYC / JPY)
- `amount` — payment amount as string
- `paid_endpoint` — the API endpoint that was paid for
- `transaction_reference` — on-chain or protocol transaction reference
- `service_response_received` — whether the service responded (boolean)
- `actual_service_response` — the response received from the service

## Optional inputs

- `expected_service_response` — expected status and required fields for mismatch detection
- `delivery_status` — delivered / failed / pending
- `evidence_ids` — list of existing evidence IDs
- `payer_agent_id` — ID of the paying agent
- `request_id` / `task_id` — for traceability

## Output

The API returns a Payment Evidence Check Result:
- `payment_evidence_status` — ok / incomplete / mismatch / requires_review
- `payment_response_matched` — true if payment and response correspond without mismatch
- `service_response_received` — echoed from input
- `missing_items` — list of missing required fields
- `mismatch_items` — list of fields where expected and actual diverge
- `audit_ready` — true only when status is ok
- `requires_human_review` — true for incomplete / mismatch / requires_review
- `recommended_next_step` — store_evidence / collect_missing_evidence / review_mismatch / escalate_to_human

## Status values

| Status | Meaning |
|---|---|
| ok | All fields present, response received, no mismatch |
| incomplete | One or more required fields missing or service_response_received = false |
| mismatch | Expected and actual service response differ |
| requires_review | High risk or undecidable — escalate to human |

## v0.1 constraints

- Rule-based verification only. No LLM-generated output.
- No payment execution.
- Not a payment facilitator.
- No tax or legal decisions.
- No invoice correctness guarantee.
- No service quality guarantee.
- Stateless — no database writes.
- Does not store confidential content.

## Safety chain position

```
Payment execution (x402 / JPYC / USDC)
  ↓
JP Payment Evidence Guard  ← this skill
  ↓ (if audit_ready = true)
Agent Memory API (evidence storage)
  ↓
JP Monthly Evidence Pack (monthly audit bundle)
```

---

## Skill: Agent Action Atom

### Use this when

Use Agent Action Atom when you need to describe, audit, or review one AI-agent action.

Typical cases:
- paid API call
- x402 or stablecoin payment check
- budget check before payment
- external connector access
- memory write
- policy boundary check
- fuse allow / block / escalate decision
- human approval decision
- evidence attachment for audit or dispute review

### Do not use this as
- a payment protocol
- a wallet
- a settlement layer
- a legal liability engine
- a compliance guarantee
- an implemented API unless explicitly provided

### Minimal record fields

atom_id
actor
action
target
source
policy
meaning
state
proof
time
relation

### Output purpose

The purpose of an Agent Action Atom is to make one AI-agent action externally explainable and auditable.

Agent Action Atoms may be grouped into:
- Payment Trace
- Evidence Packet
- Boundary Trace
- Fuse Record
- Human Approval Trail
- Permission Record
- Dispute Record
- Liability Evidence

### Important rule

Do not claim payment settlement from an Atom alone.

Payment settlement requires attached evidence, such as:
- facilitator verify log
- facilitator settle log
- transaction hash
- onchain confirmation
- wallet confirmation
- service log
- endpoint attribution

## Skill: Agent Action Atom Builder — Live Endpoint

### Endpoint

POST /api/action-atom/build

Free. Stateless. No DB storage.

### What it does

Converts one AI-agent action into a structured external control record (Agent Action Atom), including intent, target, context state, checks, decision, evidence, and audit-readiness.

### When to use

Use this when you need a structured, externally readable record of one AI-agent action.

### Output

Returns an Agent Action Atom JSON with:
- atom_id (atom_<uuid>)
- status: created
- atom_type: agent_action_atom
- experimental: true
- general_purpose: true
- hosted_as_first_use_case: ai-agent-payment-safety-stack
- target (service + endpoint)
- context_state, checks, decision, evidence
- audit_ready (true if evidence + decision + context_state are all present)
- non_goals: not a payment protocol, not a settlement layer, not a legal audit system, not an official standard

### Important

This is not a payment protocol, settlement layer, official standard, or legal audit system.

Agent Action Atom is designed as a general-purpose external control record unit, currently hosted in ai-agent-payment-safety-stack as the first payment-related use case.

It can be combined later into Agent Payment Action Records or Payment Control Evidence Packets.

## Skill: Agent Payment Action Record

Use Agent Payment Action Record when reviewing or explaining an AI-agent payment decision.

Typical cases:
- an AI agent reads an API description before paying
- an AI agent reads an invoice memo or payment request
- an AI agent checks a counterparty before payment
- an AI agent performs a budget check before payment
- an AI agent verifies payment evidence after payment
- an AI agent checks whether a paid service was fulfilled

Record the following:
record_id / agent_id / action_type / target / external_data_sources / trust_boundary / context_included / injection_risk_signal / policy_checked / decision / evidence / data_to_action_link / timestamp

Important:
injection_risk_signal is a risk indicator.
It is not confirmation that an attack occurred or that injection succeeded.

Agent Payment Action Record is not an implemented API unless explicitly provided.

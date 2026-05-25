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

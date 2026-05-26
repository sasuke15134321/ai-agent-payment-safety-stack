# AI Operational Governance Layer — Quickstart

## 1. What This Project Is

The AI Agent Payment Safety Stack is an operational governance layer designed for the era when AI systems generate and execute actions at scale. It addresses a fundamental requirement of AI autonomy: **responsible execution boundaries**. While AI can generate findings, create remediation plans, and propose deployments, human judgment and controlled execution pathways remain essential. This project provides the infrastructure to verify, approve, and audit AI-driven decisions before they affect systems.

---

## 2. The Core Problem

**Three critical misalignments:**

- **AI can generate actions.** CodeQL finds vulnerabilities. LLMs propose fixes. Autonomous agents suggest deployments. The volume and velocity of AI-generated decisions exceed human review capacity.

- **Humans still need execution boundaries.** A security finding is not authorization to deploy. A test passing is not permission for production. An approval for staging is not consent for production release. Each execution boundary requires explicit decision.

- **Approval ≠ unrestricted execution.** Even after human approval, execution must be scoped. Approved for staging? Production remains blocked. Approved for budget $100? The system enforces that limit. Approval is a decision contract, not a blank check.

**The governance layer bridges this gap.**

---

## 3. The Core Concepts

### Approval Unit = Human Decision Contract

An Approval Unit is a minimal, deterministic representation of what a human is deciding:
- What are they approving? (artifact, scope, decision type)
- What becomes allowed after approval? (allowed_actions)
- What remains blocked? (still_blocked_actions)
- What human action is suggested? (recommended_action)

Example:
```json
{
  "approval_question": "Approve this SQL injection fix for staging merge?",
  "allowed_actions": ["merge_to_staging"],
  "still_blocked_actions": ["deploy_to_production"],
  "recommended_human_action": "approve_staging_only"
}
```

The human decision is recorded atomically, with full audit trail and cryptographic hash for immutability.

### Decision Scope Policy = Execution Boundary Contract

After approval, the system enforces the approved scope. If a human approves staging deployment, production deployment is blocked by policy. If a human approves $100 spending, the system enforces that budget limit. Decision scope is a contract between human judgment and system execution.

---

## 4. The Governance Flow

```
Evidence
(CodeQL findings, Semgrep results, payment requests, API calls)
         ↓
    Verification
(Remediation Verification Gate: rule-based soundness check)
         ↓
 Human Decision Contract
(Approval Unit Builder: what human is approving?)
         ↓
  Controlled Execution
(Decision scope enforced: allowed ✓ / blocked ✗)
         ↓
     Audit Trail
(Decision + outcome recorded immutably)
```

---

## 5. The Two Live APIs

### Remediation Verification Gate

**Endpoint:** `POST /api/remediation/verify`

**Purpose:** Validate that an AI-generated remediation plan is sound before human approval.

**Key Output:** `approval_unit_ready: true/false`

When true, the remediation is safe to route to human approval. When false, the remediation plan requires rework.

---

### Approval Unit Builder

**Endpoint:** `POST /api/approval-unit/build`

**Purpose:** Convert AI-generated findings, patches, payment requests, or deployment proposals into a minimal human decision contract.

**Price:** 0.05 USDC per call (x402 payment protocol)

**Key Outputs:**
- `approval_question`: What the human is deciding
- `allowed_actions`: What becomes allowed if approved
- `still_blocked_actions`: What remains blocked even after approval
- `approval_unit_hash`: Cryptographic fingerprint for audit immutability

---

## 6. Example API Calls

### Example 1: Verify a Remediation Plan

```bash
curl -X POST "https://ai-agent-payment-safety-stack.onrender.com/api/remediation/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "finding_id": "py/sql-injection:app/models/user.py:42",
    "vulnerability_type": "SQL_INJECTION",
    "remediation_plan": "Replace string interpolation with parameterized query",
    "required_testing": ["unit_tests", "integration_tests", "security_retest"],
    "rollback_available": true
  }'
```

**Response:**
```json
{
  "verification_status": "verified",
  "approval_unit_ready": true,
  "recommended_human_action": "approve_staging_only"
}
```

---

### Example 2: Build a Human Decision Contract

```bash
curl -X POST "https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build" \
  -H "Content-Type: application/json" \
  -H "PAYMENT-SIGNATURE: <x402-payment-header>" \
  -d '{
    "source_type": "security_patch",
    "approval_unit_type": "security_patch_approval",
    "title": "Approve SQL injection remediation",
    "summary": "Replace string interpolation with parameterized query",
    "risk_level": "high",
    "evidence_ids": ["finding_001"],
    "test_results": ["unit_passed"],
    "rollback_available": true,
    "blocked_actions_until_approval": ["merge_to_staging"],
    "approver_role": "security_reviewer"
  }'
```

**Response:**
```json
{
  "approval_unit_id": "approval_abc123",
  "approval_unit_hash": "sha256:...",
  "approval_question": "Approve this security patch for staging merge?",
  "allowed_actions": ["merge_to_staging"],
  "still_blocked_actions": ["deploy_to_production"],
  "recommended_human_action": "approve_staging_only",
  "production_blocker": true,
  "production_blocker_reason": "Security patches require staged rollout. Staging approval does NOT imply production approval."
}
```

---

## 7. Important v0.1 Boundaries

**What this does NOT do (v0.1):**

❌ **No autonomous deployment.** These APIs do not execute deployments. They generate decision contracts for human judgment.

❌ **No automatic approval execution.** A human decision is captured, but not automatically executed. Downstream systems consume the decision contract and implement controlled execution.

❌ **No production auto-authorization.** Approval for staging does not authorize production. Approval for $100 budget does not authorize $200. Each boundary requires separate decision.

❌ **Verification ≠ production safety guarantee.** Verification checks that a remediation plan is sound. It does not guarantee production readiness. It does not authorize deployment. It does not assess operational impact.

**What is mandatory:**

✅ **Human approval always required.** At every execution boundary (merge to staging, deploy to production, spend budget, record payment), human decision is mandatory.

✅ **Audit trail required.** Every decision is recorded with timestamp, reviewer ID, decision reason, and cryptographic hash.

✅ **Scope enforcement required.** After human approval, the decision scope is enforced as policy (allowed actions / blocked actions).

---

## 8. Integration Examples

For detailed walkthroughs showing how to integrate these APIs with security tools and workflows:

- **[Semgrep to Human Contract](./integrations/semgrep_to_approval_flow.md)** — Integrate Semgrep findings into governance workflow
- **[CodeQL SARIF to Human Contract](./integrations/codeql_to_human_contract.md)** — Integrate GitHub Advanced Security SARIF findings

For use-case driven examples:

- **[Security Patch Approval Walkthrough](./walkthroughs/security_patch_walkthrough.md)** — Full flow from security finding to staging deployment
- **[Production Deploy Escalation](./walkthroughs/production_deploy_escalation.md)** — How production deployment requires separate approval tier
- **[Financial Approval Walkthrough](./walkthroughs/financial_approval_walkthrough.md)** — Governance for AI-initiated payments and budget decisions

---

## Next Steps

1. **Understand the core concepts**: Approval Unit as decision contract. Decision Scope as execution boundary.
2. **Review an integration example**: Pick Semgrep or CodeQL to see how real tools integrate.
3. **Test with example API calls**: Use the curl examples to see responses.
4. **Implement in your workflow**: Route AI-generated decisions through `/api/remediation/verify` → `/api/approval-unit/build`.
5. **Consume decision contracts**: Build downstream systems that enforce the approved scope (allowed_actions / still_blocked_actions).

---

## Key Reading

- [Approval Unit Builder API](../api/approval-unit-builder.md)
- [Remediation Verification Gate API](../api/remediation-verification-gate.md)
- [x402 Payment Protocol (Coinbase)](https://www.x402.dev/)

---

**Version:** v0.1  
**Status:** Production-ready for governance layer only. Execution enforcement is external responsibility.

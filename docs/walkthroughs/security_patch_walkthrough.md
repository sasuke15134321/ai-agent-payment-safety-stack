# Security Patch Governance Walkthrough

## Scenario

An AI agent detected a SQL injection vulnerability in the user API and generated a fix. Now the question is: can a human safely approve this patch, and what exactly are they approving?

This walkthrough shows how the governance layer prepares a human-readable decision contract for the AI-generated remediation.

---

## Step 1: Verify the Remediation

The AI agent submits the remediation candidate to the Remediation Verification Gate API.

### Request

```bash
curl -X POST https://ai-agent-payment-safety-stack.onrender.com/api/remediation/verify \
  -H "Content-Type: application/json" \
  -d '{
    "remediation_id": "remediation_sec_001",
    "finding_id": "finding_001",
    "source_type": "security_patch",
    "remediation_type": "security_patch",
    "title": "SQL injection fix for user API",
    "finding_summary": "Potential SQL injection in user lookup endpoint",
    "remediation_summary": "Replace raw SQL interpolation with parameterized query",
    "severity": "CRITICAL",
    "risk_level": "HIGH",
    "evidence_ids": ["finding_001", "codeql_001"],
    "source_ids": ["repo:user-api", "scanner:codeql"],
    "test_results": ["unit_tests_passed", "integration_tests_passed"],
    "security_retest_results": ["security_retest_passed"],
    "regression_test_results": ["regression_tests_passed"],
    "rollback_plan_id": "rollback_001",
    "rollback_available": true,
    "blast_radius": "single_service",
    "production_deploy_requested": false
  }'
```

### Response

```json
{
  "gate_name": "remediation_verification_gate",
  "remediation_id": "remediation_sec_001",
  "decision": "route_to_approval_unit_builder",
  "verification_status": "verified",
  "readiness_level": "human_approval_ready",
  "evidence_status": "sufficient",
  "test_status": "passed",
  "security_retest_status": "passed",
  "regression_status": "passed",
  "rollback_status": "available",
  "production_risk": "not_requested",
  "approval_unit_ready": true,
  "allowed_next_steps": ["create_approval_unit"],
  "blocked_next_steps": ["deploy_to_production"],
  "recommended_human_action": "approve_staging_only"
}
```

### What This Means

The remediation passed all automated checks:

* ✅ Evidence is sufficient (finding + CodeQL scanner confirm SQL injection)
* ✅ All tests passed (unit + integration + security retest + regression)
* ✅ Rollback is available (can undo if problems appear)
* ✅ Blast radius is contained (single service, not multi-service)
* ✅ Production deploy was NOT requested

**Key field: `approval_unit_ready = true`**

This means the remediation is ready to become a human decision contract.

---

## Step 2: Generate Human Decision Contract

The AI agent now sends the verified remediation to the Approval Unit Builder API to generate a human-readable decision contract.

### Request

```bash
curl -X POST https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "security_patch",
    "approval_unit_type": "security_patch_approval",
    "title": "Approve SQL injection fix for user API",
    "summary": "Replace raw SQL interpolation with parameterized query. All tests passed, rollback available.",
    "risk_level": "high",
    "evidence_ids": ["finding_001", "codeql_001"],
    "test_results": ["unit_passed", "integration_passed", "security_retest_passed"],
    "rollback_available": true,
    "blocked_actions_until_approval": ["merge_to_staging", "deploy_to_production"]
  }'
```

### Response

```json
{
  "approval_question": "Approve this security patch for staging merge?",
  "recommended_human_action": "approve_staging_only",
  "approval_unit_type": "security_patch_approval",
  "if_approved": {
    "allowed_actions": [
      "merge_to_staging",
      "run_staging_integration_tests"
    ],
    "still_blocked_actions": [
      "deploy_to_production",
      "release_to_customers"
    ]
  },
  "evidence_status": "sufficient",
  "test_status": "passed",
  "rollback_status": "available",
  "approval_unit_hash": "sha256:abc123def456...",
  "chain_anchor_status": "not_anchored"
}
```

---

## Step 3: What the Human Is Actually Approving

**Key concept: Approval is NOT a button to approve "the patch."**

**Approval is a scoped execution contract.**

When the human approves this decision contract, they are approving:

### Allowed Actions

* ✅ `merge_to_staging` — Code can be merged to staging branch
* ✅ `run_staging_integration_tests` — Integration tests can run in staging environment

### Still Blocked Actions

* ❌ `deploy_to_production` — Code CANNOT be deployed to production
* ❌ `release_to_customers` — Code CANNOT be released to customers

### What This Means in Practice

The human is saying:

> "Yes, I've reviewed the patch diff, the evidence (CodeQL finding), the test results, and the rollback plan.
>
> I approve this patch **for testing in staging only**.
>
> It must NOT go to production without a separate approval from me or another authorized reviewer.
>
> If issues appear in staging, we can rollback because a rollback plan exists."

---

## Step 4: Why Production Deploy Remains Blocked

Even after human approval, production deployment is intentionally blocked. Why?

### Blast Radius

This change affects user API — a critical service. Even though the patch is a security fix and all tests passed, production deployment requires:

* **Organization-level approval** — Not just one security engineer's sign-off
* **Change management process** — Production changes follow change control procedures
* **Broader stakeholder review** — Infrastructure team, on-call engineer, compliance may need to review
* **Monitoring setup** — Production metrics must be prepared before deployment

### Rollback Validation

A rollback plan exists, but:

* Is the rollback tested in production-like conditions?
* Can it be executed safely during business hours?
* Do we have runbooks documented?

### Production Governance

Staging approval and production approval serve different purposes:

* **Staging approval** = "Is this safe to test?"
* **Production approval** = "Is this safe to release to all users?"

These are different questions requiring different approvers.

### Next Step: Escalation

To deploy to production, a new approval request must be created:

```json
POST /api/approval-unit/build
{
  "source_type": "security_patch",
  "approval_unit_type": "security_patch_escalation_to_production",
  "title": "Escalate: Deploy SQL injection fix to production",
  "summary": "Staging tests passed. Now requesting production deployment approval.",
  "risk_level": "high",
  "previous_approval_unit_hash": "sha256:abc123def456...",
  "escalation_required": true,
  "escalation_reason": "production_deploy_requested",
  "approver_role": "production_lead"
}
```

This creates a NEW approval contract for production, with:

* Different approver role (production lead, not just security)
* Full staging test results
* Production monitoring plan
* Rollback procedures documented

---

## Step 5: v0.1 Boundaries

### What v0.1 DOES

* ✅ Verify remediation against evidence, tests, rollback readiness
* ✅ Generate human decision contracts
* ✅ Define allowed/blocked actions
* ✅ Route to human approval
* ✅ Audit all decisions

### What v0.1 DOES NOT

* ❌ Approve on behalf of human
* ❌ Execute approved actions automatically
* ❌ Deploy code
* ❌ Make secondary decisions
* ❌ Anchor to blockchain (fields are readiness only)

### Human Remains Responsible

At every step, a human must decide:

1. **After Verification:** "Should I review this?"
2. **After Contract Generation:** "Do I approve this scope?"
3. **After Staging Approval:** "Should this escalate to production?"
4. **After Production Approval:** "Is this the right time to deploy?"

---

## Summary

The governance layer ensures that:

| Step | What Happens | Who Decides |
|------|-------------|-----------|
| Verification | Automated checks (evidence, tests, rollback) | System |
| Decision Contract | Human-readable approval document | System generates, human reads |
| Approval | Approve limited execution scope | **Human** |
| Execution | Run approved actions only | System (within approved scope) |

**The security patch walkthrough demonstrates:**

* How verification prepares a remediation for human review
* How decision contracts define what is actually approved
* Why scoped approval (staging only) is safer than unrestricted approval
* Why production requires separate governance
* How humans remain in control throughout

Human approval is not a rubber stamp. It's a deliberate decision with defined scope and consequences.

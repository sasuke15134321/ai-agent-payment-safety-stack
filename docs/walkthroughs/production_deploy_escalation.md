# Production Deployment Escalation Walkthrough

## Scenario

A security patch has been approved for staging and tested successfully. All checks passed. The AI agent and some stakeholders want to deploy it to production.

But production deployment is intentionally difficult.

Why? And how does the governance layer handle escalation?

---

## The Core Principle

**Staging approval ≠ production approval**

```
Staging Approval Question:
"Is this safe to test?"

Production Approval Question:
"Is this safe to release to all users?"
```

These are fundamentally different questions.

---

## Staging Approval: Limited Scope

From the security patch walkthrough, the human approved:

```json
{
  "allowed_actions": [
    "merge_to_staging",
    "run_staging_integration_tests"
  ],
  "still_blocked_actions": [
    "deploy_to_production",
    "release_to_customers"
  ]
}
```

### What Staging Approval Means

* The patch is syntactically correct
* Unit tests pass
* Integration tests pass
* Security retest passes
* Rollback capability exists

### What Staging Approval Does NOT Mean

* The patch is ready for 1 million users
* We've validated production metrics
* We've prepared on-call coverage
* We've coordinated with ops team
* We've communicated to support team

---

## Why Production Deploy Is Intentionally Blocked

### 1. Blast Radius

Staging serves a small number of test accounts. Production serves real users.

A SQL injection fix in user API could affect:

* User authentication
* User data retrieval
* User profile updates
* Session management
* Customer trust

**Risk level:** Critical

### 2. Change Control

Production changes follow organizational procedures:

* **Change request submission** — Document what, why, how, when
* **Change advisory board review** — Infrastructure, security, ops review together
* **Maintenance window coordination** — When is it safe to deploy?
* **Rollback procedure documentation** — Can we safely undo this?
* **Monitoring setup** — What metrics confirm it's working?

### 3. Organizational Approval

Staging approval typically requires:

* Security engineer sign-off ✅

Production approval requires:

* Security engineer ✅
* Infrastructure lead ✅
* Product owner (business impact)
* On-call engineer (who responds if it breaks?)
* Possibly compliance officer (if data handling changed)

Different people have different risk tolerances and responsibilities.

### 4. Production-Specific Testing

Staging tests might not catch:

* Database performance at scale (1M users vs 100 test accounts)
* Cache invalidation issues
* Third-party API interactions
* Geographic deployment (CDN, multi-region)
* Concurrent request handling

---

## Escalation Flow: Creating a Production Approval Request

When the human decides production deployment should be considered, they request a NEW approval contract.

### Escalation Request

```bash
curl -X POST https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "security_patch",
    "approval_unit_type": "security_patch_production_escalation",
    "title": "Escalate: Deploy SQL injection fix to production",
    "summary": "Staging approval completed. All tests passed. Requesting production deployment approval.",
    "risk_level": "high",
    "severity": "CRITICAL",
    "evidence_ids": ["finding_001", "codeql_001"],
    "test_results": ["staging_integration_tests_passed"],
    "rollback_available": true,
    "previous_staging_approval_hash": "sha256:staging_approval_hash...",
    "escalation_required": true,
    "escalation_reason": "production_deployment_requested",
    "approver_role": "production_lead",
    "additional_context": "Staging has been running patch for 48 hours with no issues. All metrics normal."
  }'
```

### Escalation Response

```json
{
  "approval_question": "Approve this security patch for production deployment?",
  "escalation_level": 2,
  "approver_roles": [
    "production_lead",
    "infrastructure_lead"
  ],
  "if_approved": {
    "allowed_actions": [
      "deploy_to_production",
      "release_to_customers"
    ],
    "still_blocked_actions": [
      "disable_security_monitoring",
      "skip_rollback_procedure"
    ]
  },
  "escalation_requirements": {
    "required_signatories": 2,
    "required_roles": ["production_lead", "infrastructure_lead"],
    "change_control_required": true,
    "maintenance_window_required": true,
    "monitoring_plan_required": true
  },
  "approval_unit_hash": "sha256:production_escalation_hash...",
  "chain_anchor_status": "not_anchored"
}
```

---

## What Production Approval Means

### Allowed Actions (After Approval)

* ✅ `deploy_to_production` — Deploy to production servers
* ✅ `release_to_customers` — Make available to customers

### Still Blocked Actions

* ❌ `disable_security_monitoring` — Security alerting remains enabled
* ❌ `skip_rollback_procedure` — Rollback procedures must be followed
* ❌ `skip_on_call_notification` — On-call team must be notified

### Multiple Approvers Required

Production escalation typically requires:

```
Approver 1 (Security Lead):
"I reviewed the security evidence. The fix is correct."

Approver 2 (Infrastructure Lead):
"I reviewed the production impact. We can handle this."

Both must approve before deployment proceeds.
```

### Change Control Artifacts

Before deployment, governance requires:

1. **Change Request** — Formal documentation of the change
2. **Rollback Plan** — Step-by-step procedure to revert
3. **Monitoring Plan** — How do we know it's working?
4. **Communication Plan** — Who's notified before/during/after?

---

## Example Escalation Workflow

### Hour 0: Staging Approval

Human approves security patch for staging.

```json
{
  "decision": "approve_staging_only",
  "allowed_actions": ["merge_to_staging"],
  "still_blocked_actions": ["deploy_to_production"]
}
```

### Hour 0-48: Staging Testing

Patch runs in staging for 2 days. Metrics are normal. No errors.

```
Staging Metrics
- Requests: 10,000/day
- Error rate: 0.01% (normal baseline)
- Response time: 50ms (normal baseline)
- No security alerts
- No rollback needed
```

### Hour 48: Escalation Request

Stakeholders agree production deployment should proceed. Infrastructure lead creates escalation request.

```json
{
  "approval_unit_type": "security_patch_production_escalation",
  "escalation_reason": "staging_validation_complete",
  "staging_duration_hours": 48,
  "staging_request_volume": 10000,
  "staging_error_rate": 0.01,
  "approver_role": "production_lead"
}
```

### Hour 48-72: Production Review

Production leads review:

* Staging metrics ✅
* Change request ✅
* Rollback procedure ✅
* Monitoring plan ✅
* On-call coverage ✅

Two approvers sign off.

### Hour 72: Production Deployment

With both approvals in hand:

```json
{
  "decision": "approve_production",
  "allowed_actions": ["deploy_to_production", "release_to_customers"],
  "still_blocked_actions": ["disable_monitoring", "skip_rollback"]
}
```

Deployment proceeds with:

* On-call team standing by
* Rollback procedure documented
* Monitoring dashboards active
* Real-time alert thresholds set

---

## Why This Matters

### Without Escalation Governance

Scenario: Staging approval = production approval

```
If a bug exists that staging didn't catch:
→ Bug reaches 1M users
→ No on-call team standing by
→ Rollback procedure undocumented
→ Severe outage, customer impact
```

### With Escalation Governance

Scenario: Multiple approvers, documented procedures

```
If a bug exists that staging didn't catch:
→ Production monitors alert immediately
→ On-call team responds in minutes
→ Rollback procedure is documented
→ Service restored with minimal customer impact
```

The extra approvals aren't bureaucracy. They're protection.

---

## v0.1 Boundaries

### What v0.1 DOES

* ✅ Require escalation for production (route to escalation approval)
* ✅ Define separate scopes (staging vs production)
* ✅ Generate multi-approver escalation contracts
* ✅ Audit all escalation decisions

### What v0.1 DOES NOT

* ❌ Automatically approve production
* ❌ Deploy code
* ❌ Coordinate with change management system
* ❌ Update monitoring systems
* ❌ Notify on-call teams (that's the system running after approval)

### Humans Decide Escalation

Every step requires human decision:

1. "Should we escalate to production review?" → **Human decides**
2. "Are the staging metrics acceptable?" → **Human reviews**
3. "Do both production leads approve?" → **Humans decide**
4. "Is the maintenance window appropriate?" → **Human chooses time**

---

## Key Insights

| Concept | Staging | Production |
|---------|---------|-----------|
| **Scope** | Single service, test users | All users, critical service |
| **Approvers** | Security engineer | Security + Infrastructure |
| **Risk tolerance** | Medium | Low |
| **Testing period** | Hours/days | Days/weeks in staging |
| **Rollback readiness** | Medium | Critical |
| **Blast radius** | Limited | Org-wide |
| **Governance mode** | Permissive | Restrictive |

**Production deployment is intentionally difficult because the consequences of failure are high.**

The governance layer ensures that:

* Staging and production have different approval criteria
* Production requires broader consensus
* Escalation is explicit and documented
* Multiple stakeholders review before production
* Rollback procedures are validated

This is not about distrusting the AI agent. It's about distributing risk and responsibility across the organization.

Humans approve. Systems execute what's approved. Governance ensures both steps happen correctly.

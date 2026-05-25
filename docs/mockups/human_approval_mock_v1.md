# Human Decision Contract — Approval Interface Mock v1.0

## Example: Security Patch Approval

```
╔════════════════════════════════════════════════════════════════════════╗
║                      APPROVAL DECISION REQUIRED                        ║
╚════════════════════════════════════════════════════════════════════════╝

APPROVAL QUESTION:
Approve this security patch for staging merge?

═════════════════════════════════════════════════════════════════════════

REMEDIATION SUMMARY:
Title: SQL injection fix for user API
Risk Level: HIGH
Severity: CRITICAL

Finding:
Potential SQL injection in user lookup endpoint.

Remediation:
Replace raw SQL interpolation with parameterized query.

═════════════════════════════════════════════════════════════════════════

EVIDENCE STATUS: SUFFICIENT
✓ Evidence IDs: finding_001, codeql_001
✓ Source IDs: repo:user-api, scanner:codeql

TEST STATUS: PASSED
✓ Unit tests: PASSED
✓ Integration tests: PASSED

SECURITY RETEST STATUS: PASSED
✓ Security retest: PASSED

REGRESSION TEST STATUS: PASSED
✓ Regression tests: PASSED

ROLLBACK READINESS: AVAILABLE
✓ Rollback plan ID: rollback_001
✓ Rollback available: YES

═════════════════════════════════════════════════════════════════════════

AFFECTED SCOPE:
- Service: user-api
- Environment: staging
- Affected Files: api/user.py
- Blast Radius: single_service

PRODUCTION RISK: NOT REQUESTED
(Production deployment is not being requested at this time)

═════════════════════════════════════════════════════════════════════════

IF YOU APPROVE:
Allowed Actions:
  ✓ merge_to_staging
  ✓ allow_staging_merge_after_approval

Still Blocked:
  ✗ deploy_to_production (remains blocked)

═════════════════════════════════════════════════════════════════════════

IF YOU REJECT:
All Actions Blocked:
  ✗ merge_to_staging
  ✗ deploy_to_production

═════════════════════════════════════════════════════════════════════════

IF YOU REQUEST REWORK:
Route to: rework_queue
Next: AI agent must address reviewer feedback and resubmit.

═════════════════════════════════════════════════════════════════════════

SUGGESTED HUMAN ACTIONS:
1. review_patch_diff
2. check_test_results
3. verify_source_lineage
4. approve_staging_only

═════════════════════════════════════════════════════════════════════════

RECOMMENDED ACTION: approve_staging_only
Reason: All checks passed. Ready for human approval at staging level.

═════════════════════════════════════════════════════════════════════════

AUDIT TRAIL:
Approval Unit Hash: sha256:abc123...
Approval Unit ID: approval_001
Request ID: req_123
Task ID: task_sec_001
Generated: 2026-05-25T14:30:00Z

═════════════════════════════════════════════════════════════════════════

DECISION OPTIONS:

  [✓ Approve]        [✗ Reject]        [⟳ Request Rework]        [? More Evidence]        [⬆ Escalate]

═════════════════════════════════════════════════════════════════════════

v0.1 CONSTRAINTS:
• This interface ONLY prepares the decision. It does not execute it.
• You (the human) retain full responsibility for this approval.
• If approved: merge_to_staging will be ALLOWED.
• Production deployment remains BLOCKED regardless of this approval.
• No automatic deployment will occur.
• No blockchain transaction will occur until legal/compliance review.

═════════════════════════════════════════════════════════════════════════
```

---

## Visual Legend

```
✓ = Verified / Passed / Available
✗ = Blocked / Not available / Failed
⟳ = Rework / Request more info
? = Unknown / Needs review
⬆ = Escalate to higher authority
```

---

## Key Design Principles

1. **Human remains responsible** — all key decisions require human confirmation
2. **Staging-only default** — production deployment always requires explicit separate approval
3. **Transparent constraints** — what's blocked and why is always visible
4. **Audit trail** — every decision is recorded with hash and timestamp
5. **No autonomous execution** — this contract prepares decisions but does not execute them

---

## Example Workflows

### Workflow 1: Approve for staging only
```
1. Human reads approval question and evidence
2. Human selects [✓ Approve]
3. System allows: merge_to_staging
4. System blocks: deploy_to_production
5. Decision is recorded in audit trail
6. No further automation occurs until next explicit human approval
```

### Workflow 2: Request rework
```
1. Human reads decision contract
2. Human has concerns about evidence or test coverage
3. Human selects [⟳ Request Rework]
4. System routes back to AI agent
5. AI agent addresses feedback and resubmits
6. Human reviews updated contract
```

### Workflow 3: Escalate to security lead
```
1. Human sees high-risk remediation
2. Human determines security lead sign-off is needed
3. Human selects [⬆ Escalate]
4. Contract and decision history forwarded to security lead
5. Security lead receives separate approval request
6. Both approvals recorded in audit trail
```

---

## Future Enhancements (v0.2+)

- [ ] Slack/Teams integration for approval notifications
- [ ] Approval delegation to roles/teams
- [ ] Time-bound approvals (expire after N hours)
- [ ] Multi-stage approvals (engineering + security + ops)
- [ ] Approval comments and notes
- [ ] Integration with CI/CD platforms for execution after approval
- [ ] Blockchain anchor after human approval

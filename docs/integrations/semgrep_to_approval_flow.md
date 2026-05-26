# Semgrep Integration Walkthrough: Finding → Verification → Approval

## 1. What is Semgrep?

Semgrep is an open-source static analysis tool that automatically detects security vulnerabilities, misconfigurations, and code quality issues across multiple programming languages. When Semgrep scans a codebase, it produces structured JSON findings that include the vulnerable code location, severity level, OWASP/CWE references, and a suggested remediation plan. These findings are rule-based and deterministic, making them ideal for integration into automated governance workflows.

## 2. Why Integrate with Governance Layers?

Semgrep findings alone are detection without judgment. To bridge the gap between automated detection and human-responsible remediation, the AI Agent Payment Safety Stack provides two-step verification:

1. **Remediation Verification Gate** — Validates that the AI-generated remediation plan is sound, safe, and complete before approval.
2. **Approval Unit Builder** — Converts the verified finding into a minimal human decision contract, ensuring human oversight before any staging or production action.

This governance layer prevents:
- Applying patches that introduce new vulnerabilities
- Deploying remediation without evidence of testing
- Treating staging-only approvals as production deployments
- Skipping rollback readiness checks

---

## 3. Semgrep Finding → Remediation Verification Gate

### Example: SQL Injection Finding

**Semgrep Output** (simplified):
```json
{
  "check_id": "python.lang.security.injection.sql.sql-injection-autoescaping",
  "path": "app/models/user.py",
  "start": { "line": 42 },
  "message": "Detected a SQL injection vulnerability",
  "severity": "ERROR",
  "confidence": "HIGH",
  "matched_text": "SELECT * FROM users WHERE user_id = '{user_input}'",
  "remediation_plan": {
    "type": "parameterized_query",
    "patch_candidate": "db.execute('SELECT * FROM users WHERE user_id = %s', (user_input,))"
  }
}
```

### Conversion to Remediation Verification Gate Request

```json
{
  "finding_source": "semgrep",
  "finding_id": "python.lang.security.injection.sql.sql-injection-autoescaping",
  "vulnerability": {
    "type": "SQL_INJECTION",
    "severity": "CRITICAL",
    "file_path": "app/models/user.py",
    "line": 42,
    "cwe_ids": ["CWE-89"],
    "owasp_categories": ["A03:2021 - Injection"]
  },
  "remediation_candidate": {
    "type": "code_change",
    "description": "Replace string interpolation with parameterized query",
    "patch": "db.execute('SELECT * FROM users WHERE user_id = %s', (user_input,))",
    "required_testing": ["unit_tests", "integration_tests", "security_retest"]
  },
  "context": {
    "scan_date": "2026-05-25T10:30:00Z",
    "scan_tool": "semgrep",
    "scan_version": "1.65.0",
    "branch": "main"
  }
}
```

### Remediation Verification Gate Response

```json
{
  "verification_id": "rvg_20260525_001",
  "finding_id": "python.lang.security.injection.sql.sql-injection-autoescaping",
  "decision": "route_to_approval_unit_builder",
  "verification_status": "verified",
  "checks_passed": [
    "remediation_soundness",
    "no_new_vulnerabilities",
    "required_testing_specified",
    "rollback_plan_available"
  ],
  "readiness_level": "human_approval_ready",
  "production_risk": "not_requested",
  "evidence": {
    "test_status": "passed",
    "security_retest_status": "passed",
    "regression_status": "passed",
    "rollback_status": "available"
  },
  "approval_unit_ready": true,
  "recommended_human_action": "approve_staging_only",
  "approval_unit_hash": "sha256:abc123def456",
  "v0_1_constraints": [
    "This verification is rule-based and does not execute code",
    "No patches are applied by this API",
    "No payment is collected at this stage",
    "No deployment occurs",
    "Human review is mandatory before proceeding"
  ]
}
```

---

## 4. Remediation Verification Gate → Approval Unit Builder

### Approval Unit Builder Request

Once verified, the finding is converted into a human decision contract:

```json
{
  "source": "remediation_verification_gate",
  "verification_id": "rvg_20260525_001",
  "finding_id": "python.lang.security.injection.sql.sql-injection-autoescaping",
  "decision_type": "security_remediation",
  "approval_scope": "staging_only",
  "context": {
    "vulnerability_type": "SQL_INJECTION",
    "severity": "CRITICAL",
    "file_affected": "app/models/user.py",
    "proposed_remediation": "Replace string interpolation with parameterized query",
    "testing_completed": ["unit_tests", "integration_tests", "security_retest"]
  }
}
```

### Approval Unit Builder Response

```json
{
  "approval_unit_id": "aub_20260525_001",
  "approval_unit_hash": "sha256:abc123def456",
  "status": "human_decision_contract_ready",
  "decision_type": "security_remediation",
  "approval_scope": "staging_only",
  "approval_question": "Do you approve deployment of this SQL injection remediation (parameterized query patch) to the **staging environment only**? This patch has passed unit tests, integration tests, and security retesting.",
  "decision_options": [
    {
      "option": "approve_staging_only",
      "label": "Approve for Staging Only",
      "consequence": "Patch will be deployed to staging. Further approval required for production."
    },
    {
      "option": "request_changes",
      "label": "Request Changes",
      "consequence": "Return to development. New remediation plan required."
    },
    {
      "option": "reject",
      "label": "Reject This Remediation",
      "consequence": "Mark finding as rejected. Alternative remediation required or escalation needed."
    }
  ],
  "production_blocker": true,
  "production_blocker_reason": "Security patches to critical vulnerabilities require staged rollout. Staging approval does not imply production approval.",
  "v0_1_constraints": [
    "This is a decision contract only",
    "No payment is executed by this API",
    "No deployment is executed by this API",
    "No code changes are applied",
    "Approval is human-only, not automated"
  ]
}
```

---

## 5. Human Decision Contract Example

### Input
A human reviewer receives the approval unit and reads:

```
APPROVAL UNIT: aub_20260525_001

VULNERABILITY: SQL Injection in app/models/user.py (line 42)
SEVERITY: CRITICAL
CWE: CWE-89

PROPOSED FIX:
Before: SELECT * FROM users WHERE user_id = '{user_input}'
After:  db.execute('SELECT * FROM users WHERE user_id = %s', (user_input,))

TESTING COMPLETED:
✓ Unit tests passed
✓ Integration tests passed
✓ Security retest passed
✓ Rollback available

DECISION SCOPE: STAGING ONLY

---

QUESTION FOR HUMAN REVIEWER:

Do you approve deployment of this SQL injection remediation 
(parameterized query patch) to the **staging environment only**?

This patch has passed unit tests, integration tests, and security retesting.

[APPROVE FOR STAGING ONLY] [REQUEST CHANGES] [REJECT]
```

### Approval Output

If approved for staging:
```json
{
  "approval_unit_id": "aub_20260525_001",
  "human_decision": "approve_staging_only",
  "decision_timestamp": "2026-05-25T11:00:00Z",
  "reviewer_id": "reviewer_001",
  "reviewer_signature": "signature_hash",
  "approval_scope": "staging_environment",
  "next_step": "Deploy to staging. Return for production approval after 48-hour observation period.",
  "production_approval_blocked": true,
  "production_approval_reason": "Staging approval does not imply production approval. Separate approval required after observation period."
}
```

---

## 6. Staging-Only Approval vs. Production Deployment

### Key Separation

| Phase | Owner | Approval Required | Deployment Target | Rollback Available |
|-------|-------|-------------------|-------------------|------------------|
| Verification | Rule Engine | N/A | N/A | N/A |
| Approval Contract | Human Reviewer | Human Decision | Staging Only | Yes (Verified) |
| Staging Observation | Operations | Automated Monitoring | Staging Environment | Yes |
| Production Request | DevOps + Security | Separate Human Approval | Production | Yes |

### Safeguard

**The approval unit from step 5 explicitly includes:**
- `"production_blocker": true`
- `"approval_scope": "staging_only"`
- `"production_approval_blocked": true`

This ensures that even if a human approves the patch for staging, **production deployment requires a separate, explicit approval** after observation period.

---

## 7. v0.1 Constraints and Important Disclaimers

### What This Integration Does NOT Do

- ❌ Automatically apply patches
- ❌ Automatically deploy to production
- ❌ Automatically execute any code
- ❌ Automatically approve without human review
- ❌ Execute blockchain transactions
- ❌ Collect x402 payment without explicit human approval
- ❌ Provide legal or compliance advice

### What This Integration Does

- ✅ Verify remediation soundness using rule-based checks
- ✅ Ensure required testing is specified
- ✅ Confirm rollback readiness
- ✅ Convert findings into human-readable decision contracts
- ✅ Enforce staging-only approval boundaries
- ✅ Block production deployment without separate approval
- ✅ Provide audit logs of human decisions

### Human Judgment Is Mandatory

At every stage, a human decision is required:

1. **Verification Stage**: The verification result is a recommendation, not an executable decision.
2. **Approval Stage**: The approval unit requires explicit human yes/no decision.
3. **Staging Stage**: Human review of staging results is required before production consideration.
4. **Production Stage**: Separate human approval (not yet implemented in v0.1) is required for production.

### Technical Scope in v0.1

- Semgrep finding validation
- Remediation plan verification
- Approval unit generation
- Staging-only boundary enforcement
- Human decision capture

### Out of Scope (Future)

- Production deployment approval (v0.2+)
- Automated patch rollout (external tool)
- Blockchain-based approval contracts (future enhancement)
- Multi-party signature workflows (v0.2+)

---

## Integration Flow Diagram

```
Semgrep Scan
    ↓
Semgrep Finding (JSON)
    ↓
POST /api/remediation/verify
    ↓
Remediation Verification Gate
  (Rule-based checks:
   - No new vulnerabilities
   - Testing specified
   - Rollback available)
    ↓
Decision: route_to_approval_unit_builder
    ↓
POST /api/approval-unit/build
    ↓
Approval Unit (Human Decision Contract)
  approval_question:
  "Approve for staging only?"
    ↓
Human Review & Decision
  [APPROVE STAGING] / [REQUEST CHANGES] / [REJECT]
    ↓
Decision Recorded
  approval_unit_id: aub_20260525_001
  human_decision: approve_staging_only
  production_blocker: true
    ↓
Staging Deployment (Separate Process)
  [Not executed by these APIs]
    ↓
Observation Period (48 hours)
    ↓
Production Approval Required (v0.2+)
  [Separate human decision, not automatic]
```

---

## Related APIs

- **Remediation Verification Gate** v0.1: `/api/remediation/verify` (Rule-based verification, 0.05 USDC per call)
- **Approval Unit Builder** v0.1: `/api/approval-unit/build` (Decision contract generation, 0.05 USDC per call)
- **Agent Security Gateway**: `/api/security/scan` (Tool execution validation, 0.05 USDC per call)
- **Agent Budget Guard**: `/api/budget/check` (Spending limit verification, 0.03 USDC per call)
- **Agent Memory API**: `/api/memory/store` (Audit log storage, 0.05 USDC per call)

---

## Disclaimer

This documentation describes a v0.1 walkthrough for integrating Semgrep findings into the AI Agent Payment Safety Stack governance layers. This is **not a guarantee of security**, **not legal advice**, and **not a substitute for professional security review**. Human judgment and expert code review remain mandatory at all stages.

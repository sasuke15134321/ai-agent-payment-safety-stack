# CodeQL SARIF Integration Walkthrough: Evidence → Verification → Human Contract

## 1. What CodeQL Is

CodeQL is GitHub Advanced Security's enterprise-grade static application security testing (SAST) solution. It analyzes source code to detect security vulnerabilities, compliance violations, and quality issues across multiple programming languages. CodeQL findings are output in SARIF (Static Analysis Results Interchange Format), an industry-standard JSON structure that describes security alerts with machine-readable details: vulnerability type, location, severity, dataflow paths, and suggested fixes. SARIF makes security findings portable and enables seamless integration with downstream governance and remediation workflows.

## 2. Why SARIF Matters

**SARIF = Structured Security Evidence**

- **Machine-readable**: Governance systems can parse and validate findings without human interpretation
- **Industry standard**: Adopted by multiple security tools, CI/CD platforms, and policy engines
- **Natural input for governance layers**: SARIF provides the data structure needed for rule-based verification gates
- **Reproducible**: Same finding always produces identical SARIF output, enabling deterministic approval workflows

SARIF transforms security findings from unstructured alerts into structured evidence that governance layers can reason about.

## 3. Why Governance Is Still Required

**Critical principle:**
```
Security finding ≠ Deployment authorization
```

A CodeQL alert identifies a potential vulnerability. It does not authorize remediation, staging deployment, or production release. Even if CodeQL finds and reports a SQL injection vulnerability:

- The finding is **evidence**, not a decision
- The fix is a **candidate**, not confirmed safe
- The deployment target is **not yet approved**

Human judgment is required at every stage:
1. **Verification**: Is the fix sound?
2. **Testing**: Did the fix work?
3. **Approval**: Should this deploy to staging?
4. **Production**: Do we approve production deployment?

---

## 4. SARIF → Remediation Verification Gate

### Example: CodeQL SQL Injection Alert

**CodeQL SARIF Output** (simplified):
```json
{
  "ruleId": "py/sql-injection",
  "message": "SQL query is constructed by string interpolation including a non-constant value",
  "locations": [{
    "physicalLocation": {
      "artifactLocation": {"uri": "app/models/user.py"},
      "region": {"startLine": 42}
    }
  }],
  "fixes": [{
    "description": "Use a parameterized query to prevent SQL injection",
    "replacements": [{
      "insertedContent": "cursor.execute(query, (user_input,))"
    }]
  }],
  "level": "error",
  "properties": {"security-severity": "9.0"}
}
```

### Conversion to Remediation Verification Gate Request

```json
{
  "finding_source": "codeql",
  "finding_id": "py/sql-injection@app/models/user.py:42",
  "vulnerability": {
    "type": "SQL_INJECTION",
    "severity": "CRITICAL",
    "file_path": "app/models/user.py",
    "line": 42,
    "cwe_ids": ["CWE-89"],
    "owasp_categories": ["A03:2021 - Injection"],
    "security_severity_score": 9.0
  },
  "remediation_candidate": {
    "type": "code_change",
    "description": "Replace string interpolation with parameterized query",
    "patch": "cursor.execute(query, (user_input,))",
    "required_testing": ["unit_tests", "integration_tests", "security_retest"]
  },
  "context": {
    "scan_date": "2026-05-26T07:03:18Z",
    "scan_tool": "codeql",
    "tool_version": "2.14.6",
    "branch": "main",
    "repository": "https://github.com/example/repo"
  }
}
```

### Remediation Verification Gate Response

```json
{
  "verification_id": "rvg_codeql_001",
  "finding_id": "py/sql-injection@app/models/user.py:42",
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
    "This verification is rule-based",
    "No patches are applied by this API",
    "No payment is collected",
    "No deployment occurs",
    "Human review is mandatory"
  ]
}
```

---

## 5. Remediation Verification Gate → Approval Unit Builder

### Approval Unit Builder Request

Once verified, the CodeQL finding is converted into a human decision contract:

```json
{
  "source": "remediation_verification_gate",
  "verification_id": "rvg_codeql_001",
  "finding_id": "py/sql-injection@app/models/user.py:42",
  "decision_type": "security_remediation",
  "approval_scope": "staging_only",
  "context": {
    "vulnerability_type": "SQL_INJECTION",
    "severity": "CRITICAL",
    "file_affected": "app/models/user.py",
    "line_number": 42,
    "proposed_remediation": "Replace string interpolation with parameterized query",
    "testing_completed": ["unit_tests", "integration_tests", "security_retest"]
  }
}
```

### Approval Unit Builder Response

```json
{
  "approval_unit_id": "aub_codeql_001",
  "approval_unit_hash": "sha256:abc123def456",
  "status": "human_decision_contract_ready",
  "decision_type": "security_remediation",
  "approval_scope": "staging_only",
  "approval_question": "Do you approve deployment of this SQL injection remediation (parameterized query patch) to the **staging environment only**? This patch has passed unit tests, integration tests, and security retesting.",
  "decision_options": [
    {
      "option": "approve_staging_only",
      "label": "Approve for Staging Only",
      "consequence": "Patch will deploy to staging. Further approval required for production."
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
  "production_blocker_reason": "Security patches to critical vulnerabilities require staged rollout and observation. Staging approval does NOT imply production approval.",
  "v0_1_constraints": [
    "This is a decision contract only",
    "No payment is executed",
    "No deployment is executed",
    "No code changes are applied",
    "Approval is human-only"
  ]
}
```

---

## 6. Human Decision Contract Example

### Input
A human reviewer receives the approval unit and reads:

```
APPROVAL UNIT: aub_codeql_001

FINDING SOURCE: CodeQL (GitHub Advanced Security)
VULNERABILITY: SQL Injection in app/models/user.py (line 42)
SEVERITY: CRITICAL
CWE: CWE-89
SECURITY SCORE: 9.0/10

PROPOSED FIX:
Before: query = f"SELECT * FROM users WHERE user_id = '{user_input}'"
After:  cursor.execute(query, (user_input,))

TESTING COMPLETED:
✓ Unit tests passed
✓ Integration tests passed
✓ Security retest passed (CodeQL re-scan)
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
  "approval_unit_id": "aub_codeql_001",
  "human_decision": "approve_staging_only",
  "decision_timestamp": "2026-05-26T07:15:00Z",
  "reviewer_id": "reviewer_security_001",
  "reviewer_signature": "signature_hash",
  "approval_scope": "staging_environment",
  "next_step": "Deploy to staging. Return for production approval after 48-hour observation period.",
  "production_approval_blocked": true,
  "production_approval_reason": "Staging approval does NOT imply production approval. Separate approval required after observation period."
}
```

---

## 7. Production Remains Blocked

**Critical principle:**
```
CI success ≠ Production authorization
```

Even after:
- ✅ CodeQL scan completes
- ✅ Remediation is verified
- ✅ Tests pass
- ✅ Staging approval is granted
- ✅ Staging deployment succeeds
- ✅ Observation period completes

**Production deployment still requires separate, explicit human approval.**

The approval unit explicitly includes:
- `"production_blocker": true`
- `"approval_scope": "staging_only"`
- `"production_approval_blocked": true`

This ensures that staging approval cannot be misinterpreted as production authorization.

---

## 8. v0.1 Constraints and Important Disclaimers

### What This Integration Does NOT Do

- ❌ Automatically apply patches
- ❌ Automatically deploy to staging or production
- ❌ Automatically execute any code
- ❌ Automatically approve without human review
- ❌ Execute blockchain transactions
- ❌ Collect x402 payment without explicit human approval
- ❌ Treat CodeQL findings as authorization

### What This Integration Does

- ✅ Parse CodeQL SARIF findings into structured data
- ✅ Verify remediation soundness using rule-based checks
- ✅ Ensure required testing is specified
- ✅ Confirm rollback readiness
- ✅ Convert findings into human-readable decision contracts
- ✅ Enforce staging-only approval boundaries
- ✅ Block production deployment without separate approval
- ✅ Provide audit logs of human decisions

### Human Judgment Is Mandatory

At every stage, a human decision is required:

1. **Verification Stage**: CodeQL output is a recommendation, not executable
2. **Approval Stage**: Approval unit requires explicit yes/no decision
3. **Staging Stage**: Human review of staging results before production consideration
4. **Production Stage**: Separate human approval (not yet implemented in v0.1)

### Technical Scope in v0.1

- CodeQL SARIF parsing and validation
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
CodeQL Scan (GitHub Advanced Security)
    ↓
SARIF Output (JSON)
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
  approval_unit_id: aub_codeql_001
  human_decision: approve_staging_only
  production_blocker: true
    ↓
Staging Deployment (Separate Process)
  [Not executed by these APIs]
    ↓
Observation Period (48+ hours)
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

This documentation describes a v0.1 walkthrough for integrating CodeQL SARIF findings into the AI Agent Payment Safety Stack governance layers. This is **not a guarantee of security**, **not legal advice**, and **not a substitute for professional security review**. Human judgment and expert code review remain mandatory at all stages. CodeQL findings are input to governance workflows, not authorization for deployment.

# Claude Security Guidance → Governance Flow Integration

## Overview

Claude Code's security-guidance plugin detects security risks while code is being written. AI Agent Payment Safety Stack governs what may be approved, staged, executed, or kept blocked after that finding.

This document describes how security findings flow from Claude into governance decision-making, and why human judgment remains required at every step.

---

## 1. What Claude Code security-guidance Does

Claude Code's security-guidance plugin operates at write-time:

* Detects security issues, vulnerabilities, and anti-patterns as code is being modified
* Issues security finding, warning, or remediation hint
* Provides context about the issue and suggested fixes
* Flags suspicious patterns before deployment

**Critical clarity**: A security finding is not production deployment authorization.

---

## 2. Why Governance Is Still Required

Three essential principles:

**Security guidance finding ≠ deployment authorization**

The fact that a security issue was detected and fixed does not mean the code is approved for production. Finding a problem and solving it are different from authorizing execution.

**Security warning resolved ≠ production approval**

Resolving a security warning in Claude Code means the code no longer triggers the warning. It does not mean:
- The fix is correct
- The fix is tested
- The fix should execute in production
- The fix is approved by any authority

**Code edit accepted ≠ unrestricted execution**

Accepting a code edit into a branch means the code is syntactically valid and the security warning was addressed. It does not grant permission for:
- Staging deployment
- Production deployment
- API execution
- Payment execution
- Database modification

---

## 3. Integration Flow

```
Claude Code security-guidance
↓
Security finding / remediation hint
↓
Remediation Verification Gate
↓
Approval Unit Builder
↓
Human Decision Contract
↓
Scoped approval (staging only)
↓
Controlled execution / production remains blocked
```

The flow ensures that:
1. Security findings are detected at edit-time
2. Remediation is verified (not just proposed)
3. Human approval authority creates a decision contract
4. Execution is scoped to the approved boundaries only
5. Production execution remains blocked unless explicitly approved

---

## 4. Example Mapping: Claude Finding to RVG Input

When Claude security-guidance detects an issue and a fix is applied, that information flows into Remediation Verification Gate as follows:

```json
{
  "source_type": "claude_security_guidance",
  "remediation_type": "patch_candidate",
  "title": "SQL Injection Prevention in User Query",
  "finding_summary": "Detected parameterized query pattern violation in user_api.go. User input was concatenated directly into SQL query.",
  "remediation_summary": "Applied prepared statement pattern. User input now passed as query parameter, not concatenated.",
  "severity": "high",
  "evidence_ids": [
    "claude_finding_2026_05_26_10_00_sql_injection"
  ],
  "source_ids": [
    "file:user_api.go:line_142_158"
  ],
  "test_results": {
    "status": "passed",
    "tests_run": 12,
    "tests_failed": 0,
    "affected_test_suite": "user_query_tests"
  },
  "security_retest_results": {
    "status": "passed",
    "claude_recheck": "Pattern now matches parameterized query best practice",
    "additional_checks": "No new security warnings detected"
  },
  "rollback_available": true,
  "production_deploy_requested": false
}
```

---

## 5. Remediation Verification Gate Response

When RVG processes the Claude finding:

```json
{
  "verification_id": "rvg_20260526_001",
  "source_input": {
    "source_type": "claude_security_guidance",
    "finding_id": "claude_finding_2026_05_26_10_00_sql_injection"
  },
  "decision": "route_to_approval_unit_builder",
  "approval_unit_ready": true,
  "approval_unit_hash": "sha256:a1b2c3d4e5f6...",
  "recommended_human_action": "approve_staging_only",
  "blocked_next_steps": [
    "deploy_to_production",
    "payment_execution",
    "immediate_rollout"
  ],
  "verification_status": "verified",
  "verification_details": {
    "claude_finding_valid": true,
    "remediation_pattern_sound": true,
    "test_coverage_sufficient": true,
    "risk_level": "medium_after_remediation"
  }
}
```

Key point: **Verification ≠ Execution**. RVG verified that the finding and fix are sound. It did not approve execution.

---

## 6. Approval Unit Builder Response

AUB then converts the verified remediation into a human decision contract:

```json
{
  "approval_unit_id": "approval_unit_26052601",
  "approval_unit_hash": "sha256:a1b2c3d4e5f6...",
  "approval_question": "May this SQL injection remediation be merged to staging and tested in staging environment before production consideration?",
  "recommended_human_action": "approve_staging_only",
  "allowed_actions": [
    "merge_to_staging",
    "run_staging_tests",
    "monitor_staging_behavior"
  ],
  "still_blocked_actions": [
    "deploy_to_production",
    "release_to_live_traffic",
    "approve_production_deploy",
    "modify_firewall_rules",
    "execute_payment"
  ],
  "approval_unit_scope": {
    "repository": "user-api",
    "branch": "security/sql_injection_fix",
    "environment_allowed": "staging",
    "environment_blocked": "production"
  },
  "approval_duration": "7_days",
  "expiry_at": "2026-06-02T10:00:00Z",
  "human_signer": "security_lead@company",
  "signed_at": "2026-05-26T10:15:00Z"
}
```

---

## 7. What Humans Are Actually Approving

The human approval decision is **scoped, temporary, and bounded**.

**The human is NOT approving**:
- Unrestricted code execution
- Automatic production deployment
- Removal of safeguards
- Skipping validation steps
- Bypassing audit requirements

**The human IS approving**:
- Merging the staging branch
- Running tests in staging
- Monitoring staging behavior
- Escalating to production review later (if staging passes)

**Allowed actions**:
* merge_to_staging
* run_staging_tests
* monitor_staging_behavior

**Still blocked**:
* deploy_to_production
* release_to_live_traffic
* approve_production_deploy
* execute_payment

The boundary is explicit. Production deployment requires a separate decision.

---

## 8. v0.1 Boundaries

This integration is specification only. Important constraints:

* **no autonomous deployment** — All deployment decisions remain human-controlled
* **no automatic production deployment** — Staging approval does not trigger production deployment
* **no automatic approval execution** — Approvals do not self-execute
* **no payment execution** — Security findings do not authorize payment transfers
* **no blockchain transaction** — Findings do not trigger ledger writes
* **human approval required** — Every escalation point requires human decision

Verification ≠ Approval ≠ Execution.

---

## 9. Relationship to Existing Integrations

This integration sits alongside:

**Semgrep integration** (`semgrep_to_governance.md`)
- Semgrep YAML rules → Remediation Verification Gate
- Static analysis findings flow into governance

**CodeQL / SARIF integration** (`codeql_to_human_contract.md`)
- GitHub Advanced Security findings → Remediation Verification Gate
- SARIF structured security events flow into governance

**GitHub Actions governance pattern**
- CI/CD pipeline results → Decision Scope Policy
- Build success does not imply production authorization

**Claude Security Guidance** (this document)
- Claude Code write-time findings → Remediation Verification Gate
- Real-time security detection flows into governance

All four follow the same principle: **Finding ≠ Authorization**.

---

## Summary

Claude's security-guidance plugin is an excellent early-warning system. It detects issues at code-write time, before they reach production.

However, detection is not permission.

The governance stack converts Claude's findings into structured, auditable, human-controlled decision points. A security issue that Claude catches and a developer fixes still requires:

1. Verification that the fix is sound (RVG)
2. Human judgment about what scope is appropriate (AUB)
3. Controlled, bounded execution (Execution Ticket)
4. Audit trail and replay capability (Audit Layer)

This is not bureaucracy. It is operational reliability.

---

**Document Status**: Specification v0.1 (Integration Pattern)  
**Date**: 2026-05-27  
**Implementation**: Not started  
**Related**: Semgrep integration, CodeQL integration, GitHub Actions pattern

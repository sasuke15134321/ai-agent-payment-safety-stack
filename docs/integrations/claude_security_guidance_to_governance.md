# Claude Security Guidance → AI Agent Governance Flow Integration

## 1. Purpose

Claude security-guidance plugin provides security findings and remediation hints for code vulnerabilities.

However, **a finding is not an execution authorization.**

This document defines how security findings from Claude security-guidance are integrated into the AI Agent Payment Safety Stack governance flow to ensure that:
- Findings remain evidence, not approval
- Remediation suggestions remain hints, not authorized patches
- Security validation remains separate from deployment authorization
- Human approval is always required and scoped

**Core Principles (必ず明記)**:
- finding ≠ deployment authorization
- remediation hint ≠ approved patch
- CI success ≠ production authorization
- Approval ≠ unrestricted execution
- Production remains blocked until separately authorized

---

## 2. Non-goals

This document does NOT:
- Re-implement the Claude security-guidance plugin
- Replace or duplicate security scanning tools
- Authorize automatic production deployment
- Treat findings as approval by default
- Implement the governance runtime engine
- Execute security patches autonomously

---

## 3. Integration Flow

```
Claude security-guidance plugin
↓
Security finding / remediation hint
↓
Remediation Verification Gate
↓
Verification result
↓
Approval Unit Builder
↓
Human Decision Contract
↓
Scoped human approval
↓
Allowed action only
↓
Production remains blocked unless separately authorized
```

**Critical boundaries**:
- Security check success ≠ staging approval
- Staging approval ≠ production approval
- Approval Unit ≠ unrestricted execution
- Finding validation ≠ patch authorization

---

## 4. Governance Boundary

security check success ≠ deployment authorization

Production deployment requires separate approval scope and execution ticket.

---

## 5. Example Scenario

SQL injection risk の例：
- approval_question: Approve this security patch for staging merge?
- recommended_human_action: approve_staging_only
- allowed_actions: merge_to_staging
- still_blocked_actions: deploy_to_production

---

## 6. Relation to Existing Specs

- agent_remediation_verification_gate_spec.md
- agent_approval_unit_builder_spec.md
- agent_decision_scope_policy_spec.md
- agent_execution_ticket_spec.md
- agent_governance_runtime_architecture_spec.md
- agent_operational_degradation_guard_spec.md

---

## 7. Operational Degradation Note

AI Agent は security finding 確認後、確認を省略して patch / deploy に進む可能性がある。
これは hallucination ではなく operational degradation として扱う。

---

## 8. Status

This is an integration design document.
Runtime integration has not yet been implemented.

Current status:
- Claude security-guidance plugin: external security guidance source
- Remediation Verification Gate API: live
- Approval Unit Builder API: live
- Execution Ticket: specified
- Production authorization: separately required

**Important Disclaimers**:
- This document describes governance concepts, not implementation details
- No new APIs are introduced by this design
- No autonomous remediation or deployment is proposed
- Production authorization remains a separate, manual process
- Integration with actual Claude security-guidance plugin requires external connector (not specified here)

---

**Document Status**: Specification Draft (v0.1)  
**Date**: 2026-05-27  
**Implementation**: Not started  
**New APIs**: None

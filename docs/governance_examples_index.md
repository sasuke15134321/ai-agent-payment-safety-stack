# Governance Examples Index

## Quick understanding
- [Governance Quickstart](governance_quickstart.md) — Understand this project in 5 minutes

## Security governance
- [Security Patch Walkthrough](walkthroughs/security_patch_walkthrough.md) — How AI-generated fixes move through governance
- [Semgrep Integration](integrations/semgrep_to_approval_flow.md) — Semgrep findings → Human Decision Contract
- [CodeQL / SARIF Integration](integrations/codeql_to_human_contract.md) — SARIF evidence → Human Decision Contract

## Execution governance
- [Production Deploy Escalation](walkthroughs/production_deploy_escalation.md) — Why production requires separate governance
- [Financial Approval Walkthrough](walkthroughs/financial_approval_walkthrough.md) — Budget governance for AI agent spending

## Architecture
- [Governance Runtime Architecture](../03_テキスト/agent_governance_runtime_architecture_spec.md) — How primitives compose at runtime
- [Decision Scope Policy](../03_テキスト/agent_decision_scope_policy_spec.md) — Execution boundary contracts

## Core APIs
- Remediation Verification Gate: POST /api/remediation/verify
- Approval Unit Builder: POST /api/approval-unit/build (0.05 USDC)

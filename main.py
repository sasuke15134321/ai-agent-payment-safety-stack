#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Approval Unit Builder API v0.1

Converts AI-generated findings, patches, payment requests, deployment proposals,
memory writes, tool execution requests, or decision-support outputs
into minimal human decision contracts (Approval Units).

Core concept: Approval Unit = Human Decision Contract

v0.1: build-only.
No approval execution, blockchain transactions, x402/JPYC payments,
deploys, memory writes, or tool calls.
"""

import base64
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from payment_verifier import PaymentVerifier

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "0x60c402878EfcEcAe5733A88075328Aa2320C39BE")
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

payment_verifier = PaymentVerifier()

app = FastAPI(
    title="Agent Approval Unit Builder",
    version="0.1.0",
    description=(
        "Converts AI-generated findings, patches, payment requests, deployment proposals, "
        "memory writes, tool execution requests, or decision-support outputs into minimal "
        "human decision contracts (Approval Units). "
        "Approval Unit = Human Decision Contract. "
        "v0.1 is build-only: no approval execution, blockchain transactions, or payments."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# x402 paid endpoint config
_PAID_ENDPOINTS = {
    ("POST", "/api/approval-unit/build"): "0.05",
}

_ENDPOINT_DESCRIPTIONS = {
    "/api/approval-unit/build": (
        "Build a minimal human decision contract from AI-generated findings, patches, "
        "payment requests, or decision-support outputs."
    ),
}

# CDP Bazaar indexing extension
_BAZAAR_EXTENSIONS = {
    "bazaar": {
        "discoverable": True,
        "info": {
            "input": {
                "type": "http",
                "method": "POST",
                "bodyType": "json",
                "body": {
                    "source_type": "security_patch",
                    "approval_unit_type": "security_patch_approval",
                    "title": "Approve patch for SQL injection",
                    "summary": "Replace raw SQL with parameterized query.",
                    "risk_level": "high",
                },
            },
            "output": {
                "type": "json",
                "example": {
                    "approval_question": "Approve this security patch for staging merge?",
                    "recommended_human_action": "approve_staging_only",
                    "chain_anchor_status": "not_anchored",
                    "approval_unit_hash": "sha256:...",
                },
            },
        },
        "schema": {
            "type": "object",
            "properties": {
                "approval_question": {"type": "string"},
                "recommended_human_action": {"type": "string"},
                "chain_anchor_status": {"type": "string"},
                "approval_unit_hash": {"type": "string"},
            },
        },
    }
}


@app.middleware("http")
async def x402_payment_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path
    price = _PAID_ENDPOINTS.get((method, path))

    if not TEST_MODE and price is not None:
        payment_header = (
            request.headers.get("PAYMENT-SIGNATURE") or request.headers.get("X-PAYMENT")
        )
        if not payment_header:
            amount = str(round(float(price) * 1_000_000))
            _accept = {
                "scheme": "exact",
                "network": "eip155:8453",
                "amount": amount,
                "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                "payTo": WALLET_ADDRESS,
                "maxTimeoutSeconds": 300,
                "extra": {"name": "USD Coin", "version": "2"},
                "resource": {"method": method, "mimeType": "application/json"},
            }
            _pc = {
                "x402Version": 2,
                "error": "Payment required",
                "resource": {
                    "url": str(request.url),
                    "method": method,
                    "description": _ENDPOINT_DESCRIPTIONS.get(path, "Paid API endpoint"),
                    "mimeType": "application/json",
                },
                "accepts": [_accept],
            }
            if path == "/api/approval-unit/build":
                _pc["extensions"] = _BAZAAR_EXTENSIONS
                _pc["approval_unit_id"] = None
                _pc["approval_unit_hash"] = None
                _pc["next_recommended"] = "complete_x402_payment"
            return JSONResponse(
                status_code=402,
                content=_pc,
                headers={
                    "Payment-Required": base64.b64encode(json.dumps(_pc).encode()).decode()
                },
            )

    return await call_next(request)


# ─────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────

class ApprovalUnitBuildRequest(BaseModel):
    source_type: str
    source_id: Optional[str] = None
    approval_unit_type: str
    finding_id: Optional[str] = None
    claim_id: Optional[str] = None
    patch_id: Optional[str] = None
    payment_request_id: Optional[str] = None
    deployment_request_id: Optional[str] = None
    memory_write_id: Optional[str] = None
    tool_call_id: Optional[str] = None
    review_task_id: Optional[str] = None
    title: str
    summary: str
    risk_level: str
    severity: Optional[str] = None
    evidence_ids: List[str] = []
    source_ids: List[str] = []
    test_results: List[str] = []
    regression_risk: Optional[str] = None
    rollback_available: Optional[bool] = None
    cost_impact: Optional[Dict[str, Any]] = None
    blocked_actions_until_approval: List[str] = []
    allowed_human_actions: List[str] = [
        "approve", "reject", "request_rework", "request_more_evidence", "escalate"
    ]
    suggested_human_actions: List[str] = []
    recommended_decision: Optional[str] = None
    reviewer_role: Optional[str] = None
    approver_role: str = "human_approver"
    request_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_id: Optional[str] = None


class ApprovalUnitBuildResponse(BaseModel):
    approval_unit_id: str
    approval_unit_hash: str
    approval_unit_type: str
    title: str
    approval_question: str
    decision_required: str
    decision_options: List[str]
    approver_role: str
    priority: str
    risk_level: str
    summary: str
    evidence_summary: str
    required_evidence: List[str]
    required_checks_before_approval: List[str]
    test_summary: str
    regression_risk: Optional[str]
    rollback_available: Optional[bool]
    suggested_human_actions: List[str]
    recommended_human_action: str
    human_action_reason: str
    allowed_human_actions: List[str]
    blocked_actions_until_approval: List[str]
    if_approved: Dict[str, Any]
    if_rejected: Dict[str, Any]
    if_request_rework: Dict[str, Any]
    if_request_more_evidence: Dict[str, Any]
    if_escalated: Dict[str, Any]
    post_decision_route: str
    decision_effect_summary: str
    audit_required: bool
    blockchain_anchor_ready: bool
    chain_anchor_status: str
    chain_tx_hash: Optional[str]
    request_id: Optional[str]
    task_id: Optional[str]
    created_at: str


# ─────────────────────────────────────────────
# Rule-based generators
# ─────────────────────────────────────────────

def _infer_scope(blocked_actions: List[str]) -> str:
    """Infer scope from blocked_actions for template generation."""
    joined = " ".join(blocked_actions).lower()
    if "merge_to_staging" in joined or ("merge" in joined and "staging" in joined):
        return "staging merge"
    if "deploy_to_production" in joined or ("deploy" in joined and "production" in joined):
        return "production deployment"
    if "send_x402_payment" in joined or "x402_payment" in joined:
        return "x402 payment execution"
    if "memory_write" in joined or "write_to_memory" in joined:
        return "long-term memory"
    if "tool_call" in joined or "tool_execution" in joined:
        return "tool execution"
    if "use_in_decision_card" in joined or "decision_card" in joined:
        return "decision card use"
    return "the requested action"


_APPROVAL_QUESTION_TEMPLATES: Dict[str, str] = {
    "security_patch_approval":     "Approve this security patch for {scope}?",
    "remediation_plan_approval":   "Approve this remediation plan for {scope}?",
    "payment_approval":            "Approve this payment request for {scope}?",
    "deployment_approval":         "Approve this deployment action for {scope}?",
    "decision_card_approval":      "Approve this decision card for {scope}?",
    "legal_review_approval":       "Approve this legal or compliance-sensitive output for review use?",
    "financial_review_approval":   "Approve this financial decision-support output for review use?",
    "evidence_exception_approval": "Approve this evidence exception for limited decision use?",
    "memory_write_approval":       "Approve this content to be written to agent memory?",
    "tool_execution_approval":     "Approve this high-risk tool execution?",
}


def _generate_approval_question(req: ApprovalUnitBuildRequest) -> str:
    """Rule-based template generation. v0.1: no LLM generation."""
    template = _APPROVAL_QUESTION_TEMPLATES.get(
        req.approval_unit_type, "Approve this action for {scope}?"
    )
    scope = _infer_scope(req.blocked_actions_until_approval)
    return template.format(scope=scope)


_SUGGESTED_ACTIONS_BY_TYPE: Dict[str, List[str]] = {
    "security_patch_approval": [
        "review_patch_diff", "check_test_results", "verify_source_lineage",
        "request_security_retest", "approve_staging_only",
    ],
    "remediation_plan_approval": [
        "review_remediation_plan", "check_regression_risk", "verify_rollback_plan",
        "approve_limited_execution", "request_more_evidence",
    ],
    "payment_approval": [
        "check_budget_limit", "verify_payment_purpose", "reduce_payment_scope",
        "approve_payment_only", "deny_payment",
    ],
    "deployment_approval": [
        "check_deployment_scope", "verify_rollback_plan", "approve_staging_only",
        "block_production_deploy", "escalate_to_engineering_lead",
    ],
    "decision_card_approval": [
        "verify_evidence_coverage", "check_source_lineage", "request_more_evidence",
        "approve_decision_use_only", "mark_claim_as_assumption",
    ],
    "legal_review_approval": [
        "review_legal_output", "verify_compliance_scope", "escalate_to_legal_team",
        "approve_limited_use", "request_more_evidence",
    ],
    "financial_review_approval": [
        "review_financial_output", "verify_source_lineage", "escalate_to_financial_reviewer",
        "approve_decision_use_only", "request_more_evidence",
    ],
    "evidence_exception_approval": [
        "review_exception_scope", "verify_known_risks", "approve_with_exception_record",
        "reject_exception", "request_more_evidence",
    ],
    "memory_write_approval": [
        "verify_source_lineage", "check_memory_scope", "approve_memory_write",
        "reject_memory_write", "request_more_evidence",
    ],
    "tool_execution_approval": [
        "inspect_tool_call", "verify_risk_level", "approve_limited_execution",
        "reject_tool_execution", "escalate_to_operator",
    ],
}

_DEFAULT_SUGGESTED_ACTIONS = ["review_summary", "check_evidence", "approve", "reject", "request_rework"]


def _generate_suggested_actions(req: ApprovalUnitBuildRequest) -> List[str]:
    if req.suggested_human_actions:
        return req.suggested_human_actions
    return _SUGGESTED_ACTIONS_BY_TYPE.get(req.approval_unit_type, _DEFAULT_SUGGESTED_ACTIONS)


def _generate_recommended_action(
    req: ApprovalUnitBuildRequest, suggested: List[str]
) -> tuple:
    """Rule-based recommended_human_action. v0.1: deterministic rules only."""
    blocked_str = " ".join(req.blocked_actions_until_approval).lower()
    risk = req.risk_level.lower()

    # Rollback missing + deployment type
    if req.rollback_available is False and (
        "deploy" in blocked_str or "deployment" in req.approval_unit_type
    ):
        return "request_rollback_plan", "Rollback plan is missing."

    # No evidence and no sources
    if not req.evidence_ids and not req.source_ids:
        return "request_more_evidence", "No evidence or source IDs are attached."

    # Security patch without test results
    if not req.test_results and req.approval_unit_type == "security_patch_approval":
        return "request_security_retest", "Security patch approval requires test results."

    # Tests present + rollback available + staging in blocked actions
    # (takes priority over escalation when staging can be safely approved)
    if req.test_results and req.rollback_available is True and "staging" in blocked_str:
        return (
            "approve_staging_only",
            "Tests passed and rollback is available, but production should remain blocked.",
        )

    # High/critical risk + production deploy (no safe staging path available)
    if risk in ("high", "critical") and "production" in blocked_str:
        return (
            "escalate_to_security_lead",
            "High-risk production action requires escalation.",
        )

    # Default
    default = req.recommended_decision or (suggested[0] if suggested else "approve")
    return default, "Default recommended action based on approval unit type."


def _generate_required_evidence(req: ApprovalUnitBuildRequest) -> List[str]:
    base: Dict[str, List[str]] = {
        "security_patch_approval":     ["finding", "patch_diff", "test_results", "rollback_plan"],
        "remediation_plan_approval":   ["remediation_plan", "risk_assessment", "rollback_plan"],
        "payment_approval":            ["payment_purpose", "budget_limit", "approval_scope"],
        "deployment_approval":         ["deployment_plan", "rollback_plan", "test_results"],
        "decision_card_approval":      ["primary_source_ids", "evidence_coverage", "claim_list"],
        "legal_review_approval":       ["legal_summary", "compliance_scope", "risk_notes"],
        "financial_review_approval":   ["financial_summary", "source_lineage", "decision_scope"],
        "evidence_exception_approval": ["exception_reason", "known_risks", "limited_scope"],
        "memory_write_approval":       ["source_lineage", "memory_scope", "content_summary"],
        "tool_execution_approval":     ["tool_definition", "risk_assessment", "execution_scope"],
    }
    required = list(base.get(req.approval_unit_type, ["summary", "evidence_ids", "source_ids"]))
    if not req.evidence_ids:
        required.append("evidence_ids_required")
    if not req.test_results and req.approval_unit_type in (
        "security_patch_approval", "deployment_approval"
    ):
        required.append("test_results_required")
    return required


def _generate_required_checks(req: ApprovalUnitBuildRequest) -> List[str]:
    checks: Dict[str, List[str]] = {
        "security_patch_approval":     ["patch_diff_reviewed", "test_results_confirmed", "source_lineage_verified"],
        "remediation_plan_approval":   ["plan_reviewed", "regression_risk_assessed", "rollback_confirmed"],
        "payment_approval":            ["budget_limit_confirmed", "payment_purpose_verified", "approver_authorization_confirmed"],
        "deployment_approval":         ["deployment_scope_reviewed", "rollback_plan_confirmed", "test_results_confirmed"],
        "decision_card_approval":      ["evidence_coverage_verified", "primary_sources_confirmed", "claim_list_reviewed"],
        "legal_review_approval":       ["legal_output_reviewed", "compliance_scope_confirmed"],
        "financial_review_approval":   ["financial_output_reviewed", "source_lineage_confirmed"],
        "evidence_exception_approval": ["exception_scope_reviewed", "known_risks_acknowledged"],
        "memory_write_approval":       ["source_lineage_verified", "memory_scope_confirmed"],
        "tool_execution_approval":     ["tool_call_inspected", "risk_level_verified"],
    }
    base = list(checks.get(req.approval_unit_type, ["summary_reviewed", "evidence_confirmed"]))
    if req.rollback_available is True and "rollback_plan_confirmed" not in base:
        base.append("rollback_plan_confirmed")
    return base


def _generate_decision_effects(req: ApprovalUnitBuildRequest):
    blocked = req.blocked_actions_until_approval

    # Classify staging-level vs production-level blocked actions
    staging_allowed = [
        a for a in blocked
        if any(k in a.lower() for k in ("staging", "payment_only", "memory_write", "limited", "decision_use"))
    ]
    still_blocked = [
        a for a in blocked
        if any(k in a.lower() for k in ("production", "deploy_to_prod"))
    ]

    # Fallback: if no clear split, allow first blocked action only
    if not staging_allowed and blocked:
        staging_allowed = [blocked[0]]
        still_blocked = [a for a in blocked if a not in staging_allowed]

    if_approved = {
        "allowed_actions": staging_allowed,
        "still_blocked_actions": still_blocked,
        "post_decision_route": "proceed_with_approved_scope",
    }
    if_rejected = {
        "blocked_actions": blocked,
        "post_decision_route": "stop_or_reassess",
    }
    if_request_rework = {
        "post_decision_route": "route_to_rework",
        "required_changes": ["address_reviewer_feedback", "resubmit_for_approval"],
    }
    if_request_more_evidence = {
        "post_decision_route": "route_to_research",
        "required_evidence": _generate_required_evidence(req),
    }
    if_escalated = {
        "post_decision_route": "escalate_to_approver",
        "required_context": ["approval_unit", "risk_summary", "blocked_actions"],
    }
    return if_approved, if_rejected, if_request_rework, if_request_more_evidence, if_escalated


def _generate_priority(risk_level: str) -> str:
    return {"critical": "critical", "high": "high", "medium": "medium", "low": "low"}.get(
        risk_level.lower(), "medium"
    )


def _generate_evidence_summary(req: ApprovalUnitBuildRequest) -> str:
    parts = []
    if req.evidence_ids:
        parts.append(f"Evidence: {', '.join(req.evidence_ids)}.")
    if req.source_ids:
        parts.append(f"Sources: {', '.join(req.source_ids)}.")
    if req.test_results:
        parts.append(f"Tests: {', '.join(req.test_results)}.")
    return " ".join(parts) if parts else "No evidence IDs, source IDs, or test results attached."


def _generate_test_summary(req: ApprovalUnitBuildRequest) -> str:
    if not req.test_results:
        return "No test results provided."
    return f"{', '.join(req.test_results)}."


def _generate_decision_effect_summary(req: ApprovalUnitBuildRequest, if_approved: dict) -> str:
    allowed = if_approved.get("allowed_actions", [])
    still_blocked = if_approved.get("still_blocked_actions", [])
    parts = []
    if allowed:
        parts.append(f"Approval allows: {', '.join(allowed)}.")
    if still_blocked:
        parts.append(f"Still blocked after approval: {', '.join(still_blocked)}.")
    return " ".join(parts) if parts else "Approval unlocks the requested actions."


def _build_canonical(
    req: ApprovalUnitBuildRequest,
    approval_question: str,
    decision_options: List[str],
    if_approved: dict,
    if_rejected: dict,
    if_request_rework: dict,
    if_request_more_evidence: dict,
) -> dict:
    """Canonical dict for hashing. Excludes created_at for hash stability."""
    return {
        "approval_unit_type": req.approval_unit_type,
        "source_type": req.source_type,
        "source_id": req.source_id,
        "finding_id": req.finding_id,
        "claim_id": req.claim_id,
        "patch_id": req.patch_id,
        "payment_request_id": req.payment_request_id,
        "deployment_request_id": req.deployment_request_id,
        "memory_write_id": req.memory_write_id,
        "tool_call_id": req.tool_call_id,
        "evidence_ids": sorted(req.evidence_ids),
        "source_ids": sorted(req.source_ids),
        "test_results": sorted(req.test_results),
        "risk_level": req.risk_level,
        "approval_question": approval_question,
        "decision_options": decision_options,
        "blocked_actions_until_approval": req.blocked_actions_until_approval,
        "allowed_human_actions": req.allowed_human_actions,
        "if_approved": if_approved,
        "if_rejected": if_rejected,
        "if_request_rework": if_request_rework,
        "if_request_more_evidence": if_request_more_evidence,
        "request_id": req.request_id,
        "task_id": req.task_id,
    }


def _sha256(data: dict) -> str:
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@app.post("/api/approval-unit/build", response_model=ApprovalUnitBuildResponse)
async def build_approval_unit(req: ApprovalUnitBuildRequest, request: Request):
    """
    Build a minimal Approval Unit (Human Decision Contract) from an AI-generated output.

    Approval Unit = Human Decision Contract.
    Defines what the human is approving, what becomes allowed after approval,
    what remains blocked, and what human action is suggested next.

    v0.1: build-only. No approval execution, blockchain, or payments.
    approval_question is generated by rule-based templates (not LLM).
    """
    if not TEST_MODE:
        payment_header = (
            request.headers.get("PAYMENT-SIGNATURE") or request.headers.get("X-PAYMENT")
        )
        is_valid = await payment_verifier.verify_payment(payment_header, WALLET_ADDRESS, "0.05")
        if not is_valid:
            raise HTTPException(status_code=402, detail="Payment verification failed")

    approval_unit_id = "approval_" + uuid.uuid4().hex[:8]
    decision_options = ["approve", "reject", "request_rework", "request_more_evidence", "defer", "escalate"]

    approval_question = _generate_approval_question(req)
    suggested = _generate_suggested_actions(req)
    recommended_action, action_reason = _generate_recommended_action(req, suggested)
    priority = _generate_priority(req.risk_level)
    evidence_summary = _generate_evidence_summary(req)
    test_summary = _generate_test_summary(req)
    required_evidence = _generate_required_evidence(req)
    required_checks = _generate_required_checks(req)

    if_approved, if_rejected, if_request_rework, if_request_more_evidence, if_escalated = (
        _generate_decision_effects(req)
    )

    decision_effect_summary = _generate_decision_effect_summary(req, if_approved)

    canonical = _build_canonical(
        req, approval_question, decision_options,
        if_approved, if_rejected, if_request_rework, if_request_more_evidence,
    )
    approval_unit_hash = _sha256(canonical)

    return ApprovalUnitBuildResponse(
        approval_unit_id=approval_unit_id,
        approval_unit_hash=approval_unit_hash,
        approval_unit_type=req.approval_unit_type,
        title=req.title,
        approval_question=approval_question,
        decision_required=" | ".join(decision_options),
        decision_options=decision_options,
        approver_role=req.approver_role,
        priority=priority,
        risk_level=req.risk_level,
        summary=req.summary,
        evidence_summary=evidence_summary,
        required_evidence=required_evidence,
        required_checks_before_approval=required_checks,
        test_summary=test_summary,
        regression_risk=req.regression_risk,
        rollback_available=req.rollback_available,
        suggested_human_actions=suggested,
        recommended_human_action=recommended_action,
        human_action_reason=action_reason,
        allowed_human_actions=req.allowed_human_actions,
        blocked_actions_until_approval=req.blocked_actions_until_approval,
        if_approved=if_approved,
        if_rejected=if_rejected,
        if_request_rework=if_request_rework,
        if_request_more_evidence=if_request_more_evidence,
        if_escalated=if_escalated,
        post_decision_route="depends_on_human_decision",
        decision_effect_summary=decision_effect_summary,
        audit_required=True,
        blockchain_anchor_ready=True,
        chain_anchor_status="not_anchored",
        chain_tx_hash=None,
        request_id=req.request_id,
        task_id=req.task_id,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


# ─────────────────────────────────────────────
# Remediation Verification Gate v0.1
# ─────────────────────────────────────────────

class RemediationVerifyRequest(BaseModel):
    remediation_id: str
    finding_id: Optional[str] = None
    source_type: str
    source_id: Optional[str] = None
    remediation_type: str
    title: str
    finding_summary: str
    remediation_summary: str
    patch_id: Optional[str] = None
    patch_diff_id: Optional[str] = None
    configuration_change_id: Optional[str] = None
    dependency_update_id: Optional[str] = None
    affected_files: List[str] = []
    affected_services: List[str] = []
    affected_environment: Optional[str] = None
    severity: str
    risk_level: str
    exploitability: Optional[str] = None
    evidence_ids: List[str] = []
    source_ids: List[str] = []
    test_results: List[str] = []
    security_retest_results: List[str] = []
    static_analysis_results: List[str] = []
    dynamic_analysis_results: List[str] = []
    regression_test_results: List[str] = []
    rollback_plan_id: Optional[str] = None
    rollback_available: Optional[bool] = None
    blast_radius: Optional[str] = None
    production_impact: Optional[str] = None
    staging_tested: Optional[bool] = None
    production_deploy_requested: bool = False
    generated_by_agent_id: Optional[str] = None
    request_id: Optional[str] = None
    task_id: Optional[str] = None


class RemediationVerifyResponse(BaseModel):
    gate_name: str
    remediation_id: str
    finding_id: Optional[str]
    remediation_type: str
    decision: str
    verification_status: str
    readiness_level: str
    risk_level: str
    severity: str
    evidence_status: str
    test_status: str
    security_retest_status: str
    regression_status: str
    rollback_status: str
    blast_radius: Optional[str]
    production_risk: str
    allowed_next_steps: List[str]
    blocked_next_steps: List[str]
    recommended_route: str
    recommended_human_action: str
    human_action_reason: str
    required_additional_evidence: List[str]
    required_rework_items: List[str]
    approval_unit_ready: bool
    approval_unit_type_suggestion: Optional[str]
    blocked_actions_until_approval: List[str]
    audit_required: bool
    blockchain_anchor_ready: bool
    request_id: Optional[str]
    task_id: Optional[str]
    created_at: str


def _rv_evidence_status(req: RemediationVerifyRequest) -> str:
    if req.evidence_ids or req.source_ids:
        return "sufficient"
    return "missing"


def _rv_test_status(req: RemediationVerifyRequest) -> str:
    if req.test_results:
        return "passed"
    return "missing"


def _rv_security_retest_status(req: RemediationVerifyRequest) -> str:
    if req.security_retest_results:
        return "passed"
    if req.severity.lower() in ("high", "critical"):
        return "required"
    return "missing"


def _rv_regression_status(req: RemediationVerifyRequest) -> str:
    if req.regression_test_results:
        return "passed"
    return "missing"


def _rv_rollback_status(req: RemediationVerifyRequest) -> str:
    if req.rollback_available is True:
        if req.rollback_plan_id:
            return "available"
        return "available_without_plan_id"
    return "missing"


def _rv_production_risk(req: RemediationVerifyRequest) -> str:
    if req.production_deploy_requested:
        if req.risk_level.lower() in ("high", "critical"):
            return "blocked"
        return "requires_review"
    return "not_requested"


def _rv_decision(
    req: RemediationVerifyRequest,
    evidence_status: str,
    test_status: str,
    security_retest_status: str,
    rollback_status: str,
) -> tuple:
    if evidence_status == "missing":
        return (
            "require_more_evidence",
            "request_more_evidence",
            "Evidence IDs and source IDs are missing.",
        )
    if test_status == "missing":
        return (
            "require_security_retest",
            "request_tests",
            "Test results are missing.",
        )
    if security_retest_status == "required":
        return (
            "require_security_retest",
            "request_security_retest",
            "Security retest is required for high/critical severity.",
        )
    if rollback_status == "missing":
        return (
            "require_rollback_plan",
            "request_rollback_plan",
            "Rollback plan is missing or unavailable.",
        )
    if req.production_deploy_requested and req.risk_level.lower() in ("high", "critical"):
        return (
            "block_production_deploy",
            "escalate_to_security_lead",
            "High or critical risk production deploy requires escalation.",
        )
    if (
        evidence_status == "sufficient"
        and test_status == "passed"
        and security_retest_status == "passed"
        and rollback_status in ("available", "available_without_plan_id")
        and not req.production_deploy_requested
    ):
        return (
            "route_to_approval_unit_builder",
            "approve_staging_only",
            "All checks passed. Ready for human approval at staging level.",
        )
    return (
        "pass_with_warnings",
        "approve_after_review",
        "Some checks are incomplete. Human review is recommended before proceeding.",
    )


def _rv_approval_unit_ready(decision: str) -> bool:
    return decision in ("route_to_approval_unit_builder", "pass_with_warnings", "block_production_deploy")


def _rv_readiness_level(
    approval_unit_ready: bool,
    evidence_status: str,
    test_status: str,
    rollback_status: str,
) -> str:
    if approval_unit_ready:
        return "human_approval_ready"
    if evidence_status == "missing":
        return "needs_more_evidence"
    if test_status == "missing":
        return "needs_testing"
    if rollback_status == "missing":
        return "needs_rollback_plan"
    return "needs_review"


def _rv_verification_status(decision: str) -> str:
    if decision == "route_to_approval_unit_builder":
        return "verified"
    if decision == "pass_with_warnings":
        return "verified_with_warnings"
    if decision == "block_production_deploy":
        return "blocked"
    return "incomplete"


def _rv_recommended_route(decision: str) -> str:
    return {
        "route_to_approval_unit_builder": "approval_unit_builder",
        "require_more_evidence": "route_to_research",
        "require_rework": "route_to_rework",
        "require_security_retest": "route_to_rework",
        "require_rollback_plan": "route_to_rework",
        "block_production_deploy": "escalate_to_approver",
        "pass_with_warnings": "route_to_human_review",
        "block_execution": "block_execution",
    }.get(decision, "route_to_human_review")


def _rv_next_steps(decision: str) -> tuple:
    if decision == "route_to_approval_unit_builder":
        return (
            ["create_approval_unit", "allow_staging_merge_after_approval"],
            ["deploy_to_production"],
        )
    if decision == "block_production_deploy":
        return (["create_approval_unit_for_staging"], ["deploy_to_production"])
    if decision == "require_more_evidence":
        return (
            ["collect_more_evidence"],
            ["create_approval_unit", "merge_to_staging", "deploy_to_production"],
        )
    if decision == "require_security_retest":
        return (
            ["run_tests", "run_security_retest"],
            ["create_approval_unit", "merge_to_staging", "deploy_to_production"],
        )
    if decision == "require_rollback_plan":
        return (
            ["create_rollback_plan"],
            ["create_approval_unit", "merge_to_staging", "deploy_to_production"],
        )
    return (["route_to_human_review"], ["deploy_to_production"])


def _rv_approval_unit_type_suggestion(remediation_type: str) -> str:
    return {
        "patch_candidate": "security_patch_approval",
        "remediation_plan": "remediation_plan_approval",
        "configuration_change": "deployment_approval",
        "dependency_update": "deployment_approval",
        "deployment_proposal": "deployment_approval",
    }.get(remediation_type, "remediation_plan_approval")


@app.post("/api/remediation/verify", response_model=RemediationVerifyResponse)
async def verify_remediation(req: RemediationVerifyRequest):
    """
    Verify an AI-generated remediation candidate before routing to human review or Approval Unit Builder.

    v0.1: rule-based verification only.
    No patch application, deployment, approval execution, payment execution,
    memory write, tool execution, or blockchain transaction.
    """
    evidence_status = _rv_evidence_status(req)
    test_status = _rv_test_status(req)
    security_retest_status = _rv_security_retest_status(req)
    regression_status = _rv_regression_status(req)
    rollback_status = _rv_rollback_status(req)
    production_risk = _rv_production_risk(req)

    decision, recommended_human_action, human_action_reason = _rv_decision(
        req, evidence_status, test_status, security_retest_status, rollback_status
    )

    approval_unit_ready = _rv_approval_unit_ready(decision)
    readiness_level = _rv_readiness_level(
        approval_unit_ready, evidence_status, test_status, rollback_status
    )
    verification_status = _rv_verification_status(decision)
    recommended_route = _rv_recommended_route(decision)
    allowed_next_steps, blocked_next_steps = _rv_next_steps(decision)
    approval_unit_type_suggestion = _rv_approval_unit_type_suggestion(req.remediation_type)

    required_additional_evidence: List[str] = []
    if evidence_status == "missing":
        required_additional_evidence = ["evidence_ids", "source_ids"]

    required_rework_items: List[str] = []
    if test_status == "missing":
        required_rework_items.append("test_results_required")
    if security_retest_status == "required":
        required_rework_items.append("security_retest_required")
    if rollback_status == "missing":
        required_rework_items.append("rollback_plan_required")

    return RemediationVerifyResponse(
        gate_name="remediation_verification_gate",
        remediation_id=req.remediation_id,
        finding_id=req.finding_id,
        remediation_type=req.remediation_type,
        decision=decision,
        verification_status=verification_status,
        readiness_level=readiness_level,
        risk_level=req.risk_level,
        severity=req.severity,
        evidence_status=evidence_status,
        test_status=test_status,
        security_retest_status=security_retest_status,
        regression_status=regression_status,
        rollback_status=rollback_status,
        blast_radius=req.blast_radius,
        production_risk=production_risk,
        allowed_next_steps=allowed_next_steps,
        blocked_next_steps=blocked_next_steps,
        recommended_route=recommended_route,
        recommended_human_action=recommended_human_action,
        human_action_reason=human_action_reason,
        required_additional_evidence=required_additional_evidence,
        required_rework_items=required_rework_items,
        approval_unit_ready=approval_unit_ready,
        approval_unit_type_suggestion=approval_unit_type_suggestion,
        blocked_actions_until_approval=["merge_to_staging", "deploy_to_production"],
        audit_required=True,
        blockchain_anchor_ready=True,
        request_id=req.request_id,
        task_id=req.task_id,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/")
async def root():
    return {
        "name": "Agent Approval Unit Builder API",
        "version": "0.1.0",
        "endpoints": {
            "POST /api/approval-unit/build": "Build an Approval Unit (human decision contract)",
            "POST /api/remediation/verify": "Verify AI remediation before approval (free)",
        },
        "note": "v0.1 is build-only. No approval execution, blockchain, or payments.",
        "core_concept": "Approval Unit = Human Decision Contract",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/.well-known/x402", include_in_schema=False)
async def x402_discovery_manifest():
    base_url = "https://ai-agent-payment-safety-stack.onrender.com"
    amount = str(round(0.05 * 1_000_000))  # 50000 USDC atomic units
    return {
        "version": 1,
        "name": "Agent Approval Unit Builder",
        "description": (
            "Build minimal human decision contracts from AI-generated findings, patches, "
            "payment requests, deployment proposals, memory writes, tool execution requests, "
            "or decision-support outputs. Approval Unit = Human Decision Contract."
        ),
        "tags": ["AI", "Approval", "Governance"],
        "ownershipProofs": [WALLET_ADDRESS],
        "resources": [
            {
                "x402Version": 2,
                "type": "http",
                "resource": f"{base_url}/api/approval-unit/build",
                "accepts": [
                    {
                        "scheme": "exact",
                        "network": "eip155:8453",
                        "amount": amount,
                        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                        "payTo": WALLET_ADDRESS,
                        "maxTimeoutSeconds": 300,
                        "extra": {"name": "USD Coin", "version": "2"},
                    }
                ],
                "extensions": _BAZAAR_EXTENSIONS,
            }
        ],
    }


@app.get("/llms.txt", include_in_schema=False)
async def llms_txt():
    from fastapi.responses import PlainTextResponse

    base_url = "https://ai-agent-payment-safety-stack.onrender.com"

    content = """# Agent Approval Unit Builder API

## Name
Agent Approval Unit Builder v0.1

## Description
Converts AI-generated findings, patches, payment requests, deployment proposals, memory writes, tool execution requests, or decision-support outputs into minimal human decision contracts (Approval Units).

Core concept: Approval Unit = Human Decision Contract

v0.1 is build-only. No approval execution, blockchain transactions, or payments.

## Endpoints

POST /api/approval-unit/build — Build a human decision contract (0.05 USDC)
POST /api/remediation/verify — Verify AI remediation before approval (free)

## Additional Resources

OpenAPI Docs: https://ai-agent-payment-safety-stack.onrender.com/docs
OpenAPI JSON: https://ai-agent-payment-safety-stack.onrender.com/openapi.json
Health Check: https://ai-agent-payment-safety-stack.onrender.com/health
x402 Discovery: https://ai-agent-payment-safety-stack.onrender.com/.well-known/x402

## Pricing

approval-unit/build: 0.05 USDC per call
remediation/verify: Free

## Payment

x402 scheme on Base (eip155:8453)
USDC payments to 0x60c402878EfcEcAe5733A88075328Aa2320C39BE

## Recommended Flow

POST /api/remediation/verify (free) → POST /api/approval-unit/build (0.05 USDC)

## Use Cases

- Security patch approval
- Payment request approval
- Deployment proposal approval
- Memory write approval
- Tool execution approval

## Direct AtoA Usage

Use this service when an AI agent needs to:
- verify an AI-generated remediation before human approval
- convert an AI-generated proposal into a human-approvable decision unit
- preserve the boundary between verification, approval, and execution
- prevent approval from being interpreted as unrestricted execution

Do not use this service to:
- deploy to production
- execute payments directly
- approve actions automatically
- replace human review in high-risk workflows

Primary endpoints:
- POST /api/remediation/verify
- POST /api/approval-unit/build

Payment:
- /api/approval-unit/build requires x402 payment: 0.05 USDC
- /api/remediation/verify is free

## Example Payloads

### POST /api/remediation/verify

Use this first when an AI agent has generated a remediation or patch candidate and needs to verify whether it is ready for human approval.

Example request:
{
  "remediation_id": "remediation_001",
  "finding_id": "finding_001",
  "remediation_type": "security_patch",
  "title": "SQL injection fix for user API",
  "finding_summary": "SQL injection vulnerability detected in user API endpoint.",
  "remediation_summary": "Replace raw SQL interpolation with parameterized query.",
  "affected_files": ["api/user.py"],
  "severity": "critical",
  "risk_level": "high",
  "evidence_ids": ["codeql_001"],
  "test_results": ["unit_passed"],
  "rollback_available": true,
  "production_deploy_requested": false
}

Expected result:
- decision: route_to_approval_unit_builder
- approval_unit_ready: true
- recommended_human_action: approve_staging_only
- blocked_next_steps includes deploy_to_production

### POST /api/approval-unit/build

Use this after verification when an AI agent needs to convert a verified proposal into a human decision contract.

Example request:
{
  "source_type": "security_patch",
  "approval_unit_type": "security_patch_approval",
  "title": "Approve SQL injection fix for staging",
  "summary": "Patch replaces raw SQL interpolation with parameterized query.",
  "risk_level": "high",
  "evidence_ids": ["codeql_001"],
  "test_results": ["unit_passed"],
  "rollback_available": true,
  "blocked_actions_until_approval": ["merge_to_staging", "deploy_to_production"],
  "recommended_decision": "approve_staging_only"
}

Expected result:
- approval_question
- approval_unit_hash
- recommended_human_action
- allowed_actions limited to staging scope
- blocked_actions includes deploy_to_production
"""
    return PlainTextResponse(content)


@app.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    from fastapi.responses import PlainTextResponse

    content = """# robots.txt for Agent Approval Unit Builder API

User-agent: *
Allow: /

# Sitemap for API discovery
Sitemap: https://ai-agent-payment-safety-stack.onrender.com/openapi.json
Sitemap: https://ai-agent-payment-safety-stack.onrender.com/llms.txt
Sitemap: https://ai-agent-payment-safety-stack.onrender.com/.well-known/x402
"""
    return PlainTextResponse(content)


@app.get("/.well-known/agent.json", include_in_schema=False)
async def agent_json():
    base_url = "https://ai-agent-payment-safety-stack.onrender.com"

    return {
        "name": "Agent Approval Unit Builder v0.1",
        "description": (
            "Converts AI-generated findings, patches, payment requests, deployment proposals, "
            "memory writes, tool execution requests, or decision-support outputs into minimal "
            "human decision contracts (Approval Units). "
            "Approval Unit = Human Decision Contract. "
            "v0.1 is build-only: no approval execution, blockchain transactions, or payments."
        ),
        "endpoints": [
            {
                "method": "POST",
                "path": "/api/approval-unit/build",
                "description": "Build a minimal human decision contract from AI-generated findings or proposals",
                "pricing": {
                    "amount": "0.05",
                    "currency": "USDC",
                },
            },
            {
                "method": "POST",
                "path": "/api/remediation/verify",
                "description": "Verify AI-generated remediation before human approval",
                "pricing": {
                    "amount": "0",
                    "currency": "free",
                },
            },
        ],
        "payment": {
            "scheme": "x402",
            "network": "eip155:8453",
            "asset": "USDC",
            "asset_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "payTo": "0x60c402878EfcEcAe5733A88075328Aa2320C39BE",
        },
        "workflow": {
            "recommended_flow": [
                {
                    "step": 1,
                    "endpoint": "POST /api/remediation/verify",
                    "pricing": "free",
                    "description": "Verify AI-generated remediation before routing to approval",
                },
                {
                    "step": 2,
                    "endpoint": "POST /api/approval-unit/build",
                    "pricing": "0.05 USDC",
                    "description": "Build human decision contract from verified output",
                },
            ]
        },
        "metadata": {
            "a2a_compatible": True,
            "version": "0.1.0",
            "openapi_docs": f"{base_url}/docs",
            "openapi_json": f"{base_url}/openapi.json",
            "x402_discovery": f"{base_url}/.well-known/x402",
            "llms_txt": f"{base_url}/llms.txt",
        },
    }

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
    ("POST", "/api/approval-unit/build"):         "0.05",
    ("POST", "/api/payment-evidence/check"):      "0.03",
    ("POST", "/api/counterparty-invoice/check"):  "0.02",
}

_ENDPOINT_DESCRIPTIONS = {
    "/api/approval-unit/build": (
        "Build a minimal human decision contract from AI-generated findings, patches, "
        "payment requests, or decision-support outputs."
    ),
    "/api/payment-evidence/check": (
        "Verify that an AI-agent payment produced the expected service response and audit evidence."
    ),
    "/api/counterparty-invoice/check": (
        "Verify counterparty name, invoice registration number, and corporate number "
        "before AI-agent payment. Format check and name match only. No tax or legal advice."
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


# CDP Bazaar indexing extension for payment-evidence/check
_BAZAAR_EXTENSIONS_EVIDENCE = {
    "bazaar": {
        "discoverable": True,
        "info": {
            "input": {
                "type": "http",
                "method": "POST",
                "bodyType": "json",
                "body": {
                    "payment_reference": "pay_123",
                    "payment_asset": "USDC",
                    "amount": "0.03",
                    "paid_endpoint": "/api/example",
                    "service_response_received": True,
                    "delivery_status": "delivered",
                    "evidence_ids": ["ev_001"],
                },
            },
            "output": {
                "type": "json",
                "example": {
                    "payment_evidence_status": "ok",
                    "payment_response_matched": True,
                    "audit_ready": True,
                    "requires_human_review": False,
                    "recommended_next_step": "store_evidence",
                },
            },
        },
        "schema": {
            "type": "object",
            "properties": {
                "payment_evidence_status": {"type": "string"},
                "payment_response_matched": {"type": "boolean"},
                "audit_ready": {"type": "boolean"},
                "requires_human_review": {"type": "boolean"},
                "recommended_next_step": {"type": "string"},
            },
        },
    }
}


# CDP Bazaar indexing extension for counterparty-invoice/check
_BAZAAR_EXTENSIONS_COUNTERPARTY = {
    "bazaar": {
        "discoverable": True,
        "info": {
            "input": {
                "type": "http",
                "method": "POST",
                "bodyType": "json",
                "body": {
                    "counterparty_name": "Example Vendor Inc.",
                    "invoice_registration_number": "T1234567890123",
                    "corporate_number": "1234567890123",
                    "wallet_address": "0x0000000000000000000000000000000000000000",
                    "api_provider_name": "Example Vendor Inc.",
                    "payment_purpose": "AI API usage fee",
                    "payment_asset": "USDC",
                    "amount": "0.02",
                },
            },
            "output": {
                "type": "json",
                "example": {
                    "counterparty_check_status": "ok",
                    "invoice_number_format_valid": True,
                    "corporate_number_format_valid": True,
                    "name_match_status": "match",
                    "wallet_match_status": "format_valid",
                    "requires_human_review": False,
                    "recommended_next_step": "proceed_to_payment",
                },
            },
        },
        "schema": {
            "type": "object",
            "properties": {
                "counterparty_check_status": {"type": "string"},
                "invoice_number_format_valid": {"type": "boolean"},
                "corporate_number_format_valid": {"type": "boolean"},
                "name_match_status": {"type": "string"},
                "wallet_match_status": {"type": "string"},
                "requires_human_review": {"type": "boolean"},
                "recommended_next_step": {"type": "string"},
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
            elif path == "/api/payment-evidence/check":
                _pc["extensions"] = _BAZAAR_EXTENSIONS_EVIDENCE
                _pc["payment_evidence_status"] = None
                _pc["audit_ready"] = False
                _pc["next_recommended"] = "complete_x402_payment"
            elif path == "/api/counterparty-invoice/check":
                _pc["extensions"] = _BAZAAR_EXTENSIONS_COUNTERPARTY
                _pc["counterparty_check_status"] = None
                _pc["requires_human_review"] = True
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

# ─────────────────────────────────────────────
# JP Payment Evidence Guard v0.1 — models
# ─────────────────────────────────────────────

class PaymentEvidenceCheckRequest(BaseModel):
    payment_reference: Optional[str] = None
    payment_asset: Optional[str] = None
    amount: Optional[str] = None
    paid_endpoint: Optional[str] = None
    expected_service_response: Optional[Dict[str, Any]] = None
    actual_service_response: Optional[Dict[str, Any]] = None
    delivery_status: Optional[str] = None
    evidence_ids: List[str] = []
    transaction_reference: Optional[str] = None
    service_response_received: bool = False
    payer_agent_id: Optional[str] = None
    request_id: Optional[str] = None
    task_id: Optional[str] = None


class PaymentEvidenceCheckResponse(BaseModel):
    payment_evidence_status: str
    service_response_received: bool
    payment_response_matched: bool
    missing_items: List[str]
    mismatch_items: List[str]
    audit_ready: bool
    requires_human_review: bool
    recommended_next_step: str
    request_id: Optional[str]
    task_id: Optional[str]
    created_at: str


class CounterpartyInvoiceCheckRequest(BaseModel):
    counterparty_name: str
    invoice_registration_number: Optional[str] = None
    corporate_number: Optional[str] = None
    wallet_address: Optional[str] = None
    api_provider_name: Optional[str] = None
    payment_purpose: Optional[str] = None
    declared_invoice_status: Optional[str] = None
    billing_country: Optional[str] = None
    payment_asset: Optional[str] = None
    amount: Optional[str] = None
    transaction_reference: Optional[str] = None
    evidence_ids: List[str] = []
    request_id: Optional[str] = None
    task_id: Optional[str] = None


class CounterpartyInvoiceCheckResponse(BaseModel):
    counterparty_check_status: str
    invoice_number_format_valid: bool
    corporate_number_format_valid: bool
    name_match_status: str
    wallet_match_status: str
    requires_human_review: bool
    recommended_next_step: str
    missing_items: List[str]
    audit_ready: bool
    request_id: Optional[str]
    task_id: Optional[str]
    created_at: str


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


# ─────────────────────────────────────────────
# JP Payment Evidence Guard v0.1 — rule-based logic
# ─────────────────────────────────────────────

def _pe_check_missing(req: PaymentEvidenceCheckRequest) -> List[str]:
    missing = []
    if not req.payment_reference:
        missing.append("payment_reference")
    if not req.payment_asset:
        missing.append("payment_asset")
    if not req.amount:
        missing.append("amount")
    if not req.paid_endpoint:
        missing.append("paid_endpoint")
    if not req.transaction_reference:
        missing.append("transaction_reference")
    if req.actual_service_response is None:
        missing.append("actual_service_response")
    if not req.evidence_ids:
        missing.append("evidence_ids")
    return missing


def _pe_check_mismatch(req: PaymentEvidenceCheckRequest) -> List[str]:
    mismatches = []
    if not (req.expected_service_response and req.actual_service_response):
        return mismatches
    expected_status = req.expected_service_response.get("status")
    actual_status = req.actual_service_response.get("status")
    if expected_status and actual_status and expected_status != actual_status:
        mismatches.append("service_response_status_mismatch")
    for field in req.expected_service_response.get("required_fields", []):
        if field not in req.actual_service_response:
            mismatches.append(f"missing_required_field_{field}")
    return mismatches


def _pe_determine_status(
    missing: List[str],
    mismatches: List[str],
    req: PaymentEvidenceCheckRequest,
) -> str:
    if mismatches:
        return "mismatch"
    if missing or not req.service_response_received:
        return "incomplete"
    return "ok"


def _pe_recommended_next_step(status: str) -> str:
    return {
        "ok":              "store_evidence",
        "incomplete":      "collect_missing_evidence",
        "mismatch":        "review_mismatch",
        "requires_review": "escalate_to_human",
    }.get(status, "escalate_to_human")


# ─────────────────────────────────────────────
# JP Counterparty / Invoice Check v0.1 — rule-based logic
# ─────────────────────────────────────────────

import re as _re


def _ci_check_invoice_format(invoice_number: Optional[str]) -> bool:
    """T + 13桁数字の形式確認のみ。リアルタイム照合なし。"""
    if not invoice_number:
        return False
    return bool(_re.match(r"^T\d{13}$", invoice_number))


def _ci_check_corporate_format(corporate_number: Optional[str]) -> bool:
    """13桁数字の形式確認のみ。リアルタイム照合なし。"""
    if not corporate_number:
        return False
    return bool(_re.match(r"^\d{13}$", corporate_number))


def _ci_check_name_match(counterparty_name: str, api_provider_name: Optional[str]) -> str:
    """文字列比較のみ。外部照合なし。"""
    if not api_provider_name:
        return "not_provided"
    if counterparty_name == api_provider_name:
        return "match"
    if (counterparty_name.lower() in api_provider_name.lower()
            or api_provider_name.lower() in counterparty_name.lower()):
        return "partial_match"
    return "no_match"


def _ci_check_wallet(wallet_address: Optional[str]) -> str:
    """EVM アドレス形式確認のみ。オンチェーン照合なし。"""
    if not wallet_address:
        return "not_provided"
    if _re.match(r"^0x[0-9a-fA-F]{40}$", wallet_address):
        return "format_valid"
    return "format_invalid"


def _ci_check_missing(req: CounterpartyInvoiceCheckRequest) -> List[str]:
    missing = []
    if not req.invoice_registration_number:
        missing.append("invoice_registration_number")
    if not req.corporate_number:
        missing.append("corporate_number")
    if not req.api_provider_name:
        missing.append("api_provider_name")
    if not req.payment_purpose:
        missing.append("payment_purpose")
    return missing


def _ci_determine_status(
    invoice_valid: bool,
    corporate_valid: bool,
    name_match: str,
    wallet_match: str,
    missing: List[str],
) -> str:
    """counterparty_check_status の判定。"""
    format_errors = sum([
        not invoice_valid,
        not corporate_valid,
        wallet_match == "format_invalid",
    ])
    if format_errors >= 2:
        return "invalid"
    if name_match == "no_match":
        return "requires_review"
    if not invoice_valid or not corporate_valid or missing or name_match in ("partial_match", "not_provided"):
        return "requires_review"
    return "ok"


def _ci_recommended_next_step(status: str) -> str:
    return {
        "ok":              "proceed_to_payment",
        "requires_review": "verify_counterparty_before_payment",
        "invalid":         "block_and_escalate",
    }.get(status, "escalate_to_human")


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


# ─────────────────────────────────────────────
# JP Payment Evidence Guard v0.1 — endpoint
# ─────────────────────────────────────────────

@app.post("/api/payment-evidence/check", response_model=PaymentEvidenceCheckResponse)
async def check_payment_evidence(req: PaymentEvidenceCheckRequest, request: Request):
    """
    Verify that an AI-agent payment produced the expected service response and audit evidence.

    v0.1: rule-based verification only.
    Does not execute payments, act as a facilitator, make tax or legal decisions,
    guarantee output correctness, or store confidential content.
    Stateless — no database writes.
    """
    if not TEST_MODE:
        payment_header = (
            request.headers.get("PAYMENT-SIGNATURE") or request.headers.get("X-PAYMENT")
        )
        is_valid = await payment_verifier.verify_payment(payment_header, WALLET_ADDRESS, "0.03")
        if not is_valid:
            raise HTTPException(status_code=402, detail="Payment verification failed")

    missing = _pe_check_missing(req)
    mismatches = _pe_check_mismatch(req)
    status = _pe_determine_status(missing, mismatches, req)
    payment_response_matched = (len(mismatches) == 0 and req.service_response_received)
    audit_ready = (status == "ok")
    requires_human_review = (status != "ok")
    recommended_next_step = _pe_recommended_next_step(status)

    return PaymentEvidenceCheckResponse(
        payment_evidence_status=status,
        service_response_received=req.service_response_received,
        payment_response_matched=payment_response_matched,
        missing_items=missing,
        mismatch_items=mismatches,
        audit_ready=audit_ready,
        requires_human_review=requires_human_review,
        recommended_next_step=recommended_next_step,
        request_id=req.request_id,
        task_id=req.task_id,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


# ─────────────────────────────────────────────
# JP Counterparty / Invoice Check v0.1 — endpoint
# ─────────────────────────────────────────────

@app.post("/api/counterparty-invoice/check", response_model=CounterpartyInvoiceCheckResponse)
async def check_counterparty_invoice(req: CounterpartyInvoiceCheckRequest, request: Request):
    """
    Verify counterparty name, invoice registration number, and corporate number
    before AI-agent payment execution.

    v0.1: format check and name match only. No external API calls.
    Does not provide tax or legal advice.
    Does not determine eligibility for input tax credit (仕入税額控除).
    Does not perform credit checks on counterparties.
    Stateless — no database writes.
    """
    if not TEST_MODE:
        payment_header = (
            request.headers.get("PAYMENT-SIGNATURE") or request.headers.get("X-PAYMENT")
        )
        is_valid = await payment_verifier.verify_payment(payment_header, WALLET_ADDRESS, "0.02")
        if not is_valid:
            raise HTTPException(status_code=402, detail="Payment verification failed")

    invoice_valid = _ci_check_invoice_format(req.invoice_registration_number)
    corporate_valid = _ci_check_corporate_format(req.corporate_number)
    name_match = _ci_check_name_match(req.counterparty_name, req.api_provider_name)
    wallet_match = _ci_check_wallet(req.wallet_address)
    missing = _ci_check_missing(req)
    status = _ci_determine_status(invoice_valid, corporate_valid, name_match, wallet_match, missing)
    requires_human_review = (status != "ok")
    audit_ready = (status == "ok")
    recommended_next_step = _ci_recommended_next_step(status)

    return CounterpartyInvoiceCheckResponse(
        counterparty_check_status=status,
        invoice_number_format_valid=invoice_valid,
        corporate_number_format_valid=corporate_valid,
        name_match_status=name_match,
        wallet_match_status=wallet_match,
        requires_human_review=requires_human_review,
        recommended_next_step=recommended_next_step,
        missing_items=missing,
        audit_ready=audit_ready,
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
            "POST /api/approval-unit/build":        "Build an Approval Unit (human decision contract) — 0.05 USDC",
            "POST /api/remediation/verify":         "Verify AI remediation before approval (free)",
            "POST /api/payment-evidence/check":     "Verify payment evidence and audit readiness — 0.03 USDC",
            "POST /api/counterparty-invoice/check": "Verify counterparty and invoice info before payment — 0.02 USDC",
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
            },
            {
                "x402Version": 2,
                "type": "http",
                "resource": f"{base_url}/api/payment-evidence/check",
                "accepts": [
                    {
                        "scheme": "exact",
                        "network": "eip155:8453",
                        "amount": str(round(0.03 * 1_000_000)),
                        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                        "payTo": WALLET_ADDRESS,
                        "maxTimeoutSeconds": 300,
                        "extra": {"name": "USD Coin", "version": "2"},
                    }
                ],
                "extensions": _BAZAAR_EXTENSIONS_EVIDENCE,
            },
            {
                "x402Version": 2,
                "type": "http",
                "resource": f"{base_url}/api/counterparty-invoice/check",
                "accepts": [
                    {
                        "scheme": "exact",
                        "network": "eip155:8453",
                        "amount": str(round(0.02 * 1_000_000)),
                        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                        "payTo": WALLET_ADDRESS,
                        "maxTimeoutSeconds": 300,
                        "extra": {"name": "USD Coin", "version": "2"},
                    }
                ],
                "extensions": _BAZAAR_EXTENSIONS_COUNTERPARTY,
            },
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

POST /api/approval-unit/build        — Build a human decision contract (0.05 USDC)
POST /api/remediation/verify         — Verify AI remediation before approval (free)
POST /api/payment-evidence/check     — Verify payment evidence and audit readiness (0.03 USDC)
POST /api/counterparty-invoice/check — Verify counterparty and invoice info before payment (0.02 USDC)

## Additional Resources

OpenAPI Docs: https://ai-agent-payment-safety-stack.onrender.com/docs
OpenAPI JSON: https://ai-agent-payment-safety-stack.onrender.com/openapi.json
Health Check: https://ai-agent-payment-safety-stack.onrender.com/health
x402 Discovery: https://ai-agent-payment-safety-stack.onrender.com/.well-known/x402

## Pricing

approval-unit/build:        0.05 USDC per call
remediation/verify:         Free
payment-evidence/check:     0.03 USDC per call
counterparty-invoice/check: 0.02 USDC per call

## Payment

x402 scheme on Base (eip155:8453)
USDC payments to 0x60c402878EfcEcAe5733A88075328Aa2320C39BE

## Recommended Flow

POST /api/counterparty-invoice/check (0.02 USDC) → POST /api/approval-unit/build (0.05 USDC)
POST /api/remediation/verify (free) → POST /api/approval-unit/build (0.05 USDC)
payment execution → POST /api/payment-evidence/check (0.03 USDC) → store evidence

## Use Cases

- Security patch approval
- Payment request approval
- Deployment proposal approval
- Memory write approval
- Tool execution approval
- Post-payment evidence verification (JP compliance, x402/JPYC/USDC)

## Live JP Payment Evidence Guard API

Endpoint:
https://ai-agent-payment-safety-stack.onrender.com/api/payment-evidence/check

Price:
0.03 USDC / check

Use this API after completing a payment via x402, JPYC, or USDC, and after receiving the service response.
Verifies that the payment and service response correspond, and classifies audit readiness.

Does NOT:
- execute payments
- act as a facilitator
- make legal or tax decisions
- guarantee output correctness
- store confidential content

Output:
- payment_evidence_status: ok / incomplete / mismatch / requires_review
- payment_response_matched: true if payment and response correspond
- service_response_received: true if service responded
- missing_items: list of missing evidence fields
- mismatch_items: list of mismatched fields
- audit_ready: true if evidence is complete and matched
- requires_human_review: true if human review is needed
- recommended_next_step: store_evidence / collect_missing_evidence / review_mismatch / escalate_to_human

## Live JP Counterparty / Invoice Check API

Endpoint:
https://ai-agent-payment-safety-stack.onrender.com/api/counterparty-invoice/check

Price:
0.02 USDC / check

Use this API before initiating a payment to a JP counterparty.
Verifies invoice registration number format, corporate number format, counterparty name match,
and wallet address format. Format check and local match only.

Does NOT:
- connect to National Tax Agency API (国税庁API)
- connect to corporate number API (法人番号API)
- provide tax or legal advice
- determine eligibility for input tax credit (仕入税額控除)
- perform credit checks on counterparties
- guarantee invoice validity or completeness

Output:
- counterparty_check_status: ok / requires_review / invalid
- invoice_number_format_valid: true if T + 13 digits
- corporate_number_format_valid: true if 13 digits
- name_match_status: match / partial_match / no_match / not_provided
- wallet_match_status: format_valid / format_invalid / not_provided
- requires_human_review: true unless all checks pass
- recommended_next_step: proceed_to_payment / verify_counterparty_before_payment / block_and_escalate
- missing_items: list of missing fields
- audit_ready: true only when status is ok

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

### 1. Incomplete Remediation Example

This example shows a remediation that needs additional verification before approval.

POST /api/remediation/verify

Example request (missing security_retest_results):
{
  "remediation_id": "remediation_001",
  "source_type": "security_patch",
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
- decision: require_security_retest
- approval_unit_ready: false
- verification_status: incomplete
- next_step: add security_retest_results and regression_test_results before approval unit generation

### 2. Approval-ready Remediation Example

This example shows a complete remediation that is ready for approval unit generation.

POST /api/remediation/verify

Example request (complete with all test results):
{
  "remediation_id": "remediation_001",
  "source_type": "security_patch",
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
  "security_retest_results": ["security_retest_passed"],
  "regression_test_results": ["regression_passed"],
  "staging_tested": true,
  "rollback_available": true,
  "production_deploy_requested": false
}

Expected result:
- decision: route_to_approval_unit_builder
- approval_unit_ready: true
- recommended_human_action: approve_staging_only
- blocked_next_steps includes deploy_to_production

### 3. Approval Unit Build Example

Use this after successful remediation verification to convert the verified proposal into a human decision contract.

POST /api/approval-unit/build (x402 payment required: 0.05 USDC)

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

Expected result (after x402 payment):
- approval_question
- approval_unit_hash
- recommended_human_action
- allowed_actions limited to staging scope
- still_blocked_actions includes deploy_to_production
"""
    return PlainTextResponse(content)


@app.get("/skill.md", include_in_schema=False)
async def skill_md():
    from fastapi.responses import PlainTextResponse

    content = """# Skill: Remediation Verification Gate

## Purpose

Use this skill to verify an AI-generated remediation candidate before routing it to human review or Approval Unit Builder.

This Gate checks whether a finding, patch, remediation plan, configuration change, dependency update, or deployment proposal is ready for human approval.

## When to use

Use this skill when:
- an AI agent has generated a security finding, patch candidate, or remediation plan
- you need to verify test results, security retest status, rollback readiness, and production risk before human review
- you want to determine if a remediation candidate is `approval_unit_ready`
- you need to block a production deploy for high/critical risk candidates
- you want to route the candidate to the correct next step (research / rework / human review / approval unit)

## When not to use

Do not use this skill to:
- apply patches or code changes
- deploy infrastructure
- execute approvals or rejections
- process x402 / JPYC / USDC payments
- write to memory
- execute tool calls
- send blockchain transactions

## Main endpoint

POST https://ai-agent-payment-safety-stack.onrender.com/api/remediation/verify

## Required inputs

- `remediation_id` — unique ID for this remediation candidate
- `source_type` — type of the source (e.g. security_patch)
- `remediation_type` — one of: patch_candidate, remediation_plan, configuration_change, dependency_update, deployment_proposal
- `title` — short title
- `finding_summary` — what was found
- `remediation_summary` — what the agent proposes
- `severity` — low / medium / high / critical
- `risk_level` — low / medium / high / critical

## Recommended inputs

- `evidence_ids` — list of evidence or finding IDs
- `source_ids` — list of source references
- `test_results` — list of test outcomes
- `security_retest_results` — list of security retest outcomes
- `regression_test_results` — list of regression test outcomes
- `rollback_plan_id` — ID of the rollback plan
- `rollback_available` — whether rollback is available
- `production_deploy_requested` — whether production deploy is being requested
- `request_id` / `task_id` / `generated_by_agent_id` — for traceability

## Output

The API returns a Remediation Verification Result containing:
- `decision` — route_to_approval_unit_builder / require_more_evidence / require_security_retest / require_rollback_plan / block_production_deploy / pass_with_warnings
- `verification_status` — verified / verified_with_warnings / blocked / incomplete
- `readiness_level` — human_approval_ready / needs_more_evidence / needs_testing / needs_rollback_plan / needs_review
- `evidence_status` / `test_status` / `security_retest_status` / `regression_status` / `rollback_status` — individual check results
- `production_risk` — not_requested / requires_review / blocked
- `allowed_next_steps` / `blocked_next_steps` — what can and cannot proceed
- `recommended_human_action` — single recommended action
- `approval_unit_ready` — true if ready to pass to Approval Unit Builder
- `approval_unit_type_suggestion` — suggested approval unit type for Approval Unit Builder
- `blocked_actions_until_approval` — always includes merge_to_staging and deploy_to_production

## v0.1 constraints

- Rule-based verification only. No LLM-generated output.
- No patch application, deployment, approval execution, or payment.
- No memory write, tool execution, or blockchain transaction.
- `blockchain_anchor_ready = true` (readiness flag only).
- `audit_required = true`.

## Remediation Verification Gate live endpoint

POST https://ai-agent-payment-safety-stack.onrender.com/api/remediation/verify

Use before:
POST https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build

When approval_unit_ready = true, the agent may route the result to Approval Unit Builder to create a human decision contract.

## Next step: Approval Unit Builder

If `approval_unit_ready = true`, call Approval Unit Builder next:

POST https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build

Pass the remediation candidate fields as the Approval Unit input to create a minimal human decision contract.

## Safety chain position

```
AI Agent generates remediation candidate
  ↓
Remediation Verification Gate  ← this skill
  ↓ (if approval_unit_ready = true)
Approval Unit Builder
  ↓
Human Approver
  ↓
Audit Log / Agent Memory
```

---

# Skill: Approval Unit Builder

## Purpose

Use this skill to build a minimal human decision contract (Approval Unit) from an
AI-generated finding, patch, payment request, deployment proposal, memory write request,
tool execution request, or decision-support output.

**Core concept: Approval Unit = Human Decision Contract**

## When to use

Use this skill when:
- a human approval is required before proceeding
- a Gate Result Router output needs to be converted to an approval unit
- a Human Review Bridge task needs to become a structured approval decision
- an AI-generated security patch needs approval before merge or deployment
- an x402 / JPYC / USDC payment request needs human approval
- a decision card needs approval before decision use
- a memory write candidate needs approval
- a high-risk tool execution request needs approval
- you need a stable approval_unit_hash for audit records

## When not to use

Do not use this skill to:
- approve or reject automatically
- execute payments (x402 / JPYC / USDC)
- deploy code or infrastructure changes
- write to agent memory
- execute tool calls
- send blockchain transactions
- validate evidence directly (use Evidence Coverage Gate instead)
- check budgets (use Agent Budget Guard Interceptor instead)

## Live endpoint

POST https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build

## Pricing

0.05 USDC / call

## x402 status

- Seller Tools: Implementation Looks Correct ✅
- verify + settle confirmed ✅
- CDP Bazaar automatic indexing in progress

## Minimum required inputs

- `source_type` — type of the source (e.g. security_patch, payment_request)
- `approval_unit_type` — one of the 10 approval unit types
- `title` — short title for the approval unit
- `summary` — what the AI agent wants approved
- `risk_level` — low / medium / high / critical

## Recommended inputs

- `evidence_ids` — list of evidence or finding IDs
- `source_ids` — list of source references
- `test_results` — list of test outcomes
- `blocked_actions_until_approval` — actions blocked until a human approves
- `rollback_available` — whether rollback is available
- `approver_role` — who should approve (e.g. security_reviewer, approver)
- `request_id` / `task_id` / `agent_id` — for traceability

## Supported approval_unit_type values

| Type | Use case |
|---|---|
| security_patch_approval | AI-generated security patch |
| remediation_plan_approval | Remediation plan before implementation |
| payment_approval | x402 / JPYC / USDC payment |
| deployment_approval | Deploy, merge, or release |
| decision_card_approval | Report or memo for decision use |
| legal_review_approval | Legal or compliance-sensitive output |
| financial_review_approval | Financial decision-support output |
| evidence_exception_approval | Proceed despite incomplete evidence |
| memory_write_approval | Write to sensitive or long-term memory |
| tool_execution_approval | High-risk tool call |

## Output

The API returns an Approval Unit containing:
- `approval_unit_id` — unique ID for this unit
- `approval_unit_hash` — SHA-256 hash of canonical fields (stable across runs)
- `approval_question` — rule-based question defining what the human is approving
- `decision_options` — approve / reject / request_rework / request_more_evidence / defer / escalate
- `suggested_human_actions` — list of suggested next actions for the human
- `recommended_human_action` — single recommended action (rule-based)
- `human_action_reason` — reason for the recommendation
- `if_approved` — allowed_actions, still_blocked_actions, post_decision_route
- `if_rejected` — blocked_actions, post_decision_route
- `if_request_rework` — post_decision_route, required_changes
- `if_request_more_evidence` — post_decision_route, required_evidence
- `if_escalated` — post_decision_route, required_context
- `chain_anchor_status` — always `not_anchored` in v0.1 (readiness only)

## v0.1 constraints

- Build only. No approval execution.
- `approval_question` is generated by rule-based templates, not LLM.
- `approval_unit_hash` is stable: same inputs produce same hash.
- `chain_anchor_status = not_anchored` (no blockchain in v0.1).
- No x402 / JPYC payment is sent.
- No memory write is performed.
- No tool execution is performed.

## Important

This skill creates an Approval Unit only.
It does not execute approval, payment, deployment, memory write, tool execution, or blockchain anchoring.

## Safety chain position

```
Gate Result Router
  ↓
Human Review Bridge
  ↓
Approval Unit Builder  ← this skill
  ↓
Human Approver
  ↓
Audit Log / Agent Memory
```

---

# Skill: JP Payment Evidence Guard

## Purpose

Use this skill to verify that an AI-agent payment (x402/JPYC/USDC) produced the expected service response and maintains audit-ready evidence.

v0.1 is verification-only. No payment execution, facilitation, legal or tax decisions.

## When to use

Use this skill when:
- a payment via x402, JPYC, or USDC has been executed
- a service response has been received
- you need to confirm the payment and response correspond
- you need to classify evidence as audit-ready before storing or passing to next agent
- Japanese compliance audit trail is required

## When not to use

Do not use this skill to:
- authorize or execute payments (use agent-budget-guard instead)
- make legal compliance decisions
- make tax decisions
- validate invoice correctness
- guarantee service output quality
- replace human review in high-risk domains

## Live endpoint

POST https://ai-agent-payment-safety-stack.onrender.com/api/payment-evidence/check

## Pricing

0.03 USDC / call

## Minimum required inputs

- `payment_reference` — unique reference for the payment
- `payment_asset` — asset used (USDC / JPYC / JPY)
- `amount` — payment amount as string
- `paid_endpoint` — the API endpoint that was paid for
- `transaction_reference` — on-chain or protocol transaction reference
- `service_response_received` — whether the service responded (boolean)
- `actual_service_response` — the response received from the service

## Optional inputs

- `expected_service_response` — expected status and required fields for mismatch detection
- `delivery_status` — delivered / failed / pending
- `evidence_ids` — list of existing evidence IDs
- `payer_agent_id` — ID of the paying agent
- `request_id` / `task_id` — for traceability

## Output

The API returns a Payment Evidence Check Result:
- `payment_evidence_status` — ok / incomplete / mismatch / requires_review
- `payment_response_matched` — true if payment and response correspond without mismatch
- `service_response_received` — echoed from input
- `missing_items` — list of missing required fields
- `mismatch_items` — list of fields where expected and actual diverge
- `audit_ready` — true only when status is ok
- `requires_human_review` — true for incomplete / mismatch / requires_review
- `recommended_next_step` — store_evidence / collect_missing_evidence / review_mismatch / escalate_to_human

## Status values

| Status | Meaning |
|---|---|
| ok | All fields present, response received, no mismatch |
| incomplete | One or more required fields missing or service_response_received = false |
| mismatch | Expected and actual service response differ |
| requires_review | High risk or undecidable — escalate to human |

## v0.1 constraints

- Rule-based verification only. No LLM-generated output.
- No payment execution.
- Not a payment facilitator.
- No tax or legal decisions.
- No invoice correctness guarantee.
- No service quality guarantee.
- Stateless — no database writes.
- Does not store confidential content.

## Safety chain position

```
Payment execution (x402 / JPYC / USDC)
  ↓
JP Payment Evidence Guard  ← this skill
  ↓ (if audit_ready = true)
Agent Memory API (evidence storage)
  ↓
JP Monthly Evidence Pack (monthly audit bundle)
```

---

# Skill: JP Counterparty / Invoice Check

## Purpose

Use this skill to verify counterparty name, invoice registration number, corporate number,
and wallet address format before initiating a payment to a JP counterparty.

v0.1 is format check and local match only. No external API calls.

## When to use

Use this skill when:
- about to send a payment to a JP counterparty via x402, JPYC, or USDC
- the counterparty provides an invoice registration number (T + 13 digits)
- the counterparty provides a corporate number (13 digits)
- you need to check that counterparty_name and api_provider_name match
- you need to verify wallet address format (EVM 0x + 40 hex)
- you need to determine if human review is required before payment

## When not to use

Do not use this skill to:
- verify real-time invoice registration status with National Tax Agency
- check corporate number against government registry
- determine eligibility for input tax credit (仕入税額控除)
- perform credit checks on counterparties
- make tax or legal decisions
- guarantee invoice completeness

## Live endpoint

POST https://ai-agent-payment-safety-stack.onrender.com/api/counterparty-invoice/check

## Pricing

0.02 USDC / call

## Required inputs

- `counterparty_name` — name of the counterparty

## Recommended inputs

- `invoice_registration_number` — JP invoice registration number (T + 13 digits)
- `corporate_number` — JP corporate number (13 digits)
- `api_provider_name` — name used by the API provider or billing entity
- `payment_purpose` — purpose of the payment
- `wallet_address` — EVM wallet address (optional)
- `declared_invoice_status` — declared status (registered / not_registered / unknown)
- `billing_country` — billing country (JP for Japan)
- `payment_asset` — asset to be used (USDC / JPYC)
- `amount` — payment amount as string
- `request_id` / `task_id` — for traceability

## Output

The API returns a Counterparty Invoice Check Result:
- `counterparty_check_status` — ok / requires_review / invalid
- `invoice_number_format_valid` — true if T + 13 digits
- `corporate_number_format_valid` — true if 13 digits
- `name_match_status` — match / partial_match / no_match / not_provided
- `wallet_match_status` — format_valid / format_invalid / not_provided
- `requires_human_review` — true unless all checks pass
- `recommended_next_step` — proceed_to_payment / verify_counterparty_before_payment / block_and_escalate
- `missing_items` — list of missing recommended fields
- `audit_ready` — true only when status is ok

## Status values

| Status | Meaning |
|---|---|
| ok | All format checks pass, names match, no missing items |
| requires_review | Some checks incomplete or partial match |
| invalid | Two or more format errors detected |

## v0.1 constraints

- Format check and local match only. No external API calls.
- No National Tax Agency API connection (国税庁API).
- No corporate number API connection (法人番号API).
- No tax or legal advice.
- No input tax credit (仕入税額控除) determination.
- No credit checks.
- No invoice completeness guarantee.
- Stateless — no database writes.

## Safety chain position

```
Counterparty provides invoice and corporate info
  ↓
JP Counterparty / Invoice Check  ← this skill
  ↓ (if counterparty_check_status = ok)
Payment execution (x402 / JPYC / USDC)
  ↓
JP Payment Evidence Guard
  ↓
Agent Memory API (evidence storage)
```
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
            {
                "method": "POST",
                "path": "/api/payment-evidence/check",
                "description": "Verify that an AI-agent payment produced the expected service response and audit evidence",
                "pricing": {
                    "amount": "0.03",
                    "currency": "USDC",
                },
            },
            {
                "method": "POST",
                "path": "/api/counterparty-invoice/check",
                "description": "Verify counterparty name, invoice registration number, and corporate number before AI-agent payment. Format check and name match only. No tax or legal advice.",
                "pricing": {
                    "amount": "0.02",
                    "currency": "USDC",
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
        "use_cases": [
            "multi_agent_governance",
            "human_approval_boundary",
            "ai_generated_remediation_review",
            "x402_payment_governance",
            "a2a_workflow_guard",
            "post_payment_evidence_verification",
            "jp_compliance_audit_readiness",
            "jp_counterparty_verification_before_payment",
            "jp_invoice_format_check",
        ],
        "constraints": {
            "build_only": True,
            "does_not_execute_approval": True,
            "does_not_deploy_to_production": True,
            "does_not_execute_payments_directly": True,
            "does_not_replace_human_review_in_high_risk_workflows": True
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

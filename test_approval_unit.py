"""
Basic tests for Agent Approval Unit Builder API v0.1

Run: pip install pytest httpx && pytest test_approval_unit.py -v
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

EXAMPLE_REQUEST = {
    "source_type": "security_patch",
    "approval_unit_type": "security_patch_approval",
    "finding_id": "finding_001",
    "patch_id": "patch_001",
    "title": "Approve patch for SQL injection in user API",
    "summary": "Replace raw SQL interpolation with parameterized query.",
    "risk_level": "high",
    "severity": "critical",
    "evidence_ids": ["mythos_finding_001", "codeql_001"],
    "source_ids": ["repo:user-api", "scanner:codeql"],
    "test_results": ["unit_passed", "integration_passed", "security_retest_passed"],
    "regression_risk": "medium",
    "rollback_available": True,
    "blocked_actions_until_approval": ["merge_to_staging", "deploy_to_production"],
    "allowed_human_actions": ["approve", "reject", "request_rework", "request_more_evidence", "escalate"],
    "approver_role": "security_reviewer",
    "request_id": "req_123",
    "task_id": "security_remediation_001",
    "agent_id": "agent_security_01",
}


def test_build_returns_200():
    res = client.post("/api/approval-unit/build", json=EXAMPLE_REQUEST)
    assert res.status_code == 200


def test_approval_unit_hash_present():
    res = client.post("/api/approval-unit/build", json=EXAMPLE_REQUEST)
    data = res.json()
    assert "approval_unit_hash" in data
    assert data["approval_unit_hash"].startswith("sha256:")


def test_hash_stability():
    """Same input must produce same hash regardless of created_at."""
    res1 = client.post("/api/approval-unit/build", json=EXAMPLE_REQUEST)
    res2 = client.post("/api/approval-unit/build", json=EXAMPLE_REQUEST)
    assert res1.json()["approval_unit_hash"] == res2.json()["approval_unit_hash"]


def test_security_patch_staging_production_split():
    """merge_to_staging → allowed, deploy_to_production → still_blocked."""
    res = client.post("/api/approval-unit/build", json=EXAMPLE_REQUEST)
    data = res.json()
    assert "merge_to_staging" in data["if_approved"]["allowed_actions"]
    assert "deploy_to_production" in data["if_approved"]["still_blocked_actions"]


def test_no_evidence_recommends_more_evidence():
    req = {**EXAMPLE_REQUEST, "evidence_ids": [], "source_ids": []}
    res = client.post("/api/approval-unit/build", json=req)
    data = res.json()
    assert data["recommended_human_action"] == "request_more_evidence"


def test_v01_chain_anchor_status():
    """v0.1 must return not_anchored with null chain_tx_hash."""
    res = client.post("/api/approval-unit/build", json=EXAMPLE_REQUEST)
    data = res.json()
    assert data["chain_anchor_status"] == "not_anchored"
    assert data["chain_tx_hash"] is None


def test_approval_question_template():
    """security_patch_approval + merge_to_staging → expected question."""
    res = client.post("/api/approval-unit/build", json=EXAMPLE_REQUEST)
    data = res.json()
    assert data["approval_question"] == "Approve this security patch for staging merge?"


def test_payment_approval_question():
    req = {
        **EXAMPLE_REQUEST,
        "approval_unit_type": "payment_approval",
        "blocked_actions_until_approval": ["send_x402_payment"],
    }
    res = client.post("/api/approval-unit/build", json=req)
    data = res.json()
    assert "payment" in data["approval_question"].lower()


def test_if_rejected_blocks_all():
    res = client.post("/api/approval-unit/build", json=EXAMPLE_REQUEST)
    data = res.json()
    assert "merge_to_staging" in data["if_rejected"]["blocked_actions"]
    assert "deploy_to_production" in data["if_rejected"]["blocked_actions"]


def test_if_rework_routes_to_rework():
    res = client.post("/api/approval-unit/build", json=EXAMPLE_REQUEST)
    data = res.json()
    assert data["if_request_rework"]["post_decision_route"] == "route_to_rework"


def test_if_more_evidence_routes_to_research():
    res = client.post("/api/approval-unit/build", json=EXAMPLE_REQUEST)
    data = res.json()
    assert data["if_request_more_evidence"]["post_decision_route"] == "route_to_research"

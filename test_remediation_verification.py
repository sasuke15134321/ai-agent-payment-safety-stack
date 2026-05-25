"""
Tests for Remediation Verification Gate API v0.1

Run: pytest test_remediation_verification.py -v
     pytest -v  (runs all tests including existing test_approval_unit.py)
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_SECURITY_PATCH = {
    "remediation_id": "remediation_001",
    "finding_id": "finding_001",
    "source_type": "security_patch",
    "remediation_type": "patch_candidate",
    "title": "SQL injection fix for user API",
    "finding_summary": "Potential SQL injection in user lookup endpoint.",
    "remediation_summary": "Replace raw SQL interpolation with parameterized query.",
    "patch_id": "patch_001",
    "patch_diff_id": "patch_diff_001",
    "affected_files": ["api/user.py"],
    "affected_services": ["user-api"],
    "affected_environment": "staging",
    "severity": "critical",
    "risk_level": "high",
    "exploitability": "high",
    "evidence_ids": ["mythos_finding_001", "codeql_001"],
    "source_ids": ["repo:user-api", "scanner:codeql"],
    "test_results": ["unit_passed", "integration_passed"],
    "security_retest_results": ["security_retest_passed"],
    "regression_test_results": ["regression_passed"],
    "rollback_plan_id": "rollback_001",
    "rollback_available": True,
    "blast_radius": "single_service",
    "production_impact": "none_if_staging_only",
    "staging_tested": True,
    "production_deploy_requested": False,
    "generated_by_agent_id": "agent_security_01",
    "request_id": "req_123",
    "task_id": "security_remediation_001",
}


def test_valid_security_patch_returns_200():
    res = client.post("/api/remediation/verify", json=VALID_SECURITY_PATCH)
    assert res.status_code == 200


def test_valid_security_patch_decision():
    res = client.post("/api/remediation/verify", json=VALID_SECURITY_PATCH)
    data = res.json()
    assert data["decision"] == "route_to_approval_unit_builder"


def test_approval_unit_ready():
    res = client.post("/api/remediation/verify", json=VALID_SECURITY_PATCH)
    data = res.json()
    assert data["approval_unit_ready"] is True


def test_recommended_human_action():
    res = client.post("/api/remediation/verify", json=VALID_SECURITY_PATCH)
    data = res.json()
    assert data["recommended_human_action"] == "approve_staging_only"


def test_deploy_to_production_blocked():
    res = client.post("/api/remediation/verify", json=VALID_SECURITY_PATCH)
    data = res.json()
    assert "deploy_to_production" in data["blocked_next_steps"]


def test_missing_evidence_returns_require_more_evidence():
    req = {**VALID_SECURITY_PATCH, "evidence_ids": [], "source_ids": []}
    res = client.post("/api/remediation/verify", json=req)
    data = res.json()
    assert data["decision"] == "require_more_evidence"


def test_missing_test_results_returns_require_security_retest():
    req = {**VALID_SECURITY_PATCH, "test_results": []}
    res = client.post("/api/remediation/verify", json=req)
    data = res.json()
    assert data["decision"] == "require_security_retest"


def test_missing_rollback_returns_require_rollback_plan():
    req = {**VALID_SECURITY_PATCH, "rollback_available": False, "rollback_plan_id": None}
    res = client.post("/api/remediation/verify", json=req)
    data = res.json()
    assert data["decision"] == "require_rollback_plan"


def test_production_deploy_high_risk_returns_block_production_deploy():
    req = {**VALID_SECURITY_PATCH, "production_deploy_requested": True}
    res = client.post("/api/remediation/verify", json=req)
    data = res.json()
    assert data["decision"] == "block_production_deploy"


def test_blockchain_anchor_ready():
    res = client.post("/api/remediation/verify", json=VALID_SECURITY_PATCH)
    data = res.json()
    assert data["blockchain_anchor_ready"] is True


def test_existing_approval_unit_builder_unaffected():
    """Existing Approval Unit Builder API must remain unaffected."""
    req = {
        "source_type": "security_patch",
        "approval_unit_type": "security_patch_approval",
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
        "approver_role": "security_reviewer",
    }
    res = client.post("/api/approval-unit/build", json=req)
    assert res.status_code == 200
    data = res.json()
    assert "approval_unit_hash" in data
    assert data["approval_unit_hash"].startswith("sha256:")

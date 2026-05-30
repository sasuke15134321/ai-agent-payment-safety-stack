"""
Tests for JP Payment Evidence Guard v0.1
POST /api/payment-evidence/check
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

FULL_OK_REQUEST = {
    "payment_reference": "pay_123",
    "payment_asset": "USDC",
    "amount": "0.03",
    "paid_endpoint": "/api/example",
    "expected_service_response": {"status": "ok", "required_fields": ["result"]},
    "actual_service_response": {"status": "ok", "result": "delivered"},
    "delivery_status": "delivered",
    "evidence_ids": ["ev_001"],
    "transaction_reference": "tx_abc",
    "service_response_received": True,
}


def test_ok_returns_200():
    res = client.post("/api/payment-evidence/check", json=FULL_OK_REQUEST)
    assert res.status_code == 200


def test_ok_status():
    res = client.post("/api/payment-evidence/check", json=FULL_OK_REQUEST)
    data = res.json()
    assert data["payment_evidence_status"] == "ok"
    assert data["audit_ready"] is True
    assert data["requires_human_review"] is False
    assert data["recommended_next_step"] == "store_evidence"
    assert data["payment_response_matched"] is True
    assert data["missing_items"] == []
    assert data["mismatch_items"] == []


def test_incomplete_when_fields_missing():
    res = client.post("/api/payment-evidence/check", json={
        "service_response_received": False,
    })
    data = res.json()
    assert data["payment_evidence_status"] == "incomplete"
    assert data["audit_ready"] is False
    assert data["requires_human_review"] is True
    assert data["recommended_next_step"] == "collect_missing_evidence"
    assert "payment_reference" in data["missing_items"]
    assert "transaction_reference" in data["missing_items"]
    assert "evidence_ids" in data["missing_items"]


def test_mismatch_on_response_status_mismatch():
    req = dict(FULL_OK_REQUEST)
    req["actual_service_response"] = {"status": "error"}
    res = client.post("/api/payment-evidence/check", json=req)
    data = res.json()
    assert data["payment_evidence_status"] == "mismatch"
    assert data["audit_ready"] is False
    assert data["requires_human_review"] is True
    assert data["recommended_next_step"] == "review_mismatch"
    assert "service_response_status_mismatch" in data["mismatch_items"]


def test_mismatch_on_missing_required_field():
    req = dict(FULL_OK_REQUEST)
    req["actual_service_response"] = {"status": "ok"}
    res = client.post("/api/payment-evidence/check", json=req)
    data = res.json()
    assert data["payment_evidence_status"] == "mismatch"
    assert "missing_required_field_result" in data["mismatch_items"]


def test_response_has_all_required_fields():
    res = client.post("/api/payment-evidence/check", json=FULL_OK_REQUEST)
    data = res.json()
    required = [
        "payment_evidence_status",
        "service_response_received",
        "payment_response_matched",
        "missing_items",
        "mismatch_items",
        "audit_ready",
        "requires_human_review",
        "recommended_next_step",
        "created_at",
    ]
    for field in required:
        assert field in data, f"Missing field: {field}"


def test_existing_approval_unit_build_unaffected():
    res = client.post("/api/approval-unit/build", json={
        "source_type": "security_patch",
        "approval_unit_type": "security_patch_approval",
        "title": "Test",
        "summary": "Test summary",
        "risk_level": "medium",
        "evidence_ids": ["ev_001"],
        "test_results": ["unit_passed"],
        "rollback_available": True,
        "blocked_actions_until_approval": ["merge_to_staging"],
    })
    assert res.status_code == 200
    data = res.json()
    assert "approval_unit_hash" in data
    assert data["approval_unit_hash"].startswith("sha256:")

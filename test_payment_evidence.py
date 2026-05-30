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


# ===== Real x402 Settlement Tests (using x402ClientSync) =====
if __name__ == "__main__":
    import os
    import sys
    from dotenv import load_dotenv

    load_dotenv()

    EVM_PRIVATE_KEY = os.getenv("EVM_PRIVATE_KEY")
    if not EVM_PRIVATE_KEY:
        print("[ERROR] EVM_PRIVATE_KEY is not set for real settlement test")
        sys.exit(1)

    from eth_account import Account
    from x402 import x402ClientSync
    from x402.mechanisms.evm.signers import EthAccountSigner
    from x402.mechanisms.evm.exact import register_exact_evm_client
    from x402.http.clients.requests import wrapRequestsWithPayment
    import requests
    import json

    account = Account.from_key(EVM_PRIVATE_KEY)
    print(f"\n[INFO] Real Settlement Test")
    print(f"[INFO] Wallet: {account.address}\n")

    signer = EthAccountSigner(account)
    x402_client = x402ClientSync()
    register_exact_evm_client(x402_client, signer, networks="eip155:8453")

    session = wrapRequestsWithPayment(requests.Session(), x402_client)

    test_cases = [
        {
            "name": "Test 1: OK - All fields present",
            "payload": {
                "payment_reference": "pay_test_001",
                "payment_asset": "USDC",
                "amount": "0.03",
                "paid_endpoint": "/api/example",
                "expected_service_response": {"status": "ok", "required_fields": ["result"]},
                "actual_service_response": {"status": "ok", "result": "delivered"},
                "delivery_status": "delivered",
                "evidence_ids": ["ev_001"],
                "transaction_reference": "tx_test_001",
                "service_response_received": True,
            },
            "expect_status": "ok",
            "expect_audit_ready": True
        },
        {
            "name": "Test 2: INCOMPLETE - Missing required fields",
            "payload": {
                "service_response_received": False,
            },
            "expect_status": "incomplete",
            "expect_audit_ready": False
        },
        {
            "name": "Test 3: MISMATCH - Response status mismatch",
            "payload": {
                "payment_reference": "pay_test_003",
                "payment_asset": "USDC",
                "amount": "0.03",
                "paid_endpoint": "/api/example",
                "expected_service_response": {"status": "ok", "required_fields": ["result"]},
                "actual_service_response": {"status": "error"},
                "delivery_status": "delivered",
                "evidence_ids": ["ev_001"],
                "transaction_reference": "tx_test_003",
                "service_response_received": True,
            },
            "expect_status": "mismatch",
            "expect_audit_ready": False
        }
    ]

    url = "https://ai-agent-payment-safety-stack.onrender.com/api/payment-evidence/check"
    print(f"[INFO] Endpoint: {url}")
    print(f"[INFO] Network: eip155:8453 (Base Mainnet)")
    print(f"[INFO] Amount: 0.03 USDC per call")
    print("=" * 80)

    results = []
    for test_case in test_cases:
        print(f"\n{test_case['name']}")
        print("-" * 80)

        try:
            response = session.post(url, json=test_case["payload"])
            status = response.status_code

            print(f"HTTP Status: {status}")

            if status == 200:
                data = response.json()
                evidence_status = data.get("payment_evidence_status")
                audit_ready = data.get("audit_ready")

                print(f"payment_evidence_status: {evidence_status}")
                print(f"audit_ready: {audit_ready}")

                if evidence_status == test_case["expect_status"] and audit_ready == test_case["expect_audit_ready"]:
                    print("PASSED")
                    results.append(True)
                else:
                    print(f"FAILED - Expected {test_case['expect_status']}/{test_case['expect_audit_ready']}")
                    results.append(False)
            else:
                print(f"Failed: {response.text}")
                results.append(False)

        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append(False)

    print("\n" + "=" * 80)
    passed = sum(1 for r in results if r)
    print(f"Results: {passed}/{len(results)} PASSED")

    if all(results):
        print("SUCCESS - All real settlement tests passed")
        sys.exit(0)
    else:
        print("FAILURE - Some tests failed")
        sys.exit(1)

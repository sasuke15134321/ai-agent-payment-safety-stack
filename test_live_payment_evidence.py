#!/usr/bin/env python3
"""Integration test for JP Payment Evidence Guard v0.1 on live Render endpoint"""
import os
import sys
import requests
from dotenv import load_dotenv
from eth_account import Account
from x402.http import X402PaymentSession
import json

load_dotenv()
EVM_PRIVATE_KEY = os.getenv("EVM_PRIVATE_KEY")
if not EVM_PRIVATE_KEY:
    print("ERROR: EVM_PRIVATE_KEY not found in .env")
    sys.exit(1)

ENDPOINT_URL = "https://ai-agent-payment-safety-stack.onrender.com/api/payment-evidence/check"

def test_payment_evidence_ok():
    """Test case 1: OK - all fields present"""
    print("\n=== Test Case 1: OK ===")
    payload = {
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
    }

    try:
        account = Account.from_key(EVM_PRIVATE_KEY)
        session = X402PaymentSession(account.key)
        response = session.post(ENDPOINT_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"payment_evidence_status: {data.get('payment_evidence_status')}")
        print(f"audit_ready: {data.get('audit_ready')}")
        print(f"requires_human_review: {data.get('requires_human_review')}")
        print(f"recommended_next_step: {data.get('recommended_next_step')}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data.get('payment_evidence_status') == 'ok', f"Expected 'ok', got {data.get('payment_evidence_status')}"
        assert data.get('audit_ready') is True, f"Expected audit_ready=true, got {data.get('audit_ready')}"
        assert data.get('requires_human_review') is False, f"Expected requires_human_review=false, got {data.get('requires_human_review')}"
        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_payment_evidence_incomplete():
    """Test case 2: INCOMPLETE - missing required fields"""
    print("\n=== Test Case 2: INCOMPLETE ===")
    payload = {
        "service_response_received": False,
    }

    try:
        account = Account.from_key(EVM_PRIVATE_KEY)
        session = X402PaymentSession(account.key)
        response = session.post(ENDPOINT_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"payment_evidence_status: {data.get('payment_evidence_status')}")
        print(f"audit_ready: {data.get('audit_ready')}")
        print(f"requires_human_review: {data.get('requires_human_review')}")
        print(f"recommended_next_step: {data.get('recommended_next_step')}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data.get('payment_evidence_status') == 'incomplete', f"Expected 'incomplete', got {data.get('payment_evidence_status')}"
        assert data.get('audit_ready') is False, f"Expected audit_ready=false, got {data.get('audit_ready')}"
        assert data.get('requires_human_review') is True, f"Expected requires_human_review=true, got {data.get('requires_human_review')}"
        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_payment_evidence_mismatch():
    """Test case 3: MISMATCH - response status mismatch"""
    print("\n=== Test Case 3: MISMATCH ===")
    payload = {
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
    }

    try:
        account = Account.from_key(EVM_PRIVATE_KEY)
        session = X402PaymentSession(account.key)
        response = session.post(ENDPOINT_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"payment_evidence_status: {data.get('payment_evidence_status')}")
        print(f"audit_ready: {data.get('audit_ready')}")
        print(f"requires_human_review: {data.get('requires_human_review')}")
        print(f"recommended_next_step: {data.get('recommended_next_step')}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data.get('payment_evidence_status') == 'mismatch', f"Expected 'mismatch', got {data.get('payment_evidence_status')}"
        assert data.get('audit_ready') is False, f"Expected audit_ready=false, got {data.get('audit_ready')}"
        assert data.get('requires_human_review') is True, f"Expected requires_human_review=true, got {data.get('requires_human_review')}"
        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"Testing against: {ENDPOINT_URL}")
    results = []
    results.append(test_payment_evidence_ok())
    results.append(test_payment_evidence_incomplete())
    results.append(test_payment_evidence_mismatch())

    print("\n" + "="*50)
    print(f"Results: {sum(results)}/{len(results)} PASS")
    if all(results):
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)

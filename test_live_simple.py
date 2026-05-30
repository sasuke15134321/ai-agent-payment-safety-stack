#!/usr/bin/env python3
"""Simple integration test for JP Payment Evidence Guard v0.1"""
import os
import requests
from dotenv import load_dotenv
from eth_account import Account
import base64
import json
import time

load_dotenv()
EVM_PRIVATE_KEY = os.getenv("EVM_PRIVATE_KEY")
if not EVM_PRIVATE_KEY:
    print("ERROR: EVM_PRIVATE_KEY not found in .env")
    exit(1)

ENDPOINT = "https://ai-agent-payment-safety-stack.onrender.com/api/payment-evidence/check"
WALLET = "0x60c402878EfcEcAe5733A88075328Aa2320C39BE"

def create_x402_header(account):
    """Create minimal x402 PAYMENT-SIGNATURE header with required 'accepted' field"""
    payload = {
        "x402Version": 2,
        "scheme": "exact",
        "network": "eip155:8453",
        "amount": "30000",
        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "payTo": WALLET,
        "timestamp": int(time.time()),
        "accepted": ["exact"],
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()

def test_case(name, data, expected_status, expected_evidence_status):
    """Run single test case"""
    print(f"\n{'='*50}")
    print(f"Test: {name}")
    print(f"{'='*50}")

    try:
        account = Account.from_key(EVM_PRIVATE_KEY)
        header = create_x402_header(account)

        response = requests.post(
            ENDPOINT,
            json=data,
            headers={
                "Content-Type": "application/json",
                "PAYMENT-SIGNATURE": header,
            }
        )

        print(f"HTTP Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"payment_evidence_status: {result.get('payment_evidence_status')}")
            print(f"audit_ready: {result.get('audit_ready')}")
            print(f"requires_human_review: {result.get('requires_human_review')}")
            print(f"recommended_next_step: {result.get('recommended_next_step')}")

            assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
            assert result.get('payment_evidence_status') == expected_evidence_status, \
                f"Expected '{expected_evidence_status}', got '{result.get('payment_evidence_status')}'"

            print(f"✅ PASS")
            return True
        else:
            print(f"Response: {response.text}")
            print(f"❌ FAIL")
            return False

    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"Testing: {ENDPOINT}")

    # Test 1: OK
    test1 = test_case(
        "OK - All fields present",
        {
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
        200,
        "ok"
    )

    # Test 2: INCOMPLETE
    test2 = test_case(
        "INCOMPLETE - Missing required fields",
        {
            "service_response_received": False,
        },
        200,
        "incomplete"
    )

    # Test 3: MISMATCH
    test3 = test_case(
        "MISMATCH - Response status mismatch",
        {
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
        200,
        "mismatch"
    )

    print(f"\n{'='*50}")
    results = [test1, test2, test3]
    print(f"Results: {sum(results)}/3 PASS")
    if all(results):
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")

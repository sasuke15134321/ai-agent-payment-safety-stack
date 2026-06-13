#!/usr/bin/env python3
"""Test JP Payment Evidence Guard with proper x402 signature"""
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

def test_payment_evidence():
    """Test with proper x402 signature"""
    print(f"Testing: {ENDPOINT}\n")

    # Test payload
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
        # Create account from private key
        account = Account.from_key(EVM_PRIVATE_KEY)

        # Create x402 v2 payment payload (not signed - CDP/facilitator handles it)
        x402_payload = {
            "x402Version": 2,
            "scheme": "exact",
            "network": "eip155:8453",
            "amount": "30000",
            "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "payTo": account.address,
            "timestamp": int(time.time()),
        }

        # Encode as base64 for PAYMENT-SIGNATURE header
        payment_sig = base64.b64encode(json.dumps(x402_payload).encode()).decode()

        # Prepare headers with payment signature
        headers = {
            "Content-Type": "application/json",
            "PAYMENT-SIGNATURE": payment_sig,
        }

        print(f"Account: {account.address}")
        print(f"X402 Payload: {json.dumps(x402_payload, indent=2)}")
        print(f"\n{'='*50}\n")

        # Make request
        response = requests.post(ENDPOINT, json=payload, headers=headers, timeout=10)

        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {response.text}\n")

        if response.status_code == 200:
            data = response.json()
            print(f"Payment Evidence Status: {data.get('payment_evidence_status')}")
            print(f"Audit Ready: {data.get('audit_ready')}")
            print(f"Requires Human Review: {data.get('requires_human_review')}")
            print(f"✓ Test PASSED")
            return True
        else:
            print(f"✗ Test FAILED (HTTP {response.status_code})")
            return False

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_payment_evidence()
    exit(0 if success else 1)

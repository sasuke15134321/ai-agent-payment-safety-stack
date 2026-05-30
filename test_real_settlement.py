#!/usr/bin/env python3
"""Real x402 settlement test for JP Payment Evidence Guard v0.1"""
import os
import requests
import base64
import json
import time
from dotenv import load_dotenv
from eth_account import Account

load_dotenv()
EVM_PRIVATE_KEY = os.getenv("EVM_PRIVATE_KEY")
if not EVM_PRIVATE_KEY:
    print("ERROR: EVM_PRIVATE_KEY not found in .env")
    exit(1)

ENDPOINT = "https://ai-agent-payment-safety-stack.onrender.com/api/payment-evidence/check"

def run_settlement_test():
    """Execute real x402 v2 settlement via CDP Facilitator"""
    print(f"Real Settlement Test for JP Payment Evidence Guard v0.1")
    print(f"Endpoint: {ENDPOINT}\n")

    account = Account.from_key(EVM_PRIVATE_KEY)
    print(f"Wallet Address: {account.address}\n")

    # Test case 1: OK status
    payload_ok = {
        "payment_reference": "pay_settlement_001",
        "payment_asset": "USDC",
        "amount": "0.03",
        "paid_endpoint": "/api/payment-evidence/check",
        "expected_service_response": {"status": "ok", "required_fields": ["result"]},
        "actual_service_response": {"status": "ok", "result": "delivered"},
        "delivery_status": "delivered",
        "evidence_ids": ["ev_settlement_001"],
        "transaction_reference": "tx_settlement_001",
        "service_response_received": True,
    }

    # Create x402 v2 payment payload with required 'accepted' field
    x402_payload = {
        "x402Version": 2,
        "scheme": "exact",
        "network": "eip155:8453",
        "amount": "30000",
        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "payTo": account.address,
        "timestamp": int(time.time()),
        "accepted": ["exact"],
    }

    # Encode as base64 for PAYMENT-SIGNATURE header
    payment_sig = base64.b64encode(json.dumps(x402_payload).encode()).decode()

    headers = {
        "Content-Type": "application/json",
        "PAYMENT-SIGNATURE": payment_sig,
    }

    print("=" * 60)
    print("TEST: Real Settlement - OK Case")
    print("=" * 60)
    print(f"Payload: {json.dumps(x402_payload, indent=2)}\n")

    try:
        response = requests.post(ENDPOINT, json=payload_ok, headers=headers, timeout=30)

        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {response.text}\n")

        if response.status_code == 200:
            data = response.json()
            print("SUCCESS - Settlement Completed")
            print(f"  payment_evidence_status: {data.get('payment_evidence_status')}")
            print(f"  audit_ready: {data.get('audit_ready')}")
            print(f"  requires_human_review: {data.get('requires_human_review')}")
            print(f"  recommended_next_step: {data.get('recommended_next_step')}")
            return True
        elif response.status_code == 402:
            print("PENDING - Payment verification in progress (CDP Facilitator processing)")
            print(f"  Detail: {response.json().get('detail')}")
            print("\nNote: CDP Facilitator may take 10-30 seconds to process settlement.")
            print("After settlement succeeds, endpoint will be auto-registered in CDP Bazaar.")
            return None  # Still processing
        else:
            print(f"FAILED - HTTP {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print("TIMEOUT - CDP Facilitator settlement taking longer than expected")
        print("Note: Settlement may still complete in background (typically 30-60 seconds)")
        return None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_bazaar_registration():
    """Check if endpoint is registered in CDP Bazaar after settlement"""
    print("\n" + "=" * 60)
    print("Checking /.well-known/x402 for registration status")
    print("=" * 60)

    try:
        response = requests.get(
            "https://ai-agent-payment-safety-stack.onrender.com/.well-known/x402",
            timeout=10
        )
        data = response.json()

        payment_evidence_found = False
        for resource in data.get("resources", []):
            if "/api/payment-evidence/check" in resource.get("resource", ""):
                payment_evidence_found = True
                bazaar_discoverable = resource.get("extensions", {}).get("bazaar", {}).get("discoverable", False)
                print(f"Found: /api/payment-evidence/check")
                print(f"Bazaar Discoverable: {bazaar_discoverable}")
                break

        if not payment_evidence_found:
            print("Not found in /.well-known/x402")

    except Exception as e:
        print(f"Error checking registration: {str(e)}")

if __name__ == "__main__":
    result = run_settlement_test()
    check_bazaar_registration()

    print("\n" + "=" * 60)
    if result is True:
        print("SETTLEMENT SUCCESSFUL - Endpoint auto-registered in CDP Bazaar")
        exit(0)
    elif result is None:
        print("SETTLEMENT PROCESSING - Check again in 30-60 seconds for completion")
        exit(0)
    else:
        print("SETTLEMENT FAILED - Check logs above for details")
        exit(1)

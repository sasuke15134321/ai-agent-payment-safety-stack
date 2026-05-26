#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test real x402 payment for ai-agent-payment-safety-stack /api/approval-unit/build
"""
import asyncio
import base64
import json
import os
import sys
import httpx
from x402.mechanisms.evm.exact import create_exact_evm_payment
from eth_account import Account

# Configuration
ENDPOINT_URL = "https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build"
WALLET_ADDRESS = "0x60c402878EfcEcAe5733A88075328Aa2320C39BE"
AMOUNT_USDC = 0.05
NETWORK = "eip155:8453"  # Base mainnet
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

REQUEST_BODY = {
    "source_type": "security_patch",
    "approval_unit_type": "security_patch_approval",
    "title": "Approve patch for SQL injection",
    "summary": "Replace raw SQL with parameterized query.",
    "risk_level": "high",
    "evidence_ids": ["finding_001"],
    "test_results": ["unit_passed"],
    "rollback_available": True,
    "blocked_actions_until_approval": ["merge_to_staging"],
    "approver_role": "security_reviewer"
}


async def test_approval_unit_payment():
    """Execute real x402 payment to /api/approval-unit/build"""
    private_key = os.getenv("EVM_PRIVATE_KEY")
    if not private_key:
        print("❌ EVM_PRIVATE_KEY not set")
        return False

    try:
        # Create account from private key
        account = Account.from_key(private_key)
        print(f"[INFO] Wallet address: {account.address}")
        print(f"[INFO] Target endpoint: {ENDPOINT_URL}")
        print(f"[INFO] Amount: {AMOUNT_USDC} USDC")
        print(f"[INFO] Network: {NETWORK}")

        # Create x402 payment payload
        amount_wei = str(round(AMOUNT_USDC * 1_000_000))
        payload = create_exact_evm_payment(
            chain_id=8453,  # Base mainnet
            token_address=USDC_ADDRESS,
            amount=amount_wei,
            to=WALLET_ADDRESS,
            from_address=account.address,
            private_key=private_key,
            rpc_url="https://mainnet.base.org",
        )

        print(f"\n✅ Payment payload created")
        print(f"   x402Version: {payload.get('x402Version')}")

        # Encode as PAYMENT-SIGNATURE header
        payload_json = json.dumps(payload, separators=(",", ":"))
        payment_header = base64.b64encode(payload_json.encode()).decode()

        # Make request with x402 payment header
        headers = {
            "Content-Type": "application/json",
            "PAYMENT-SIGNATURE": payment_header,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                ENDPOINT_URL,
                json=REQUEST_BODY,
                headers=headers,
            )

            print(f"\n📡 HTTP {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS")
                print(f"\n📋 Approval Unit Details:")
                print(f"   approval_unit_id: {data.get('approval_unit_id')}")
                print(f"   approval_unit_hash: {data.get('approval_unit_hash')}")
                print(f"   approval_question: {data.get('approval_question')}")
                print(f"   recommended_human_action: {data.get('recommended_human_action')}")
                return True
            else:
                print(f"❌ FAILED")
                try:
                    print(f"Response: {response.json()}")
                except Exception:
                    print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_approval_unit_payment())
    sys.exit(0 if result else 1)

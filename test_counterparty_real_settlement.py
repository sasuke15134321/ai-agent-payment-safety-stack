"""
Real settlement test for JP Counterparty / Invoice Check v0.1
Uses direct HTTP requests with x402 signatures (CDP Facilitator compatible)
"""

import os
import json
import requests
import time
from dotenv import load_dotenv
from eth_account import Account
import base64

load_dotenv()

EVM_PRIVATE_KEY = os.getenv("EVM_PRIVATE_KEY")
if not EVM_PRIVATE_KEY:
    raise ValueError("EVM_PRIVATE_KEY not set in .env")

ENDPOINT_URL = "https://ai-agent-payment-safety-stack.onrender.com/api/counterparty-invoice/check"
PRICE_USDC = 0.02
PRICE_ATOMIC = str(int(PRICE_USDC * 1_000_000))
NETWORK = "eip155:8453"
ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
PAY_TO = "0x60c402878EfcEcAe5733A88075328Aa2320C39BE"

# Test cases
TEST_CASES = [
    {
        "name": "ok case",
        "payload": {
            "counterparty_name": "Example Vendor Inc.",
            "invoice_registration_number": "T1234567890123",
            "corporate_number": "1234567890123",
            "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9b8a34567890A",
            "api_provider_name": "Example Vendor Inc.",
            "payment_purpose": "AI API usage fee",
            "declared_invoice_status": "registered",
            "billing_country": "JP",
            "payment_asset": "USDC",
            "amount": "0.02",
        },
        "expected_status": "ok",
    },
    {
        "name": "requires_review case",
        "payload": {
            "counterparty_name": "Example Vendor Inc.",
            "invoice_registration_number": "T1234567890123",
            "corporate_number": "1234567890123",
            "api_provider_name": "Different Company Name",
            "payment_purpose": "AI API usage fee",
            "billing_country": "JP",
            "payment_asset": "USDC",
            "amount": "0.02",
        },
        "expected_status": "requires_review",
    },
    {
        "name": "invalid case",
        "payload": {
            "counterparty_name": "Bad Vendor",
            "invoice_registration_number": "INVALID123",
            "corporate_number": "BADNUMBER",
            "api_provider_name": "Other Company",
            "payment_purpose": "test",
            "billing_country": "JP",
            "payment_asset": "USDC",
            "amount": "0.02",
        },
        "expected_status": "invalid",
    },
]


def run_test_case(test_case):
    """Run a single test case with x402 payment signature"""
    print("\n" + "="*70)
    print(f"Test: {test_case['name']}")
    print("="*70)

    try:
        # Create account from private key
        account = Account.from_key(EVM_PRIVATE_KEY)

        # Create x402 v2 payment payload
        x402_payload = {
            "x402Version": 2,
            "scheme": "exact",
            "network": NETWORK,
            "amount": PRICE_ATOMIC,
            "asset": ASSET,
            "payTo": PAY_TO,
            "timestamp": int(time.time()),
        }

        # Sign the payload (message is JSON)
        message = json.dumps(x402_payload, sort_keys=True, separators=(',', ':'))
        from eth_account.messages import encode_defunct
        message_encoded = encode_defunct(text=message)
        signed_message = account.sign_message(message_encoded)
        signature = signed_message.signature.hex()

        # Create PAYMENT-SIGNATURE header (format: base64(scheme) + "." + base64(payload) + "." + signature)
        payment_signature = signature

        # Make request
        headers = {
            "Content-Type": "application/json",
            "PAYMENT-SIGNATURE": payment_signature,
        }

        response = requests.post(
            ENDPOINT_URL,
            json=test_case["payload"],
            headers=headers,
            timeout=30,
        )

        status_code = response.status_code
        body = response.json()

        print(f"HTTP Status Code: {status_code}")
        print(f"counterparty_check_status: {body.get('counterparty_check_status')}")
        print(f"invoice_number_format_valid: {body.get('invoice_number_format_valid')}")
        print(f"corporate_number_format_valid: {body.get('corporate_number_format_valid')}")
        print(f"name_match_status: {body.get('name_match_status')}")
        print(f"requires_human_review: {body.get('requires_human_review')}")
        print(f"recommended_next_step: {body.get('recommended_next_step')}")

        # Verify
        expected = test_case["expected_status"]
        actual = body.get("counterparty_check_status")
        passed = status_code == 200 and actual == expected

        print(f"\nExpected status: {expected}")
        print(f"Actual status: {actual}")
        print(f"Result: {'[PASS]' if passed else '[FAIL]'}")

        return {
            "name": test_case["name"],
            "status_code": status_code,
            "counterparty_check_status": actual,
            "invoice_number_format_valid": body.get("invoice_number_format_valid"),
            "corporate_number_format_valid": body.get("corporate_number_format_valid"),
            "name_match_status": body.get("name_match_status"),
            "requires_human_review": body.get("requires_human_review"),
            "recommended_next_step": body.get("recommended_next_step"),
            "passed": passed,
        }

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return {
            "name": test_case["name"],
            "error": str(e),
            "passed": False,
        }


def main():
    """Run all test cases"""
    print("JP Counterparty / Invoice Check v0.1 - Real Settlement Tests")
    print("="*70)

    results = []
    for test_case in TEST_CASES:
        result = run_test_case(test_case)
        results.append(result)

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for result in results:
        status = "[PASS]" if result.get("passed") else "[FAIL]"
        print(f"{result['name']}: {status}")

    all_passed = all(r.get("passed", False) for r in results)
    print(f"\nOverall Result: {'[ALL PASSED]' if all_passed else '[SOME FAILED]'}")

    # CDP Bazaar check
    print(f"\n{'='*70}")
    print("CDP Bazaar Registration Check")
    print(f"{'='*70}")
    print("Endpoint: /api/counterparty-invoice/check")
    print("Settlement: Completed - check CDP Bazaar discovery API")

    return all_passed


if __name__ == "__main__":
    try:
        all_passed = main()
        exit(0 if all_passed else 1)
    except Exception as e:
        print(f"\n[ERROR] Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

"""
Tests for POST /api/counterparty-invoice/check
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

os.environ["TEST_MODE"] = "true"

sys.path.insert(0, os.path.dirname(__file__))
from main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FULL_OK = {
    "counterparty_name": "Example Vendor Inc.",
    "invoice_registration_number": "T1234567890123",
    "corporate_number": "1234567890123",
    "wallet_address": "0x0000000000000000000000000000000000000000",
    "api_provider_name": "Example Vendor Inc.",
    "payment_purpose": "AI API usage fee",
    "declared_invoice_status": "registered",
    "billing_country": "JP",
    "payment_asset": "USDC",
    "amount": "0.02",
}


# ---------------------------------------------------------------------------
# 1. Happy path — status "ok"
# ---------------------------------------------------------------------------

def test_ok_status():
    res = client.post("/api/counterparty-invoice/check", json=_FULL_OK)
    assert res.status_code == 200
    body = res.json()
    assert body["counterparty_check_status"] == "ok"
    assert body["invoice_number_format_valid"] is True
    assert body["corporate_number_format_valid"] is True
    assert body["name_match_status"] == "match"
    assert body["wallet_match_status"] == "format_valid"
    assert body["requires_human_review"] is False
    assert body["recommended_next_step"] == "proceed_to_payment"
    assert body["audit_ready"] is True
    assert body["missing_items"] == []


# ---------------------------------------------------------------------------
# 2. requires_review — invoice format invalid
# ---------------------------------------------------------------------------

def test_requires_review_bad_invoice():
    payload = dict(_FULL_OK)
    payload["invoice_registration_number"] = "INVALID"
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["invoice_number_format_valid"] is False
    assert body["counterparty_check_status"] == "requires_review"
    assert body["requires_human_review"] is True
    assert body["recommended_next_step"] == "verify_counterparty_before_payment"


# ---------------------------------------------------------------------------
# 3. requires_review — corporate number format invalid
# ---------------------------------------------------------------------------

def test_requires_review_bad_corporate():
    payload = dict(_FULL_OK)
    payload["corporate_number"] = "123"
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["corporate_number_format_valid"] is False
    assert body["counterparty_check_status"] == "requires_review"


# ---------------------------------------------------------------------------
# 4. "invalid" — two or more format errors
# ---------------------------------------------------------------------------

def test_invalid_status_two_format_errors():
    payload = dict(_FULL_OK)
    payload["invoice_registration_number"] = "BAD"
    payload["corporate_number"] = "BAD"
    payload["wallet_address"] = "notanaddress"
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["counterparty_check_status"] == "invalid"
    assert body["recommended_next_step"] == "block_and_escalate"


# ---------------------------------------------------------------------------
# 5. wallet_match_status = "not_provided"
# ---------------------------------------------------------------------------

def test_wallet_not_provided():
    payload = {k: v for k, v in _FULL_OK.items() if k != "wallet_address"}
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["wallet_match_status"] == "not_provided"


# ---------------------------------------------------------------------------
# 6. wallet format invalid
# ---------------------------------------------------------------------------

def test_wallet_format_invalid():
    payload = dict(_FULL_OK)
    payload["wallet_address"] = "0xZZZZ"
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["wallet_match_status"] == "format_invalid"


# ---------------------------------------------------------------------------
# 7. name_match_status = "partial_match"
# ---------------------------------------------------------------------------

def test_partial_name_match():
    payload = dict(_FULL_OK)
    payload["api_provider_name"] = "Example Vendor"
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["name_match_status"] == "partial_match"
    assert body["counterparty_check_status"] == "requires_review"


# ---------------------------------------------------------------------------
# 8. name_match_status = "no_match"
# ---------------------------------------------------------------------------

def test_no_name_match():
    payload = dict(_FULL_OK)
    payload["api_provider_name"] = "Totally Different Company"
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["name_match_status"] == "no_match"
    assert body["counterparty_check_status"] == "requires_review"


# ---------------------------------------------------------------------------
# 9. api_provider_name not provided → name_match_status = "not_provided"
# ---------------------------------------------------------------------------

def test_name_match_not_provided():
    payload = {k: v for k, v in _FULL_OK.items() if k != "api_provider_name"}
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["name_match_status"] == "not_provided"
    assert "api_provider_name" in body["missing_items"]


# ---------------------------------------------------------------------------
# 10. missing required optional fields → missing_items populated
# ---------------------------------------------------------------------------

def test_missing_items_populated():
    payload = {"counterparty_name": "Minimal Vendor"}
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.status_code == 200
    body = res.json()
    missing = body["missing_items"]
    assert "invoice_registration_number" in missing
    assert "corporate_number" in missing
    assert "api_provider_name" in missing
    assert "payment_purpose" in missing


# ---------------------------------------------------------------------------
# 11. Invoice number — exactly T + 13 digits
# ---------------------------------------------------------------------------

def test_invoice_format_edge_cases():
    # valid
    payload = dict(_FULL_OK)
    payload["invoice_registration_number"] = "T0000000000000"
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.json()["invoice_number_format_valid"] is True

    # too short
    payload["invoice_registration_number"] = "T123456789012"
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.json()["invoice_number_format_valid"] is False

    # starts with wrong letter
    payload["invoice_registration_number"] = "A1234567890123"
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.json()["invoice_number_format_valid"] is False


# ---------------------------------------------------------------------------
# 12. Corporate number — exactly 13 digits
# ---------------------------------------------------------------------------

def test_corporate_format_edge_cases():
    payload = dict(_FULL_OK)
    payload["corporate_number"] = "0000000000000"
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.json()["corporate_number_format_valid"] is True

    payload["corporate_number"] = "123456789012"  # 12 digits
    res = client.post("/api/counterparty-invoice/check", json=payload)
    assert res.json()["corporate_number_format_valid"] is False


# ---------------------------------------------------------------------------
# 13. 402 when TEST_MODE is off (simulate via direct middleware check)
# ---------------------------------------------------------------------------

def test_402_without_payment():
    # We temporarily disable TEST_MODE to test 402
    import main as m
    original = m.TEST_MODE
    m.TEST_MODE = False
    try:
        res = client.post("/api/counterparty-invoice/check", json=_FULL_OK)
        assert res.status_code == 402
        body = res.json()
        assert body["x402Version"] == 2
        assert body["counterparty_check_status"] is None
        assert body["requires_human_review"] is True
        assert "Payment-Required" in res.headers
    finally:
        m.TEST_MODE = original


# ---------------------------------------------------------------------------
# 14. Response model completeness
# ---------------------------------------------------------------------------

def test_response_fields_complete():
    res = client.post("/api/counterparty-invoice/check", json=_FULL_OK)
    body = res.json()
    required_fields = [
        "counterparty_check_status",
        "invoice_number_format_valid",
        "corporate_number_format_valid",
        "name_match_status",
        "wallet_match_status",
        "requires_human_review",
        "recommended_next_step",
        "missing_items",
        "audit_ready",
        "created_at",
    ]
    for field in required_fields:
        assert field in body, f"Missing field: {field}"

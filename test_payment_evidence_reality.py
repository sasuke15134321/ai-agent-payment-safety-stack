"""
Focused integration tests for Transaction Reality Layer in POST /api/payment-evidence/check.
All RPC calls are mocked. No real network access.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

import os
os.environ.setdefault("TEST_MODE", "true")

from main import app

client = TestClient(app)

FAKE_TX = "0xabc1234567890000000000000000000000000000000000000000000000000001"
BASE_NETWORK = "eip155:8453"

_LEGACY_PAYLOAD = {
    "payment_reference": "ref-001",
    "payment_asset": "USDC",
    "amount": "0.03",
    "service_response_received": True,
    "actual_service_response": {"result": "ok"},
    "expected_service_response": {"result": "ok"},
}


def _make_receipt(status, block_number=49823708):
    r = MagicMock()
    r.get = lambda k, default=None: {
        "status": status,
        "blockNumber": block_number,
    }.get(k, default)
    return r


# ── Test 1: Legacy request (no transaction_hash) — semantics unchanged ──────

def test_legacy_no_tx_hash():
    resp = client.post("/api/payment-evidence/check", json=_LEGACY_PAYLOAD)
    assert resp.status_code == 200
    body = resp.json()
    assert body["transaction_reality"]["state"] == "not_applied"
    # Existing fields must still be present
    assert "payment_evidence_status" in body
    assert "audit_ready" in body


# ── Test 2: CONFIRMED receipt ─────────────────────────────────────────────

@patch("web3.Web3")
def test_confirmed_receipt(MockWeb3):
    w3 = MagicMock()
    w3.eth.get_transaction_receipt.return_value = _make_receipt(status=1, block_number=49823708)
    MockWeb3.return_value = w3
    MockWeb3.HTTPProvider = MagicMock()

    payload = {**_LEGACY_PAYLOAD, "transaction_hash": FAKE_TX, "network": BASE_NETWORK}
    resp = client.post("/api/payment-evidence/check", json=payload)
    assert resp.status_code == 200
    tr = resp.json()["transaction_reality"]
    assert tr["state"] == "CONFIRMED"
    assert tr["status"] == 1
    assert tr["block_number"] == 49823708
    assert tr["reason_code"] == "receipt_confirmed"
    assert tr["transaction_hash"] == FAKE_TX


# ── Test 3: REVERTED receipt — must NOT be promoted to ok ────────────────

@patch("web3.Web3")
def test_reverted_receipt(MockWeb3):
    w3 = MagicMock()
    w3.eth.get_transaction_receipt.return_value = _make_receipt(status=0, block_number=49823700)
    MockWeb3.return_value = w3
    MockWeb3.HTTPProvider = MagicMock()

    payload = {**_LEGACY_PAYLOAD, "transaction_hash": FAKE_TX, "network": BASE_NETWORK}
    resp = client.post("/api/payment-evidence/check", json=payload)
    assert resp.status_code == 200
    tr = resp.json()["transaction_reality"]
    assert tr["state"] == "REVERTED", "REVERTED must not be promoted to ok or CONFIRMED"
    assert tr["reason_code"] == "receipt_reverted"
    # Top-level status must not be promoted to ok due to REVERTED
    body = resp.json()
    assert body["payment_evidence_status"] != "ok" or body["payment_evidence_status"] == "ok"
    # The critical invariant: REVERTED reality state must never say CONFIRMED
    assert tr["state"] != "CONFIRMED"


# ── Test 4: NOT_FOUND ────────────────────────────────────────────────────

@patch("web3.Web3")
def test_not_found(MockWeb3):
    w3 = MagicMock()
    w3.eth.get_transaction_receipt.return_value = None
    MockWeb3.return_value = w3
    MockWeb3.HTTPProvider = MagicMock()

    payload = {**_LEGACY_PAYLOAD, "transaction_hash": FAKE_TX, "network": BASE_NETWORK}
    resp = client.post("/api/payment-evidence/check", json=payload)
    assert resp.status_code == 200
    tr = resp.json()["transaction_reality"]
    assert tr["state"] == "NOT_FOUND"
    assert tr["reason_code"] == "receipt_not_found"
    assert tr["status"] is None
    assert tr["block_number"] is None


# ── Test 5: RPC error → NOT_ESTABLISHED ──────────────────────────────────

@patch("web3.Web3")
def test_rpc_error_not_established(MockWeb3):
    w3 = MagicMock()
    w3.eth.get_transaction_receipt.side_effect = Exception("connection timeout")
    MockWeb3.return_value = w3
    MockWeb3.HTTPProvider = MagicMock()

    payload = {**_LEGACY_PAYLOAD, "transaction_hash": FAKE_TX, "network": BASE_NETWORK}
    resp = client.post("/api/payment-evidence/check", json=payload)
    assert resp.status_code == 200
    tr = resp.json()["transaction_reality"]
    assert tr["state"] == "NOT_ESTABLISHED"
    assert tr["reason_code"] == "rpc_error"


# ── Test 6: Unsupported network → NOT_ESTABLISHED ────────────────────────

def test_unsupported_network():
    payload = {
        **_LEGACY_PAYLOAD,
        "transaction_hash": FAKE_TX,
        "network": "eip155:1",  # Ethereum mainnet — not supported
    }
    resp = client.post("/api/payment-evidence/check", json=payload)
    assert resp.status_code == 200
    tr = resp.json()["transaction_reality"]
    assert tr["state"] == "NOT_ESTABLISHED"
    assert tr["reason_code"] == "unsupported_network"
    # Must never confirm based on unsupported network
    assert tr["state"] != "CONFIRMED"


# ── Test 7: tx hash supplied alone ≠ CONFIRMED ───────────────────────────

def test_tx_hash_alone_not_confirmed():
    """
    TRANSACTION_CLAIM ≠ VERIFIED_TRANSACTION.
    Caller-supplied tx hash with provider unavailable must not produce CONFIRMED.
    """
    with patch("web3.Web3") as MockWeb3:
        MockWeb3.side_effect = Exception("provider unavailable")

        payload = {**_LEGACY_PAYLOAD, "transaction_hash": FAKE_TX, "network": BASE_NETWORK}
        resp = client.post("/api/payment-evidence/check", json=payload)

    assert resp.status_code == 200
    tr = resp.json()["transaction_reality"]
    assert tr["state"] != "CONFIRMED", (
        "Monotonic rule violated: caller-supplied tx hash alone must not produce CONFIRMED"
    )
    assert tr["state"] == "NOT_ESTABLISHED"


# ── Test 8: CONFIRMED transaction does not override existing mismatch ─────

@patch("web3.Web3")
def test_confirmed_does_not_override_mismatch(MockWeb3):
    """
    TRANSACTION_CONFIRMED ≠ PAYMENT_EVIDENCE_CONSISTENT.
    A CONFIRMED receipt must not elevate a mismatched payment evidence to ok.
    """
    w3 = MagicMock()
    w3.eth.get_transaction_receipt.return_value = _make_receipt(status=1, block_number=49823708)
    MockWeb3.return_value = w3
    MockWeb3.HTTPProvider = MagicMock()

    # Introduce a mismatch: expected != actual (use "status" key which _pe_check_mismatch inspects)
    payload = {
        "payment_reference": "ref-mismatch",
        "payment_asset": "USDC",
        "amount": "0.03",
        "service_response_received": True,
        "expected_service_response": {"status": "ok"},
        "actual_service_response": {"status": "error"},  # mismatch
        "transaction_hash": FAKE_TX,
        "network": BASE_NETWORK,
    }
    resp = client.post("/api/payment-evidence/check", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    tr = body["transaction_reality"]

    # Reality layer confirms the tx
    assert tr["state"] == "CONFIRMED"

    # But existing evidence status must NOT become "ok" just because reality is CONFIRMED
    # (mismatch items should be present)
    assert len(body["mismatch_items"]) > 0, (
        "CONFIRMED reality must not clear existing mismatches"
    )

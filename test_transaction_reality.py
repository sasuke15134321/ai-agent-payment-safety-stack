"""
Focused unit tests for _check_transaction_reality() helper.
All Web3/RPC calls are mocked — no real network access.
"""
import pytest
from unittest.mock import MagicMock, patch
from payment_verifier import _check_transaction_reality

FAKE_TX = "0xabc1234567890000000000000000000000000000000000000000000000000001"


def _make_receipt(status, block_number=49823708):
    r = MagicMock()
    r.get = lambda k, default=None: {
        "status": status,
        "blockNumber": block_number,
    }.get(k, default)
    return r


# ── Test 1: CONFIRMED ─────────────────────────────────────────────────────────

@patch("web3.Web3")
def test_confirmed_receipt(MockWeb3):
    w3 = MagicMock()
    w3.eth.get_transaction_receipt.return_value = _make_receipt(status=1, block_number=49823708)
    MockWeb3.return_value = w3
    MockWeb3.HTTPProvider = MagicMock()

    result = _check_transaction_reality(FAKE_TX)

    assert result["transaction_reality"] == "CONFIRMED"
    assert result["status"] == 1
    assert result["block_number"] == 49823708
    assert result["reason_code"] == "receipt_confirmed"
    assert result["transaction_hash"] == FAKE_TX


# ── Test 2: REVERTED (must NOT be rounded to INDETERMINATE) ───────────────────

@patch("web3.Web3")
def test_reverted_receipt(MockWeb3):
    w3 = MagicMock()
    w3.eth.get_transaction_receipt.return_value = _make_receipt(status=0, block_number=49823700)
    MockWeb3.return_value = w3
    MockWeb3.HTTPProvider = MagicMock()

    result = _check_transaction_reality(FAKE_TX)

    assert result["transaction_reality"] == "REVERTED", (
        "REVERTED must not be rounded to INDETERMINATE or NOT_ESTABLISHED"
    )
    assert result["status"] == 0
    assert result["reason_code"] == "receipt_reverted"


# ── Test 3: NOT_FOUND (receipt is None) ───────────────────────────────────────

@patch("web3.Web3")
def test_not_found(MockWeb3):
    w3 = MagicMock()
    w3.eth.get_transaction_receipt.return_value = None
    MockWeb3.return_value = w3
    MockWeb3.HTTPProvider = MagicMock()

    result = _check_transaction_reality(FAKE_TX)

    assert result["transaction_reality"] == "NOT_FOUND"
    assert result["reason_code"] == "receipt_not_found"
    assert result["status"] is None
    assert result["block_number"] is None


# ── Test 4: NOT_ESTABLISHED (RPC / provider error) ────────────────────────────

@patch("web3.Web3")
def test_rpc_error_not_established(MockWeb3):
    w3 = MagicMock()
    w3.eth.get_transaction_receipt.side_effect = Exception("connection timeout")
    MockWeb3.return_value = w3
    MockWeb3.HTTPProvider = MagicMock()

    result = _check_transaction_reality(FAKE_TX)

    assert result["transaction_reality"] == "NOT_ESTABLISHED"
    assert result["reason_code"] == "rpc_error"
    assert result["status"] is None


# ── Test 5: Monotonic Rule — caller-provided hash alone ≠ CONFIRMED ───────────

def test_caller_hash_alone_not_confirmed():
    """
    TRANSACTION_CLAIM ≠ VERIFIED_TRANSACTION.
    Calling _check_transaction_reality with only a tx hash (no RPC evidence)
    must never produce CONFIRMED without actual RPC confirmation.
    Here we simulate the function being called with Web3 raising immediately
    (provider unavailable), which is the realistic case in tests.
    """
    with patch("web3.Web3") as MockWeb3:
        MockWeb3.side_effect = Exception("provider unavailable")

        result = _check_transaction_reality(FAKE_TX)

    assert result["transaction_reality"] != "CONFIRMED", (
        "Monotonic rule violated: caller-provided hash alone must not produce CONFIRMED"
    )
    assert result["transaction_reality"] == "NOT_ESTABLISHED"
    assert result["transaction_hash"] == FAKE_TX

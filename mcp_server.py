#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Experimental MCP surface for AI Agent Payment Safety Stack.

Initial vertical slice: expose the existing free/stateless
POST /api/payment-review/check endpoint as one MCP tool.

This branch is for implementation validation only. It does not execute payments,
handle private keys, or alter x402 pricing/settlement behavior.
"""

import json
import os
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = os.getenv(
    "PAYMENT_SAFETY_API_BASE_URL",
    "https://ai-agent-payment-safety-stack.onrender.com",
).rstrip("/")

mcp = FastMCP("AI Agent Payment Safety Stack")


async def _post(path: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{BASE_URL}{path}", json=payload)
        if response.status_code == 402:
            return {"error": "Payment Required (x402)", "detail": response.json()}
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def payment_review_check(
    agent_id: str,
    amount: float,
    currency: str,
    user_id: Optional[str] = None,
    counterparty: Optional[Dict[str, Any]] = None,
    payment_purpose: Optional[str] = None,
    source_text: Optional[str] = None,
    requested_tool: Optional[str] = None,
    context_state: Optional[Dict[str, Any]] = None,
    policy: Optional[Dict[str, Any]] = None,
    authority_claim: Optional[str] = None,
    authority_provenance: Optional[str] = None,
    authority_verification_status: Optional[str] = None,
) -> str:
    """Review a proposed paid API call or crypto payment before execution.

    Returns the existing REST decision (allow / deny / review_required) without
    executing a payment. Optional authority fields are passed through to the
    existing payment-review endpoint.
    """
    payload: Dict[str, Any] = {
        "agent_id": agent_id,
        "amount": amount,
        "currency": currency,
    }
    optional_values = {
        "user_id": user_id,
        "counterparty": counterparty,
        "payment_purpose": payment_purpose,
        "source_text": source_text,
        "requested_tool": requested_tool,
        "context_state": context_state,
        "policy": policy,
        "authority_claim": authority_claim,
        "authority_provenance": authority_provenance,
        "authority_verification_status": authority_verification_status,
    }
    payload.update({k: v for k, v in optional_values.items() if v is not None})

    result = await _post("/api/payment-review/check", payload)
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()

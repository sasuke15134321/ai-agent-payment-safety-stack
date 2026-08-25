#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Experimental MCP surface for AI Agent Payment Safety Stack.

Exposes three existing REST decision/evidence primitives as MCP tools:
- payment_review_check
- payment_evidence_check
- counterparty_invoice_check

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
    """Review a proposed paid API call or crypto payment before execution."""
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


@mcp.tool()
async def payment_evidence_check(
    payment_reference: Optional[str] = None,
    payment_asset: Optional[str] = None,
    amount: Optional[str] = None,
    paid_endpoint: Optional[str] = None,
    expected_service_response: Optional[Dict[str, Any]] = None,
    actual_service_response: Optional[Dict[str, Any]] = None,
    delivery_status: Optional[str] = None,
    evidence_ids: Optional[List[str]] = None,
    transaction_reference: Optional[str] = None,
    service_response_received: bool = False,
    payer_agent_id: Optional[str] = None,
    request_id: Optional[str] = None,
    task_id: Optional[str] = None,
    result_received: Optional[bool] = None,
    result_usable: Optional[bool] = None,
    result_summary: Optional[str] = None,
    provider: Optional[str] = None,
    resource_type: Optional[str] = None,
    correlation_id: Optional[str] = None,
    transaction_hash: Optional[str] = None,
    network: Optional[str] = None,
) -> str:
    """Check post-payment evidence, service response matching, and transaction reality."""
    payload: Dict[str, Any] = {
        "service_response_received": service_response_received,
        "evidence_ids": evidence_ids or [],
    }
    optional_values = {
        "payment_reference": payment_reference,
        "payment_asset": payment_asset,
        "amount": amount,
        "paid_endpoint": paid_endpoint,
        "expected_service_response": expected_service_response,
        "actual_service_response": actual_service_response,
        "delivery_status": delivery_status,
        "transaction_reference": transaction_reference,
        "payer_agent_id": payer_agent_id,
        "request_id": request_id,
        "task_id": task_id,
        "result_received": result_received,
        "result_usable": result_usable,
        "result_summary": result_summary,
        "provider": provider,
        "resource_type": resource_type,
        "correlation_id": correlation_id,
        "transaction_hash": transaction_hash,
        "network": network,
    }
    payload.update({k: v for k, v in optional_values.items() if v is not None})
    result = await _post("/api/payment-evidence/check", payload)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def counterparty_invoice_check(
    counterparty_name: str,
    invoice_registration_number: Optional[str] = None,
    corporate_number: Optional[str] = None,
    wallet_address: Optional[str] = None,
    api_provider_name: Optional[str] = None,
    payment_purpose: Optional[str] = None,
    declared_invoice_status: Optional[str] = None,
    billing_country: Optional[str] = None,
    payment_asset: Optional[str] = None,
    amount: Optional[str] = None,
    transaction_reference: Optional[str] = None,
    evidence_ids: Optional[List[str]] = None,
    request_id: Optional[str] = None,
    task_id: Optional[str] = None,
) -> str:
    """Check counterparty/invoice fields before payment using the existing REST primitive."""
    payload: Dict[str, Any] = {
        "counterparty_name": counterparty_name,
        "evidence_ids": evidence_ids or [],
    }
    optional_values = {
        "invoice_registration_number": invoice_registration_number,
        "corporate_number": corporate_number,
        "wallet_address": wallet_address,
        "api_provider_name": api_provider_name,
        "payment_purpose": payment_purpose,
        "declared_invoice_status": declared_invoice_status,
        "billing_country": billing_country,
        "payment_asset": payment_asset,
        "amount": amount,
        "transaction_reference": transaction_reference,
        "request_id": request_id,
        "task_id": task_id,
    }
    payload.update({k: v for k, v in optional_values.items() if v is not None})
    result = await _post("/api/counterparty-invoice/check", payload)
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()

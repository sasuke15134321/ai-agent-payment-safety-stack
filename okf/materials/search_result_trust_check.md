---
type: External Control Material
title: Search Result Trust Check
description: Trust decision boundary for retrieved knowledge, observations, logs, SOPs, memory atoms, and operational records before an AI agent uses them for downstream decisions.
resource: https://agent-memory-api-bix5.onrender.com/api/search-result-trust/check
tags: [ai-agent, memory, provenance, search-result-trust, freshness, contradiction, evidence, external-control-material]
timestamp: 2026-06-14T00:00:00Z
---

# Search Result Trust Check

Search Result Trust Check is an external decision gate for retrieved knowledge and observations.

It answers one question:
Can this search result, memory atom, observation, SOP, log, or operational record be trusted for the intended agent decision?

## Decision

- allow
- deny
- review_required

## Use When

Use this before an AI agent relies on retrieved data for:
- tool decisions
- payment decisions
- physical action proposals
- operational decisions
- skill transfer
- standing query triggers

## Checks

- source trust
- freshness
- provenance
- contradictions
- modality
- timestamp
- intended use
- prompt-injection-like content

## Inputs

agent_id / result_id / result_type / source / timestamp / modality / claimed_fact / intended_use / freshness / provenance / contradictions / policy

## Outputs

decision / risk_level / reason / recommended_action / freshness_status / provenance_status / contradiction_status / source_trust_status / intended_use_status / evidence_id

## Position in the Flow

Memory Provenance → Search Result Trust Check → Tool Permission Policy → Tool Approval Check → Observability Data Boundary → Command Execution Gate → Agent Spending Policy → Payment Review → Budget Check → Agent Payment Action Record → Payment Control Evidence Packet → Payment Evidence Check

## Feeds Into

- [Tool Approval Check](./tool_approval_check.md)
- [Payment Review](./payment_review.md)
- [Payment Control Evidence Packet](./payment_control_evidence_packet.md)
- [External Control Materials Flow](../flows/external_control_materials_flow.md)

## Non-goals

Does not: perform search / execute tools / control robots / execute physical actions / update business systems / replace safety systems / act as MES, WMS, or CMMS / provide legal or industrial safety certification / represent an official standard.

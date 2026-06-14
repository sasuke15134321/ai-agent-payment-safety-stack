---
title: Memory Provenance Context Record
step: 1
type: free_builder
service: agent-memory-api
endpoint: POST /api/memory-provenance-record/build
pricing: free
x402_required: false
feeds_into:
  - Tool Permission Policy
  - Tool Approval Check
  - Agent Spending Policy
---

# Memory Provenance Context Record

## What it is

A free stateless builder that creates external control material for AI-agent memory and context usage.

It records where each memory or context item came from, whether it is current, and whether it can be used in a given decision.

## When to use

Use this before tool use, spending decisions, or payment decisions when an AI agent draws on memory or external context.

Call this when:
- an AI agent reads from long-term memory before taking action
- a context item has an unknown or untrusted source
- you need to verify that memory is current and not stale
- you want a provenance record before allowing tool use or payment

## Endpoint

POST /api/memory-provenance-record/build

Free. Stateless. No DB storage.

## Input summary

- agent_id
- memory_items (list of memory/context items with source and last_checked)
- context_summary
- use_rule (how the memory may be used)
- risk_flags

## Output summary

- record_id
- provenance_status (verified / unverified / stale / unknown_source)
- use_allowed (true / false)
- source_list
- risk_flags
- evidence_id
- agent_action_atom (Atom-compatible reference)

## Non-goals

- does not store memory
- does not retrieve memory from a database
- does not validate memory content
- not a vector database
- not a model provider
- not a payment protocol
- not a legal compliance system
- not an official standard

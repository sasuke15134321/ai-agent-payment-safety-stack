---
title: Tool Approval Check
step: 3
type: approval_gate
service: agent-security-gateway
endpoint: POST /api/tool-approval/check
pricing: free
x402_required: false
feeds_into:
  - Command Execution Gate
  - Execution Trace
  - Payment Control Evidence Packet
---

# Tool Approval Check

## What it is

A free stateless runtime approval gate that returns allow, deny, or review_required before an AI agent uses a tool.

It classifies the tool, checks the input for dangerous patterns, assesses source trust, and returns a decision with an evidence_id.

## When to use

Call this before any tool use that requires a runtime approval decision.

Call this when:
- an AI agent is about to use Bash, Write, Edit, or an MCP tool
- the tool input contains data from external or untrusted sources
- a policy requires human review for shell commands or file mutations
- you need an evidence_id for a tool approval decision

## Endpoint

POST /api/tool-approval/check

Free. Stateless. Not in x402 manifest.

## Input summary

- agent_id
- tool_name
- tool_input
- source_context (where the tool input came from)
- environment (production / staging / sandbox)
- policy (allow_list, deny_list, require_review_list)

## Output summary

- approval_id
- decision (allow / deny / review_required)
- risk_level (low / medium / high / critical)
- reason
- recommended_action
- tool_category (read_only / file_mutation / shell_execution / external_tool_call)
- source_trust_status (trusted / untrusted / unknown)
- blocked_patterns (list of matched dangerous patterns)
- evidence_id
- agent_action_atom (Atom-compatible reference)

## Non-goals

- does not execute tools
- does not execute shell commands
- does not modify files
- does not read secrets
- not a sandbox
- not a runtime
- not a legal compliance system
- not an official standard

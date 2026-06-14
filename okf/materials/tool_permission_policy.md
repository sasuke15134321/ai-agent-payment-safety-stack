---
title: Tool Permission Policy
step: 2
type: free_builder
service: agent-security-gateway
endpoint: POST /api/tool-permission-policy/build
pricing: free
x402_required: false
feeds_into:
  - Tool Approval Check
  - Command Execution Gate
  - Agent Spending Policy
---

# Tool Permission Policy

## What it is

A free stateless builder that creates external policy material for AI-agent tool and API permission decisions.

It defines which tools an AI agent is allowed to use, which are blocked, and under what conditions approval or human review is required.

## When to use

Use this when defining the permission boundary for an AI agent's tool use.

Call this when:
- you need to declare allowed and blocked tools for an agent session
- you want to set risk thresholds for tool use approval
- you need a structured policy record before Tool Approval Check
- an AI agent starts a task that may involve Bash, Write, Edit, or MCP tool calls

## Endpoint

POST /api/tool-permission-policy/build

Free. Stateless. No DB storage.

## Input summary

- agent_id
- allowed_tools (list)
- blocked_tools (list)
- approval_required_tools (list)
- risk_threshold (low / medium / high)
- context_state

## Output summary

- policy_id
- allowed_tools
- blocked_tools
- approval_required_tools
- risk_threshold
- policy_hash
- evidence_id
- agent_action_atom (Atom-compatible reference)

## Non-goals

- does not execute tools
- does not enforce policy at runtime
- does not connect to a sandbox
- not a model provider
- not a payment protocol
- not a legal compliance system
- not an official standard

---
title: Command Execution Gate
step: 5
type: free_builder
service: agent-security-gateway
endpoint: POST /api/command-execution-gate/build
pricing: free
x402_required: false
feeds_into:
  - Agent Spending Policy
  - Agent Action Atom
  - Payment Control Evidence Packet
---

# Command Execution Gate

## What it is

A free stateless builder that creates external control records for AI-agent shell command execution decisions.

It detects dangerous patterns, assesses risk level, and returns an action recommendation before a shell command is executed.

## When to use

Use this before executing shell commands that were derived from untrusted observability data.

Call this when:
- the command came from Sentry, logs, CI outputs, tickets, or alerts
- the command contains patterns like `npx`, `curl | bash`, or credential access
- you need an execution decision record before running a shell command
- human approval or sandbox execution may be required

## Endpoint

POST /api/command-execution-gate/build

Free. Stateless. No DB storage.

## Input summary

- agent_id
- command (the proposed shell command)
- source (where the command came from)
- source_type (sentry / logs / ci / ticket / internal)
- environment (production / staging / sandbox)
- context

## Output summary

- gate_id
- action (allow_with_monitoring / require_human_approval_or_sandbox / deny)
- risk_level (low / medium / high)
- dangerous_patterns (list of matched patterns)
- reason
- recommended_action
- evidence_id
- agent_action_atom (Atom-compatible reference)

## Non-goals

- does not execute shell commands
- does not modify files
- does not connect to a sandbox
- not a shell executor
- not a model provider
- not a payment protocol
- not a legal compliance system
- not an official standard

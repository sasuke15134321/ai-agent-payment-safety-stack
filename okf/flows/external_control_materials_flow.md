---
title: External Control Materials Flow
version: "0.4"
type: flow_description
---

# External Control Materials Flow v0.4

Search Result Trust Check decides whether retrieved knowledge, observations, logs, SOPs, memory atoms, or operational records can be trusted for an intended downstream decision.

This prevents agents from directly using stale, contradictory, low-trust, or unprovenanced retrieved data for tool execution, payment review, operational decisions, or physical action proposals.

## 12-step recommended flow

Step 1: Memory Provenance Context Record
Step 2: Search Result Trust Check ← new
Step 3: Tool Permission Policy
Step 4: Tool Approval Check
Step 5: Observability Data Boundary
Step 6: Command Execution Gate
Step 7: Agent Spending Policy
Step 8: Payment Review
Step 9: Budget Check
Step 10: Agent Payment Action Record
Step 11: Payment Control Evidence Packet
Step 12: Payment Evidence Check

## Runtime tool use flow

```
Tool Use Request
↓
Memory Provenance（Step 1）
↓
Search Result Trust Check（Step 2）→ allow / deny / review_required
↓
Tool Permission Policy（Step 3）
↓
Tool Approval Check（Step 4）→ allow / deny / review_required
↓
[if shell/Bash] Observability Data Boundary（Step 5）
↓
[if shell/Bash] Command Execution Gate（Step 6）
↓
[if approved] Execute Tool
```

## Payment flow

```
Payment Intent
↓
Agent Spending Policy（Step 7）
↓
Payment Review（Step 8）→ allow / deny / review_required
↓
[if allowed] Budget Check（Step 9, paid）
↓
[after payment] Payment Action Record（Step 10）
↓
Payment Control Evidence Packet（Step 11）
↓
[if needed] Payment Evidence Check（Step 12, paid）
```

## Combined flow (tool use + payment)

```
AI Agent Action
↓
Memory Provenance Context Record（Step 1）
↓
Search Result Trust Check（Step 2）→ allow / deny / review_required
↓
Tool Permission Policy（Step 3）
↓
Tool Approval Check（Step 4）→ allow / deny / review_required
↓
Observability Data Boundary（Step 5, if applicable）
↓
Command Execution Gate（Step 6, if shell command）
↓
Agent Spending Policy（Step 7）
↓
Payment Review（Step 8）→ allow / deny / review_required
↓
Budget Check（Step 9, paid）
↓
Agent Payment Action Record（Step 10）
↓
Payment Control Evidence Packet（Step 11）
↓
Payment Evidence Check（Step 12, paid）
```

## Key rules

- Free materials create structure and policy
- Paid checks perform real validation
- Approval gates return allow / deny / review_required
- All materials can feed into Evidence Packet for audit
- Steps 2, 4, and 8 are approval gates — they must be called before downstream actions
- Steps 9 and 12 are paid checks via x402 on Base (eip155:8453)

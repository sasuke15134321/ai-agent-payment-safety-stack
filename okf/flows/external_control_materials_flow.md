---
title: External Control Materials Flow
version: "0.3"
type: flow_description
---

# External Control Materials Flow v0.3

## Runtime tool use flow

```
Tool Use Request
↓
Memory Provenance（Step 1）
↓
Tool Permission Policy（Step 2）
↓
Tool Approval Check（Step 3）→ allow / deny / review_required
↓
[if shell/Bash] Observability Data Boundary（Step 4）
↓
[if shell/Bash] Command Execution Gate（Step 5）
↓
[if approved] Execute Tool
```

## Payment flow

```
Payment Intent
↓
Agent Spending Policy（Step 6）
↓
Payment Review（Step 7）→ allow / deny / review_required
↓
[if allowed] Budget Check（Step 8, paid）
↓
[after payment] Payment Action Record（Step 9）
↓
Payment Control Evidence Packet（Step 10）
↓
[if needed] Payment Evidence Check（Step 11, paid）
```

## Combined flow (tool use + payment)

```
AI Agent Action
↓
Memory Provenance Context Record（Step 1）
↓
Tool Permission Policy（Step 2）
↓
Tool Approval Check（Step 3）→ allow / deny / review_required
↓
Observability Data Boundary（Step 4, if applicable）
↓
Command Execution Gate（Step 5, if shell command）
↓
Agent Spending Policy（Step 6）
↓
Payment Review（Step 7）→ allow / deny / review_required
↓
Budget Check（Step 8, paid）
↓
Agent Payment Action Record（Step 9）
↓
Payment Control Evidence Packet（Step 10）
↓
Payment Evidence Check（Step 11, paid）
```

## Key rules

- Free materials create structure and policy
- Paid checks perform real validation
- Approval gates return allow / deny / review_required
- All materials can feed into Evidence Packet for audit
- Steps 3 and 7 are approval gates — they must be called before execution
- Steps 8 and 11 are paid checks via x402 on Base (eip155:8453)

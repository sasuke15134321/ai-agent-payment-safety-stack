# Financial Approval & Budget Governance Walkthrough

## Scenario

An AI agent discovered that solving a critical infrastructure problem requires:

* Purchasing an external API service for 30 days (cost: $500 USDC)
* Scaling up database capacity (cost: $200 USDC)
* Total spend: $700 USDC (approximately $700 USD)

The AI agent has authority to spend up to $100/month for routine operations. This request exceeds that limit.

**The question:** How does the governance layer help humans approve financial decisions by AI agents?

---

## The Budget Control Problem

### Without Governance

* AI agent can request any amount
* No visibility into spending decisions
* No approval workflow
* Unexpected charges to the organization
* Audit trail is unclear

### With Governance

* Budget requests require explicit approval
* Humans can see what's being requested and why
* Approval defines scope (what's allowed, what's blocked)
* Full audit trail
* Clear decision records

---

## Step 1: Budget Check Before Execution

Before executing the expensive remediation, the AI agent calls the Budget Guard API.

### Request

```bash
curl -X POST https://ai-agent-payment-safety-stack.onrender.com/api/budget/check \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "remediation_agent_001",
    "requested_amount_usdc": 700,
    "currency": "USDC",
    "remediation_id": "remediation_infra_001",
    "remediation_type": "infrastructure_scaling",
    "title": "Critical database scaling and API integration",
    "spending_reason": "Solve critical infrastructure bottleneck",
    "cost_breakdown": [
      {
        "item": "External API service (30 days)",
        "cost": 500,
        "vendor": "third_party_api.com"
      },
      {
        "item": "Database capacity scaling",
        "cost": 200,
        "provider": "cloud_provider"
      }
    ],
    "monthly_budget_limit": 100,
    "urgency": "high",
    "expected_roi": "critical system reliability"
  }'
```

### Response

```json
{
  "agent_id": "remediation_agent_001",
  "requested_amount_usdc": 700,
  "status": "requires_approval",
  "decision": "escalate_to_human_approval",
  "reason": "Requested amount (700 USDC) exceeds monthly budget (100 USDC)",
  "excess_amount": 600,
  "approval_required": true,
  "approval_level": "financial_review_required",
  "suggested_action": "submit_approval_request",
  "audit_log_id": "budget_check_001"
}
```

### What This Means

The Budget Guard determined:

* ❌ The request exceeds the AI agent's standard spending authority
* ✅ The request is reasonable and documented
* ⚠️ Human financial review is required
* → Next step: Create approval request

---

## Step 2: Generate Financial Approval Contract

Since budget approval is required, the AI agent (or a human stakeholder) creates an approval request through the Approval Unit Builder.

### Request

```bash
curl -X POST https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "budget_request",
    "approval_unit_type": "financial_approval",
    "title": "Approve $700 USDC for critical infrastructure scaling",
    "summary": "AI agent identified critical infrastructure bottleneck. Cost: $500 API service + $200 database scaling. Estimated ROI: system reliability.",
    "requested_amount_usdc": 700,
    "currency": "USDC",
    "currency_scope": "USDC_on_base",
    "cost_breakdown": [
      {
        "item": "External API service",
        "cost": 500,
        "duration": "30 days"
      },
      {
        "item": "Database capacity",
        "cost": 200,
        "duration": "ongoing"
      }
    ],
    "agent_monthly_limit": 100,
    "excess_amount": 600,
    "urgency": "high",
    "expected_benefit": "critical_system_reliability",
    "approver_role": "financial_lead"
  }'
```

### Response

```json
{
  "approval_question": "Approve $700 USDC spending for critical infrastructure scaling?",
  "recommended_human_action": "approve_with_conditions",
  "approval_unit_type": "financial_approval",
  "requested_amount": {
    "amount_usdc": 700,
    "currency": "USDC",
    "currency_scope": "USDC_on_base"
  },
  "if_approved": {
    "allowed_actions": [
      "execute_api_service_purchase",
      "scale_database_capacity",
      "spend_up_to_700_usdc"
    ],
    "still_blocked_actions": [
      "spend_beyond_700_usdc",
      "purchase_optional_services",
      "change_currency_without_approval"
    ]
  },
  "spending_governance": {
    "total_approved": 700,
    "api_service_approved": 500,
    "database_scaling_approved": 200,
    "contingency_allowed": 0
  },
  "approval_unit_hash": "sha256:financial_approval_hash...",
  "chain_anchor_status": "not_anchored"
}
```

---

## Step 3: What the Human Is Approving

**Key concept: Financial approval is also a scoped execution contract.**

When a human approves this financial decision contract, they are NOT approving:

* ❌ "Spend money on anything you want"
* ❌ "Spend beyond $700"
* ❌ "Change spending priorities without asking"

They ARE approving:

* ✅ "Spend exactly $700 USDC for these two specific items"
* ✅ "Execute API service purchase ($500)"
* ✅ "Execute database scaling ($200)"
* ✅ "Use USDC on Base blockchain"

### Spending Scope

```
Approved:
- $500 for External API service
- $200 for Database capacity
- Total: $700 USDC

Blocked:
- Any amount beyond $700
- Other optional services
- Currency changes (USDC → other coin)
- Multiple month extension without re-approval
```

### Why This Scope Matters

The AI agent could theoretically say:

> "I'll buy the $500 API service and use the remaining $200 for other optimizations."

But the approval contract says:

> "No. The remaining $200 is specifically for database scaling. Not flexible for other uses."

This prevents scope creep and keeps the human in control of financial decisions.

---

## Step 4: Financial Approval Criteria

### Human Decision Points

The approver (financial lead) reviews:

1. **Necessity** — Is this truly critical?
   - Yes: System reliability depends on it
   - Approve: ✅

2. **Cost Justification** — Is the cost reasonable?
   - $700 for 30-day API + infrastructure = $23/day
   - Typical rate for similar services: $25/day
   - Approve: ✅

3. **ROI** — What's the expected return?
   - Benefit: System remains stable, no outages
   - Cost: $700
   - ROI: Very high (preventing potential customer impact)
   - Approve: ✅

4. **Vendor Evaluation** — Is the vendor reliable?
   - Third-party API: 99.99% uptime SLA
   - Cloud provider: Existing trusted partner
   - Approve: ✅

5. **Duration** — Is the time frame appropriate?
   - 30-day API service: Reasonable for evaluation period
   - Database scaling: Ongoing (can be reviewed monthly)
   - Approve with conditions: ✅

### Decision

```json
{
  "decision": "approve_with_conditions",
  "approved_by": "financial_lead_001",
  "approved_at": "2026-05-25T10:30:00Z",
  "conditions": [
    "Monthly review required for database scaling cost",
    "API service must be re-evaluated at 30-day mark",
    "If cost exceeds $750 due to usage, requires new approval"
  ]
}
```

---

## Step 5: Why Budget Governance Matters

### Scenario: Without Financial Approval Governance

```
AI agent: "I'll buy this API service"
Cost: $500/month
What human approved: Nothing

Result after 3 months:
- $1,500 spent
- No one reviewed it
- No one knows why
- It shows up as mysterious charge
- Audit questions why this wasn't approved
```

### Scenario: With Financial Approval Governance

```
AI agent requests: $700 for API + database
Human approves: "Yes, these 2 items for this amount"
Decision recorded: Approval contract with hash

Result after 3 months:
- Month 1: $700 spent (within approval)
- Month 2: AI requests new $500 (30-day renewal)
- Human approves or denies
- Full audit trail: who approved what, when, why
- Clear records for compliance/finance
```

---

## Step 6: Currency and Payment Rail Governance

### The USDC Dimension

The approval contract specifies:

```json
{
  "currency": "USDC",
  "currency_scope": "USDC_on_base"
}
```

This means:

* ✅ Allowed: Spend USDC on Base blockchain
* ❌ Blocked: Spend JPYC (Japanese yen stablecoin) without new approval
* ❌ Blocked: Spend USDC on different blockchain (Polygon, Ethereum, etc.)
* ❌ Blocked: Use credit card or bank transfer without new approval

### Why This Matters

Different payment rails have different:

* Fees
* Speed
* Risk profiles
* Compliance requirements
* Tax implications (especially for JPYC)

By approving specific currency + rail, humans ensure:

* Transparent payment flow
* Predictable costs (no surprise fees)
* Compliance with organizational policy
* Clear audit trail

---

## Step 7: v0.1 Boundaries

### What v0.1 DOES

* ✅ Check budget against agent limits
* ✅ Generate financial approval contracts
* ✅ Define spending scope (allowed items, amounts, currency)
* ✅ Record approval decisions
* ✅ Audit spending against approvals

### What v0.1 DOES NOT

* ❌ Execute payments (separate payment processing system)
* ❌ Interact with blockchain wallets
* ❌ Convert currencies
* ❌ Process USDC/JPYC transfers
* ❌ Access bank accounts

### The Payment Flow

```
Governance Layer (v0.1):
"Approve $700 USDC spending for these items"

Payment Execution System (separate):
1. Initiate payment from wallet
2. Transfer USDC on Base
3. Execute smart contract
4. Record transaction hash
5. Return to governance layer

Governance Layer:
Record payment in audit log
```

The governance layer is the decision layer. A separate system executes the decision.

---

## Example: Monthly Budget Review

### Month 1: Initial Approval

```json
{
  "approval": "Approve $700 for API service + database",
  "approved_amount": 700,
  "approver": "financial_lead_001",
  "valid_until": "2026-06-25"
}
```

### Month 2: Renewal Request

```bash
curl -X POST https://ai-agent-payment-safety-stack.onrender.com/api/approval-unit/build \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "budget_request",
    "approval_unit_type": "financial_renewal",
    "title": "Approve renewal of API service ($500 USDC for next 30 days)",
    "summary": "API service performing well. Requests: 50K/month. Uptime: 99.99%. Renewing for another 30 days.",
    "requested_amount_usdc": 500,
    "previous_approval_hash": "sha256:financial_approval_hash...",
    "approval_period": "30_days",
    "metrics": {
      "requests_per_month": 50000,
      "uptime": 99.99,
      "cost_per_request": 0.01,
      "roi": "critical_for_system_stability"
    }
  }'
```

### Decision

```json
{
  "decision": "approve_renewal",
  "approved_amount": 500,
  "approval_duration": "30_days",
  "review_required_before": "2026-07-25"
}
```

Each month, humans re-review. This prevents:

* Forgotten standing charges
* Silent cost increases
* Vendor lock-in without periodic review
* Outdated spending justifications

---

## Key Insights: Financial Governance

| Aspect | Without Governance | With Governance |
|--------|-------------------|-----------------|
| **Approval** | Implicit / unclear | Explicit contract |
| **Scope** | Unlimited | Defined (amount, items, currency) |
| **Audit** | Missing | Full trail with hashes |
| **Review** | One-time? | Periodic renewal |
| **Vendor changes** | Untracked | Requires new approval |
| **Currency changes** | Untracked | Blocks without new approval |
| **ROI review** | None | Required before approval |
| **Compliance** | At risk | Clear record |

---

## Why This Matters for AI Governance

**AI agents will spend money.** They'll call paid APIs, provision infrastructure, purchase services.

Without financial governance:

* Costs grow unexpectedly
* No one knows why decisions were made
* Audits reveal unknown charges
* Budget surprises the CFO

With financial governance:

* Every significant spend requires explicit human approval
* Decisions are documented with justification
* Approvals define scope (what's allowed, what's blocked)
* Humans review, AI executes approved decisions
* Full audit trail for compliance

**The financial approval contract is the same concept as the security approval contract.**

Approval is not a button to approve "whatever the AI wants."

Approval is a scoped execution contract that defines exactly what's allowed, what's blocked, and why.

Humans decide. Governance layer records. Systems execute only what's approved.

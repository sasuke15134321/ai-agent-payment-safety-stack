# Agent Decision Provenance Spec

## /api/agent/verify-decision

AIエージェントの支払い・承認・支払い解放・評判更新などの判断根拠を検証するAPI仕様案。

---

## Design Philosophy

AI agents can explain their decisions convincingly.
But the origin of those decisions may not be traceable.

A decision may come from:
- verified evidence
- long-term memory
- policy rules
- RAG results
- learned patterns
- unverifiable reasoning

The most dangerous case is a decision that sounds confident but has no verifiable origin.

Agent Decision Provenance is a deterministic verification layer placed outside the AI.
It checks whether an AI agent's decision is grounded in evidence, memory, or policy,
or whether it is based on unverifiable pattern-based reasoning.

This design follows the principle:
Wrap probabilistic AI with a deterministic external layer.

**Critical distinction**:
- Confidence is reported metadata, not governance authorization.
- The governance layer produces deterministic verdicts, not probabilistic permission.

---

## 目的

AIエージェントが「なぜその判断をしたか」を後から検証・証明できるようにする。
支払い承認・支払い拒否・タスク完了判定・評判更新などの意思決定に対して、根拠・参照情報・ポリシーを記録・検証する。

---

## input schema

```json
{
  "agent_id": "string — 判断を行ったエージェントID",
  "decision_type": "payment_approve | payment_reject | task_complete | reputation_update | budget_override",
  "decision_context": {
    "instruction": "string — エージェントが受け取った指示・プロンプト",
    "instruction_hash": "string — 指示のSHA-256ハッシュ",
    "referenced_data": ["string — 参照したデータソースURL・ID"],
    "timestamp": "ISO8601"
  },
  "evidence": {
    "payment_ref": "string (任意) — 関連する決済のtx_hashまたはreceipt_id",
    "task_ref": "string (任意) — 関連するタスクID",
    "memory_ids": ["string — 参照したメモリID (agent-memory-api)"],
    "policy_ref": "string — 参照したポリシーID・バージョン"
  },
  "memory_used": {
    "recalled_memory_ids": ["string"],
    "memory_summary": "string — 参照メモリの要約 (説明的メタデータ、証跡ではない)"
  },
  "policy_used": {
    "policy_id": "string",
    "policy_version": "string",
    "policy_hash": "string — ポリシー内容のSHA-256ハッシュ"
  }
}
```

---

## output schema

```json
{
  "provenance_id": "string — 一意の検証ID",
  "decision": {
    "type": "payment_approve | payment_reject | task_complete | ...",
    "verdict": "verified | unverified | requires_review",
    "confidence": "number (0.0-1.0) — AI self-reported confidence (not governance decision)"
  },
  "evidence_status": {
    "payment_ref_valid": "bool",
    "memory_ids_resolvable": "bool",
    "policy_found": "bool",
    "instruction_hash_matches": "bool"
  },
  "memory_used": {
    "resolved_memories": ["object — 参照できたメモリの概要"],
    "unresolvable_ids": ["string — 参照できなかったメモリID"]
  },
  "policy_used": {
    "policy_found": "bool",
    "policy_hash_matches": "bool",
    "policy_summary": "string"
  },
  "trust_score": "number (0-10) — 判断の信頼性スコア",
  "unsupported_claims": [
    "string — 根拠が確認できなかった主張のリスト"
  ],
  "requires_human_review": "bool",
  "human_review_reasons": ["string — レビューが必要な理由"],
  "provenance_score": "number (0-10) — 証跡の完全性スコア",
  "stored_at": "ISO8601",
  "provenance_hash": "string — このレコード全体のSHA-256ハッシュ"
}
```

---

## Score and Verdict Definitions

### provenance_score vs trust_score

**provenance_score** (0-10):
- Measures traceability and resolvability of decision origins
- Indicates whether evidence, memory, and policy sources can be resolved and verified
- Hash validation, reference availability, documented chain of reasoning

**trust_score** (0-10):
- Includes provenance_score plus governance factors
- Adds: policy match, unsupported claims detection, conflict detection, review requirements
- Higher holistic assessment of decision reliability

**Critical principle**: **Score ≠ authorization.**

Neither score authorizes execution. Both are advisory for human review and routing.

### memory_summary handling

**Summary ≠ source of truth.**

Memory summary is descriptive metadata, not evidence.

Verification targets resolved memory_ids (resolvable, hashable, auditable).
AI-generated summary is information about evidence, not evidence itself.

---

## decision_type 一覧

| type | 説明 |
|------|------|
| payment_approve | 支払い承認 |
| payment_reject | 支払い拒否 |
| payment_release | 支払い解放（エスクロー解除） |
| task_complete | タスク完了判定 |
| reputation_update | 評判スコア更新 |
| budget_override | 予算上限の例外承認 |
| memory_write | 長期メモリへの書き込み承認 |

---

## use cases

### ケース1：支払い承認の根拠検証
```
AIエージェントが0.20 USDCの支払いを承認した
→ /api/agent/verify-decision でpayment_approveの根拠を確認
→ どのポリシーに基づいて承認したか、参照したメモリは何か を検証
→ provenance_hash を監査ログに保存
```

### ケース2：タスク完了後の支払い解放
```
ワーカーエージェントがタスクを完了と報告
→ /api/agent/verify-decision でtask_completeの根拠確認
→ 成果物の参照・評価根拠が証跡に含まれているか確認
→ requires_human_review == false なら支払い解放
```

### ケース3：評判スコア更新の監査
```
エージェントが別エージェントの評判スコアを更新しようとする
→ /api/agent/verify-decision でreputation_updateの根拠を事前検証
→ 根拠不十分 → unsupported_claims に記録 → requires_human_review = true
```

---

## Payment Safety Stackとの接続

本仕様は以下のLive APIと統合される設計：

```
POST /api/remediation/verify (Live API)
    ↓ AI-generated fix validation
POST /api/approval-unit/build (Live API, 0.05 USDC)
    ↓ Human decision contract generation
Agent Decision Provenance (this spec)
    ↓ Decision root cause verification & audit trail
x402 Payment (決済実行)
    ↓
agent-memory-api (Design spec: post-execution audit layer)
    ↓ provenance_id + provenance_hash を監査ログとして保存
```

**Note**: Previous references to agent-security-gateway (/api/security/scan) and agent-budget-guard (/api/budget/check) are design concepts, not current Live APIs.

---

## Core Principle

**Decision ≠ Provenance.**

AI agents make decisions. These decisions may sound plausible.
But plausibility is not traceability.

A decision that seems reasonable does not automatically mean its root causes are documented, 
resolvable, and auditable. This specification ensures that what an AI agent decided 
can be separately verified from WHY that decision was made and whether the reasoning 
chain is traceable.

---

## 実装フェーズ

- **現在**：仕様書として整理（API実装なし）
- **中期**：agent-evolution-engineのオーケストレーションフローに組み込み
- **長期**：agent-memory-apiとの統合で永続的な証跡チェーンを構成

---

## Status

**This is a design specification.**
- It does not indicate that a runtime API has already been implemented.
- It is part of the 13 confirmed design specs.
- It does not add a new Live API.

**Version information**:
- Spec version: 2026-05-27 revision
- Original draft: 2026-05-19
- Revised: 2026-05-27

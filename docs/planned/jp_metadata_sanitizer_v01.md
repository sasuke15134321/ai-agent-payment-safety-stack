# JP Metadata Sanitizer
# v0.1 仕様書
# 最終更新：2026-05-29

> **Status: Specification draft only. Not implemented. Not deployed. Do not call this endpoint.**

> **位置づけ：** L4 Pre-Payment Guard / L6 Safety Check
> **戦略根拠：** STRATEGY.md / EXTERNAL_PRIMITIVE_MAP.md 参照
> **実装方針：** まず md として仕様公開

---

## 一言で言えば

AIエージェントがx402 / A2A / AtoA支払い時のメタデータに、余計な情報・漏洩リスク・混入が含まれていないかを確認する API。

英語：

> Scan payment metadata (x402/A2A/AtoA) for accidental exposure of personal information, contract details, credentials, or internal memos before transmission to external services.

---

## なぜ必要か

AIエージェントが支払いを実行する際、メタデータに以下が混入する可能性がある：

```
個人情報（名前・メールアドレス・電話番号）
契約情報（機密な交渉内容・条件）
インボイス情報（銀行口座・個人番号等）
社内メモ（プロジェクト内部情報・意思決定理由）
認証情報（APIキー・パスワード・シークレット）
```

支払いメタデータはファシリテーター・決済レール・ブロックチェーンノードを経由して外部に流出する。この確認を外部 API として持つ需要が増える。

---

## API仕様

### Endpoint

```
POST /api/jp/metadata/sanitize
```

### 価格

```
0.03〜0.10 USDC / scan
```

### AIが呼ぶタイミング

- 支払い前：JP Counterparty / Invoice Check 後、支払い実行直前
- メタデータ確認：x402 / A2A / AtoA のいずれの支払い前にも適用可能
- ファシリテーター手前：外部サービスへのメタデータ送信前の最終チェック

---

## 入力（Request Body）

```json
{
  "payment_protocol": "x402",
  "metadata_payload": {
    "payer_agent_id": "agent-translation-001",
    "payee": "api.example.com",
    "payment_purpose": "translation_service",
    "project_context": "Internal Project X - Confidential",
    "internal_memo": "Budget approved by finance team",
    "contact_email": "john@company.example.com"
  },
  "context_type": "x402",
  "payer_agent_id": "agent-translation-001",
  "payee": "api.example.com",
  "payment_purpose": "translation_service",
  "scan_targets": ["personal_info", "contract_info", "credential", "internal_memo"]
}
```

### 入力フィールド説明

| フィールド | 必須 | 説明 |
|-----------|------|------|
| payment_protocol | ✅ | 支払いプロトコル（x402 / jpyc / other） |
| metadata_payload | ✅ | スキャン対象のメタデータオブジェクト |
| context_type | ✅ | x402 / A2A / AtoA / other |
| payer_agent_id | ✅ | 支払い実行 AI エージェント ID |
| payee | ✅ | 支払い先（ドメイン・API ID） |
| payment_purpose | ✅ | 支払い目的分類 |
| scan_targets | △ | スキャン対象カテゴリ（指定しない場合は全て） |

---

## 出力（Response Body）

```json
{
  "sanitization_status": "flagged",
  "detected_sensitive_fields": ["contact_email", "internal_memo"],
  "detected_categories": ["personal_info", "internal_memo"],
  "flagged_fields": ["contact_email", "internal_memo"],
  "redaction_required": true,
  "risk_level": "high",
  "safe_to_send_to_payment_metadata": false,
  "issues": [
    {
      "field": "contact_email",
      "category": "personal_info",
      "risk": "pii_exposure",
      "reason": "Email address detected - should not be transmitted to external API"
    },
    {
      "field": "internal_memo",
      "category": "internal_memo",
      "risk": "confidential_context",
      "reason": "Internal project reference detected"
    }
  ],
  "requires_human_review": true,
  "recommended_next_step": "remove_flagged_fields_or_block_payment",
  "audit_ready": false
}
```

### 出力フィールド説明

| フィールド | 説明 |
|-----------|------|
| sanitization_status | メタデータ衛生化ステータス（ok / flagged / blocked） |
| detected_sensitive_fields | 検出された機密フィールド名リスト |
| detected_categories | 検出されたカテゴリリスト |
| flagged_fields | 問題のあるフィールド名リスト |
| redaction_required | マスキング・削除が必要か |
| risk_level | リスク度合い（low / medium / high） |
| safe_to_send_to_payment_metadata | 支払いメタデータとして安全に送信可能か（必須フィールド） |
| issues | 検出内容の詳細リスト |
| requires_human_review | 人間確認が必要か |
| recommended_next_step | 推奨される次のアクション |
| audit_ready | 監査ログに記録可能か |

---

## 判定ステータス定義

| 値 | 意味 |
|----|------|
| ok | メタデータに問題なし・送信可能 |
| flagged | 潜在的リスク検出・人間確認推奨 |
| blocked | 高リスク検出・支払い前に対応必須 |

---

## 判定例

### ケース1：安全（ok）

```json
{
  "sanitization_status": "ok",
  "detected_sensitive_fields": [],
  "detected_categories": [],
  "flagged_fields": [],
  "redaction_required": false,
  "risk_level": "low",
  "safe_to_send_to_payment_metadata": true,
  "issues": [],
  "requires_human_review": false,
  "recommended_next_step": "proceed_with_payment",
  "audit_ready": true
}
```

### ケース2：フラグ（flagged）

```json
{
  "sanitization_status": "flagged",
  "detected_sensitive_fields": ["project_context"],
  "detected_categories": ["internal_memo"],
  "flagged_fields": ["project_context"],
  "redaction_required": true,
  "risk_level": "medium",
  "safe_to_send_to_payment_metadata": false,
  "issues": [
    {
      "field": "project_context",
      "category": "internal_memo",
      "risk": "internal_reference",
      "reason": "Internal project name may leak business strategy"
    }
  ],
  "requires_human_review": true,
  "recommended_next_step": "remove_field_and_retry_or_approve_with_caution",
  "audit_ready": false
}
```

### ケース3：ブロック（blocked）

```json
{
  "sanitization_status": "blocked",
  "detected_sensitive_fields": ["email", "api_key"],
  "detected_categories": ["personal_info", "credential"],
  "flagged_fields": ["email", "api_key"],
  "redaction_required": true,
  "risk_level": "high",
  "safe_to_send_to_payment_metadata": false,
  "issues": [
    {
      "field": "email",
      "category": "personal_info",
      "risk": "pii_exposure",
      "reason": "Personal email address - BLOCKED"
    },
    {
      "field": "api_key",
      "category": "credential",
      "risk": "credential_leakage",
      "reason": "API key detected - BLOCKED"
    }
  ],
  "requires_human_review": true,
  "recommended_next_step": "block_payment_and_remediate",
  "audit_ready": false
}
```

---

## やらないこと

```
- 送信されたメタデータを保存・ログしない
- メタデータを外部に送信しない
- 支払いを実行しない
- 支払いレール機能を提供しない
- x402 / JPYC / USDC のファシリテーター機能を提供しない
- 法律判断・コンプライアンス判断をしない
- 個人情報を復号・復元しない
- メタデータの内容から個人を特定しない
- v0.1ではAI生成メタデータの検出は行わない
```

このAPIは「検出・フラグ・ルーティング」に徹する。

---

## agent-security-gateway との関係

**派生・拡張として実装可能**

JP Metadata Sanitizer は agent-security-gateway の拡張として実装可能。

### 位置づけの違い

| API | スコープ | 対象 | 実装形態 |
|-----|---------|------|---------|
| agent-security-gateway | プロンプト注入・不正指示検出 | 支払い指示そのもの（request body） | 独立 API |
| JP Metadata Sanitizer | メタデータ漏洩リスク検出 | メタデータ欄（payment metadata） | security-gateway の拡張・派生可 |

### 実装オプション

**オプション A：独立 API**
- 別エンドポイント `/api/jp/metadata/sanitize` として実装
- agent-security-gateway とは分離
- 呼び出し順序：security-gateway（指示チェック）→ metadata-sanitizer（メタデータチェック）

**オプション B：security-gateway 統合**
- agent-security-gateway の `/api/security/scan` に metadata scanning 機能を追加
- single endpoint で prompt injection + metadata sanitization を実行
- 効率性向上・呼び出し数削減

**オプション C：ミドルウェア**
- x402 payment middleware として実装
- 全 x402 支払いのメタデータを自動スキャン
- API 呼び出し不要（透過的）

v0.1 では仕様のみ。v0.2 以降で実装オプションを決定。

---

## JP Counterparty / Invoice Check との接続

JP Counterparty / Invoice Check は **相手先身元確認**、
JP Metadata Sanitizer は **メタデータ安全確認** を行う。

**呼び出し順序：**

1. JP Counterparty / Invoice Check → 相手先確認（支払い先は信頼できるか）
2. JP Metadata Sanitizer → メタデータ確認（送付するメタデータは安全か）
3. 支払い実行

---

## JP Payment Evidence Guard との接続

JP Metadata Sanitizer は支払い **前** のメタデータをスキャン。
JP Payment Evidence Guard は支払い **後** の成果物・応答を確認。

**フロー：**

```
JP Counterparty Check → JP Metadata Sanitizer → Payment → JP Payment Evidence Guard → audit-memory-api
```

Metadata Sanitizer の output（flagged_fields / risk_level）は Payment Evidence Guard の input として参照可能。「メタデータに既知の問題あり」という context を提供。

---

## v0.2以降への積み残し

```
- AI生成メタデータの異常検出（パターン学習）
- 言語別メタデータ検出（日本語特有の個人情報パターン）
- PII（Personally Identifiable Information）データベース連携
- サードパーティ API との秘匿性検証
- メタデータの難読化・マスキング提案
- v0.2以降での実装オプション決定（独立 / security-gateway 統合 / middleware）
- ブロック判定後の自動修復提案
- 多言語メタデータサポート
```

---

## 実装判断（v0.1時点）

現時点では以下の順で進める：

**D案（採用可能）：** まず md・openapi.yaml・llms.txt・agent.json として仕様を公開し、市場テスト

**実装選択肢：**
- オプション A（後続）：独立 API として実装
- オプション B（後続）：agent-security-gateway に統合
- オプション C（後続）：payment middleware として実装

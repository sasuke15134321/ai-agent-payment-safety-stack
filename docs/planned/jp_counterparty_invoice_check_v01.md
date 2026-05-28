# JP Counterparty / Invoice Check
# v0.1 仕様書
# 最終更新：2026-05-29

> **Status: Specification draft only. Not implemented. Not deployed. Do not call this endpoint.**

> **位置づけ：** L6 Trust / Source / Counterparty Check
> **戦略根拠：** STRATEGY.md / EXTERNAL_PRIMITIVE_MAP.md 参照
> **実装方針：** まず md・openapi.yaml・llms.txt・agent.json として仕様公開

---

## 一言で言えば

AIエージェントが支払い前・支払い後・月次証跡化の前に、支払い先・請求元・法人番号・インボイス登録番号の整合性を確認する API。

英語：

> Verify that counterparty names, invoice registration numbers, and corporate numbers are consistent across payment records and Japanese tax compliance requirements.

---

## なぜ必要か

支払い前には予算確認（agent-budget-guard）を行い、支払い後には成果物確認（JP Payment Evidence Guard）を行う。

しかし、その間に以下が欠落しやすい：

```
支払い先の名義が一貫しているか
請求元の法人番号は正しいか
適格請求書登録番号は有効か
支払い目的と請求内容は対応しているか
月次監査のための証跡は揃っているか
```

x402 / JPYC / USDC による AI エージェント間決済が増えるほど、この確認を外部 API として持つ需要が増える。

---

## API仕様

### Endpoint

```
POST /api/jp/counterparty-invoice/check
```

### 価格

```
0.02 USDC / check
```

### AIが呼ぶタイミング

- 支払い前：予算確認（agent-budget-guard）後、支払い実行前
- 支払い後：成果物確認（JP Payment Evidence Guard）後、月次証跡化前
- 月次証跡化：月次パック（JP Monthly Evidence Pack）に含める前

---

## 入力（Request Body）

```json
{
  "counterparty_name": "Example Corporation",
  "payment_recipient_name": "Example Corp Japan Branch",
  "invoice_registration_number": "T1234567890123",
  "corporate_number": "1234567890123",
  "payment_asset": "USDC",
  "payment_purpose": "translation_service",
  "transaction_reference": "tx-2026-05-29-001",
  "evidence_ids": ["ev-001", "ev-002", "ev-003"]
}
```

### 入力フィールド説明

| フィールド | 必須 | 説明 |
|-----------|------|------|
| counterparty_name | ✅ | 支払い先企業の公式名称 |
| payment_recipient_name | ✅ | 請求書記載の受け取り人/部門名 |
| invoice_registration_number | ✅ | 適格請求書発行事業者登録番号（T〜で始まる） |
| corporate_number | ✅ | 法人番号（13桁） |
| payment_asset | ✅ | 支払いアセット（USDC / JPYC / JPY） |
| payment_purpose | ✅ | 支払い目的の分類（translation_service など） |
| transaction_reference | ✅ | 取引参照番号（支払い・請求を追跡するキー） |
| evidence_ids | △ | 既存の証跡 ID リスト |

---

## 出力（Response Body）

```json
{
  "counterparty_status": "verified | requires_review | unverified | mismatch",
  "invoice_registration_status": "valid | expired | unregistered | invalid_format",
  "corporate_number_verified": true,
  "name_match_status": "exact_match | partial_match | no_match",
  "missing_items": ["invoice_registration_number_blank", "corporate_number_mismatch"],
  "requires_human_review": true,
  "recommended_next_step": "verify_corporate_registration",
  "evidence_status": "sufficient | insufficient",
  "audit_ready": false
}
```

### 出力フィールド説明

| フィールド | 説明 |
|-----------|------|
| counterparty_status | 支払い先の総合ステータス |
| invoice_registration_status | 適格請求書登録番号の有効性 |
| corporate_number_verified | 法人番号が国税庁データベースで確認できたか |
| name_match_status | 企業名義の一致度（exact / partial / no_match） |
| missing_items | 不足・不一致の項目リスト |
| requires_human_review | 人間確認が必要か |
| recommended_next_step | 次に取るべきアクション推奨 |
| evidence_status | 証跡の充足度 |
| audit_ready | 月次監査パックに渡せるか |

### counterparty_status の定義

| 値 | 意味 |
|----|------|
| verified | 名義・法人番号・インボイス番号が全て一致・確認済み |
| requires_review | 確認不足の項目があるが致命的ではない |
| unverified | 確認しきれない項目があり、追加情報が必要 |
| mismatch | 名義・法人番号・インボイス番号が対応していない |

---

## 判定例

### ケース1：正常（audit_ready）

```json
{
  "counterparty_status": "verified",
  "invoice_registration_status": "valid",
  "corporate_number_verified": true,
  "name_match_status": "exact_match",
  "missing_items": [],
  "requires_human_review": false,
  "recommended_next_step": "proceed_to_monthly_pack",
  "evidence_status": "sufficient",
  "audit_ready": true
}
```

### ケース2：法人番号未確認

```json
{
  "counterparty_status": "requires_review",
  "invoice_registration_status": "valid",
  "corporate_number_verified": false,
  "name_match_status": "exact_match",
  "missing_items": ["corporate_number_verification_pending"],
  "requires_human_review": true,
  "recommended_next_step": "verify_corporate_registration",
  "evidence_status": "insufficient",
  "audit_ready": false
}
```

### ケース3：名義不一致

```json
{
  "counterparty_status": "mismatch",
  "invoice_registration_status": "valid",
  "corporate_number_verified": true,
  "name_match_status": "no_match",
  "missing_items": ["counterparty_name_mismatch", "payment_recipient_mismatch"],
  "requires_human_review": true,
  "recommended_next_step": "escalate_to_human_for_name_verification",
  "evidence_status": "insufficient",
  "audit_ready": false
}
```

---

## やらないこと

```
- 税務判断しない
- 法律判断しない
- 仕入税額控除の可否を判断しない
- 適格請求書として法的に完全かを断定しない
- 税理士業務を代替しない
- 相手先の与信判断をしない
- v0.1ではリアルタイム国税庁API・法人番号API連携を行わない
```

このAPIは「確認・証跡・ルーティング」に徹する。

---

## 接続関係

```
agent-budget-guard                    → 支払い前確認（L4）
        ↓
JP Counterparty / Invoice Check       → 支払い先確認（L6）← このAPI
        ↓
    支払い実行（x402 / JPYC / USDC）
        ↓
JP Payment Evidence Guard             → 支払い後確認（L5）
        ↓
agent-memory-api                      → 証跡保存（L8）
        ↓
JP Monthly Evidence Pack              → 月次証跡パック（L8上位商品）
```

---

## JP Payment Evidence Guard との接続

JP Payment Evidence Guard は **支払い後** に支払いと成果物の対応を確認するのに対し、
JP Counterparty / Invoice Check は **支払い前後** に支払い先の身元確認を行う。

**呼び出し順序：**

1. agent-budget-guard → 予算確認
2. **JP Counterparty / Invoice Check** → 支払い先身元確認
3. 支払い実行
4. JP Payment Evidence Guard → 成果物確認
5. agent-memory-api → 証跡保存

**共通点：**
- 両方とも Live API ではなく specification draft
- 両方とも確認・ルーティング・証跡に徹する
- 両方とも tax/legal judgment をしない

---

## agent-memory-api との接続

agent-memory-api は証跡を **暗号化して保存** する。
JP Counterparty / Invoice Check の結果は agent-memory-api に保存し、月次パックに含める。

**保存項目：**
- counterparty_status
- invoice_registration_status
- corporate_number_verified
- audit_ready
- timestamp
- evidence_ids

---

## JP Monthly Evidence Pack との接続

JP Monthly Evidence Pack は月次会計・監査用パック。
JP Counterparty / Invoice Check で `audit_ready: true` となった証跡のみを月次パックに含める。

**パック内での役割：**
- 支払い者：AIエージェント ID
- 支払い目的：payment_purpose
- 支払い先：counterparty_name（検証済み）
- インボイス登録番号：invoice_registration_number（検証済み）
- 法人番号：corporate_number（検証済み）
- 監査対応可：audit_ready: true

---

## v0.2以降への積み残し

```
- error_codes / validation_errors の追加
- 国税庁 適格請求書発行事業者公表システムWeb-APIとの連携検討
- 国税庁 法人番号Web-APIとの連携検討
- リアルタイム照会ではなく、キャッシュ/スナップショット方式も検討
- キャッシュの更新戦略（法人番号・インボイス番号の変更に対応）
- 月次集計データとの突合
- JP Monthly Evidence Pack フォーマット統一
- multi-language support
```

---

## 実装判断（v0.1時点）

現時点では以下の順で進める：

**D案（採用可能）：** まず md・openapi.yaml・llms.txt・agent.json として仕様を公開し、市場テスト

**実装選択肢：**
- A案（後続）：既存 ai-agent-payment-safety-stack に追加実装
- B案（後続）：JP Payment Evidence Guard と統合実装
- C案（後続）：新規小 API として Render に出す

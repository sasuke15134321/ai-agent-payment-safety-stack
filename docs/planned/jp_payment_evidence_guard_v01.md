# JP Payment Evidence Guard
# v0.1 仕様書
# 最終更新：2026-05-28

> **Status: Specification draft only. Not implemented. Not deployed. Do not call this endpoint.**

> **位置づけ：** L5 Post-Payment Evidence
> **戦略根拠：** STRATEGY.md / EXTERNAL_PRIMITIVE_MAP.md 参照
> **実装方針：** まず /llms.txt・openapi.yaml として店頭テスト（D案）

---

## 一言で言えば

AIエージェントが支払い後に、その支払いとAPI応答・成果物・証跡が対応しているか確認するAPI。

英語：

> Verify that an AI-agent payment produced the expected service response and audit evidence.

---

## なぜ必要か

決済レール・ファシリテーター・ウォレットは、支払いの実行までを担う。

しかし以下は担わない：

```
支払いと成果物が対応しているか
API応答は実際に返ったか
証跡は次のAIや人間確認に渡せる状態か
日本ローカルの請求・会計・監査に耐えられるか
```

x402 / JPYC / USDC / Kova / Tempo / AP2 / ACP が広がるほど、この確認を外部APIとして持つ需要が増える。

---

## API仕様

### Endpoint

```
POST /api/jp/payment-evidence/check
```

### 価格

```
0.03 USDC / check
```

### AIが呼ぶタイミング

- x402 / JPYC / USDC 支払い直後
- API応答受取後
- 次のAIへ結果を渡す前
- 月次証跡へ保存する前

---

## 入力（Request Body）

```json
{
  "payment_protocol": "x402 | jpyc | usdc | other",
  "asset": "USDC | JPYC | JPY | other",
  "amount": 0.03,
  "payer_agent_id": "agent-abc-001",
  "payee": "api.example.com",
  "payment_purpose": "translation_api_call",
  "service_endpoint": "https://api.example.com/translate",
  "service_response_received": true,
  "expected_output_type": "translated_text",
  "actual_output_summary": "200文字の翻訳テキストが返却された",
  "invoice_registration_number": "T1234567890123",
  "corporate_number": "1234567890123",
  "evidence_ids": ["ev-001", "ev-002"]
}
```

### 入力フィールド説明

| フィールド | 必須 | 説明 |
|-----------|------|------|
| payment_protocol | ✅ | 使用した支払いプロトコル |
| asset | ✅ | 支払いアセット種別 |
| amount | ✅ | 支払い金額 |
| payer_agent_id | ✅ | 支払いを行ったAIエージェントのID |
| payee | ✅ | 支払い先（ドメイン or ID） |
| payment_purpose | ✅ | 支払い目的の分類 |
| service_endpoint | ✅ | 呼び出したAPIのエンドポイント |
| service_response_received | ✅ | API応答が返ったか（boolean） |
| expected_output_type | ✅ | 期待していた成果物の種別 |
| actual_output_summary | ✅ | 実際に返ってきた成果物の要約 |
| invoice_registration_number | △ | 適格請求書発行事業者登録番号（日本向け） |
| corporate_number | △ | 法人番号（日本向け） |
| evidence_ids | △ | 既存の証跡IDリスト |

---

## 出力（Response Body）

```json
{
  "evidence_status": "ok | requires_review | insufficient | failed",
  "payment_response_matched": true,
  "service_response_received": true,
  "missing_items": ["invoice_registration_verified"],
  "requires_human_review": true,
  "recommended_next_step": "verify_invoice_registration",
  "audit_ready": false
}
```

### 出力フィールド説明

| フィールド | 説明 |
|-----------|------|
| evidence_status | 証跡の総合ステータス |
| payment_response_matched | 支払いとAPI応答が対応しているか |
| service_response_received | サービス応答が実際に返ったか |
| missing_items | 不足している証跡・確認項目のリスト |
| requires_human_review | 人間確認が必要か |
| recommended_next_step | 次に取るべきアクションの推奨 |
| audit_ready | 監査・月次証跡パックに渡せる状態か |

### evidence_status の定義

| 値 | 意味 |
|----|------|
| ok | 支払い・応答・証跡がすべて対応している |
| requires_review | 確認不足の項目があるが致命的ではない |
| insufficient | 証跡が不十分で次工程に渡せない |
| failed | 支払いと応答・成果物が対応していない |

---

## 判定例

### ケース1：正常（audit_ready）

```json
{
  "evidence_status": "ok",
  "payment_response_matched": true,
  "service_response_received": true,
  "missing_items": [],
  "requires_human_review": false,
  "recommended_next_step": "proceed_to_next_agent",
  "audit_ready": true
}
```

### ケース2：インボイス番号未確認

```json
{
  "evidence_status": "requires_review",
  "payment_response_matched": true,
  "service_response_received": true,
  "missing_items": ["invoice_registration_verified"],
  "requires_human_review": true,
  "recommended_next_step": "verify_invoice_registration",
  "audit_ready": false
}
```

### ケース3：成果物不一致

```json
{
  "evidence_status": "failed",
  "payment_response_matched": false,
  "service_response_received": true,
  "missing_items": ["output_match", "delivery_evidence"],
  "requires_human_review": true,
  "recommended_next_step": "escalate_to_human",
  "audit_ready": false
}
```

---

## やらないこと

```
- 決済しない
- ファシリテーターにならない
- 法律判断しない
- 税務判断しない
- 成果物の絶対的正しさを保証しない
- 支払いを自動承認しない（automatic approval decisions）
- 相手先の与信判断をしない（counterparty credit check）
- 証跡確認・ルーティング・監査準備分類のみ行う（evidence routing only）
```

このAPIは「確認・証跡・ルーティング」に徹する。

---

## 接続関係

```
agent-budget-guard          → 支払い前確認（L4）
        ↓
    支払い実行（x402 / JPYC / USDC）
        ↓
JP Payment Evidence Guard   → 支払い後確認（L5）← このAPI
        ↓
agent-memory-api            → 証跡保存（L8）
        ↓
JP Monthly Evidence Pack    → 月次証跡パック（L8上位商品）
```

---

## 実装判断（v0.1時点）

現時点では以下の順で進める：

**D案（採用）：** まず /llms.txt・openapi.yaml として仕様を公開し、店頭テスト

```
Step 1：openapi.yaml 作成
Step 2：llms.txt に追記
Step 3：/.well-known/agent.json に追記
Step 4：Agentic.Market / CDP Bazaar への掲載確認
Step 5：反応を見てから実装判断（A〜C案）
```

**A案（後続）：** 既存 ai-agent-payment-safety-stack に設計追加
**B案（後続）：** agent-memory-api / agent-budget-guard と接続
**C案（後続）：** 新規小APIとしてRenderに出す

---

## v0.2以降への積み残し

```
- error_codes / validation_errors の追加
- JP Counterparty / Invoice Check との連携
- Metadata Sanitizer との連携
- x402 payment_receipt フィールドの追加
- Replay用の evidence_bundle 出力
```

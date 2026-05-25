# Agent Approval Unit Builder - Project Context

## Project Overview
Agent Approval Unit Builder API v0.1 converts AI-generated findings, patches, payment requests, deployment proposals, memory writes, tool execution requests, or decision-support outputs into minimal human decision contracts (Approval Units).

Core concept: **Approval Unit = Human Decision Contract**

## Implementation Status

### x402 & CDP Bazaar Integration
**Dynamic routes実装完了（2026-05-25）**
- `/.well-known/x402` を CDP Bazaar 標準の dynamic routes 形式に更新
- `/api/approval-unit/build` エンドポイントを含む（0.05 USDC）
- resources 配列内に各エンドポイントをフル仕様で記載
  - `accepts`: 支払い要件（scheme, network, amount, asset, payTo）
  - `extensions.bazaar.info`: input/output schemas
  - `type`: "http"
  - `x402Version`: 2
- CDP Bazaar クローラー検出待ち

## Architecture Notes
- **Payment Middleware**: x402 exact payment scheme on Base mainnet (eip155:8453)
- **Endpoints**: 
  - `POST /api/approval-unit/build` (0.05 USDC) - Paid endpoint
  - `POST /api/remediation/verify` (Free) - Verification gate
- **Bazaar Discovery**: Automatic discovery via /.well-known/x402 for CDP Bazaar facilitators

## Dependencies
- FastAPI
- Pydantic
- x402 payment infrastructure (Coinbase Commerce)

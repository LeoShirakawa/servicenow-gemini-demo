# 製薬業界向け ServiceNow × Gemini Enterprise デモ計画

## 1. エグゼクティブサマリー

**目的**: 製薬企業のCFOに対し、ServiceNow と Google Gemini Enterprise の連携による IT運用コスト削減・業務効率化の価値を実証する。

**ターゲット**: CFO（最高財務責任者）
**フォーカス**: コスト削減、ROI、運用効率、リスク低減

---

## 2. デモ構成

### 2.1 アーキテクチャ概要

```
[ServiceNow Instance] ←→ [Gemini Enterprise Connector] ←→ [Google Cloud / Vertex AI]
       ↓                                                          ↓
  ITSM / ITOM / ITFM                                    Gemini 2.5 Pro/Flash
  インシデント管理                                         自然言語処理
  変更管理                                                要約・分類・予測
  ナレッジベース                                           多言語対応
```

### 2.2 ServiceNow アカウント情報

| 項目 | 値 |
|------|-----|
| アカウント | （ServiceNow管理者アカウント） |
| パスワード | （管理者パスワード） |
| インスタンスURL | `https://<YOUR_INSTANCE>.service-now.com` |

---

## 3. デモシナリオ（CFO向け 3部構成）

### シナリオ1: AI駆動インシデント対応 — MTTR 50%削減の実証

**ストーリー**: 製薬会社の基幹システム（SAP）でバッチ処理が失敗。Gemini が過去の類似インシデントを分析し、解決策を自動提案。

**CFOへの訴求ポイント**:
- MTTR（平均復旧時間）50%削減 → ダウンタイムコスト年間 ¥2億削減シミュレーション
- L1エンジニアの対応能力向上 → 人件費最適化

**デモフロー**:
1. インシデント発生（SAP バッチジョブ失敗）
2. Gemini が自動でインシデントを分類・優先度設定
3. 過去の類似インシデント（ナレッジベース）から解決策を自動提案
4. 解決策のサマリーを日本語で生成
5. **ダッシュボード**: MTTR改善トレンド、コスト削減効果をリアルタイム表示

### シナリオ2: インテリジェント変更管理 — リスク予測と承認効率化

**ストーリー**: GxP対応システムの変更リクエスト。Gemini がリスク分析を行い、過去の変更失敗パターンから影響度を予測。

**CFOへの訴求ポイント**:
- 変更失敗率30%低減 → 障害対応コスト削減
- 承認プロセス自動化 → 管理工数40%削減
- コンプライアンスリスクの定量化

**デモフロー**:
1. 変更リクエスト起票（本番DBパッチ適用）
2. Gemini がリスクスコアを自動算出（過去の類似変更分析）
3. 影響を受けるCI（Configuration Item）を自動特定
4. 承認者への要約レポート自動生成
5. **ダッシュボード**: 変更成功率推移、リスクスコア分布

### シナリオ3: IT財務可視化 — コスト最適化レコメンデーション

**ストーリー**: 四半期レビューに向けて、IT運用コストの分析とGeminiによる最適化提案。

**CFOへの訴求ポイント**:
- IT支出の部門別・サービス別可視化
- AI による異常コスト検知と最適化提案
- 予算対実績の自動分析レポート

**デモフロー**:
1. IT財務ダッシュボード表示（部門別コスト分析）
2. Gemini が異常な支出パターンを検知・アラート
3. コスト最適化の推奨アクション提示
4. 自然言語での質問応答（「前四半期比でインフラコストが増加した要因は？」）
5. **サマリーレポート**: CFO向け定型レポート自動生成

---

## 4. サンプルデータ設計

### 4.1 インシデントデータ（100件）

| フィールド | 設定値例 |
|-----------|---------|
| short_description | 製薬業界特有のシステム障害（SAP, LIMS, MES, EDC等） |
| category | Software, Hardware, Network, Database |
| priority | 1-Critical, 2-High, 3-Moderate, 4-Low |
| state | New, In Progress, Resolved, Closed |
| assignment_group | SAP Support, Infrastructure, Network, Application |
| business_impact | GxP系/非GxP系で分類 |
| opened_at | 過去6ヶ月分（2025-09〜2026-03） |
| resolved_at | MTTRが計算可能な日時 |
| close_notes | 解決策の詳細（ナレッジ連携用） |

### 4.2 変更リクエストデータ（50件）

| フィールド | 設定値例 |
|-----------|---------|
| short_description | パッチ適用、設定変更、マイグレーション等 |
| type | Standard, Normal, Emergency |
| risk | High, Moderate, Low |
| state | New, Assess, Authorize, Implement, Review, Closed |
| cmdb_ci | 関連するCI |

### 4.3 ナレッジ記事（30件）

| フィールド | 設定値例 |
|-----------|---------|
| short_description | 障害対応手順、FAQ、ベストプラクティス |
| category | Troubleshooting, How-To, FAQ |
| text | 詳細な手順（Gemini検索対象） |

### 4.4 コストデータ（ITFM用）

| カテゴリ | 月額（万円） | 備考 |
|---------|------------|------|
| インフラ（クラウド） | 3,500 | GCP/AWS |
| ソフトウェアライセンス | 2,800 | SAP, ServiceNow等 |
| 人件費（IT部門） | 5,200 | 80名想定 |
| 外注費 | 1,500 | SI/運用委託 |
| セキュリティ | 800 | SOC, EDR等 |
| ネットワーク | 600 | 拠点間接続 |

---

## 5. 技術実装計画

### Phase 1: 環境準備（Day 1）

| タスク | 詳細 | 所要時間 |
|--------|------|---------|
| 1-1 | ServiceNow Developer Instance 確認・ログイン | 30分 |
| 1-2 | Gemini Enterprise コネクタのインストール（ServiceNow Store） | 1時間 |
| 1-3 | Google Cloud プロジェクトとの連携設定（OAuth/API Key） | 1時間 |
| 1-4 | Vertex AI API 有効化・サービスアカウント設定 | 30分 |

### Phase 2: サンプルデータ投入（Day 1-2）

| タスク | 詳細 | 所要時間 |
|--------|------|---------|
| 2-1 | ServiceNow REST API 用 Python スクリプト作成 | 2時間 |
| 2-2 | インシデントデータ投入（100件） | 30分 |
| 2-3 | 変更リクエストデータ投入（50件） | 30分 |
| 2-4 | ナレッジ記事投入（30件） | 30分 |
| 2-5 | CMDB データ投入（CI情報） | 30分 |
| 2-6 | コストデータ投入 | 30分 |

### Phase 3: Gemini コネクタ設定（Day 2）

| タスク | 詳細 | 所要時間 |
|--------|------|---------|
| 3-1 | Now Assist（GenAI Controller）設定 | 1時間 |
| 3-2 | Gemini モデル接続テスト | 30分 |
| 3-3 | インシデント要約・分類の Prompt 設計 | 1時間 |
| 3-4 | ナレッジ検索連携設定 | 1時間 |

### Phase 4: ダッシュボード・レポート構築（Day 2-3）

| タスク | 詳細 | 所要時間 |
|--------|------|---------|
| 4-1 | CFO向けダッシュボード（Performance Analytics） | 2時間 |
| 4-2 | MTTR/コスト削減KPIウィジェット | 1時間 |
| 4-3 | AI活用効果のBefore/Afterビュー | 1時間 |
| 4-4 | 月次レポートテンプレート | 1時間 |

### Phase 5: デモリハーサル（Day 3）

| タスク | 詳細 | 所要時間 |
|--------|------|---------|
| 5-1 | シナリオ1〜3の通しリハーサル | 2時間 |
| 5-2 | バックアッププラン準備 | 30分 |
| 5-3 | デモスクリプト最終化 | 1時間 |

---

## 6. CFO向け ROI サマリー（デモ中に提示）

### 想定効果（年間）

| 効果項目 | 削減額（年間） | 根拠 |
|---------|-------------|------|
| MTTR短縮によるダウンタイム削減 | ¥2.0億 | MTTR 50%改善 × 年間インシデント数 |
| L1対応自動化 | ¥0.8億 | チケットの30%を自動解決 |
| 変更管理効率化 | ¥0.5億 | 承認プロセス40%短縮 |
| レポート作成自動化 | ¥0.3億 | 月次レポート工数80%削減 |
| **合計** | **¥3.6億** | |

### 投資額

| 項目 | 年間コスト |
|------|----------|
| Gemini Enterprise ライセンス | ¥0.3億 |
| ServiceNow ITSM Pro + Now Assist | （既存想定） |
| 導入・カスタマイズ費用（初年度） | ¥0.5億 |
| **ROI** | **約 450%** |

---

## 7. デモ当日のアジェンダ（60分想定）

| 時間 | 内容 | 担当 |
|------|------|------|
| 0:00-0:05 | オープニング・アジェンダ説明 | Google |
| 0:05-0:15 | Gemini Enterprise × ServiceNow 概要 | Google |
| 0:15-0:30 | シナリオ1: AI駆動インシデント対応 | Google + SE |
| 0:30-0:40 | シナリオ2: インテリジェント変更管理 | Google + SE |
| 0:40-0:50 | シナリオ3: IT財務可視化・最適化 | Google + SE |
| 0:50-0:55 | ROIサマリー・導入ロードマップ | Google |
| 0:55-1:00 | Q&A | 全員 |

---

## 8. 次のステップ

1. [ ] ServiceNow インスタンスURL確認・ログインテスト
2. [ ] Gemini コネクタの利用可否確認（ServiceNow Store）
3. [ ] サンプルデータ投入スクリプト作成・実行
4. [ ] ダッシュボード構築
5. [ ] デモリハーサル
6. [ ] 顧客側のIT環境・課題ヒアリング（可能であれば事前に）

---

## 付録: ServiceNow REST API リファレンス

### 基本エンドポイント

```
Base URL: https://<instance>.service-now.com/api/now/table/

インシデント: /api/now/table/incident
変更リクエスト: /api/now/table/change_request
ナレッジ: /api/now/table/kb_knowledge
CMDB CI: /api/now/table/cmdb_ci
```

### 認証

```python
import requests

instance = "https://<your-instance>.service-now.com"
auth = ("<YOUR_USERNAME>", "<YOUR_PASSWORD>")
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

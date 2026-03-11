"""
ServiceNow サンプルデータ投入スクリプト（製薬業界向け）
CFOデモ用: インシデント、変更リクエスト、ナレッジ記事、CMDBデータを作成
"""

import json
import random
import requests
from datetime import datetime, timedelta

# ============================================================
# 設定 - ServiceNow インスタンス情報
# ============================================================
INSTANCE_URL = "https://<YOUR_INSTANCE>.service-now.com"  # TODO: 変更してください
USERNAME = "admin"  # TODO: 変更してください
PASSWORD = "<YOUR_PASSWORD>"  # TODO: 変更してください

AUTH = (USERNAME, PASSWORD)
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ============================================================
# ユーティリティ
# ============================================================

def create_record(table: str, data: dict) -> dict:
    """ServiceNow REST API でレコードを作成"""
    url = f"{INSTANCE_URL}/api/now/table/{table}"
    response = requests.post(url, auth=AUTH, headers=HEADERS, json=data)
    if response.status_code in (200, 201):
        result = response.json().get("result", {})
        print(f"  Created {table}: {result.get('number', result.get('sys_id', 'OK'))}")
        return result
    else:
        print(f"  ERROR creating {table}: {response.status_code} - {response.text[:200]}")
        return {}


def random_date(start_str: str, end_str: str) -> str:
    """ランダムな日時を生成（ServiceNow形式: YYYY-MM-DD HH:MM:SS）"""
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    dt = start + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# サンプルデータ定義（製薬業界向け）
# ============================================================

# --- インシデントデータ ---
INCIDENT_TEMPLATES = [
    # SAP関連
    {"short_description": "SAP ERP バッチジョブ異常終了 - 生産計画モジュール",
     "category": "Software", "subcategory": "Operating System",
     "impact": "2", "urgency": "1",
     "description": "SAP PP（生産計画）モジュールのバッチジョブが22:00の定時実行で異常終了。MRP計算が完了せず、翌日の生産指示に影響。エラーコード: SAPSYSTEM-001",
     "assignment_group": "SAP Support"},
    {"short_description": "SAP S/4HANA レスポンス低下 - 財務モジュール",
     "category": "Software", "subcategory": "Operating System",
     "impact": "2", "urgency": "2",
     "description": "SAP FI/CO モジュールのトランザクション応答時間が通常の3倍以上に劣化。月次決算処理に影響の可能性。",
     "assignment_group": "SAP Support"},
    {"short_description": "SAP BW データロード失敗 - 売上分析レポート",
     "category": "Software", "subcategory": "Operating System",
     "impact": "3", "urgency": "2",
     "description": "SAP BW/4HANAへの日次データロード（売上データ）が失敗。経営ダッシュボードのデータが更新されていない。",
     "assignment_group": "SAP Support"},

    # LIMS（実験室情報管理）関連
    {"short_description": "LIMS システム接続エラー - 品質管理部門",
     "category": "Software", "subcategory": "Application",
     "impact": "1", "urgency": "1",
     "description": "品質管理部門のLIMS（Laboratory Information Management System）が接続不可。GxP対象システムのため、品質試験が実施できず出荷判定に影響。",
     "assignment_group": "Application Support"},
    {"short_description": "LIMS 分析機器連携エラー - HPLCデータ取込不可",
     "category": "Hardware", "subcategory": "Peripherals",
     "impact": "2", "urgency": "2",
     "description": "HPLC（高速液体クロマトグラフィー）からLIMSへのデータ自動取込が停止。手動入力が必要な状態。",
     "assignment_group": "Application Support"},

    # MES（製造実行システム）関連
    {"short_description": "MES 製造指図同期エラー - 注射剤ライン",
     "category": "Software", "subcategory": "Application",
     "impact": "1", "urgency": "1",
     "description": "MES（Manufacturing Execution System）とSAP間の製造指図同期が失敗。注射剤製造ラインの生産開始が遅延。GxP影響あり。",
     "assignment_group": "Application Support"},
    {"short_description": "MES 電子バッチ記録エラー - 錠剤ライン",
     "category": "Software", "subcategory": "Application",
     "impact": "2", "urgency": "2",
     "description": "錠剤製造ラインの電子バッチ記録（EBR）で署名プロセスエラー。21 CFR Part 11準拠の電子署名が完了できない。",
     "assignment_group": "Application Support"},

    # EDC（電子データキャプチャ）関連
    {"short_description": "EDC システムアクセス不可 - Phase III 治験",
     "category": "Software", "subcategory": "Application",
     "impact": "1", "urgency": "1",
     "description": "Phase III治験のEDC（Electronic Data Capture）システムにアクセスできない。治験施設からのデータ入力が停止。被験者安全性報告にも影響。",
     "assignment_group": "Clinical Systems"},
    {"short_description": "EDC データバリデーションルール異常 - Phase II",
     "category": "Software", "subcategory": "Application",
     "impact": "3", "urgency": "3",
     "description": "Phase II治験のEDCバリデーションルールが誤って適用され、正常データがエラー判定される。CRAからの問い合わせ多数。",
     "assignment_group": "Clinical Systems"},

    # インフラ関連
    {"short_description": "データセンター空調異常 - サーバールームA",
     "category": "Hardware", "subcategory": "Facilities",
     "impact": "1", "urgency": "1",
     "description": "つくば研究所データセンターのサーバールームA空調ユニットが故障。室温が28°Cまで上昇。自動シャットダウン閾値は35°C。",
     "assignment_group": "Infrastructure"},
    {"short_description": "VPN接続不安定 - 海外拠点（米国）",
     "category": "Network", "subcategory": "VPN",
     "impact": "2", "urgency": "2",
     "description": "米国拠点（ノースカロライナ）からの VPN 接続が断続的に切断。現地50名のリモートワークに影響。",
     "assignment_group": "Network Support"},
    {"short_description": "ファイルサーバー容量逼迫 - 研究開発部門",
     "category": "Hardware", "subcategory": "Storage",
     "impact": "3", "urgency": "3",
     "description": "研究開発部門共有ファイルサーバーの使用率が95%に到達。新規ファイル保存に支障。ゲノムデータの急増が原因。",
     "assignment_group": "Infrastructure"},
    {"short_description": "Active Directory 認証遅延 - 全社",
     "category": "Software", "subcategory": "Authentication",
     "impact": "2", "urgency": "1",
     "description": "Active Directory の認証応答が10秒以上かかる事象が発生。全社的にログイン・アプリケーション認証に影響。",
     "assignment_group": "Infrastructure"},
    {"short_description": "メールサーバー送受信遅延 - Exchange Online",
     "category": "Software", "subcategory": "Email",
     "impact": "2", "urgency": "2",
     "description": "Exchange Online でメール送受信に最大30分の遅延。経営会議資料の共有に支障。",
     "assignment_group": "Infrastructure"},

    # セキュリティ関連
    {"short_description": "不審なログイン試行検知 - SAP本番環境",
     "category": "Software", "subcategory": "Security",
     "impact": "1", "urgency": "1",
     "description": "SAP本番環境で特権アカウントへの不審なログイン試行を検知。SOCチームによる調査が必要。",
     "assignment_group": "Security Operations"},
    {"short_description": "エンドポイントマルウェア検知 - 営業部門PC",
     "category": "Software", "subcategory": "Security",
     "impact": "2", "urgency": "1",
     "description": "EDR（CrowdStrike）が営業部門の3台のPCでマルウェアを検知。隔離済みだが、データ漏洩の調査が必要。",
     "assignment_group": "Security Operations"},

    # GCP/クラウド関連
    {"short_description": "GCP Cloud SQL レプリケーション遅延",
     "category": "Software", "subcategory": "Database",
     "impact": "3", "urgency": "3",
     "description": "GCP上のCloud SQLリードレプリカへのレプリケーション遅延が発生。分析系ワークロードの応答時間に影響。",
     "assignment_group": "Cloud Infrastructure"},
    {"short_description": "GKEクラスターノード不足 - AI/ML基盤",
     "category": "Software", "subcategory": "Application",
     "impact": "3", "urgency": "2",
     "description": "創薬AI/MLプラットフォーム用GKEクラスターのGPUノードが不足。モデル学習ジョブがキュー待ち状態。",
     "assignment_group": "Cloud Infrastructure"},
    {"short_description": "BigQuery コスト急増アラート - 研究開発部門",
     "category": "Software", "subcategory": "Application",
     "impact": "3", "urgency": "3",
     "description": "研究開発部門のBigQuery利用コストが前月比300%増。大規模クエリの最適化が必要。",
     "assignment_group": "Cloud Infrastructure"},
]

# --- 変更リクエストデータ ---
CHANGE_TEMPLATES = [
    {"short_description": "SAP S/4HANA セキュリティパッチ適用（2026年3月定期）",
     "type": "Normal", "risk": "Moderate",
     "description": "SAP S/4HANA本番環境への月次セキュリティパッチ適用。GxPバリデーション済み。影響: 4時間の計画停止。"},
    {"short_description": "LIMS バージョンアップグレード v12.3 → v13.0",
     "type": "Normal", "risk": "High",
     "description": "品質管理LIMSのメジャーバージョンアップ。FDA 21 CFR Part 11準拠の再バリデーション必要。"},
    {"short_description": "VPN ゲートウェイ機器交換 - 東京本社",
     "type": "Normal", "risk": "Moderate",
     "description": "東京本社VPNゲートウェイのEOL対応。Palo Alto PA-5200 → PA-5400シリーズへ交換。"},
    {"short_description": "Active Directory ドメインコントローラー追加",
     "type": "Normal", "risk": "Low",
     "description": "認証負荷分散のため、ADドメインコントローラーを2台追加。"},
    {"short_description": "GCP プロジェクト間ネットワーク再構成",
     "type": "Normal", "risk": "Moderate",
     "description": "Shared VPC構成の見直し。研究開発環境と本番環境のネットワーク分離強化。"},
    {"short_description": "EDC システム緊急パッチ - セキュリティ脆弱性対応",
     "type": "Emergency", "risk": "High",
     "description": "EDCシステムで重大なセキュリティ脆弱性（CVE-2026-XXXX）が発見。緊急パッチ適用。"},
    {"short_description": "メールシステム Microsoft 365 テナント統合",
     "type": "Normal", "risk": "High",
     "description": "グローバル拠点のMicrosoft 365テナント統合。約5,000メールボックスの移行。"},
    {"short_description": "ファイルサーバー容量拡張 - 研究開発部門",
     "type": "Standard", "risk": "Low",
     "description": "研究開発部門ファイルサーバーのストレージ拡張。20TB → 50TB。"},
    {"short_description": "MES データベースパフォーマンスチューニング",
     "type": "Normal", "risk": "Moderate",
     "description": "製造実行システムのOracle DBパフォーマンス改善。インデックス再構築とクエリ最適化。"},
    {"short_description": "セキュリティ監視システム SIEM ルール更新",
     "type": "Standard", "risk": "Low",
     "description": "Splunk SIEMの検知ルール更新。最新の脅威インテリジェンスに基づく検知精度向上。"},
    {"short_description": "社内Wi-Fi 6E 全社展開 - フェーズ2（研究棟）",
     "type": "Normal", "risk": "Moderate",
     "description": "研究棟（つくば・焼津）のWi-Fi 6E環境整備。AP 120台設置。"},
    {"short_description": "DR（災害復旧）環境 年次テスト実施",
     "type": "Normal", "risk": "Moderate",
     "description": "BCP対応の年次DRテスト。大阪DCへのフェイルオーバー演習。"},
    {"short_description": "SAP BW/4HANA → BigQuery データ連携パイプライン構築",
     "type": "Normal", "risk": "Moderate",
     "description": "SAP BWのデータをBigQueryにリアルタイム連携するパイプライン構築。経営ダッシュボード刷新の第一歩。"},
    {"short_description": "エンドポイントEDR ポリシー変更 - CrowdStrike",
     "type": "Standard", "risk": "Low",
     "description": "CrowdStrike Falcon のポリシー変更。USB制御ルールの厳格化。"},
    {"short_description": "GKE クラスター Kubernetes バージョンアップ v1.30",
     "type": "Normal", "risk": "Moderate",
     "description": "AI/ML基盤GKEクラスターのKubernetes v1.29 → v1.30 アップグレード。"},
]

# --- ナレッジ記事 ---
KNOWLEDGE_TEMPLATES = [
    {"short_description": "SAP バッチジョブ異常終了時の復旧手順",
     "category": "Troubleshooting",
     "text": """## SAP バッチジョブ異常終了時の復旧手順

### 症状
- SM37でジョブステータスが「Canceled」
- syslogにABAPダンプ記録

### 原因候補
1. メモリ不足（SM04確認）
2. テーブルロック競合（SM12確認）
3. 接続タイムアウト（SMGW確認）

### 復旧手順
1. SM37でジョブログを確認
2. ST22でABAPダンプの詳細を分析
3. 必要に応じてSM12でロック解除
4. ジョブを再スケジュール（SM36）
5. 再実行後、結果を確認

### エスカレーション
上記で解決しない場合はSAP Support（優先度: Medium以上）にチケット起票"""},

    {"short_description": "LIMS システム接続エラーのトラブルシューティング",
     "category": "Troubleshooting",
     "text": """## LIMS 接続エラー トラブルシューティング

### 確認手順
1. LIMSアプリケーションサーバーのステータス確認
2. データベース接続確認（Oracle RAC）
3. ネットワーク疎通確認（ping/traceroute）
4. SSL証明書の有効期限確認

### GxP注意事項
- LIMSはGxP対象システム。復旧作業はCSV手順書に従うこと
- 変更管理番号を取得してから作業開始
- 作業ログは必ず記録（21 CFR Part 11対応）"""},

    {"short_description": "VPN接続トラブル - ユーザー向けセルフヘルプガイド",
     "category": "How-To",
     "text": """## VPN接続トラブル セルフヘルプ

### 確認ステップ
1. インターネット接続を確認
2. VPNクライアント（GlobalProtect）を再起動
3. 社内認証情報（ID/パスワード）の有効期限を確認
4. 多要素認証（MFA）トークンを再発行

### それでも解決しない場合
- ヘルプデスクに連絡: ext.1234
- チケット起票: ServiceNow セルフサービスポータル"""},

    {"short_description": "GCP BigQuery コスト最適化ガイド",
     "category": "How-To",
     "text": """## BigQuery コスト最適化ガイド

### 即効性のある対策
1. SELECT * を避け、必要なカラムのみ指定
2. パーティションテーブルを活用
3. クエリの実行前にドライランでスキャン量を確認
4. マテリアライズドビューの活用

### 中長期的な対策
1. Flex Slots の検討（予約割引）
2. BI Engine の活用
3. データライフサイクル管理（古いデータのアーカイブ）
4. 部門別コスト配分の設定（ラベル活用）"""},

    {"short_description": "インシデント優先度判定基準 - 製薬業界ガイドライン",
     "category": "FAQ",
     "text": """## インシデント優先度判定基準

### Priority 1 (Critical)
- GxP対象システムの完全停止
- 患者安全性に直接影響
- 規制当局報告義務のあるシステム障害
- データセンター全体障害

### Priority 2 (High)
- GxP対象システムの部分的機能停止
- 製造ライン停止（1ライン以上）
- 500名以上が影響を受けるシステム障害

### Priority 3 (Moderate)
- 非GxPシステムの機能停止
- 回避策が存在する障害
- パフォーマンス劣化

### Priority 4 (Low)
- 個人レベルの問題
- 外観上の問題
- 情報提供依頼"""},

    {"short_description": "変更管理プロセス - GxPシステム向け手順",
     "category": "How-To",
     "text": """## GxPシステム変更管理プロセス

### フロー
1. 変更リクエスト起票（ServiceNow）
2. 影響度分析（CSV担当者）
3. リスクアセスメント
4. CAB（変更諮問委員会）レビュー
5. テスト計画策定・実施
6. 本番適用
7. PV（Post Validation）確認
8. クローズ

### 必須ドキュメント
- 変更要求書
- 影響度分析書
- テスト計画書/結果書
- リスクアセスメント
- 承認記録"""},

    {"short_description": "EDC システム障害時の BCP 手順",
     "category": "Troubleshooting",
     "text": """## EDC障害時BCP手順

### 即座に実施すること
1. 治験責任医師への連絡
2. 紙CRFへの切替判断
3. SAE（重篤な有害事象）報告手段の確保

### データ復旧後
1. 紙CRFデータの電子化
2. 監査証跡の確認
3. データマネジメント部門への報告"""},

    {"short_description": "セキュリティインシデント対応フロー",
     "category": "Troubleshooting",
     "text": """## セキュリティインシデント対応フロー

### 初動対応（30分以内）
1. インシデント検知・記録
2. 影響範囲の特定
3. 封じ込め（ネットワーク隔離等）
4. CSIRT への報告

### 調査・分析
1. フォレンジック調査
2. IOC（侵害指標）の特定
3. 攻撃ベクトルの分析

### 報告・改善
1. 経営層への報告
2. 必要に応じ規制当局・個人情報保護委員会への報告
3. 再発防止策の策定"""},

    {"short_description": "MES 電子バッチ記録（EBR）エラー対応",
     "category": "Troubleshooting",
     "text": """## MES EBR エラー対応

### 電子署名エラー
1. ユーザーの認証情報確認
2. タイムサーバー同期確認
3. 署名サーバーの証明書確認

### データ整合性エラー
1. バッチ記録のステータス確認
2. ワークフロー定義との整合性チェック
3. 必要に応じ手動介入（品質部門承認要）"""},

    {"short_description": "GCP 月次コストレビュー手順",
     "category": "How-To",
     "text": """## GCP月次コストレビュー手順

### 確認項目
1. Billing Console で全体コスト確認
2. プロジェクト別コスト内訳
3. サービス別コスト内訳
4. 予算アラートのステータス確認

### レポート作成
1. BigQueryエクスポートデータを活用
2. Looker Studioダッシュボードを更新
3. 部門別チャージバック計算
4. 翌月予測値の算出"""},
]

# --- CMDB Configuration Items ---
CMDB_ITEMS = [
    {"name": "SAP-S4HANA-PROD-01", "category": "Business Application",
     "short_description": "SAP S/4HANA 本番環境（財務・生産・販売）",
     "environment": "Production", "operational_status": "1"},
    {"name": "SAP-S4HANA-DEV-01", "category": "Business Application",
     "short_description": "SAP S/4HANA 開発環境",
     "environment": "Development", "operational_status": "1"},
    {"name": "LIMS-PROD-01", "category": "Business Application",
     "short_description": "LIMS 本番環境（品質管理）",
     "environment": "Production", "operational_status": "1"},
    {"name": "MES-PROD-01", "category": "Business Application",
     "short_description": "MES 本番環境（製造実行）",
     "environment": "Production", "operational_status": "1"},
    {"name": "EDC-PROD-01", "category": "Business Application",
     "short_description": "EDC 本番環境（治験データキャプチャ）",
     "environment": "Production", "operational_status": "1"},
    {"name": "GCP-PROJECT-AIML", "category": "Cloud Infrastructure",
     "short_description": "GCP AI/ML 基盤プロジェクト",
     "environment": "Production", "operational_status": "1"},
    {"name": "GCP-PROJECT-ANALYTICS", "category": "Cloud Infrastructure",
     "short_description": "GCP データ分析基盤プロジェクト",
     "environment": "Production", "operational_status": "1"},
    {"name": "DC-TSUKUBA-SRV-ROOM-A", "category": "Data Center",
     "short_description": "つくば研究所 データセンター サーバールームA",
     "environment": "Production", "operational_status": "1"},
    {"name": "VPN-GW-TOKYO-01", "category": "Network",
     "short_description": "東京本社 VPN ゲートウェイ",
     "environment": "Production", "operational_status": "1"},
    {"name": "AD-DC-TOKYO-01", "category": "Server",
     "short_description": "Active Directory ドメインコントローラー 東京",
     "environment": "Production", "operational_status": "1"},
]


# ============================================================
# データ投入関数
# ============================================================

def create_incidents(count: int = 100):
    """インシデントデータを作成"""
    print(f"\n{'='*60}")
    print(f"インシデントデータ作成中... ({count}件)")
    print(f"{'='*60}")

    states = [
        ("1", "New"),
        ("2", "In Progress"),
        ("6", "Resolved"),
        ("7", "Closed"),
    ]
    state_weights = [10, 15, 25, 50]  # Closedが多め

    for i in range(count):
        template = random.choice(INCIDENT_TEMPLATES)
        state = random.choices(states, weights=state_weights, k=1)[0]

        opened_at = random_date("2025-09-01", "2026-03-10")
        resolved_at = None
        closed_at = None

        if state[0] in ("6", "7"):  # Resolved or Closed
            # MTTR: Priority に応じて変動
            priority = int(template.get("urgency", "3"))
            if priority == 1:
                mttr_hours = random.randint(1, 8)
            elif priority == 2:
                mttr_hours = random.randint(4, 24)
            else:
                mttr_hours = random.randint(8, 72)

            opened_dt = datetime.strptime(opened_at, "%Y-%m-%d %H:%M:%S")
            resolved_dt = opened_dt + timedelta(hours=mttr_hours)
            resolved_at = resolved_dt.strftime("%Y-%m-%d %H:%M:%S")

            if state[0] == "7":
                closed_dt = resolved_dt + timedelta(hours=random.randint(1, 48))
                closed_at = closed_dt.strftime("%Y-%m-%d %H:%M:%S")

        # バリエーション追加
        suffix = f" (#{i+1:03d})"
        data = {
            "short_description": template["short_description"] + suffix,
            "description": template["description"],
            "category": template["category"],
            "impact": template["impact"],
            "urgency": template["urgency"],
            "state": state[0],
            "opened_at": opened_at,
            "assignment_group": template["assignment_group"],
        }
        if resolved_at:
            data["resolved_at"] = resolved_at
            data["close_notes"] = f"解決策: {template['short_description']}に対する標準手順で対応完了。"
            data["close_code"] = random.choice([
                "Solution provided", "Workaround provided",
                "Resolved by change", "Known error",
                "Resolved by caller", "Resolved by request",
            ])
        if closed_at:
            data["closed_at"] = closed_at

        create_record("incident", data)


def create_changes(count: int = 50):
    """変更リクエストデータを作成"""
    print(f"\n{'='*60}")
    print(f"変更リクエストデータ作成中... ({count}件)")
    print(f"{'='*60}")

    risk_map = {"High": "1", "Moderate": "2", "Low": "3"}
    type_map = {"Normal": "Normal", "Standard": "Standard", "Emergency": "Emergency"}
    states = ["-5", "-4", "-3", "-2", "-1"]  # New, Assess, Authorize, Scheduled, Implement

    for i in range(count):
        template = random.choice(CHANGE_TEMPLATES)
        state = random.choice(states)

        planned_start = random_date("2026-01-01", "2026-04-30")
        planned_start_dt = datetime.strptime(planned_start, "%Y-%m-%d %H:%M:%S")
        planned_end_dt = planned_start_dt + timedelta(hours=random.randint(2, 12))

        data = {
            "short_description": template["short_description"] + f" (#{i+1:03d})",
            "description": template["description"],
            "type": type_map.get(template["type"], "Normal"),
            "risk": risk_map.get(template["risk"], "2"),
            "state": state,
            "start_date": planned_start,
            "end_date": planned_end_dt.strftime("%Y-%m-%d %H:%M:%S"),
        }

        create_record("change_request", data)


def create_knowledge_articles():
    """ナレッジ記事を作成"""
    print(f"\n{'='*60}")
    print(f"ナレッジ記事作成中... ({len(KNOWLEDGE_TEMPLATES)}件)")
    print(f"{'='*60}")

    for template in KNOWLEDGE_TEMPLATES:
        data = {
            "short_description": template["short_description"],
            "text": template["text"],
            "workflow_state": "published",
            "valid_to": "2027-12-31",
        }
        create_record("kb_knowledge", data)


def create_cmdb_items():
    """CMDB CI データを作成"""
    print(f"\n{'='*60}")
    print(f"CMDB CI データ作成中... ({len(CMDB_ITEMS)}件)")
    print(f"{'='*60}")

    for item in CMDB_ITEMS:
        data = {
            "name": item["name"],
            "short_description": item["short_description"],
            "operational_status": item["operational_status"],
        }
        create_record("cmdb_ci", data)


# ============================================================
# メイン実行
# ============================================================

def main():
    print("=" * 60)
    print("製薬業界向け ServiceNow サンプルデータ投入")
    print("=" * 60)
    print(f"Instance: {INSTANCE_URL}")
    print(f"User: {USERNAME}")
    print()

    # 接続テスト
    print("接続テスト中...")
    try:
        test_url = f"{INSTANCE_URL}/api/now/table/incident?sysparm_limit=1"
        resp = requests.get(test_url, auth=AUTH, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            print("接続成功!")
        else:
            print(f"接続エラー: {resp.status_code}")
            print(f"レスポンス: {resp.text[:300]}")
            return
    except Exception as e:
        print(f"接続失敗: {e}")
        print("INSTANCE_URL を正しく設定してください。")
        return

    # データ投入
    create_cmdb_items()
    create_knowledge_articles()
    create_incidents(count=100)
    create_changes(count=50)

    print("\n" + "=" * 60)
    print("サンプルデータ投入完了!")
    print("=" * 60)


if __name__ == "__main__":
    main()

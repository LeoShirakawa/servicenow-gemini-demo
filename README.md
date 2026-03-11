# ServiceNow × Gemini Enterprise デモ環境構築（製薬業界向け）

ServiceNow と Google Cloud Gemini Enterprise（Agentspace）を連携させたCFOデモ環境を構築するための手順書とスクリプト一式。

---

## 前提条件

- Python 3.10+
- `requests` ライブラリ (`pip install requests`)
- `gcloud` CLI（認証済み）
- ServiceNow Developer Instance（admin権限）
- GCP プロジェクト（Vertex AI API 有効化済み）

---

## ファイル構成

```
servicenow-gemini-demo/
├── README.md                          # 本ファイル
├── create_sample_data.py              # IT運用サンプルデータ投入
├── create_helpdesk_data.py            # ヘルプデスク問い合わせデータ投入
├── setup_federation_prereqs.py        # Federation Connector 接続前準備
├── implementation_plan.md             # 全体計画書
├── implementation_plan_federation.md  # Federation設定計画書
├── demo_script.md                     # CFOデモ台本（IT運用シナリオ）
└── demo_scenario_helpdesk.md          # CFOデモ台本（ヘルプデスクシナリオ）
```

---

## 手順概要

```
Step 1  サンプルデータ投入（IT運用 + ヘルプデスク）
  ↓
Step 2  Federation Connector 接続前準備（GCP SA + OAuth + REST Message）
  ↓
Step 3  ServiceNow プラグイン有効化（GUI）
  ↓
Step 4  Google Cloud Agentspace コネクタ設定
  ↓
Step 5  デモリハーサル
```

---

## Step 1: サンプルデータ投入

### 1-1. IT運用データ（インシデント・変更リクエスト・ナレッジ・CMDB）

スクリプト冒頭の接続情報を対象インスタンスに合わせて編集する。

```python
# create_sample_data.py 内の設定
INSTANCE_URL = "https://<YOUR_INSTANCE>.service-now.com"
USERNAME = "admin"
PASSWORD = "<YOUR_PASSWORD>"
```

実行:

```bash
python3 create_sample_data.py
```

投入されるデータ:

| テーブル | 件数 | 内容 |
|---------|------|------|
| cmdb_ci | 10件 | SAP, LIMS, MES, EDC, GCP 等のCI |
| kb_knowledge | 10件 | 障害対応手順、ベストプラクティス |
| incident | 100件 | 製薬業界向けインシデント（SAP, LIMS, MES, EDC, セキュリティ等） |
| change_request | 50件 | パッチ適用、バージョンアップ、インフラ変更 |

注意事項:
- Resolved/Closed ステータスのインシデントには `close_code` と `close_notes` が必須（Data Policy）
- 変更リクエストのステートは `-5`〜`-1` のみ使用（Business Rule による遷移制約）

### 1-2. ヘルプデスク問い合わせデータ

```bash
python3 create_helpdesk_data.py
```

投入されるデータ:

| テーブル | 件数 | 内容 |
|---------|------|------|
| kb_knowledge | 6件 | パスワードリセット、VPN、LIMS、MFA、会議室AV、SAP経費精算 |
| incident | 150件 | LoBユーザーからの日常問い合わせ（経理・研究・営業・製造・人事） |

特徴:
- `contact_type` に `virtual_agent`, `self-service`, `phone`, `chat`, `email`, `walk-in` を設定
- `caller_id` に既存ユーザーの sys_id を設定（実ユーザーに紐づけ）
- Virtual Agent 経由のチケットは MTTR 2〜15分（AI自動解決を模擬）
- 製薬業界特有の問い合わせ（LIMS, MES, GxP, EDC）を含む

### 1-3. 別のインスタンスに投入する場合

各スクリプト冒頭の以下3行を変更して実行する。

```python
INSTANCE_URL = "https://<YOUR_INSTANCE>.service-now.com"
USERNAME = "admin"
PASSWORD = "<YOUR_PASSWORD>"
```

---

## Step 2: Federation Connector 接続前準備

### 2-1. 自動化スクリプト実行

GCPサービスアカウント作成、ServiceNow側のOAuth/REST Message設定を一括実行する。

```bash
python3 setup_federation_prereqs.py
```

このスクリプトが自動で行うこと:

| # | 処理 | 作成先 |
|---|------|-------|
| 1 | プラグイン有効化チェック（3件） | ServiceNow |
| 2 | GCPサービスアカウント作成 + キー発行 | GCP |
| 3 | IAM権限付与（`roles/aiplatform.user`, `roles/discoveryengine.viewer`） | GCP |
| 4 | OAuth 2.0 Provider（JWT Bearer） | ServiceNow `oauth_entity` |
| 5 | JWT Provider（SA秘密鍵登録） | ServiceNow `jwt_provider` |
| 6 | Connection Alias + Credential Alias | ServiceNow `sys_alias` |
| 7 | HTTP Connection Record | ServiceNow `http_connection` |
| 8 | REST Message（Gemini generateContent / streamGenerateContent） | ServiceNow `sys_rest_message` |
| 9 | AI Search System Properties | ServiceNow `sys_properties` |
| 10 | Now Assist / GenAI System Properties | ServiceNow `sys_properties` |

スクリプト実行後、以下が生成される:

- `servicenow_sa_key.json` — GCPサービスアカウントの秘密鍵（取扱注意）

設定値の変更:

```python
# setup_federation_prereqs.py 内の設定
SERVICENOW_INSTANCE = "https://<YOUR_INSTANCE>.service-now.com"
SERVICENOW_USER = "admin"
SERVICENOW_PASS = "<YOUR_PASSWORD>"

GCP_PROJECT = "<YOUR_GCP_PROJECT_ID>"
GCP_REGION = "us-central1"
GEMINI_MODEL = "gemini-2.5-pro"
```

### 2-2. Google Cloud Agentspace コネクタ用 OAuth Client

`setup_federation_prereqs.py` とは別に、Google Cloud 側から ServiceNow へ接続するための
OAuth Client（Application Registry）を作成する必要がある。

以下のコマンドで作成可能:

```python
import requests, secrets

INSTANCE_URL = "https://<YOUR_INSTANCE>.service-now.com"
AUTH = ("admin", "<YOUR_PASSWORD>")
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

data = {
    "name": "Google Cloud Agentspace Connector",
    "type": "client",
    "active": "true",
    "client_secret": secrets.token_urlsafe(32),
    "redirect_url": "https://vertexaisearch.cloud.google.com/oauth-redirect,https://vertexaisearch.cloud.google.com/console/oauth/default_oauth.html",
    "token_lifetime_seconds": "1800",
    "refresh_token_lifespan": "8640000",
    "default_grant_type": "password",
}

resp = requests.post(
    f"{INSTANCE_URL}/api/now/table/oauth_entity",
    auth=AUTH, headers=HEADERS, json=data
)
result = resp.json()["result"]
print(f"Client ID:     {result['client_id']}")
print(f"Client Secret: {result['client_secret']}")
```

作成後、Google Cloud コネクタ設定画面に以下を入力する:

| 項目 | 値 |
|------|-----|
| Instance URL | `https://<YOUR_INSTANCE>.service-now.com` |
| Client ID | （上記スクリプトの出力値） |
| Client Secret | （上記スクリプトの出力値） |
| Auth URI | `https://<YOUR_INSTANCE>.service-now.com/oauth_auth.do` |
| Token URI | `https://<YOUR_INSTANCE>.service-now.com/oauth_token.do` |
| User Account | `admin` |
| Password | （admin パスワード） |

**redirect_url の重要な注意**: Google Cloud が送信する `redirect_uri` は以下の2種類が確認されている。
OAuth Client の `redirect_url` に両方を登録しておくこと。

```
https://vertexaisearch.cloud.google.com/oauth-redirect
https://vertexaisearch.cloud.google.com/console/oauth/default_oauth.html
```

`Invalid redirect_uri` エラーが出た場合は、ブラウザのURLバーから `redirect_uri=` パラメータの値を
確認し、ServiceNow の OAuth Client に追加する。

---

## Step 3: ServiceNow プラグイン有効化（GUI操作）

以下のプラグインは API では有効化できないため、GUI から操作する。

### 有効化手順

1. ServiceNow にログイン
2. ナビゲーター検索バーに `v_plugin` と入力 → **System Plugins** を開く
   - URL直接: `https://<YOUR_INSTANCE>.service-now.com/nav_to.do?uri=v_plugin_list.do`
3. 以下を検索して **Install** または **Activate** をクリック

| プラグイン ID | 名前 |
|--------------|------|
| `com.glide.cs.genai` | Glide Conversation Generative AI |
| `com.now_assist_self_service` | Now Assist Self-Service |
| `com.glide.utilities.flow_designer_genai_extensions` | Flow Designer - Generative AI Extensions |

---

## Step 4: Google Cloud Agentspace コネクタ設定

### 4-1. コネクタ作成

1. Google Cloud Console → Agent Builder → Data Stores
2. **Create Data Store** → **ServiceNow** を選択
3. Step 2-2 で取得した接続情報を入力
4. 認証フロー完了後、同期対象のテーブルを選択:
   - `incident` — インシデント
   - `kb_knowledge` — ナレッジ記事
   - `change_request` — 変更リクエスト

### 4-2. ユーザー認証

エンドユーザーが Agentspace から ServiceNow データを検索する際、
OAuth 認証画面が表示される。`Invalid redirect_uri` エラーが出た場合:

1. エラー画面のブラウザURLバーから `redirect_uri=` の値をコピー
2. ServiceNow の OAuth Client (`oauth_entity`) の `redirect_url` に追加
   - URL: `https://<YOUR_INSTANCE>.service-now.com/nav_to.do?uri=oauth_entity_list.do`
   - 「Google Cloud Agentspace Connector」を開く → Redirect URL フィールドに追加（カンマ区切り）

---

## データ確認用リンク

以下の `<YOUR_INSTANCE>` をインスタンス名に置換してアクセスする。

- インシデント一覧: `https://<YOUR_INSTANCE>.service-now.com/incident_list.do`
- 変更リクエスト一覧: `https://<YOUR_INSTANCE>.service-now.com/change_request_list.do`
- ナレッジ記事一覧: `https://<YOUR_INSTANCE>.service-now.com/kb_knowledge_list.do`
- CMDB CI一覧: `https://<YOUR_INSTANCE>.service-now.com/cmdb_ci_list.do`
- OAuth Client一覧: `https://<YOUR_INSTANCE>.service-now.com/nav_to.do?uri=oauth_entity_list.do`
- REST Message一覧: `https://<YOUR_INSTANCE>.service-now.com/nav_to.do?uri=sys_rest_message_list.do`
- Connection Alias一覧: `https://<YOUR_INSTANCE>.service-now.com/nav_to.do?uri=sys_alias_list.do`
- System Properties: `https://<YOUR_INSTANCE>.service-now.com/nav_to.do?uri=sys_properties_list.do`

---

## トラブルシューティング

### インシデント作成で 403 エラー

```
Data Policy Exception: The following fields are mandatory: Resolution code
```

**原因**: Resolved (state=6) / Closed (state=7) のインシデントには `close_code` と `close_notes` が必須。

**対処**: データに以下を追加する。

```python
data["close_code"] = "Solution provided"  # or "Workaround provided" etc.
data["close_notes"] = "解決内容の説明"
```

有効な `close_code` 値:
`Solution provided`, `Workaround provided`, `Resolved by change`, `Known error`,
`Resolved by caller`, `Resolved by request`, `Resolved by problem`,
`User error`, `Duplicate`, `No resolution provided`

### 変更リクエスト作成で 403 エラー

```
Business Rule 'Change Model: Check State Transition' aborted
```

**原因**: 無効なステート遷移。新規作成時には特定のステートしか設定できない。

**対処**: `state` に `-5`（New）〜 `-1`（Implement）のみを使用する。`0`（Review）や `3`（Closed）は直接設定不可。

### Invalid redirect_uri エラー

**原因**: Google Cloud が送信する `redirect_uri` が ServiceNow OAuth Client の `redirect_url` に登録されていない。

**対処**:
1. エラー画面のブラウザURLから `redirect_uri=` パラメータを確認
2. URL デコードして実際の URI を取得
3. ServiceNow の OAuth Client (`oauth_entity`) → `redirect_url` に追加

### GCP サービスアカウントの IAM 権限付与エラー

```
Policy modification failed ... condition
```

**対処**: `gcloud alpha` を使用する。

```bash
gcloud alpha projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member="serviceAccount:<SA_EMAIL>" \
  --role="roles/aiplatform.user" \
  --condition=None --quiet
```

---

## セキュリティに関する注意

- `servicenow_sa_key.json` はGCPサービスアカウントの秘密鍵。Git にコミットしないこと
- ServiceNow の `admin` パスワードは本番環境では使用しないこと
- OAuth Client Secret は安全に管理すること
- デモ終了後、Developer Instance のパスワードを変更することを推奨

# ServiceNow Federation Connector 接続前準備 — API実装計画

## 対象インスタンス
- **URL**: `https://<YOUR_INSTANCE>.service-now.com`
- **アカウント**: admin

---

## 現状分析

### 利用可能な資産
| 項目 | 状態 | 備考 |
|------|------|------|
| OAuth 2.0 プラグイン | Active | `com.snc.platform.security.oauth` |
| Now Assist Core | Active | `com.now_assist_core` |
| AI Search Assist | Active | `com.snc.ai_search_assist` |
| Connection & Credential | Active | `com.snc.core.automation.connection_credential` |
| Google OAuth Provider | Active（テンプレートのみ） | Client ID 未設定、Token/Auth URL 空 |

### 未設定・未有効化
| 項目 | 状態 | 必要なアクション |
|------|------|-----------------|
| Generative AI Controller | 未インストール | プラグイン有効化が必要 |
| Now Assist Self-Service | Inactive | 有効化が必要 |
| Glide Conversation GenAI | Inactive | Virtual Agent + Gemini 連携に必要 |
| Flow Designer GenAI | Inactive | フロー内でのAI活用に必要 |
| Google OAuth 実設定 | テンプレートのみ | GCPプロジェクトのOAuth情報で設定 |
| GCP用 X.509 証明書 | なし | サービスアカウントキーの登録 |
| Google Cloud REST Message | なし | Vertex AI API 呼び出し用 |
| Connection Alias（GCP） | なし | Gemini API接続用 |

---

## 実装計画（8ステップ）

### Step 1: プラグイン有効化

API では直接有効化できないプラグインもあるため、**一部はGUI操作が必須**。APIで可能な範囲を自動化する。

```
有効化対象:
1. com.glide.cs.genai               — Glide Conversation Generative AI
2. com.now_assist_self_service       — Now Assist Self-Service
3. com.glide.utilities.flow_designer_genai_extensions — Flow Designer GenAI
```

**API実装**: プラグイン有効化リクエスト（`/api/now/cicd/plugin/{plugin_id}/activate`）

---

### Step 2: Google Cloud サービスアカウント証明書の登録

GCPサービスアカウントのJSON キーから X.509 証明書を ServiceNow に登録する。

**API実装**:
- `sys_certificate` テーブルに証明書レコードを作成
- JWT署名用の秘密鍵を登録

**必要な入力**:
- GCPサービスアカウントの JSON キーファイル
- プロジェクトID: `<YOUR_GCP_PROJECT_ID>`（既存）

---

### Step 3: OAuth 2.0 プロバイダー設定（Google Cloud / Vertex AI用）

既存の Google OAuth Provider テンプレートを更新、または新規作成して GCP Vertex AI 用に設定する。

**API実装**: `oauth_entity` テーブルの更新/作成

```json
{
  "name": "Google Cloud - Vertex AI",
  "type": "oauth_provider",
  "active": true,
  "client_id": "<GCP_CLIENT_ID>",
  "client_secret": "<GCP_CLIENT_SECRET>",
  "token_url": "https://oauth2.googleapis.com/token",
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
  "default_grant_type": "jwt",
  "scope": "https://www.googleapis.com/auth/cloud-platform"
}
```

**JWT Bearer Flow（サービスアカウント認証）用の追加設定**:
- `oauth_entity_profile` にJWTプロファイルを作成
- `jwt_provider` テーブルにJWTプロバイダーを登録

---

### Step 4: Connection & Credential Alias の作成

Federation Connector が使用する接続情報を定義する。

**API実装**: `sys_alias` テーブルにレコード作成

```json
{
  "name": "Google Cloud Vertex AI Connection",
  "type": "connection",
  "active": true
}
```

**Credential Alias**:
```json
{
  "name": "Google Cloud Vertex AI Credential",
  "type": "credential",
  "active": true
}
```

**Connection Record**（`sys_connection`）:
```json
{
  "name": "Vertex AI API",
  "connection_alias": "<alias_sys_id>",
  "host": "us-central1-aiplatform.googleapis.com",
  "protocol": "https",
  "port": "443",
  "credential": "<credential_sys_id>"
}
```

---

### Step 5: REST Message 定義（Vertex AI API呼び出し用）

Gemini API を呼び出すための REST Message を作成する。

**API実装**: `sys_rest_message` + `sys_rest_message_fn` テーブル

**エンドポイント定義**:

| メソッド名 | HTTP Method | Endpoint |
|-----------|-------------|----------|
| Generate Content | POST | `/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:generateContent` |
| Stream Generate | POST | `/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:streamGenerateContent` |

---

### Step 6: Now Assist GenAI Controller 設定

Now Assist が Gemini をバックエンドLLMとして使用するための設定。

**API実装**: GenAI Controller 関連テーブル（プラグイン有効化後に利用可能）

```
設定項目:
- LLM Provider: Google Cloud (Vertex AI)
- Model: gemini-2.5-pro
- Endpoint: Step 5 で作成した REST Message
- Authentication: Step 3-4 で作成した OAuth/Connection
```

---

### Step 7: AI Search Assist 設定（Federation用）

外部検索ソース（Google Cloud Search / Vertex AI Search）を ServiceNow の検索に統合する。

**API実装**: `sys_search_context_config` テーブルの設定更新

```
設定項目:
- Search Source: Vertex AI Search
- Connection: Step 4 の Connection Alias
- Result Mapping: ServiceNow フィールドへのマッピング
```

---

### Step 8: テスト用 System Property の設定

**API実装**: `sys_properties` テーブル

```json
[
  {"name": "glide.now_assist.enabled", "value": "true"},
  {"name": "sn.genai.default.provider", "value": "google_vertex_ai"},
  {"name": "sn.genai.incident.summarization.enabled", "value": "true"},
  {"name": "sn.genai.knowledge.search.enabled", "value": "true"}
]
```

---

## 実装の依存関係フロー

```
Step 1 (プラグイン有効化)
  ↓
Step 2 (証明書登録)  ←  GCPサービスアカウントキー（手動入力）
  ↓
Step 3 (OAuth設定)
  ↓
Step 4 (Connection/Credential Alias)
  ↓
Step 5 (REST Message)
  ↓
Step 6 (GenAI Controller)  ←  Step 1 完了後に利用可能
  ↓
Step 7 (AI Search設定)
  ↓
Step 8 (System Properties)
  ↓
★ Federation Connector 接続準備完了
```

---

## API自動化 vs GUI手動操作

| ステップ | API自動化 | GUI必須 | 備考 |
|---------|----------|---------|------|
| Step 1: プラグイン有効化 | △ | ○ | 一部プラグインはGUIから有効化推奨 |
| Step 2: 証明書登録 | ○ | — | API で完全自動化可能 |
| Step 3: OAuth設定 | ○ | — | API で完全自動化可能 |
| Step 4: Connection Alias | ○ | — | API で完全自動化可能 |
| Step 5: REST Message | ○ | — | API で完全自動化可能 |
| Step 6: GenAI Controller | △ | △ | プラグイン依存、一部GUI推奨 |
| Step 7: AI Search設定 | ○ | — | API で完全自動化可能 |
| Step 8: System Properties | ○ | — | API で完全自動化可能 |

---

## 必要な事前入力情報

スクリプト実行前に以下を準備してください:

1. **GCP プロジェクトID**: `<YOUR_GCP_PROJECT_ID>`（確認済み）
2. **GCP サービスアカウント JSON キー**: Vertex AI API 権限付き
3. **Vertex AI リージョン**: `us-central1`（推奨）
4. **使用モデル**: `gemini-2.5-pro`（推奨）
5. **（オプション）OAuth Client ID / Secret**: Web Application タイプ

---

## 次のアクション

承認いただければ、以下を実装します:

1. **`setup_federation_prereqs.py`** — Step 2〜5, 7〜8 の自動化スクリプト
2. **Step 1（プラグイン有効化）の GUI手順書** — スクリーンショット付き
3. **Step 6（GenAI Controller）の設定手順書**

"""
ServiceNow Federation Connector 接続前準備 自動化スクリプト

実行内容:
  Step 1: プラグイン有効化チェック（GUI手順を案内）
  Step 2: GCPサービスアカウント作成 & キー発行
  Step 3: ServiceNow に OAuth 2.0 JWT Provider 設定
  Step 4: Connection & Credential Alias 作成
  Step 5: REST Message 定義（Vertex AI Gemini API）
  Step 7: AI Search 関連 System Properties
  Step 8: Now Assist 関連 System Properties
"""

import base64
import json
import os
import subprocess
import sys
import time

import requests

# ============================================================
# 設定
# ============================================================
SERVICENOW_INSTANCE = "https://<YOUR_INSTANCE>.service-now.com"  # TODO: 変更してください
SERVICENOW_USER = "admin"  # TODO: 変更してください
SERVICENOW_PASS = "<YOUR_PASSWORD>"  # TODO: 変更してください

GCP_PROJECT = "<YOUR_GCP_PROJECT_ID>"  # TODO: 変更してください
GCP_REGION = "us-central1"
GCP_SA_NAME = "servicenow-connector"
GCP_SA_DISPLAY = "ServiceNow Federation Connector"
GEMINI_MODEL = "gemini-2.5-pro"

AUTH = (SERVICENOW_USER, SERVICENOW_PASS)
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

SA_KEY_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "servicenow_sa_key.json",
)


# ============================================================
# ユーティリティ
# ============================================================

def sn_get(table, query="", fields=""):
    """ServiceNow REST API GET"""
    params = {}
    if query:
        params["sysparm_query"] = query
    if fields:
        params["sysparm_fields"] = fields
    params["sysparm_limit"] = "10"
    url = f"{SERVICENOW_INSTANCE}/api/now/table/{table}"
    resp = requests.get(url, auth=AUTH, headers=HEADERS, params=params)
    if resp.status_code == 200:
        return resp.json().get("result", [])
    return []


def sn_create(table, data):
    """ServiceNow REST API POST (create)"""
    url = f"{SERVICENOW_INSTANCE}/api/now/table/{table}"
    resp = requests.post(url, auth=AUTH, headers=HEADERS, json=data)
    if resp.status_code in (200, 201):
        result = resp.json().get("result", {})
        return True, result
    return False, resp.text[:300]


def sn_update(table, sys_id, data):
    """ServiceNow REST API PATCH (update)"""
    url = f"{SERVICENOW_INSTANCE}/api/now/table/{table}/{sys_id}"
    resp = requests.patch(url, auth=AUTH, headers=HEADERS, json=data)
    if resp.status_code == 200:
        return True, resp.json().get("result", {})
    return False, resp.text[:300]


def run_gcloud(args, check=True):
    """gcloud コマンド実行"""
    cmd = ["gcloud"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  gcloud ERROR: {result.stderr[:300]}")
    return result


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================
# Step 1: プラグイン有効化チェック
# ============================================================

def step1_check_plugins():
    section("Step 1: プラグイン有効化チェック")

    required_plugins = [
        ("com.glide.cs.genai", "Glide Conversation Generative AI"),
        ("com.now_assist_self_service", "Now Assist Self-Service"),
        ("com.glide.utilities.flow_designer_genai_extensions", "Flow Designer GenAI"),
    ]

    needs_activation = []
    for plugin_id, plugin_name in required_plugins:
        results = sn_get("v_plugin", f"id={plugin_id}", "id,name,active")
        if results:
            status = results[0].get("active", "")
            if status == "active":
                print(f"  [OK] {plugin_name} ({plugin_id})")
            else:
                print(f"  [要有効化] {plugin_name} ({plugin_id})")
                needs_activation.append((plugin_id, plugin_name))
        else:
            print(f"  [未検出] {plugin_name} ({plugin_id})")
            needs_activation.append((plugin_id, plugin_name))

    if needs_activation:
        print("\n  以下のプラグインをGUIから有効化してください:")
        print(f"  URL: {SERVICENOW_INSTANCE}/nav_to.do?uri=v_plugin_list.do")
        for pid, pname in needs_activation:
            print(f"    - {pname} ({pid})")
        print("\n  手順: 上記URLにアクセス → プラグイン検索 → Install/Activate")

        # API経由でのプラグイン有効化を試行
        print("\n  API経由での有効化を試行中...")
        for pid, pname in needs_activation:
            url = f"{SERVICENOW_INSTANCE}/api/now/cicd/plugin/{pid}/activate"
            resp = requests.post(url, auth=AUTH, headers=HEADERS)
            if resp.status_code in (200, 201, 202):
                print(f"    [送信OK] {pname} — 有効化リクエスト受理")
            else:
                print(f"    [要GUI] {pname} — API有効化不可 ({resp.status_code})")

    return len(needs_activation) == 0


# ============================================================
# Step 2: GCPサービスアカウント作成 & キー発行
# ============================================================

def step2_create_gcp_sa():
    section("Step 2: GCPサービスアカウント作成 & キー発行")

    sa_email = f"{GCP_SA_NAME}@{GCP_PROJECT}.iam.gserviceaccount.com"

    # サービスアカウント存在チェック
    result = run_gcloud([
        "iam", "service-accounts", "describe", sa_email,
        f"--project={GCP_PROJECT}", "--format=json",
    ], check=False)

    if result.returncode == 0:
        print(f"  [既存] サービスアカウント: {sa_email}")
    else:
        print(f"  サービスアカウント作成中: {sa_email}")
        result = run_gcloud([
            "iam", "service-accounts", "create", GCP_SA_NAME,
            f"--project={GCP_PROJECT}",
            f"--display-name={GCP_SA_DISPLAY}",
        ])
        if result.returncode != 0:
            print("  [ERROR] サービスアカウント作成失敗")
            return None
        print("  [OK] 作成完了")

    # Vertex AI 権限付与
    print("  IAM 権限付与中...")
    roles = [
        "roles/aiplatform.user",
        "roles/discoveryengine.viewer",
    ]
    for role in roles:
        result = run_gcloud([
            "projects", "add-iam-policy-binding", GCP_PROJECT,
            f"--member=serviceAccount:{sa_email}",
            f"--role={role}",
            "--condition=None",
            "--quiet",
        ], check=False)
        if result.returncode == 0:
            print(f"    [OK] {role}")
        else:
            # 既に付与済みの場合もエラーにならないが念のため
            print(f"    [WARN] {role}: {result.stderr[:100]}")

    # キー発行
    if os.path.exists(SA_KEY_PATH):
        print(f"  [既存] キーファイル: {SA_KEY_PATH}")
    else:
        print(f"  キー発行中...")
        result = run_gcloud([
            "iam", "service-accounts", "keys", "create", SA_KEY_PATH,
            f"--iam-account={sa_email}",
            f"--project={GCP_PROJECT}",
        ])
        if result.returncode != 0:
            print("  [ERROR] キー発行失敗")
            return None
        print(f"  [OK] キーファイル: {SA_KEY_PATH}")

    # キー内容を読み込み
    with open(SA_KEY_PATH, "r") as f:
        sa_key = json.load(f)

    print(f"  SA Email: {sa_key.get('client_email', '')}")
    print(f"  Key ID:   {sa_key.get('private_key_id', '')[:16]}...")

    return sa_key


# ============================================================
# Step 3: OAuth 2.0 JWT Provider 設定
# ============================================================

def step3_setup_oauth(sa_key):
    section("Step 3: OAuth 2.0 Provider 設定（JWT Bearer for Google Cloud）")

    provider_name = "Google Cloud - Vertex AI (JWT)"

    # 既存チェック
    existing = sn_get("oauth_entity", f"name={provider_name}", "sys_id,name,active")
    if existing:
        sys_id = existing[0]["sys_id"]
        print(f"  [既存] OAuth Provider: {provider_name} (sys_id={sys_id})")
        return sys_id

    # OAuth Provider (oauth_entity) 作成
    # Google の JWT Bearer フローでは、ServiceNow からトークンエンドポイントに
    # JWT を送信してアクセストークンを取得する
    data = {
        "name": provider_name,
        "type": "oauth_provider",
        "active": "true",
        "client_id": sa_key.get("client_id", ""),
        "token_url": "https://oauth2.googleapis.com/token",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "default_grant_type": "jwt",
        "comments": f"GCP Project: {GCP_PROJECT}\nSA: {sa_key.get('client_email', '')}\nFor Vertex AI / Gemini API access",
    }

    ok, result = sn_create("oauth_entity", data)
    if ok:
        sys_id = result.get("sys_id", "")
        print(f"  [OK] OAuth Provider 作成: {provider_name} (sys_id={sys_id})")
        return sys_id
    else:
        print(f"  [ERROR] OAuth Provider 作成失敗: {result}")
        return None


# ============================================================
# Step 3b: JWT Provider 設定
# ============================================================

def step3b_setup_jwt_provider(sa_key):
    section("Step 3b: JWT Provider 設定")

    jwt_provider_name = "Google Cloud Vertex AI JWT"

    # 既存チェック
    existing = sn_get("jwt_provider", f"name={jwt_provider_name}", "sys_id,name")
    if existing:
        sys_id = existing[0]["sys_id"]
        print(f"  [既存] JWT Provider: {jwt_provider_name} (sys_id={sys_id})")
        return sys_id

    # JWT Provider 作成
    # private_key の PEM 形式を取得
    private_key = sa_key.get("private_key", "")

    data = {
        "name": jwt_provider_name,
        "signing_algorithm": "RSA 256",
        "signing_key_source": "User defined",
        "signing_key": private_key,
        "iss": sa_key.get("client_email", ""),
        "aud": "https://oauth2.googleapis.com/token",
        "sub": sa_key.get("client_email", ""),
        "expiry_interval": "3600",
        "active": "true",
    }

    ok, result = sn_create("jwt_provider", data)
    if ok:
        sys_id = result.get("sys_id", "")
        print(f"  [OK] JWT Provider 作成: {jwt_provider_name} (sys_id={sys_id})")
        return sys_id
    else:
        print(f"  [ERROR] JWT Provider 作成失敗: {result}")

        # jwt_provider テーブルが存在しない場合のフォールバック
        # sys_certificate に証明書を直接登録
        print("\n  フォールバック: X.509 証明書として登録中...")
        cert_data = {
            "name": "Google Cloud SA - ServiceNow Connector",
            "type": "trust_store",
            "format": "PEM",
            "pem_certificate": private_key,
            "active": "true",
        }
        ok2, result2 = sn_create("sys_certificate", cert_data)
        if ok2:
            print(f"  [OK] 証明書登録完了: {result2.get('sys_id', '')}")
            return result2.get("sys_id", "")
        else:
            print(f"  [ERROR] 証明書登録失敗: {result2}")
            return None


# ============================================================
# Step 4: Connection & Credential Alias
# ============================================================

def step4_setup_connection(sa_key, oauth_sys_id):
    section("Step 4: Connection & Credential Alias 作成")

    results = {}

    # 4a: Credential Alias
    cred_alias_name = "Google Cloud Vertex AI Credential"
    existing = sn_get("sys_alias", f"name={cred_alias_name}", "sys_id,name")
    if existing:
        cred_alias_id = existing[0]["sys_id"]
        print(f"  [既存] Credential Alias: {cred_alias_name}")
    else:
        ok, result = sn_create("sys_alias", {
            "name": cred_alias_name,
            "type": "credential",
            "active": "true",
        })
        if ok:
            cred_alias_id = result.get("sys_id", "")
            print(f"  [OK] Credential Alias 作成: {cred_alias_id}")
        else:
            print(f"  [ERROR] Credential Alias 作成失敗: {result}")
            cred_alias_id = None
    results["credential_alias"] = cred_alias_id

    # 4b: Connection Alias
    conn_alias_name = "Google Cloud Vertex AI Connection"
    existing = sn_get("sys_alias", f"name={conn_alias_name}", "sys_id,name")
    if existing:
        conn_alias_id = existing[0]["sys_id"]
        print(f"  [既存] Connection Alias: {conn_alias_name}")
    else:
        ok, result = sn_create("sys_alias", {
            "name": conn_alias_name,
            "type": "connection",
            "active": "true",
        })
        if ok:
            conn_alias_id = result.get("sys_id", "")
            print(f"  [OK] Connection Alias 作成: {conn_alias_id}")
        else:
            print(f"  [ERROR] Connection Alias 作成失敗: {result}")
            conn_alias_id = None
    results["connection_alias"] = conn_alias_id

    # 4c: Connection Record
    conn_name = "Vertex AI API Endpoint"
    existing = sn_get("sys_connection", f"name={conn_name}", "sys_id,name")
    if existing:
        conn_id = existing[0]["sys_id"]
        print(f"  [既存] Connection Record: {conn_name}")
    else:
        conn_data = {
            "name": conn_name,
            "host": f"{GCP_REGION}-aiplatform.googleapis.com",
            "protocol": "https",
            "port": "443",
            "active": "true",
        }
        if conn_alias_id:
            conn_data["connection_alias"] = conn_alias_id
        ok, result = sn_create("sys_connection", conn_data)
        if ok:
            conn_id = result.get("sys_id", "")
            print(f"  [OK] Connection Record 作成: {conn_id}")
        else:
            print(f"  [ERROR] Connection Record 作成失敗: {result}")
            conn_id = None
    results["connection"] = conn_id

    # 4d: Credential Record (Basic Auth with SA key info)
    cred_name = "Google Cloud SA Credential"
    existing = sn_get("discovery_credentials", f"name={cred_name}", "sys_id,name")
    if not existing:
        # OAuth Credential として登録を試みる
        existing = sn_get("oauth_credential", f"name={cred_name}", "sys_id,name")

    if existing:
        print(f"  [既存] Credential Record: {cred_name}")
    else:
        print(f"  [INFO] Credential Recordは OAuth Provider (Step 3) で管理されます")

    return results


# ============================================================
# Step 5: REST Message 定義
# ============================================================

def step5_setup_rest_messages(connection_info):
    section("Step 5: REST Message 定義（Vertex AI Gemini API）")

    rest_msg_name = "Vertex AI - Gemini API"
    base_endpoint = f"https://{GCP_REGION}-aiplatform.googleapis.com"

    # 既存チェック
    existing = sn_get("sys_rest_message", f"name={rest_msg_name}", "sys_id,name")
    if existing:
        msg_sys_id = existing[0]["sys_id"]
        print(f"  [既存] REST Message: {rest_msg_name} (sys_id={msg_sys_id})")
    else:
        # REST Message 作成
        data = {
            "name": rest_msg_name,
            "rest_endpoint": base_endpoint,
            "authentication_type": "oauth2",
            "description": f"Vertex AI Gemini API\nProject: {GCP_PROJECT}\nRegion: {GCP_REGION}\nModel: {GEMINI_MODEL}",
            "active": "true",
        }
        ok, result = sn_create("sys_rest_message", data)
        if ok:
            msg_sys_id = result.get("sys_id", "")
            print(f"  [OK] REST Message 作成: {rest_msg_name} (sys_id={msg_sys_id})")
        else:
            print(f"  [ERROR] REST Message 作成失敗: {result}")
            return None

    # REST Message Function: generateContent
    fn_name = "Generate Content"
    existing_fn = sn_get(
        "sys_rest_message_fn",
        f"rest_message={msg_sys_id}^function_name={fn_name}",
        "sys_id,function_name",
    )
    if existing_fn:
        print(f"  [既存] HTTP Method: {fn_name}")
    else:
        fn_endpoint = (
            f"/v1/projects/{GCP_PROJECT}/locations/{GCP_REGION}"
            f"/publishers/google/models/{GEMINI_MODEL}:generateContent"
        )
        fn_data = {
            "rest_message": msg_sys_id,
            "function_name": fn_name,
            "http_method": "POST",
            "rest_endpoint": base_endpoint + fn_endpoint,
            "content": json.dumps({
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": "${prompt}"}],
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 2048,
                },
            }, ensure_ascii=False, indent=2),
            "authentication_type": "inherit_from_parent",
        }
        ok, result = sn_create("sys_rest_message_fn", fn_data)
        if ok:
            print(f"  [OK] HTTP Method 作成: {fn_name}")
        else:
            print(f"  [ERROR] HTTP Method 作成失敗: {result}")

    # REST Message Function: streamGenerateContent
    fn_name2 = "Stream Generate Content"
    existing_fn2 = sn_get(
        "sys_rest_message_fn",
        f"rest_message={msg_sys_id}^function_name={fn_name2}",
        "sys_id,function_name",
    )
    if existing_fn2:
        print(f"  [既存] HTTP Method: {fn_name2}")
    else:
        fn_endpoint2 = (
            f"/v1/projects/{GCP_PROJECT}/locations/{GCP_REGION}"
            f"/publishers/google/models/{GEMINI_MODEL}:streamGenerateContent"
        )
        fn_data2 = {
            "rest_message": msg_sys_id,
            "function_name": fn_name2,
            "http_method": "POST",
            "rest_endpoint": base_endpoint + fn_endpoint2,
            "content": json.dumps({
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": "${prompt}"}],
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 4096,
                },
            }, ensure_ascii=False, indent=2),
            "authentication_type": "inherit_from_parent",
        }
        ok, result = sn_create("sys_rest_message_fn", fn_data2)
        if ok:
            print(f"  [OK] HTTP Method 作成: {fn_name2}")
        else:
            print(f"  [ERROR] HTTP Method 作成失敗: {result}")

    return msg_sys_id


# ============================================================
# Step 7: AI Search 関連設定
# ============================================================

def step7_setup_ai_search():
    section("Step 7: AI Search Assist 設定")

    # AI Search が有効であることを確認
    existing = sn_get(
        "v_plugin", "id=com.snc.ai_search_assist", "id,name,active"
    )
    if existing and existing[0].get("active") == "active":
        print("  [OK] AI Search Assist プラグイン: Active")
    else:
        print("  [WARN] AI Search Assist プラグインが未有効化")

    # Search Context Configuration の確認
    configs = sn_get("sys_search_context_config", "", "name,active,sys_id")
    print(f"\n  既存 Search Configurations: {len(configs)}件")
    for c in configs[:5]:
        print(f"    - {c.get('name', '')}")

    # Vertex AI Search 用の検索設定はプラグイン依存のため、
    # ここでは System Properties を設定
    print("\n  AI Search 関連プロパティ設定中...")

    properties = [
        ("sn.ai_search.enabled", "true", "Enable AI Search"),
        ("sn.ai_search.external_sources.enabled", "true", "Enable external search sources"),
    ]

    for prop_name, prop_value, description in properties:
        existing = sn_get("sys_properties", f"name={prop_name}", "sys_id,name,value")
        if existing:
            current = existing[0].get("value", "")
            if current == prop_value:
                print(f"    [OK] {prop_name} = {prop_value}")
            else:
                ok, _ = sn_update("sys_properties", existing[0]["sys_id"], {"value": prop_value})
                if ok:
                    print(f"    [更新] {prop_name}: {current} → {prop_value}")
                else:
                    print(f"    [ERROR] {prop_name} 更新失敗")
        else:
            ok, _ = sn_create("sys_properties", {
                "name": prop_name,
                "value": prop_value,
                "description": description,
                "type": "boolean",
            })
            if ok:
                print(f"    [作成] {prop_name} = {prop_value}")
            else:
                print(f"    [ERROR] {prop_name} 作成失敗")


# ============================================================
# Step 8: Now Assist / GenAI System Properties
# ============================================================

def step8_setup_system_properties():
    section("Step 8: Now Assist / GenAI System Properties 設定")

    properties = [
        # Now Assist 基本設定
        ("glide.now_assist.enabled", "true", "boolean", "Enable Now Assist"),
        ("sn.genai.incident.summarization.enabled", "true", "boolean", "Enable GenAI incident summarization"),
        ("sn.genai.knowledge.search.enabled", "true", "boolean", "Enable GenAI knowledge search"),
        ("sn.genai.case.summarization.enabled", "true", "boolean", "Enable GenAI case summarization"),
        ("sn.genai.change.risk_assessment.enabled", "true", "boolean", "Enable GenAI change risk assessment"),
        # Vertex AI 接続情報
        ("sn.genai.vertex_ai.project_id", GCP_PROJECT, "string", "GCP Project ID for Vertex AI"),
        ("sn.genai.vertex_ai.region", GCP_REGION, "string", "GCP Region for Vertex AI"),
        ("sn.genai.vertex_ai.model", GEMINI_MODEL, "string", "Gemini model name"),
    ]

    for prop_name, prop_value, prop_type, description in properties:
        existing = sn_get("sys_properties", f"name={prop_name}", "sys_id,name,value")
        if existing:
            current = existing[0].get("value", "")
            if current == prop_value:
                print(f"  [OK] {prop_name} = {prop_value}")
            else:
                ok, _ = sn_update("sys_properties", existing[0]["sys_id"], {"value": prop_value})
                if ok:
                    print(f"  [更新] {prop_name}: {current} → {prop_value}")
                else:
                    print(f"  [ERROR] {prop_name} 更新失敗")
        else:
            ok, _ = sn_create("sys_properties", {
                "name": prop_name,
                "value": prop_value,
                "description": description,
                "type": prop_type,
            })
            if ok:
                print(f"  [作成] {prop_name} = {prop_value}")
            else:
                print(f"  [ERROR] {prop_name} 作成失敗")


# ============================================================
# サマリー出力
# ============================================================

def print_summary(results):
    section("セットアップ完了サマリー")

    print(f"""
  ServiceNow Instance: {SERVICENOW_INSTANCE}
  GCP Project:         {GCP_PROJECT}
  GCP Region:          {GCP_REGION}
  Gemini Model:        {GEMINI_MODEL}
  SA Key Path:         {SA_KEY_PATH}

  === 次のステップ ===

  1. プラグイン有効化（GUIで確認）:
     {SERVICENOW_INSTANCE}/nav_to.do?uri=v_plugin_list.do

  2. OAuth Provider にアクセストークンを設定:
     {SERVICENOW_INSTANCE}/nav_to.do?uri=oauth_entity_list.do
     → 「Google Cloud - Vertex AI (JWT)」を開き、認証情報を確認

  3. REST Message のテスト:
     {SERVICENOW_INSTANCE}/nav_to.do?uri=sys_rest_message_list.do
     → 「Vertex AI - Gemini API」→ Test でAPI呼び出しを検証

  4. Now Assist 設定:
     {SERVICENOW_INSTANCE}/now-assist-admin-console
     → LLM Provider として設定した Google Cloud を選択

  5. Federation Connector 接続:
     上記設定完了後、ServiceNow Store から Federation Connector を
     インストールし、Connection Alias を紐づけて接続
""")


# ============================================================
# メイン
# ============================================================

def main():
    print("=" * 60)
    print("  ServiceNow Federation Connector 接続前準備")
    print("=" * 60)
    print(f"  Target: {SERVICENOW_INSTANCE}")
    print(f"  GCP:    {GCP_PROJECT}")

    # 接続テスト
    print("\n  ServiceNow 接続テスト中...")
    test = sn_get("incident", "", "sys_id")
    if test:
        print("  [OK] ServiceNow 接続成功")
    else:
        print("  [ERROR] ServiceNow 接続失敗")
        sys.exit(1)

    # Step 1
    step1_check_plugins()

    # Step 2
    sa_key = step2_create_gcp_sa()
    if not sa_key:
        print("\n[ERROR] GCPサービスアカウント設定に失敗しました")
        sys.exit(1)

    # Step 3
    oauth_sys_id = step3_setup_oauth(sa_key)

    # Step 3b
    jwt_sys_id = step3b_setup_jwt_provider(sa_key)

    # Step 4
    connection_info = step4_setup_connection(sa_key, oauth_sys_id)

    # Step 5
    rest_msg_id = step5_setup_rest_messages(connection_info)

    # Step 7
    step7_setup_ai_search()

    # Step 8
    step8_setup_system_properties()

    # サマリー
    print_summary({
        "oauth": oauth_sys_id,
        "jwt": jwt_sys_id,
        "connection": connection_info,
        "rest_message": rest_msg_id,
    })


if __name__ == "__main__":
    main()

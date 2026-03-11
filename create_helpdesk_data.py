"""
ServiceNow ヘルプデスク問い合わせサンプルデータ投入（製薬業界向け）
LoBユーザーからの日常的なIT問い合わせを作成
"""

import random
import requests
from datetime import datetime, timedelta

# ============================================================
# 設定
# ============================================================
INSTANCE_URL = "https://<YOUR_INSTANCE>.service-now.com"  # TODO: 変更してください
USERNAME = "admin"  # TODO: 変更してください
PASSWORD = "<YOUR_PASSWORD>"  # TODO: 変更してください

AUTH = (USERNAME, PASSWORD)
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# 既存ユーザー sys_id（caller_id として使用）
CALLER_IDS = [
    "02826bf03710200044e0bfc8bcbe5d3f",  # Lucius Bagnoli
    "02826bf03710200044e0bfc8bcbe5d55",  # Jimmie Barninger
    "02826bf03710200044e0bfc8bcbe5d5e",  # Melinda Carleton
    "02826bf03710200044e0bfc8bcbe5d64",  # Jewel Agresta
    "02826bf03710200044e0bfc8bcbe5d6d",  # Sean Bonnet
    "02826bf03710200044e0bfc8bcbe5d76",  # Jacinto Gawron
    "02826bf03710200044e0bfc8bcbe5d7f",  # Krystle Stika
    "02826bf03710200044e0bfc8bcbe5d88",  # Billie Cowley
    "02826bf03710200044e0bfc8bcbe5d91",  # Christian Marnell
]

# ============================================================
# ユーティリティ
# ============================================================

def create_record(table: str, data: dict) -> tuple[bool, str]:
    url = f"{INSTANCE_URL}/api/now/table/{table}"
    resp = requests.post(url, auth=AUTH, headers=HEADERS, json=data)
    if resp.status_code in (200, 201):
        result = resp.json().get("result", {})
        num = result.get("number", result.get("sys_id", "OK"))
        return True, num
    else:
        return False, resp.text[:200]


def random_date(start_str: str, end_str: str) -> str:
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")
    delta = end - start
    dt = start + timedelta(
        days=random.randint(0, delta.days),
        hours=random.randint(7, 19),  # 業務時間帯
        minutes=random.randint(0, 59),
    )
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# LoBユーザー ヘルプデスク問い合わせテンプレート
# ============================================================

HELPDESK_TICKETS = [
    # ========================================
    # 経理・財務部門（Finance）
    # ========================================
    {
        "short_description": "SAP 経費精算の承認ボタンが反応しない",
        "description": "経理部の田中です。SAP上で経費精算の承認処理を行おうとしましたが、承認ボタンをクリックしても反応がありません。月末の締め処理が迫っているため、早急に対応をお願いします。ブラウザはChromeを使用しています。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "phone",
        "impact": "2",
        "urgency": "2",
        "business_service": "SAP",
        "department": "Finance",
    },
    {
        "short_description": "SAP 月次決算レポートが出力されない",
        "description": "経理部です。SAP FI/COモジュールから月次決算レポート（PL/BS）を出力しようとしましたが、レポートが空白で表示されます。先月までは問題なく出力できていました。決算スケジュールに影響するため至急対応お願いします。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "phone",
        "impact": "2",
        "urgency": "1",
        "business_service": "SAP",
        "department": "Finance",
    },
    {
        "short_description": "経費精算システムにログインできない",
        "description": "経費精算システム（Concur）にログインできません。パスワードをリセットしても状況が変わりません。出張精算の提出期限が明日です。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "self-service",
        "impact": "3",
        "urgency": "2",
        "business_service": "Concur",
        "department": "Finance",
    },
    {
        "short_description": "請求書スキャンデータがSAPに取り込めない",
        "description": "スキャナーで読み取った請求書PDFをSAPに取り込もうとすると「フォーマットエラー」が表示されます。先週から発生しています。手動入力で対応していますが、件数が多く業務に支障が出ています。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "email",
        "impact": "3",
        "urgency": "3",
        "business_service": "SAP",
        "department": "Finance",
    },
    {
        "short_description": "共有フォルダの決算資料にアクセスできない",
        "description": "\\\\fileserver01\\finance\\202603 のフォルダにアクセスしようとすると「アクセスが拒否されました」と表示されます。先週までは問題なくアクセスできていました。四半期決算の資料が入っているので至急お願いします。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "phone",
        "impact": "2",
        "urgency": "2",
        "business_service": "File Server",
        "department": "Finance",
    },

    # ========================================
    # 研究開発部門（R&D / Development）
    # ========================================
    {
        "short_description": "LIMS にログインできない - パスワード正しいはず",
        "description": "研究開発部の佐藤です。LIMSにいつものIDとパスワードでログインしようとしましたが「認証エラー」が表示されます。パスワードは間違っていないはずです。試験データの入力が急ぎで必要です。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "virtual_agent",
        "impact": "2",
        "urgency": "2",
        "business_service": "LIMS",
        "department": "Development",
    },
    {
        "short_description": "研究データ分析用PCのメモリ不足エラー",
        "description": "ゲノムデータの解析中にメモリ不足エラーが頻発します。現在16GBのメモリですが、解析ツール（R/Bioconductor）で大規模データセットを扱うには不足しています。メモリ増設またはクラウド環境の利用を希望します。",
        "category": "Hardware",
        "subcategory": "Memory",
        "contact_type": "self-service",
        "impact": "3",
        "urgency": "3",
        "business_service": "Workstation",
        "department": "Development",
    },
    {
        "short_description": "電子実験ノート（ELN）のデータ保存でタイムアウト",
        "description": "電子実験ノートに実験結果を保存しようとすると、タイムアウトエラーが出ます。大きな画像データ（顕微鏡写真）を含む実験記録です。何度やっても保存できません。実験データを失うわけにはいかないので急ぎ対応お願いします。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "phone",
        "impact": "2",
        "urgency": "1",
        "business_service": "ELN",
        "department": "Development",
    },
    {
        "short_description": "統計解析ソフト（SAS）のライセンスエラー",
        "description": "SAS 9.4を起動しようとすると「ライセンスの有効期限が切れています」と表示されます。治験データの統計解析を今週中に完了する必要があります。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "email",
        "impact": "2",
        "urgency": "2",
        "business_service": "SAS",
        "department": "Development",
    },
    {
        "short_description": "研究棟のWi-Fiが遅い - 論文のダウンロードに10分以上",
        "description": "つくば研究棟3Fの無線LANが非常に遅いです。PubMedから論文PDFをダウンロードするのに10分以上かかります。有線LANポートも空きがありません。研究業務に支障が出ています。",
        "category": "Network",
        "subcategory": "Wireless",
        "contact_type": "self-service",
        "impact": "3",
        "urgency": "3",
        "business_service": "Network",
        "department": "Development",
    },
    {
        "short_description": "GCPのJupyter Notebook環境に接続できない",
        "description": "Vertex AI Workbench上のJupyter Notebook環境が「接続中」のまま動きません。昨日まで使えていました。創薬AIモデルの学習を回す必要があるので困っています。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "chat",
        "impact": "3",
        "urgency": "2",
        "business_service": "GCP",
        "department": "Development",
    },
    {
        "short_description": "分析機器PCのWindows Update後にHPLC制御ソフトが起動しない",
        "description": "昨晩のWindows Updateの後、HPLC制御ソフト（Chromeleon）が起動しなくなりました。GxP対応の分析機器なので、勝手にソフトを再インストールできません。品質試験が止まっています。",
        "category": "Software",
        "subcategory": "Operating System",
        "contact_type": "phone",
        "impact": "1",
        "urgency": "1",
        "business_service": "LIMS",
        "department": "Development",
    },

    # ========================================
    # 営業部門（Sales）
    # ========================================
    {
        "short_description": "VPN接続が不安定で顧客提案書にアクセスできない",
        "description": "営業部の鈴木です。出張先からVPN接続していますが、頻繁に切断されます。SharePoint上の顧客向け提案書にアクセスできず、午後の商談に間に合わない可能性があります。至急対応お願いします。",
        "category": "Network",
        "subcategory": "VPN",
        "contact_type": "phone",
        "impact": "2",
        "urgency": "1",
        "business_service": "VPN",
        "department": "Sales",
    },
    {
        "short_description": "CRM（Salesforce）のダッシュボードが表示されない",
        "description": "Salesforceにログインはできますが、売上ダッシュボードが「読み込みエラー」で表示されません。週次の営業会議で使うので今日中に直してほしいです。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "chat",
        "impact": "2",
        "urgency": "2",
        "business_service": "Salesforce",
        "department": "Sales",
    },
    {
        "short_description": "モバイルデバイスでメールの添付ファイルが開けない",
        "description": "iPhoneのOutlookアプリで顧客からの添付ファイル（Excel）が開けません。「サポートされていない形式」と表示されます。PCでは開けます。外出が多いのでモバイルで確認できないと困ります。",
        "category": "Software",
        "subcategory": "Email",
        "contact_type": "self-service",
        "impact": "3",
        "urgency": "3",
        "business_service": "Email",
        "department": "Sales",
    },
    {
        "short_description": "営業用タブレットの動作が極端に遅い",
        "description": "MR（医薬情報担当者）用のiPadが非常に遅くなっています。医師への製品説明用のプレゼンアプリ（iRep）の起動に2分以上かかります。来週の新薬説明会までに改善してほしいです。",
        "category": "Hardware",
        "subcategory": "Monitor",
        "contact_type": "walk-in",
        "impact": "3",
        "urgency": "2",
        "business_service": "Mobile Device",
        "department": "Sales",
    },
    {
        "short_description": "Teams会議で画面共有ができない",
        "description": "Microsoft Teamsで顧客とのWeb会議中に画面共有ができません。「組織のポリシーにより画面共有が制限されています」と表示されます。明日も顧客会議があるので急ぎ対応お願いします。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "chat",
        "impact": "2",
        "urgency": "2",
        "business_service": "Microsoft Teams",
        "department": "Sales",
    },
    {
        "short_description": "出張先のホテルWi-Fiからメールが送信できない",
        "description": "大阪出張中です。ホテルのWi-Fiに接続してOutlookからメールを送信しようとすると、送信トレイに留まったままです。VPNに接続しても状況は変わりません。",
        "category": "Network",
        "subcategory": "Email",
        "contact_type": "phone",
        "impact": "3",
        "urgency": "2",
        "business_service": "Email",
        "department": "Sales",
    },

    # ========================================
    # 製造部門（Manufacturing）
    # ========================================
    {
        "short_description": "MES 製造記録画面がフリーズ - 注射剤ライン",
        "description": "製造部の山田です。MESの電子バッチ記録画面が操作中にフリーズしました。注射剤ラインの製造工程記録が入力できません。GxPシステムのためリブートには品質部門の承認が必要です。製造が止まっています。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "phone",
        "impact": "1",
        "urgency": "1",
        "business_service": "MES",
        "department": "Manufacturing",
    },
    {
        "short_description": "製造ライン監視モニターの表示が消えた",
        "description": "錠剤製造ラインの監視モニター2台のうち1台が真っ暗になりました。SCADA画面が表示されません。ケーブル接続は確認しましたが改善しません。",
        "category": "Hardware",
        "subcategory": "Monitor",
        "contact_type": "phone",
        "impact": "2",
        "urgency": "2",
        "business_service": "SCADA",
        "department": "Manufacturing",
    },
    {
        "short_description": "バーコードリーダーが原材料ラベルを読み取れない",
        "description": "入荷した原材料のバーコードラベルがリーダーで読み取れません。手入力で対応していますが、ダブルチェックの工数がかかりGMP手順上も好ましくありません。リーダーの故障か確認してください。",
        "category": "Hardware",
        "subcategory": "Peripherals",
        "contact_type": "walk-in",
        "impact": "2",
        "urgency": "2",
        "business_service": "MES",
        "department": "Manufacturing",
    },
    {
        "short_description": "クリーンルーム内の環境モニタリングシステムのデータ欠損",
        "description": "クリーンルームの温湿度モニタリングシステムで昨日の午後3時から6時間分のデータが記録されていません。GMP逸脱調査が必要になる可能性があります。システムログの確認をお願いします。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "phone",
        "impact": "1",
        "urgency": "1",
        "business_service": "Environmental Monitoring",
        "department": "Manufacturing",
    },
    {
        "short_description": "製造現場のプリンターでバッチ記録が印刷できない",
        "description": "製造エリアの専用プリンター（ラベルプリンター）でバッチ記録の紙コピーが印刷できません。「印刷キューが一杯です」と表示されますが、ジョブを削除しても改善しません。",
        "category": "Hardware",
        "subcategory": "Peripherals",
        "contact_type": "walk-in",
        "impact": "2",
        "urgency": "2",
        "business_service": "Printer",
        "department": "Manufacturing",
    },

    # ========================================
    # 人事部門（HR）
    # ========================================
    {
        "short_description": "人事システム（SuccessFactors）で勤怠データが反映されない",
        "description": "人事部です。SuccessFactorsの勤怠管理で、先月分の残業時間が正しく反映されていない社員が複数います。給与計算に影響するため、至急確認をお願いします。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "email",
        "impact": "2",
        "urgency": "1",
        "business_service": "SuccessFactors",
        "department": "HR",
    },
    {
        "short_description": "新入社員のアカウント作成依頼 - 4月入社20名分",
        "description": "4月1日入社の新入社員20名分のADアカウント、メールアカウント、SAP/LIMSアクセス権を作成してください。リストは添付のExcelの通りです。3月25日までに完了をお願いします。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "email",
        "impact": "3",
        "urgency": "2",
        "business_service": "Active Directory",
        "department": "HR",
    },
    {
        "short_description": "退職者のアカウント無効化が反映されていない",
        "description": "先月末退職した社員（2名）のADアカウントがまだ有効のようです。メールも受信可能な状態です。セキュリティ上問題があるので、即座に無効化をお願いします。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "phone",
        "impact": "2",
        "urgency": "1",
        "business_service": "Active Directory",
        "department": "HR",
    },

    # ========================================
    # 一般的なIT問い合わせ（全部門共通）
    # ========================================
    {
        "short_description": "PCが突然ブルースクリーンで落ちる",
        "description": "作業中にPCが突然ブルースクリーン（BSOD）になり再起動を繰り返します。今日だけで3回発生しました。保存していないデータが消えてしまいました。",
        "category": "Hardware",
        "subcategory": "CPU",
        "contact_type": "walk-in",
        "impact": "3",
        "urgency": "2",
        "business_service": "Workstation",
        "department": "General",
    },
    {
        "short_description": "パスワードの有効期限切れでロックアウトされた",
        "description": "今朝PCにログインしようとしたら「パスワードの有効期限が切れました」と表示されました。変更画面が表示されず、完全にロックアウトされています。今日の午前中に重要な会議があります。",
        "category": "Software",
        "subcategory": "Operating System",
        "contact_type": "phone",
        "impact": "3",
        "urgency": "2",
        "business_service": "Active Directory",
        "department": "General",
    },
    {
        "short_description": "Outlookで特定の相手にメールが送れない",
        "description": "取引先の特定のメールアドレスにメールを送ると「配信不能」で戻ってきます。他の人には送れます。先週までは問題なくやり取りできていました。",
        "category": "Software",
        "subcategory": "Email",
        "contact_type": "self-service",
        "impact": "3",
        "urgency": "3",
        "business_service": "Email",
        "department": "General",
    },
    {
        "short_description": "会議室のプロジェクターが映らない",
        "description": "5F大会議室のプロジェクターにPCを接続しても映りません。HDMIケーブルを変えても駄目でした。30分後に役員会議が始まります。",
        "category": "Hardware",
        "subcategory": "Monitor",
        "contact_type": "phone",
        "impact": "2",
        "urgency": "1",
        "business_service": "Conference Room",
        "department": "General",
    },
    {
        "short_description": "USBメモリが認識されない",
        "description": "USBメモリをPCに接続しても認識されません。デバイスマネージャーにも表示されません。学会発表用のデータを持ち出す必要があるのですが。",
        "category": "Hardware",
        "subcategory": "Peripherals",
        "contact_type": "walk-in",
        "impact": "3",
        "urgency": "3",
        "business_service": "Workstation",
        "department": "General",
    },
    {
        "short_description": "Zoomのカメラが認識されない - 在宅勤務",
        "description": "在宅勤務中にZoomでWeb会議に参加しようとしましたが、内蔵カメラが認識されません。設定でカメラが「使用できません」と表示されます。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "virtual_agent",
        "impact": "3",
        "urgency": "3",
        "business_service": "Zoom",
        "department": "General",
    },
    {
        "short_description": "Excelファイルが壊れて開けない - 月次レポート",
        "description": "昨日まで編集していたExcelファイル（月次実績レポート.xlsx）を開こうとすると「ファイルが破損しています」と表示されます。バックアップから復旧可能ですか？",
        "category": "Software",
        "subcategory": "Operating System",
        "contact_type": "self-service",
        "impact": "3",
        "urgency": "2",
        "business_service": "Office 365",
        "department": "General",
    },
    {
        "short_description": "多要素認証（MFA）のスマホを機種変更した",
        "description": "スマートフォンを機種変更しました。Microsoft Authenticatorの再設定が必要です。現在メールやTeamsにログインできない状態です。",
        "category": "Software",
        "subcategory": "Operating System",
        "contact_type": "virtual_agent",
        "impact": "3",
        "urgency": "2",
        "business_service": "Active Directory",
        "department": "General",
    },
    {
        "short_description": "社内ポータルサイトの表示が崩れる",
        "description": "社内ポータルサイト（SharePoint）のレイアウトが崩れて表示されます。メニューが重なって読めません。Chromeのバージョンは最新です。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "self-service",
        "impact": "3",
        "urgency": "3",
        "business_service": "SharePoint",
        "department": "General",
    },
    {
        "short_description": "OneDriveの同期が止まっている",
        "description": "OneDriveの同期アイコンが赤い×マークになっており、同期が止まっています。最新のファイルがクラウドにアップロードされていない状態です。1週間前からこの状態のようです。",
        "category": "Software",
        "subcategory": "Internal Application",
        "contact_type": "self-service",
        "impact": "3",
        "urgency": "3",
        "business_service": "OneDrive",
        "department": "General",
    },
]

# close_code 値（Resolved/Closed用）
CLOSE_CODES = [
    "Solution provided",
    "Workaround provided",
    "Resolved by caller",
    "Resolved by request",
    "Known error",
]

# contact_type の重み（AI導入後のチャネルシフトを反映）
CONTACT_TYPES = ["phone", "self-service", "virtual_agent", "chat", "email", "walk-in"]


# ============================================================
# データ投入
# ============================================================

def create_helpdesk_incidents(count: int = 150):
    """LoBユーザーからのヘルプデスク問い合わせインシデントを作成"""
    print(f"\n{'='*60}")
    print(f"ヘルプデスク問い合わせデータ作成中... ({count}件)")
    print(f"{'='*60}")

    states_new = [("1", "New"), ("2", "In Progress")]
    states_resolved = [("6", "Resolved"), ("7", "Closed")]

    success = 0
    fail = 0

    for i in range(count):
        template = random.choice(HELPDESK_TICKETS)

        # 70% Resolved/Closed, 30% New/In Progress
        if random.random() < 0.7:
            state = random.choice(states_resolved)
        else:
            state = random.choice(states_new)

        opened_at = random_date("2025-09-01", "2026-03-10")
        caller_id = random.choice(CALLER_IDS)

        data = {
            "short_description": template["short_description"] + f" (HD#{i+1:03d})",
            "description": template["description"],
            "category": template["category"],
            "subcategory": template.get("subcategory", ""),
            "contact_type": template.get("contact_type", random.choice(CONTACT_TYPES)),
            "impact": template["impact"],
            "urgency": template["urgency"],
            "state": state[0],
            "opened_at": opened_at,
            "caller_id": caller_id,
        }

        # Resolved/Closed にはclose_code, close_notes, resolved_at が必要
        if state[0] in ("6", "7"):
            imp = int(template["impact"])
            urg = int(template["urgency"])
            priority = max(1, (imp + urg) // 2)

            if priority == 1:
                mttr_minutes = random.randint(10, 120)
            elif priority == 2:
                mttr_minutes = random.randint(30, 360)
            else:
                mttr_minutes = random.randint(60, 1440)

            # Virtual Agent 経由は短時間で解決
            if template.get("contact_type") == "virtual_agent":
                mttr_minutes = random.randint(2, 15)

            opened_dt = datetime.strptime(opened_at, "%Y-%m-%d %H:%M:%S")
            resolved_dt = opened_dt + timedelta(minutes=mttr_minutes)

            data["resolved_at"] = resolved_dt.strftime("%Y-%m-%d %H:%M:%S")
            data["close_code"] = random.choice(CLOSE_CODES)
            data["close_notes"] = f"対応完了。対応時間: {mttr_minutes}分。チャネル: {template.get('contact_type', 'N/A')}。"

            if state[0] == "7":
                closed_dt = resolved_dt + timedelta(hours=random.randint(1, 24))
                data["closed_at"] = closed_dt.strftime("%Y-%m-%d %H:%M:%S")

        ok, msg = create_record("incident", data)
        if ok:
            success += 1
        else:
            fail += 1
            if fail <= 5:
                print(f"  ERROR: {msg}")

    print(f"\n  結果: 成功={success}, 失敗={fail}")
    return success, fail


def create_helpdesk_knowledge():
    """ヘルプデスク向けナレッジ記事を追加"""
    print(f"\n{'='*60}")
    print("ヘルプデスク向けナレッジ記事作成中...")
    print(f"{'='*60}")

    articles = [
        {
            "short_description": "パスワードリセット セルフサービス手順",
            "text": """## パスワードリセット セルフサービス手順

### 手順
1. パスワードリセットポータル（https://passwordreset.example.com）にアクセス
2. ユーザーIDを入力
3. 登録済み携帯電話にSMS認証コードが送信されます
4. 認証コードを入力
5. 新しいパスワードを設定（8文字以上、大文字小文字数字記号を含む）

### 注意事項
- 過去5回使用したパスワードは再利用できません
- パスワード変更後、すべてのデバイスで再ログインが必要です
- 問題が解決しない場合はヘルプデスク（ext.1234）に連絡してください""",
        },
        {
            "short_description": "VPN接続トラブル クイック診断ガイド",
            "text": """## VPN接続トラブル クイック診断

### ステップ1: 基本確認
- インターネット接続は正常ですか？（ブラウザでWebサイトが開けるか確認）
- GlobalProtectクライアントは最新版ですか？

### ステップ2: 再接続
1. GlobalProtectアイコンを右クリック → 切断
2. 5秒待つ
3. 再接続

### ステップ3: クライアント再起動
1. GlobalProtectを終了
2. タスクマネージャーでPanGPS.exeプロセスが残っていないか確認
3. GlobalProtectを再起動

### ステップ4: 解決しない場合
ヘルプデスクに連絡し、以下を伝えてください:
- エラーメッセージのスクリーンショット
- 接続先（自宅/ホテル/カフェ等）
- 事象発生時刻""",
        },
        {
            "short_description": "LIMS ログイントラブルシューティング",
            "text": """## LIMS ログイン トラブルシューティング

### よくある原因と対処
1. **ブラウザキャッシュ**: Chrome設定 → 閲覧データの削除 → Cookieとキャッシュをクリア
2. **パスワード有効期限**: LIMSのパスワードはADとは別管理。90日で期限切れ
3. **アカウントロック**: 5回連続失敗でロック。15分後に自動解除
4. **ブラウザ互換性**: Chrome最新版を推奨。IEは非対応

### GxP注意事項
- 他人のアカウントでのログインは厳禁（21 CFR Part 11違反）
- パスワードの共有・メモ書きは禁止""",
        },
        {
            "short_description": "多要素認証（MFA） スマホ機種変更時の再設定手順",
            "text": """## MFA再設定手順（スマートフォン機種変更時）

### 事前準備
機種変更前に旧端末でバックアップを取ることを推奨します。

### 再設定手順
1. ヘルプデスクに連絡しMFAリセットを依頼
2. 本人確認（社員番号、部署、上司名）
3. リセット後、新しいスマートフォンにMicrosoft Authenticatorをインストール
4. PCでMicrosoft 365にログイン → 追加のセキュリティ確認画面が表示
5. 画面のQRコードをAuthenticatorアプリで読み取り
6. テスト通知で動作確認

### 所要時間
ヘルプデスクでの対応: 約10分""",
        },
        {
            "short_description": "会議室AV機器 トラブル対応クイックガイド",
            "text": """## 会議室AV機器 トラブル対応

### プロジェクターが映らない場合
1. 電源ランプを確認（緑=正常、赤=エラー）
2. HDMIケーブルを抜き差し
3. PCの外部ディスプレイ設定を確認（Win+P → 複製 or 拡張）
4. 別のHDMIポートを試す
5. プロジェクターの電源OFF→ONを試す

### Teams会議の音声が出ない場合
1. 会議室のスピーカーフォンの電源確認
2. Teamsのオーディオデバイスがスピーカーフォンになっているか確認
3. 音量を確認

### 解決しない場合
総務部（ext.5678）に連絡""",
        },
        {
            "short_description": "SAP 経費精算 よくあるエラーと対処法",
            "text": """## SAP 経費精算 よくあるエラー

### 「承認ボタンが反応しない」
- ブラウザのポップアップブロッカーを無効化してください
- SAP GUI の場合、セッションタイムアウトの可能性 → 再ログイン

### 「添付ファイルがアップロードできない」
- ファイルサイズ上限: 10MB
- 対応形式: PDF, JPG, PNG（Excelは不可）

### 「勘定科目エラー」
- 経費種類と勘定科目の対応表を確認
- 不明な場合は経理部（ext.3456）に確認""",
        },
    ]

    success = 0
    for article in articles:
        data = {
            "short_description": article["short_description"],
            "text": article["text"],
            "workflow_state": "published",
            "valid_to": "2027-12-31",
        }
        ok, msg = create_record("kb_knowledge", data)
        if ok:
            success += 1
            print(f"  OK: {msg}")
        else:
            print(f"  ERROR: {msg}")

    print(f"  結果: {success}/{len(articles)} 件作成")


# ============================================================
# メイン
# ============================================================

def main():
    print("=" * 60)
    print("製薬業界向け ヘルプデスク問い合わせデータ投入")
    print("=" * 60)
    print(f"Instance: {INSTANCE_URL}")

    # 接続テスト
    print("\n接続テスト中...")
    try:
        url = f"{INSTANCE_URL}/api/now/table/incident?sysparm_limit=1"
        resp = requests.get(url, auth=AUTH, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            print("接続成功!")
        else:
            print(f"接続エラー: {resp.status_code}")
            return
    except Exception as e:
        print(f"接続失敗: {e}")
        return

    # ナレッジ記事（ヘルプデスク向け）
    create_helpdesk_knowledge()

    # ヘルプデスクインシデント
    create_helpdesk_incidents(count=150)

    print("\n" + "=" * 60)
    print("ヘルプデスクデータ投入完了!")
    print("=" * 60)


if __name__ == "__main__":
    main()

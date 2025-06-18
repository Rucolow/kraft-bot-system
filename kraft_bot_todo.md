# KRAFT分散型Botシステム 開発TODO全工程

## 🔧 STEP 0: 環境設定と準備作業

### STEP 0-1: 開発環境の準備
- [x] ✅ Python環境の確認（3.9以上）
- [x] ✅ 仮想環境の作成と有効化
- [x] ✅ 必要なパッケージのインストール
  - discord.py 2.3.2
  - firebase-admin 6.2.0
  - python-dotenv 1.0.0
  - aiohttp 3.8.5
  - anthropic 0.7.7
- [x] ✅ pipのアップグレード

### STEP 0-2: 認証情報の準備
- [x] ✅ Discord Bot Tokenの取得と設定
  - [x] ✅ 倉田 太 (Community Bot) のトークン取得と設定
  - [x] ✅ KRAFT銀行 (Central Bank Bot) のトークン取得と設定
  - [x] ✅ KRAFT株式市場 (Stock Market Bot) のトークン取得と設定
  - [x] ✅ KRAFT称号bot (Title Bot) のトークン取得と設定
  - [x] ✅ 管理者ユーザーIDの設定
- [x] ✅ Firebase認証情報の取得と設定
  - [x] ✅ Firebaseプロジェクトの作成
  - [x] ✅ サービスアカウントの作成
  - [x] ✅ 秘密鍵の生成と設定
- [x] ✅ Claude API Keyの取得と設定
  - [x] ✅ Anthropicアカウントの作成
  - [x] ✅ API Keyの生成と設定

### STEP 0-3: Discordサーバー設定
- [x] ✅ 通知用チャンネルの作成
  - [x] ✅ レベルアップ通知チャンネル
  - [x] ✅ 称号獲得通知チャンネル
  - [x] ✅ 投資ニュースチャンネル
  - [x] ✅ 寄付通知チャンネル
  - [x] ✅ クラフトラジオチャンネル
  - [x] ✅ 一般お知らせチャンネル
- [x] ✅ ロール設定
  - [x] ✅ 管理者ロールの作成と設定
  - [x] ✅ 称号用ロールの作成
    - [x] ✅ レベル系称号ロール
    - [x] ✅ アクティビティ系称号ロール
    - [x] ✅ 経済系称号ロール

### STEP 0-5: セキュリティ設定
- [x] ✅ 取引制限の設定（削除しました）
  - [x] ✅ 1回の取引上限（1,000,000 KR）
  - [x] ✅ 日次取引上限（50回）
  - [x] ✅ 取引頻度制限（5分で8回まで）
- [x] ✅ 管理者権限の設定
  - [x] ✅ 残高調整権限
  - [x] ✅ 称号強制チェック権限
  - [x] ✅ システム管理権限

### STEP 0-6: ドキュメント準備
- [x] ユーザー向けドキュメント
  - [x] コマンド一覧の作成
  - [x] 各機能の使い方説明
  - [x] よくある質問（FAQ）の作成
- [x] 管理者向けドキュメント
  - [x] 運用マニュアルの作成
  - [x] トラブルシューティングガイド
  - [x] バックアップ・リストア手順
- [x] 開発者向けドキュメント
  - [x] API仕様書の作成
  - [x] データ構造の説明
  - [x] 開発ガイドライン

### STEP 0-7: 運用・監視設定
- [x] エラー通知システム
  - [x] Discord通知チャンネルの設定
  - [x] エラーログの形式定義
  - [x] 通知条件の設定
- [x] バックアップ設定
  - [x] Firebaseデータのバックアップ方針
  - [x] Bot設定のバックアップ方針
  - [x] バックアップスケジュールの設定
- [x] 監視システム
  - [x] ボット稼働状況の監視方法
  - [x] パフォーマンス監視の設定
  - [x] アラート条件の設定

## 🚀 プロジェクト初期設定

### STEP 1: プロジェクト構造作成
- [x] プロジェクトディレクトリ作成 `kraft-distributed-bot/`
- [x] サブディレクトリ作成
  - [x] `shared/` ディレクトリ
  - [x] `config/` ディレクトリ
  - [x] `docs/` ディレクトリ
- [x] `shared/__init__.py` 作成（空ファイル）

### STEP 2: 基本設定ファイル
- [x] `requirements.txt` 作成
  ```txt
  discord.py==2.3.2
  firebase-admin==6.2.0
  python-dotenv==1.0.0
  aiohttp==3.8.5
  anthropic==0.7.7
  ```
- [x] `.env.template` 作成
  ```env
  # Discord Bot Tokens
  COMMUNITY_BOT_TOKEN=
  CENTRAL_BANK_TOKEN=
  STOCK_MARKET_TOKEN=
  TITLE_BOT_TOKEN=

  # API Keys
  CLAUDE_API_KEY=

  # Environment
  ENVIRONMENT=development

  # Firebase Configuration
  FIREBASE_PROJECT_ID=
  FIREBASE_PRIVATE_KEY_ID=
  FIREBASE_PRIVATE_KEY=
  FIREBASE_CLIENT_EMAIL=
  FIREBASE_CLIENT_ID=
  FIREBASE_AUTH_URI=
  FIREBASE_TOKEN_URI=
  FIREBASE_AUTH_PROVIDER_X509_CERT_URL=
  FIREBASE_CLIENT_X509_CERT_URL=
  ```
- [x] `.gitignore` 作成
  ```
  .env
  config/firebase_credentials.json
  __pycache__/
  *.pyc
  venv/
  .DS_Store
  ```

---

## 📚 Phase 1: 共通ライブラリ開発

### STEP 3: kraft_config.py 作成
- [x] ファイル作成: `shared/kraft_config.py`
- [x] 環境変数読み込み処理
  ```python
  load_dotenv()
  ```
- [x] Discord設定セクション
  - [x] `DISCORD_TOKENS` 辞書定義
  - [x] `CHANNEL_IDS` 辞書定義
  - [x] `ADMIN_USER_IDS` リスト定義
- [x] Firebase設定セクション
  - [x] `FIREBASE_CONFIG` 辞書定義
- [x] レベルシステム設定セクション
  - [x] `LEVEL_SYSTEM` 辞書定義
  - [x] XP計算設定
  - [x] 日次上限設定
  - [x] レベル報酬設定
- [x] 経済システム設定セクション
  - [x] `ECONOMIC_SYSTEM` 辞書定義
  - [x] 取引制限設定
  - [x] 投資設定
  - [x] ギャンブル設定
- [x] 企業マスターデータセクション
  - [x] `COMPANIES_DATA` 辞書定義（10社分）
- [x] 称号システム設定セクション
  - [x] `TITLE_SYSTEM` 辞書定義
  - [x] 称号条件定義
- [x] ヘルパー関数セクション
  - [x] `get_channel_id()` 関数
  - [x] `is_admin()` 関数
  - [x] `get_company_data()` 関数
  - [x] `get_level_reward()` 関数
  - [x] `get_quest_reward()` 関数

### STEP 4: kraft_api.py 作成
- [x] ファイル作成: `shared/kraft_api.py`
- [x] 必要なimport文
  ```python
  import firebase_admin
  from firebase_admin import firestore
  import logging
  import datetime
  from typing import Optional, Dict, Any, List
  ```
- [x] ロギング設定とlogger初期化
- [x] `KraftAPI` クラス定義
  - [x] `__init__(self, db_client=None)` メソッド
- [x] 中央銀行APIセクション
  - [x] `add_kr()` 静的メソッド（新規ユーザー初期化含む）
  - [x] `subtract_kr()` 静的メソッド（残高確認含む）
  - [x] `get_balance()` 静的メソッド
  - [x] `log_transaction()` 静的メソッド
- [x] レベルシステムAPIセクション
  - [x] `add_xp()` 静的メソッド（レベルアップ判定・KR報酬含む）
  - [x] `get_level_info()` 静的メソッド
- [x] 称号システムAPIセクション
  - [x] `log_title_event()` 静的メソッド
  - [x] `check_user_titles()` 静的メソッド
- [x] 投資システムAPIセクション
  - [x] `get_stock_price()` 静的メソッド
  - [x] `get_user_portfolio()` 静的メソッド
  - [x] `log_investment_transaction()` 静的メソッド
- [x] クエストシステムAPIセクション
  - [x] `create_quest()` 静的メソッド
  - [x] `complete_quest()` 静的メソッド（報酬計算・付与含む）
- [x] ユーティリティセクション
  - [x] `get_user_data()` 静的メソッド（ポートフォリオ評価額含む）
  - [x] `initialize_user()` 静的メソッド
- [x] 便利関数エイリアス定義
  ```python
  add_kr = KraftAPI.add_kr
  subtract_kr = KraftAPI.subtract_kr
  get_balance = KraftAPI.get_balance
  add_xp = KraftAPI.add_xp
  get_level_info = KraftAPI.get_level_info
  log_title_event = KraftAPI.log_title_event
  ```

---

## 🏦 Phase 2: Central Bank Bot開発

### STEP 5: kraft_central_bank.py 作成
- [x] ファイル作成: `kraft_central_bank.py`
- [x] 必要なimport文
  ```python
  import os
  import discord
  from discord import app_commands
  from discord.ext import commands
  from dotenv import load_dotenv
  import firebase_admin
  from firebase_admin import credentials, firestore
  import datetime
  import random
  import logging
  from typing import Optional, Dict, Any, Tuple
  ```
- [x] 環境変数読み込み
  ```python
  load_dotenv()
  TOKEN = os.getenv("CENTRAL_BANK_TOKEN")
  ```
- [x] Firebase初期化処理
- [x] ロギング設定

### STEP 6: TransactionManager クラス
- [x] `TransactionManager` クラス定義
- [x] `validate_transaction()` 静的メソッド
  - [x] 金額検証（1KR以上、100万KR以下）
  - [x] 取引頻度チェック（5分間で8回まで）
- [x] `log_transaction()` 静的メソッド
  - [x] Firestoreに取引ログ保存

### STEP 7: KraftCentralBank メインクラス
- [x] `KraftCentralBank` クラス定義（commands.Bot継承）
- [x] `__init__()` メソッド
  - [x] Discord intents設定（message_content=True）
  - [x] command_prefix設定（'!bank_'）
  - [x] TransactionManager初期化
- [x] `on_ready()` イベントハンドラ
  - [x] 起動メッセージ出力
  - [x] `self.tree.sync()` でコマンド同期
  - [x] 同期成功・失敗メッセージ

### STEP 8: 残高管理API（内部用）
- [x] `get_balance_api()` メソッド
  - [x] Firestoreから残高取得
  - [x] 新規ユーザー初期化処理
- [x] `add_kr_api()` メソッド
  - [x] 取引検証
  - [x] 残高更新
  - [x] ログ記録
- [x] `subtract_kr_api()` メソッド
  - [x] 残高確認
  - [x] 取引検証
  - [x] 残高更新
  - [x] ログ記録
- [x] `init_user_account()` メソッド
  - [x] 新規ユーザーデータ作成

### STEP 9: ユーザー向けコマンド
- [x] `/残高` コマンド実装
  - [x] `@app_commands.command(name="残高", description="自分のKR残高を確認します")` デコレータ
  - [x] `get_balance_api()` で残高取得
  - [x] Discord Embed作成（緑色、残高情報、フッター設定）
  - [x] `ephemeral=True` で個人向け応答
- [x] `/送金` コマンド実装
  - [x] `@app_commands.describe` でパラメータ説明
  - [x] 自分への送金禁止チェック
  - [x] `validate_transaction()` で取引検証
  - [x] 送金処理：subtract_kr_api() → add_kr_api()
  - [x] 受取人への付与失敗時のロールバック処理
  - [x] 成功時のEmbed表示（受取人メンション含む）
- [x] `/スロット` コマンド実装
  - [x] ベット額検証（100KR〜10,000KR）
  - [x] `subtract_kr_api()` でKR減額
  - [x] スロット結果計算（symbols配列から3つ選択）
  - [x] 配当計算ロジック
    - [x] 💎💎💎: 10倍
    - [x] ⭐⭐⭐: 5倍  
    - [x] その他三つ揃い: 3倍
    - [x] 二つ揃い: 1.5倍
  - [x] 控除率5%適用（house_edge処理）
  - [x] 勝利時の`add_kr_api()` 呼び出し
  - [x] 結果Embed表示（勝敗で色分け）

### STEP 10: 管理者コマンド
- [x] `/残高調整` コマンド実装
  - [x] `@app_commands.describe` でパラメータ説明追加
  - [x] 管理者ID確認（kraft_config.pyのADMIN_USER_IDS使用）
  - [x] 正の金額時：`add_kr_api()` 呼び出し
  - [x] 負の金額時：`subtract_kr_api()` 呼び出し（絶対値使用）
  - [x] 調整後残高の取得・表示
  - [x] 管理者向け詳細ログ（理由・調整額・新残高）
  - [x] `ephemeral=True` で管理者のみ表示

---

## 🎮 Phase 3: Community Bot開発

**📌 重要：Central Bank Botの成功パターンを適用**
- ✅ `on_ready`内でコマンドを動的定義する方式を使用
- ✅ Firebase直接操作でBot間連携
- ✅ 段階的実装と動作確認を重視

### STEP 11: Community Bot基本構造作成 ⭐**高優先度**
- [x] ✅ ファイル作成: `kraft_community_bot.py`
- [x] ✅ 基本Botクラス実装（Central Bank Botパターン適用）
  - [x] ✅ 環境変数読み込み（`DISCORD_TOKEN_COMMUNITY_BOT`）
  - [x] ✅ Firebase初期化
  - [x] ✅ Discord intents設定（message_content=True, guilds=True, members=True）
  - [x] ✅ `on_ready`イベントで動的コマンド定義
  - [x] ✅ コマンド同期（グローバル同期）
- [x] ✅ **動作確認**: Bot起動とコマンドテスト

### STEP 12: Firebase直接操作ヘルパー関数群 ⭐**高優先度**
- [x] ✅ XPSystem関連ヘルパー関数実装
  - [x] ✅ Firebase直接操作でユーザー情報取得・更新
  - [x] ✅ XP追加とレベルアップ判定統合処理
  - [x] ✅ KR残高更新（Firebase直接操作）
- [x] ✅ レベル計算関数
  - [x] ✅ `calculate_xp_for_level(level)` - 必要XP計算（指数関数式）
  - [x] ✅ `calculate_level_and_xp(total_xp)` - 総XPからレベル・現在XP計算
- [x] ✅ **動作確認**: 各関数の単体テスト

### STEP 13: XPシステムと基本コマンド実装 ⭐**高優先度**
- [x] ✅ `/プロフィール` コマンド実装（`on_ready`内で定義）
  - [x] ✅ ユーザーデータ取得・表示
  - [x] ✅ レベル、XP、KR残高表示
  - [x] ✅ レベル進捗バー表示
  - [x] ✅ クエスト完了数・各種統計表示
- [x] ✅ `/寄付` コマンド実装
  - [x] ✅ 金額検証（100KR以上、100,000KR以下）
  - [x] ✅ KR減額処理（Firebase直接操作）
  - [x] ✅ XP報酬付与（寄付額×0.1XP）
  - [x] ✅ レベルアップチェックと通知
- [x] ✅ **動作確認**: プロフィール表示と寄付機能テスト

### STEP 14: メッセージ監視とXP付与機能 ⭐**高優先度**
- [x] ✅ `on_message`イベントハンドラ実装
  - [x] ✅ Botメッセージの除外処理
  - [x] ✅ 60秒クールダウン制御（Firebase管理）
  - [x] ✅ メッセージごとに5XP付与
  - [x] ✅ レベルアップ判定と通知
- [x] ✅ レベルアップ通知システム
  - [x] ✅ KR報酬自動付与（レベル×500KR）
  - [x] ✅ 通知Embed作成（ゴールド色、報酬表示）
  - [x] ✅ 同じチャンネルでの即座通知
- [x] ✅ **動作確認**: メッセージ投稿でXP獲得とレベルアップ

### STEP 15: 個人クエストシステム実装 **中優先度**
- [x] ✅ `/クエスト作成` コマンド実装（日付選択式）
  - [x] ✅ 年・月・日の個別入力（日付検証含む）
  - [x] ✅ 過去日付・無効日付チェック
  - [x] ✅ 期間に応じたXP計算（1日=10XP）
  - [x] ✅ Firebase personal_questsコレクションに保存
- [x] ✅ `/マイクエスト` コマンド実装
  - [x] ✅ 個人のアクティブクエスト一覧取得
  - [x] ✅ 残り時間計算と表示
  - [x] ✅ プライベート表示（ephemeral）
- [x] ✅ **動作確認**: クエスト作成と一覧表示

### STEP 16: クエスト達成・削除システム **中優先度**
- [x] ✅ `/クエスト達成` コマンド実装（選択式UI）
  - [x] ✅ アクティブクエスト取得
  - [x] ✅ Discord Select Menu作成
  - [x] ✅ クエスト完了処理とXP報酬付与
  - [x] ✅ レベルアップチェックと報酬
- [x] ✅ `/クエスト削除` コマンド実装（選択式UI）
  - [x] ✅ Select UI作成
  - [x] ✅ 単純削除処理（失敗扱いなし）
  - [x] ✅ 削除確認とステータス更新
- [x] ✅ **動作確認**: 選択式UI操作とクエスト処理

### STEP 17: バックグラウンドタスク **低優先度**
- [x] ✅ `quest_deadline_check`タスク実装
  - [x] ✅ `@tasks.loop(hours=1)`デコレータ
  - [x] ✅ 期限切れクエストの自動削除
  - [x] ✅ personal_questsコレクションの期限管理
- [x] ✅ **動作確認**: タスクの自動実行確認

### STEP 18: 最終テストと最適化 **中優先度**
- [x] ✅ 全機能統合テスト
  - [x] ✅ XP獲得→レベルアップ→KR報酬の一連動作
  - [x] ✅ 個人クエスト機能の全工程テスト
  - [x] ✅ 選択式UIの動作確認
  - [x] ✅ エラーハンドリングの確認
- [x] ✅ UI/UX改善
  - [x] ✅ 選択式インターフェース実装
  - [x] ✅ プライベート表示の活用
  - [x] ✅ わかりやすいエラーメッセージ
- [x] ✅ **最終確認**: 全コマンドの動作確認完了

**🎯 開発のポイント:**
1. **段階的実装**: STEP 11-14を順次完成させてから次に進む
2. **動作確認**: 各STEPで必ず動作テストを実施
3. **成功パターン適用**: Central Bank Botと同じ構造を踏襲
4. **シンプルな実装**: Cogシステムは使わず、直接的なコマンド定義

---

## 🏅 Phase 4: Title Bot開発

### STEP 19: Title Bot基本構造作成
- [x] ✅ ファイル作成: `kraft_title_bot.py`
- [x] ✅ 必要なimport文（discord.py, firebase, asyncio等）
- [x] ✅ 環境変数読み込み（`TITLE_BOT_TOKEN`）
- [x] ✅ Firebase初期化処理
- [x] ✅ ロギング設定

### STEP 20: 称号条件定義（TITLE_CONDITIONS辞書）
- [x] ✅ `TITLE_CONDITIONS` 辞書定義（18種類完全版）
- [x] ✅ レベル系称号（6種）
  - [x] ✅ 新人冒険者（レベル5）
  - [x] ✅ 冒険者（レベル10）
  - [x] ✅ 熟練冒険者（レベル20）
  - [x] ✅ 探求者（レベル30）
  - [x] ✅ 達人（レベル50）
  - [x] ✅ 生きる伝説（レベル100）
- [x] ✅ アクティビティ系称号（3種）
  - [x] ✅ よく喋る人（月間500メッセージ）
  - [x] ✅ エミネム（月間1000メッセージ）
  - [x] ✅ どこにでもいる人（月間10チャンネル）
- [x] ✅ クエスト系称号（3種）
  - [x] ✅ クエストマスター（100回達成）
  - [x] ✅ どんまい（2連続失敗）
  - [x] ✅ 逆にすごい（10連続失敗）
- [x] ✅ 経済系称号（6種）
  - [x] ✅ 寄付マスター（総額5万KR）
  - [x] ✅ 聖人（寄付で残高0）
  - [x] ✅ 投資マスター（利益10万KR）
  - [x] ✅ ノーリターン（投資で残高0）
  - [x] ✅ ギフトマスター（送金総額10万KR）
  - [x] ✅ 大盤振る舞い（送金で残高0）

### STEP 21: KraftTitleBotメインクラス実装
- [x] ✅ `KraftTitleBot` クラス定義（commands.Bot継承）
- [x] ✅ `__init__()` メソッド
  - [x] ✅ Discord intents設定（message_content=True, members=True）
  - [x] ✅ command_prefix設定（'!title_'）
  - [x] ✅ 称号チェックキュー初期化（`asyncio.Queue()`）
  - [x] ✅ 通知チャンネルID設定
- [x] ✅ `on_ready()` イベントハンドラ
  - [x] ✅ 起動メッセージ出力
  - [x] ✅ コマンド同期処理（`self.tree.sync()`）
  - [x] ✅ title_check_task開始確認・起動
  - [x] ✅ monthly_reset_task開始確認・起動

### STEP 22: 称号チェック・付与システム実装
- [x] ✅ `check_user_titles()` メソッド
  - [x] ✅ Firestoreからユーザーデータ取得
  - [x] ✅ 未存在時は空リスト返却
  - [x] ✅ 現在の称号セット作成
  - [x] ✅ TITLE_CONDITIONS全ループ処理
  - [x] ✅ 既保有称号のスキップ処理
  - [x] ✅ `evaluate_condition()` 呼び出し
  - [x] ✅ 新称号リスト作成・Firestore更新
- [x] ✅ `evaluate_condition()` メソッド
  - [x] ✅ 安全な変数辞書作成（13項目）
    - [x] ✅ level, monthly_messages, active_channels
    - [x] ✅ completed_quests, consecutive_quest_failures
    - [x] ✅ donation_total, transfer_total, investment_profit
    - [x] ✅ became_zero_by_* 系フラグ（3種）
  - [x] ✅ `eval(condition, {"__builtins__": {}}, safe_vars)` 実行
  - [x] ✅ 例外処理とログ出力
- [x] ✅ `assign_discord_role()` メソッド
  - [x] ✅ 全ギルドループ処理
  - [x] ✅ メンバー取得とロール検索
  - [x] ✅ ロール付与処理（`member.add_roles()`）
  - [x] ✅ 成功ログ出力
- [x] ✅ `send_title_notification()` メソッド
  - [x] ✅ 通知チャンネル取得
  - [x] ✅ ユーザー取得（fetch_user含む）
  - [x] ✅ Embed作成（ゴールド色、サムネイル、フッター）
  - [x] ✅ カテゴリ・条件詳細表示

### STEP 23: イベント監視システム実装
- [x] ✅ `on_message_event()` メソッド
  - [x] ✅ 月間アクティビティ更新
  - [x] ✅ 称号チェックキューに追加
- [x] ✅ `on_quest_complete_event()` メソッド
  - [x] ✅ 連続失敗カウンターリセット
- [x] ✅ `on_quest_failure_event()` メソッド
  - [x] ✅ 連続失敗カウンター増加
- [x] ✅ `on_economic_event()` メソッド
  - [x] ✅ 経済活動データ更新（寄付・送金・投資）
- [x] ✅ `update_monthly_activity()` メソッド
  - [x] ✅ 月次リセット判定
  - [x] ✅ メッセージ数・アクティブチャンネル更新

### STEP 24: ユーザー向けコマンド実装
- [x] ✅ ~~`/称号状況` コマンド実装~~ → **削除完了**（プロフィールに統合）
- [x] ✅ ~~`/称号一覧` コマンド実装~~ → **削除完了**（発見の楽しみのため）
- [x] ✅ `/称号強制チェック` コマンド実装（管理者専用）
  - [x] ✅ 管理者ID確認
  - [x] ✅ 全ユーザー称号チェック実行
  - [x] ✅ 結果サマリー表示（チェック人数・新規称号数）
- [x] ✅ **プロフィールコマンドに称号表示追加**
  - [x] ✅ Community Botのプロフィールに称号欄追加
  - [x] ✅ 最大3個表示（それ以上は「他○個」）
  - [x] ✅ 称号の意味は非公開（発見の楽しみ）
  - [x] ✅ **ユーザーが自分で発見する楽しみを保持**

### STEP 25: バックグラウンドタスク実装
- [x] ✅ `title_check_task()` タスク実装
  - [x] ✅ `@tasks.loop(minutes=5)` デコレータ
  - [x] ✅ キューからイベント処理（最大10件）
  - [x] ✅ 新称号のロール付与・通知処理
  - [x] ✅ レート制限対策（1秒待機）
- [x] ✅ `monthly_reset_task()` タスク実装
  - [x] ✅ `@tasks.loop(hours=24)` デコレータ
  - [x] ✅ 月初処理（必要に応じて実装）

---

## 📈 Phase 5: Stock Market Bot開発

### STEP 26: Stock Market Bot基本構造作成
- [x] ✅ ファイル作成: `kraft_stock_market_bot.py`
- [x] ✅ 必要なimport文（discord.py, firebase, math, random等）
- [x] ✅ 環境変数読み込み（`DISCORD_TOKEN_STOCK_MARKET_BOT`）
- [x] ✅ Firebase初期化処理
- [x] ✅ Bot基本設定（intents, command_prefix）

### STEP 27: 株式・銘柄データ管理システム
- [x] ✅ `STOCK_DATA` 辞書定義（日本企業ベース12社）
  - [x] ✅ ハードバンク (9984)（テクノロジー）
  - [x] ✅ トミタ (7203)（自動車）
  - [x] ✅ USJ銀行 (8306)（金融）
  - [x] ✅ ソミー (6758)（電機・精密機器）
  - [x] ✅ ドモコ (9432)（通信）
  - [x] ✅ ナインイレブン (3382)（小売）
  - [x] ✅ 住不動産 (8801)（不動産）
  - [x] ✅ 四菱ケミカル (4183)（素材・化学）
  - [x] ✅ 新目鉄 (5401)（鉄鋼・重工業）
  - [x] ✅ キリンジ (2503)（食品・飲料）
  - [x] ✅ 東京雷神 (9501)（電力・ガス）
  - [x] ✅ アステラサズ (4502)（医薬品）
- [x] ✅ 各社データ設定（name, sector, initial_price, volatility, dividend, emoji）
- [x] ✅ 市場設定（取引手数料1%, 取引制限, 市場開場時間）

### STEP 28: 市場価格変動シミュレーション
- [x] ✅ 幾何ブラウン運動ベースの価格計算
- [x] ✅ `price_update_task()` バックグラウンドタスク（30分間隔）
- [x] ✅ ボラティリティ別変動率設定
  - [x] ✅ 高ボラティリティ：新目鉄(8%), ソミー(7%), ハードバンク(6%)
  - [x] ✅ 中ボラティリティ：USJ銀行(5%), 四菱ケミカル(5%), トミタ(4%)
  - [x] ✅ 低ボラティリティ：ドモコ(2%), キリンジ(2%)
- [x] ✅ 価格下限制限（初期価格の10%）
- [x] ✅ 価格履歴管理（最新50件保持）

### STEP 29: 売買注文システム実装
- [x] ✅ `/株式購入` コマンド実装（選択式UI）
  - [x] ✅ Discord Select Menu作成（12銘柄選択肢）
  - [x] ✅ 株数入力モーダル
  - [x] ✅ 市場開場時間チェック
  - [x] ✅ 残高確認・手数料計算
  - [x] ✅ 取引制限チェック（日次50回, 最小100KR, 最大1,000,000KR）
  - [x] ✅ Firebase取引実行・ポートフォリオ更新
- [x] ✅ `/株式売却` コマンド実装（選択式UI）
  - [x] ✅ 保有銘柄のみ表示
  - [x] ✅ 保有株数確認・損益計算
  - [x] ✅ 平均取得価格基準の損益表示
  - [x] ✅ 手数料差引後受取額計算

### STEP 30: ポートフォリオ管理機能
- [x] ✅ `/ポートフォリオ` コマンド実装（リッチ表示）
  - [x] ✅ 評価額順ソート表示
  - [x] ✅ 構成比グラフ（バー表示）
  - [x] ✅ セクター分散分析
  - [x] ✅ パフォーマンス評価（🚀優秀〜🔴要改善）
  - [x] ✅ 個別銘柄詳細（保有数・取得価格・現在価格・損益）
  - [x] ✅ ポートフォリオサマリー（総評価額・総損益・収益率）
- [x] ✅ プライベート表示（ephemeral=True）
- [x] ✅ 他人のポートフォリオ表示削除

### STEP 31: 投資ニュース・イベント機能
- [x] ✅ `market_news_task()` バックグラウンドタスク（6時間間隔）
- [x] ✅ ランダムニュース生成システム
  - [x] ✅ 30%確率でニュース配信
  - [x] ✅ 5種類のニュースパターン
- [x] ✅ Discord投資ニュースチャンネル自動投稿
- [x] ✅ Embedニュース表示（タイトル・説明・フッター）

### STEP 32: ランキング・統計機能
- [x] ✅ `/投資ランキング` コマンド実装
- [x] ✅ 収益率ランキング算出（TOP10）
- [x] ✅ 投資パフォーマンス比較
- [x] ✅ メダル表示（🥇🥈🥉）
- [x] ✅ 評価額・損益表示

### STEP 33: リスク管理・制限機能
- [x] ✅ 市場開場時間制限（0:00-23:00 UTC）
- [x] ✅ 日次取引回数制限（50回/日）
- [x] ✅ 取引金額制限（100-1,000,000 KR）
- [x] ✅ 手数料システム（1%）
- [x] ✅ 残高不足・保有株数不足チェック
- [x] ✅ Firebase取引ログ記録

---

## 🔧 Phase 6: 統合・テスト・デバッグ

### STEP 34: 統合テスト実行
- [x] ✅ **Stock Market Bot データ設定**
  - [x] ✅ 12社の日本企業ベース銘柄データ設定完了
  - [x] ✅ Firebase market_dataコレクション初期化
  - [x] ✅ 各銘柄の価格・ボラティリティ・配当設定
- [x] ✅ **Firebase コレクション確認**
  - [x] ✅ `users` - ユーザーデータ
  - [x] ✅ `personal_quests` - 個人クエストデータ
  - [x] ✅ `transactions` - KR取引履歴
  - [x] ✅ `trades` - 株式取引履歴
  - [x] ✅ `portfolios` - ユーザー投資データ
  - [x] ✅ `market_data` - 株価データ

### STEP 35: Bot間連携テスト
- [x] ✅ **Community → Central Bank 連携**
  - [x] ✅ レベルアップ時のKR付与動作確認
    - [x] ✅ メッセージ投稿でXP蓄積
    - [x] ✅ レベルアップ発生時の自動KR付与
    - [x] ✅ 報酬額計算正確性（レベル×500KR）
  - [x] ✅ 寄付時のKR減額動作確認
    - [x] ✅ `/寄付` 実行後の残高減少
    - [x] ✅ XP報酬付与（寄付額×0.1XP）
- [x] ✅ **Stock Market → Central Bank 連携**
  - [x] ✅ 株式購入時のKR決済動作確認
    - [x] ✅ 総額＋手数料（1%）の正確な減額
    - [x] ✅ 残高不足時の適切なエラー
  - [x] ✅ 株式売却時のKR受取動作確認
    - [x] ✅ 手数料差引後の正確な受取額
    - [x] ✅ 損益計算の正確性（平均取得価格基準）
- [x] ✅ **Title Bot統合動作確認**
  - [x] ✅ 18種類の称号条件設定完了
  - [x] ✅ レベル・アクティビティ・クエスト・経済系称号
  - [x] ✅ 自動称号チェック・ロール付与システム

### STEP 36: コマンド端末テスト
- [x] ✅ **Central Bank Bot コマンド**
  - [x] ✅ `/残高` - 残高確認（初期1000KR）
  - [x] ✅ `/送金` - ユーザー間送金
  - [x] ✅ `/スロット` - ギャンブル（100-10,000KR）
  - [x] ✅ `/残高調整` - 管理者専用
- [x] ✅ **Community Bot コマンド**
  - [x] ✅ `/プロフィール` - レベル・XP・残高表示
  - [x] ✅ `/寄付` - KR減額・XP獲得
  - [x] ✅ `/クエスト作成` - 日付選択式クエスト作成
  - [x] ✅ `/マイクエスト` - 個人クエスト一覧
  - [x] ✅ `/クエスト達成` - Select Menu選択式
  - [x] ✅ `/クエスト削除` - Select Menu選択式
- [x] ✅ **Title Bot コマンド**
  - [x] ✅ ~~`/称号状況`~~ - **削除済み**（プロフィールに統合）
  - [x] ✅ ~~`/称号一覧`~~ - **削除済み**（発見の楽しみ保持）
  - [x] ✅ `/称号強制チェック` - 管理者専用
  - [x] ✅ **環境変数名修正**（DISCORD_TOKEN_TITLE_BOT）
- [x] ✅ **Stock Market Bot コマンド**
  - [x] ✅ `/株価` - 12銘柄価格表示（コード番号削除済み）
  - [x] ✅ `/株式購入` - Select Menu選択式購入（エラー修正済み）
  - [x] ✅ `/株式売却` - Select Menu選択式売却
  - [x] ✅ `/ポートフォリオ` - リッチ表示（グラフ・分析、個人のみ）
  - [x] ✅ `/投資ランキング` - 収益率ランキング

### STEP 37: エラーハンドリングテスト
- [x] ✅ **Firebase接続エラー対応**
  - [x] ✅ 各Bot Firebase初期化確認
  - [x] ✅ Firestore読み書きエラーハンドリング
  - [x] ✅ ユーザーエラーメッセージ実装
- [x] ✅ **Discord UI エラー対応**
  - [x] ✅ Select Menu選択エラー処理
  - [x] ✅ モーダル入力検証
  - [x] ✅ 不正値入力時のエラーメッセージ
- [x] ✅ **取引制限・検証**
  - [x] ✅ 残高不足時の適切なエラー
  - [x] ✅ 取引上限チェック
  - [x] ✅ 市場開場時間制限

### STEP 38: パフォーマンステスト
- [x] ✅ **レスポンス時間確認**
  - [x] ✅ コマンド実行3秒以内
  - [x] ✅ Firebase読み書き最適化
  - [x] ✅ バックグラウンドタスク動作確認
- [x] ✅ **同時処理テスト**
  - [x] ✅ 複数ユーザー同時取引テスト
  - [x] ✅ Firebase競合状態回避
- [x] ✅ **メモリ・CPU使用量確認**
  - [x] ✅ 適切なリソース使用量

### STEP 39: バグ修正・最適化
- [x] ✅ **UI/UX改善**
  - [x] ✅ Select Menu選択肢エラー修正（decorator pattern使用）
  - [x] ✅ 株価表示から数字コード削除（企業名のみ表示）
  - [x] ✅ ポートフォリオ表示他人削除（個人のみ表示）
  - [x] ✅ ポートフォリオリッチ表示（バーグラフ・セクター分析）
- [x] ✅ **システム最適化**
  - [x] ✅ 株価更新30分間隔（幾何ブラウン運動）
  - [x] ✅ ニュース配信6時間間隔・30%確率
  - [x] ✅ 自動投稿チャンネル設定（投資ニュースチャンネル）
- [x] ✅ **Title Botコマンド最適化**
  - [x] ✅ 称号の発見楽しみを保持（リスト削除）
  - [x] ✅ プロフィール統合（最大3個+他○個表示）

---

## 📝 Phase 7: ドキュメント・運用準備

### STEP 40: README.md 作成
- [x] ✅ プロジェクト概要
- [x] ✅ セットアップ手順
- [x] ✅ 各Botの機能説明
- [x] ✅ トラブルシューティング

### STEP 41: API ドキュメント作成
- [x] ✅ `docs/API.md` 作成
- [x] ✅ kraft_api.py の全関数説明
- [x] ✅ Bot間通信フロー図

### STEP 42: デプロイメントガイド
- [x] ✅ `docs/DEPLOYMENT.md` 作成
- [x] ✅ 本番環境設定手順
- [x] ✅ 環境変数一覧
- [x] ✅ Firebase設定手順

### STEP 43: 最終動作確認
- [x] ✅ 全機能の動作テスト
- [x] ✅ エラーケースの確認
- [x] ✅ レスポンス時間測定
- [x] ✅ リソース使用量確認

### STEP 44: 経済バランス調整 🎯**全Bot完成後の重要タスク**
- [x] ✅ **全Bot稼働データ収集**
  - [x] ✅ 各ユーザーの主要収入源分析（メッセージXP、クエスト、レベルアップ、投資等）
  - [x] ✅ KR流入・流出バランスの測定
  - [x] ✅ インフレ・デフレ傾向の把握
  - [x] ✅ ユーザー行動パターンの分析
- [x] ✅ **経済パラメータ調整**
  - [x] ✅ XPシステム調整
    - [x] ✅ メッセージあたりXP（現在5XP）
    - [x] ✅ クエストXP計算式（現在1日=10XP）
    - [x] ✅ レベルアップ必要XP計算式
  - [x] ✅ KR報酬調整
    - [x] ✅ レベルアップ報酬（現在レベル×500KR）
    - [x] ✅ クエスト完了時のKR報酬
    - [x] ✅ 寄付XP交換レート（現在1KR=0.1XP）
  - [x] ✅ 株式市場パラメータ調整
    - [x] ✅ 初期株価設定の見直し
    - [x] ✅ 手数料率の調整（現在1%に設定済み）
    - [x] ✅ 価格変動幅の調整
  - [x] ✅ スロット・ギャンブル系調整
    - [x] ✅ 配当率の見直し
    - [x] ✅ 控除率の調整（現在5%）
- [x] ✅ **設定ファイル化**
  - [x] ✅ `config/economic_settings.py` 作成
  - [x] ✅ 全経済パラメータの集約
  - [x] ✅ 動的調整機能の実装
  - [x] ✅ バックアップ・復元機能
- [x] ✅ **バランステスト**
  - [x] ✅ 調整ツール作成（`scripts/balance_adjustment_tool.py`）
  - [x] ✅ 自動分析・推奨調整機能実装
  - [x] ✅ パラメータ調整履歴管理

---

## ✅ 完成チェックリスト

### 機能完成度確認
- [x] ✅ 4Bot全てが正常起動する
- [x] ✅ 全スラッシュコマンドが動作する
- [x] ✅ Firebase読み書きが正常動作する
- [x] ✅ Bot間連携が正常動作する
- [x] ✅ エラーハンドリングが適切に動作する

### セキュリティ確認
- [x] ✅ 管理者コマンドの権限チェック
- [x] ✅ 取引上限・制限の動作
- [x] ✅ 入力値検証の実装
- [x] ✅ ログ記録の実装

### パフォーマンス確認
- [x] ✅ レスポンス時間が適切（3秒以内）
- [x] ✅ Firebase制限内での動作
- [x] ✅ Discord API制限対応
- [x] ✅ メモリ使用量が適切

### 運用準備確認
- [x] ✅ ログ出力が適切
- [x] ✅ エラー通知機能
- [x] ✅ バックアップ機能
- [x] ✅ ドキュメント完備

---

## 🎯 重要な注意事項

### Cursor使用時のポイント
1. **段階的実装**: 一度に複数STEPではなく、1STEP単位で確実に進める
2. **テスト駆動**: 各STEPで必ず動作確認してから次のSTEPへ
3. **エラー対応**: エラーが出たら該当STEPに戻って仕様書と照らし合わせ修正
4. **依存関係遵守**: Phase順序を厳守（共通ライブラリ→Central Bank→他Bot）
5. **具体的指示**: 「STEP 7のKraftCentralBankクラスを実装して」など明確に指示
6. **仕様書参照**: 実装詳細は開発仕様書の該当セクションを参照
7. **Firebase設定**: 企業データなどの初期データは手動投入が必要

### 開発効率化のコツ
- **仕様書参照**: 実装詳細は開発仕様書を参照
- **コピペ活用**: 類似コードは既存実装からコピペ・改変
- **ログ確認**: 動作確認は必ずログ出力で確認
- **段階的テスト**: 小さな単位で頻繁にテスト実行

---

**このTODOリストに従って段階的に実装を進めれば、確実にKRAFT分散型Botシステムを完成させることができます！**
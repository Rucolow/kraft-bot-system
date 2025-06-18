# KRAFT Botシステム - 運用マニュアル

このドキュメントでは、KRAFT Botシステムの運用に必要な手順と注意事項を説明します。

## 1. システム概要

KRAFT Botシステムは、以下の4つの独立したDiscord Botで構成されています。

*   **KRAFT Community Bot (倉田 太)**: XP・レベルシステム、寄付、プロフィール管理
*   **KRAFT Central Bank Bot (KRAFT銀行)**: KR残高、送金、ギャンブル（スロット）、管理者による残高調整
*   **KRAFT Stock Market Bot (KRAFT株式市場)**: 株式売買、株価管理、ニュース生成、ポートフォリオ
*   **KRAFT Title Bot (KRAFT称号bot)**: 称号付与、Discordロール連携、行動データ監視

これらのボットはそれぞれ独立して動作しますが、Firebaseを通じてデータ連携を行っています。

## 2. セットアップ手順

1. プロジェクトディレクトリに移動します。
   ```bash
   cd /path/to/KRAFT/New\ bot
   ```

2. 仮想環境を有効化します。
   ```bash
   source venv/bin/activate
   ```

3. 各ボットを起動します。必要に応じて複数のターミナルウィンドウを使用してください。
   ```bash
   python3 kraft_community_bot.py
   python3 kraft_central_bank_bot.py
   python3 kraft_stock_market_bot.py
   python3 kraft_title_bot.py
   ```
   または、`nohup` や `screen` / `tmux` などのツールを使用してバックグラウンドで実行することもできます。

---

## 2. ボットの起動と停止

各ボットは個別のPythonスクリプトとして実行されます。

### 起動方法
各ボットのPythonスクリプトを個別に実行します。通常、開発環境では以下のコマンドを使用します。

1.  プロジェクトルートディレクトリに移動します。
    ```bash
    cd /Users/kenseidojima/Desktop/KRAFT/New\ bot
    ```
2.  仮想環境をアクティベートします。
    ```bash
    source venv/bin/activate
    ```
3.  各ボットを起動します。必要に応じて複数のターミナルウィンドウを使用してください。
    ```bash
    python3 kraft_community_bot.py
    python3 kraft_central_bank_bot.py
    python3 kraft_stock_market_bot.py
    python3 kraft_title_bot.py
    ```
    または、`nohup` や `screen` / `tmux` などのツールを使用してバックグラウンドで実行することもできます。

### 停止方法
実行中のターミナルで `Ctrl+C` を押すことで、各ボットプロセスを停止できます。バックグラウンドで実行している場合は、該当するプロセスを `kill` コマンドなどで停止してください。

---

## 3. 設定ファイルの管理

### `.env` ファイル
機密情報（APIトークン、APIキーなど）は `.env` ファイルに保存されています。このファイルはGit管理から除外されており、公開されるべきではありません。

*   `COMMUNITY_BOT_TOKEN`: Community BotのDiscordトークン
*   `CENTRAL_BANK_TOKEN`: Central Bank BotのDiscordトークン
*   `STOCK_MARKET_TOKEN`: Stock Market BotのDiscordトークン
*   `TITLE_BOT_TOKEN`: Title BotのDiscordトークン
*   `CLAUDE_API_KEY`: Claude APIのキー (ニュース生成用)
*   `ENVIRONMENT`: 環境設定（`development` または `production`）
*   `ADMIN_USER_IDS`: 管理者DiscordユーザーIDのカンマ区切りリスト (例: `1234567890,9876543210`)

### `config/firebase_credentials.json`
Firebaseサービスアカウントの秘密鍵ファイルです。このファイルも機密情報であり、Git管理から除外されています。

### `shared/kraft_config.py`
ボットの動作に関する一般的な設定（チャンネルID、称号ロール名など）が定義されています。設定変更はここで行います。変更後にはボットの再起動が必要です。

---

## 4. 監視とログ

各ボットは、起動時や重要な処理（取引、レベルアップ、称号付与など）の際にコンソールにログを出力します。これらのログは、ボットの稼働状況やエラーの特定に役立ちます。

*   **コンソールログ**: 各ボットを実行しているターミナルでリアルタイムに確認できます。
*   **Discord通知**: エラー発生時や重要なイベント（例: レベルアップ、称号獲得、投資ニュース）は、設定されたDiscordチャンネルに通知が送信されます。

---

## 5. トラブルシューティング

### ボットがオフラインの場合
1.  該当するボットのPythonスクリプトが実行されているか確認してください。
2.  ターミナルにエラーメッセージが出力されていないか確認してください。
3.  `.env` ファイルのトークンが正しいか、有効期限が切れていないか確認してください。

### コマンドが反応しない場合
1.  ボットがオンラインか確認してください。
2.  コマンドの入力に誤りがないか確認してください（スラッシュコマンドは正確な入力が必要です）。
3.  ボットが参加しているサーバーに必要な権限（メッセージの読み取り、送信、スラッシュコマンドの使用など）が付与されているか確認してください。
4.  コンソールログにエラーが出力されていないか確認してください。

### 残高がおかしい、または取引ができない場合
1.  Firebase Firestoreの`users`コレクションにあるユーザーデータを確認し、`balance`フィールドが正しいか確認してください。
2.  `kraft_central_bank_bot.py` のログを確認し、取引検証やエラーに関するメッセージがないか確認してください。
3.  `shared/kraft_config.py` 内の経済システム設定（取引制限など）が意図した通りか確認してください。

### 称号が付与されない場合
1.  `kraft_title_bot.py` のログを確認し、称号チェックに関するエラーがないか確認してください。
2.  Firebase Firestoreの`users`コレクションにあるユーザーデータが、称号条件を満たしているか確認してください。
3.  `shared/kraft_config.py` 内の称号条件設定が正しいか確認してください。
4.  称号ロールがDiscordサーバーに正しく作成されているか、ボットにロール管理権限があるか確認してください。

---

## 6. 管理者コマンド

管理者権限を持つユーザー（`.env`の`ADMIN_USER_IDS`に設定されたIDを持つユーザー）のみが実行できるコマンドです。

*   **`/残高調整 [user] [金額] [理由]` (KRAFT銀行Bot)**
    *   指定したユーザーのKR残高を直接調整します。負の数を指定すると減額されます。悪用厳禁です。
*   **`/称号強制チェック` (KRAFT称号bot)**
    *   全ユーザーの称号獲得条件を強制的に再チェックし、必要なロールを付与します。主にシステム変更後や整合性チェックのために使用します。 
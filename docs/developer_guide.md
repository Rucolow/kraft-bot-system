# KRAFT Botシステム - 開発者ガイド

このドキュメントでは、KRAFT Botシステムの開発に必要な情報と手順を説明します。

## 1. プロジェクト構造

```
KRAFT/New bot/
├── docs/                      # ドキュメント
│   ├── developer_guide.md     # 開発者ガイド（本ドキュメント）
│   ├── user_commands.md       # ユーザーコマンド一覧
│   ├── feature_guide.md       # 機能ガイド
│   ├── operation_manual.md    # 運用マニュアル
│   ├── faq.md                # よくある質問
│   └── backup_restore.md      # バックアップとリストア手順
├── kraft_community_bot.py     # コミュニティBot（XP・レベル・クエスト）
├── kraft_central_bank_bot.py  # 中央銀行Bot（KR管理・送金）
├── kraft_stock_market_bot.py  # 株式市場Bot（投資・ニュース）
├── kraft_title_bot.py         # 称号Bot（称号・ロール管理）
├── kraft_config.py           # 共通設定
├── kraft_api.py              # APIクライアント
├── kraft_bot_todo.md         # 開発TODOリスト
└── kraft_distributed_architecture.md  # システムアーキテクチャ
```

## 2. 開発環境のセットアップ

### 2.1 必要条件
- Python 3.11以上
- pip（Pythonパッケージマネージャー）
- Git
- Firebaseアカウントとプロジェクト
- Discord Developer PortalでのBot設定

### 2.2 環境構築手順

1. リポジトリのクローン
   ```bash
   git clone <repository-url>
   cd "KRAFT/New bot"
   ```

2. 仮想環境の作成と有効化
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # または
   .\venv\Scripts\activate  # Windows
   ```

3. 依存パッケージのインストール
   ```bash
   pip install -r requirements.txt
   ```

4. 環境変数の設定
   `.env`ファイルを作成し、以下の変数を設定：
   ```
   # Discord Bot Tokens
   COMMUNITY_BOT_TOKEN=your_token_here
   CENTRAL_BANK_TOKEN=your_token_here
   STOCK_MARKET_TOKEN=your_token_here
   TITLE_BOT_TOKEN=your_token_here

   # Firebase
   FIREBASE_PROJECT_ID=your_project_id
   FIREBASE_PRIVATE_KEY=your_private_key
   FIREBASE_CLIENT_EMAIL=your_client_email

   # API Keys
   CLAUDE_API_KEY=your_api_key_here
   ```

5. Firebase認証情報の配置
   - Firebase Consoleからダウンロードした認証情報JSONファイルを`config/firebase_credentials.json`として配置

## 3. 開発ガイドライン

### 3.1 コード規約
- PEP 8に準拠したPythonコードスタイル
- 関数とクラスには必ずdocstringを記述
- 型ヒントを使用（Python 3.11の機能を活用）
- ログ出力は`logging`モジュールを使用
- 例外処理は適切な例外クラスを使用

### 3.2 コミットメッセージ規約
```
<type>: <subject>

<body>

<footer>
```
- type: feat, fix, docs, style, refactor, test, chore
- subject: 変更内容の簡潔な説明
- body: 変更の詳細な説明（必要な場合）
- footer: 関連するIssue番号など（必要な場合）

### 3.3 テスト
- 各Botの機能は`tests/`ディレクトリにテストコードを作成
- テスト実行: `python -m pytest tests/`
- カバレッジレポート: `python -m pytest --cov=. tests/`

## 4. デプロイメント

### 4.1 本番環境へのデプロイ
1. コードのテスト実行
2. 環境変数の確認
3. 各Botの起動
   ```bash
   # バックグラウンドで実行する場合
   nohup python3 kraft_community_bot.py > community.log 2>&1 &
   nohup python3 kraft_central_bank_bot.py > central_bank.log 2>&1 &
   nohup python3 kraft_stock_market_bot.py > stock_market.log 2>&1 &
   nohup python3 kraft_title_bot.py > title.log 2>&1 &
   ```

### 4.2 モニタリング
- ログファイルの監視
- Firebase Consoleでのデータ監視
- Discord Botのステータス監視

## 5. トラブルシューティング

### 5.1 一般的な問題
- Botが応答しない
  - トークンの有効性確認
  - インターネット接続確認
  - ログファイルの確認
- Firebase接続エラー
  - 認証情報の確認
  - プロジェクトIDの確認
  - ネットワーク接続確認

### 5.2 デバッグ方法
- ログレベルの変更（DEBUG）
- Firebase Consoleでのデータ確認
- Discord Developer PortalでのBot設定確認

## 6. セキュリティ

### 6.1 機密情報の管理
- 環境変数は`.env`ファイルで管理
- `.env`ファイルは`.gitignore`に追加
- Firebase認証情報は安全に保管

### 6.2 アクセス制御
- 管理者コマンドの権限設定
- Firebaseのセキュリティルール
- Discordのロールベースアクセス制御

## 7. パフォーマンス最適化

### 7.1 データベース
- Firebaseのインデックス設定
- クエリの最適化
- キャッシュの活用

### 7.2 ボット
- 非同期処理の適切な使用
- メモリ使用量の監視
- 定期的なクリーンアップタスク

## 8. 今後の開発

### 8.1 計画されている機能
- `kraft_bot_todo.md`を参照

### 8.2 改善点
- パフォーマンスの最適化
- エラーハンドリングの強化
- テストカバレッジの向上
- ドキュメントの充実 
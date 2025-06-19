# 自動デプロイメント設定ガイド

## 概要

このガイドでは、KRAFT Bot SystemのGitHub → VPS自動デプロイメントを設定する手順を説明します。

## 🎯 実装された機能

### 1. 自動デプロイメント
- GitHub main ブランチへのプッシュで自動実行
- SSH経由でVPSに接続し、最新コードをデプロイ
- 依存関係のアップデート
- サービスの自動再起動

### 2. 自動再起動機能
- ボットプロセスのクラッシュを検知
- 最大10回まで自動再起動
- systemdレベルでの冗長性

### 3. ヘルスモニタリング
- 5分間隔での自動ヘルスチェック
- システムリソース監視
- Discord API接続確認
- 問題発生時のDiscord通知

### 4. ロールバック機能
- 前バージョンへの緊急復旧
- ワンコマンドでの簡単実行

## 🚀 セットアップ手順

### Step 1: VPS上での初期セットアップ

```bash
# 1. VPSにSSH接続
ssh ubuntu@160.16.76.218
sudo su - kraftbot
cd kraft-bot-system

# 2. 最新コードを取得
git pull origin main

# 3. スクリプトに実行権限を付与
chmod +x scripts/*.sh
chmod +x scripts/*.py

# 4. 必要なPythonパッケージを追加
pip install psutil aiohttp

# 5. ログディレクトリを作成
mkdir -p logs/health

# 6. 現在の環境を確認
./scripts/check_vps_setup.sh
```

### Step 2: systemdサービスの設定

```bash
# kraftbotユーザーで実行
sudo bash scripts/setup_systemd.sh
```

### Step 3: GitHub Secretsの設定

1. GitHubリポジトリ → Settings → Secrets and variables → Actions
2. 以下のSecretsを追加:

| Secret名 | 値 | 説明 |
|----------|----|----- |
| `VPS_HOST` | `160.16.76.218` | VPSのIPアドレス |
| `VPS_USER` | `ubuntu` | SSH接続ユーザー |
| `SSH_PRIVATE_KEY` | SSH秘密鍵の内容 | `cat ~/.ssh/id_rsa` の出力 |
| `DISCORD_WEBHOOK` | WebhookのURL | デプロイ通知用（オプション） |

### Step 4: 動作確認

```bash
# 1. 手動でGitHub Actionsをテスト
# GitHub → Actions → Deploy to VPS → Run workflow

# 2. VPSでログを確認
tail -f ~/kraft-bot-system/deploy.log

# 3. サービス状況を確認
systemctl status kraft-*

# 4. ヘルスモニターを確認
systemctl status kraft-health-monitor
```

## 🔧 日常的な操作

### デプロイメント

```bash
# 自動デプロイ（GitHub経由）
git add .
git commit -m "Update: 機能改善"
git push origin main
# → 自動的にVPSにデプロイされる

# 手動デプロイ（VPS上で）
cd ~/kraft-bot-system
bash scripts/deploy.sh
```

### 監視・メンテナンス

```bash
# サービス状況確認
systemctl status kraft-*

# ログ確認
journalctl -u kraft-* -f

# ヘルスチェック実行
python scripts/health_monitor.py --once

# リソース使用量確認
top -u kraftbot
```

### 緊急時の対応

```bash
# 全サービス再起動
sudo systemctl restart kraft-*

# ロールバック（前バージョンに戻す）
bash scripts/rollback.sh

# 個別サービス再起動
sudo systemctl restart kraft-central-bank
sudo systemctl restart kraft-community
sudo systemctl restart kraft-title
sudo systemctl restart kraft-stock-market
```

## 📊 監視・アラート

### ヘルスモニター

- **実行間隔**: 5分
- **チェック内容**: 
  - 各ボットプロセスの稼働状況
  - システムリソース（CPU, メモリ, ディスク）
  - Discord API接続
- **アラート**: 問題発生時にDiscord通知

### ログファイル

| ログファイル | 内容 |
|-------------|------|
| `deploy.log` | デプロイメント履歴 |
| `logs/health_monitor.log` | ヘルスチェック履歴 |
| `logs/wrapper_*.log` | 各ボットの再起動履歴 |
| `logs/*.log` | 各ボットの実行ログ |

## 🔍 トラブルシューティング

### デプロイメント失敗

```bash
# GitHub Actionsのログを確認
# SSH接続エラーの場合:
ssh-keygen -R 160.16.76.218  # ホストキーをリセット
ssh ubuntu@160.16.76.218     # 手動接続テスト

# VPS上での確認
systemctl status kraft-*
journalctl -u kraft-* --since "1 hour ago"
```

### ボット停止

```bash
# 自動再起動の確認
systemctl status kraft-*

# 手動再起動
sudo systemctl restart kraft-[bot-name]

# ログで原因確認
journalctl -u kraft-[bot-name] -n 50
```

### ヘルスモニター問題

```bash
# ヘルスモニター状況確認
systemctl status kraft-health-monitor

# 手動実行でテスト
python scripts/health_monitor.py --once

# Discord Webhook テスト
python scripts/health_monitor.py --webhook YOUR_WEBHOOK_URL --once
```

## 🎮 追加機能

### Discord通知のカスタマイズ

ヘルスモニターでDiscord Webhookを設定すると、以下の場合に通知が送信されます：

- ボットの停止・障害
- システムリソースの異常
- Discord API接続問題

### 定期メンテナンス

```bash
# 月次実行推奨
sudo systemctl daemon-reload
pip install -r requirements.txt --upgrade
find logs/ -name "*.log" -mtime +30 -delete
```

これで完全な自動化システムが構築されました！
# KRAFT分散型Botシステム デプロイメントガイド

## 🎯 概要

このガイドでは、KRAFTシステムを本番環境にデプロイする手順を説明します。開発環境から本番環境への移行、監視設定、バックアップ戦略まで網羅しています。

## 📋 デプロイメント要件

### システム要件
- **OS**: Ubuntu 20.04 LTS以上 / CentOS 8以上
- **Python**: 3.9以上
- **RAM**: 最低2GB、推奨4GB以上
- **Storage**: 最低10GB、推奨20GB以上
- **Network**: 安定したインターネット接続

### 外部サービス
- **Discord**: Bot Application × 4個
- **Firebase**: Firestore Database
- **Claude API**: Anthropic アカウント
- **ドメイン**: (オプション) 監視用Webhook

## 🚀 本番環境セットアップ

### 1. サーバー準備

#### Ubuntu/Debian系
```bash
# システム更新
sudo apt update && sudo apt upgrade -y

# 必要パッケージインストール
sudo apt install -y python3 python3-pip python3-venv git curl nginx

# Python仮想環境作成
python3 -m venv /opt/kraft_bot
source /opt/kraft_bot/bin/activate

# 権限設定
sudo chown -R kraft_user:kraft_user /opt/kraft_bot
```

#### CentOS/RHEL系
```bash
# システム更新
sudo yum update -y

# 必要パッケージインストール
sudo yum install -y python3 python3-pip git curl

# Python仮想環境作成
python3 -m venv /opt/kraft_bot
source /opt/kraft_bot/bin/activate
```

### 2. アプリケーションデプロイ

```bash
# アプリケーション配置
cd /opt/kraft_bot
git clone [your-repository-url] kraft_system
cd kraft_system

# 依存関係インストール
pip install -r requirements.txt

# 設定ディレクトリ作成
mkdir -p config logs
chmod 750 config logs
```

### 3. 環境変数設定

#### 本番用 `.env` ファイル作成
```bash
# /opt/kraft_bot/kraft_system/.env
nano .env
```

```env
# Discord Bot Tokens (本番用)
DISCORD_TOKEN_CENTRAL_BANK_BOT=your_production_token_1
DISCORD_TOKEN_COMMUNITY_BOT=your_production_token_2
DISCORD_TOKEN_TITLE_BOT=your_production_token_3
DISCORD_TOKEN_STOCK_MARKET_BOT=your_production_token_4

# Firebase設定 (本番用)
FIREBASE_CREDENTIALS_PATH=/opt/kraft_bot/kraft_system/config/firebase_credentials_prod.json

# Claude API (本番用)
CLAUDE_API_KEY=your_production_claude_api_key

# 管理者設定
ADMIN_USER_IDS=prod_admin_id_1,prod_admin_id_2

# 本番チャンネルID
LEVELUP_CHANNEL_ID=prod_levelup_channel_id
TITLE_NOTIFICATION_CHANNEL_ID=prod_title_channel_id
INVESTMENT_NEWS_CHANNEL_ID=prod_investment_channel_id
DONATION_CHANNEL_ID=prod_donation_channel_id

# 本番環境設定
ENVIRONMENT=production
LOG_LEVEL=INFO
```

#### 権限設定
```bash
chmod 600 .env
chown kraft_user:kraft_user .env
```

### 4. Firebase本番設定

#### 本番用Firebase設定
```bash
# 本番用認証ファイル配置
cp firebase_credentials_prod.json /opt/kraft_bot/kraft_system/config/
chmod 600 /opt/kraft_bot/kraft_system/config/firebase_credentials_prod.json
```

#### Firestore セキュリティルール (本番用)
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // ユーザーデータ: 読み取り制限
    match /users/{userId} {
      allow read, write: if request.auth != null;
    }
    
    // 取引履歴: 管理者のみ
    match /transactions/{transactionId} {
      allow read, write: if request.auth != null && 
        request.auth.uid in ['admin_uid_1', 'admin_uid_2'];
    }
    
    // 市場データ: 読み取り専用
    match /market_data/{symbol} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    
    // その他のコレクション
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 🔧 systemd サービス設定

### 各Bot用systemdサービス作成

#### 1. Central Bank Bot
```bash
sudo nano /etc/systemd/system/kraft-central-bank.service
```

```ini
[Unit]
Description=KRAFT Central Bank Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=kraft_user
Group=kraft_user
WorkingDirectory=/opt/kraft_bot/kraft_system
Environment=PATH=/opt/kraft_bot/bin
ExecStart=/opt/kraft_bot/bin/python kraft_central_bank.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kraft-central-bank

[Install]
WantedBy=multi-user.target
```

#### 2. Community Bot
```bash
sudo nano /etc/systemd/system/kraft-community.service
```

```ini
[Unit]
Description=KRAFT Community Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=kraft_user
Group=kraft_user
WorkingDirectory=/opt/kraft_bot/kraft_system
Environment=PATH=/opt/kraft_bot/bin
ExecStart=/opt/kraft_bot/bin/python kraft_community_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kraft-community

[Install]
WantedBy=multi-user.target
```

#### 3. Title Bot
```bash
sudo nano /etc/systemd/system/kraft-title.service
```

```ini
[Unit]
Description=KRAFT Title Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=kraft_user
Group=kraft_user
WorkingDirectory=/opt/kraft_bot/kraft_system
Environment=PATH=/opt/kraft_bot/bin
ExecStart=/opt/kraft_bot/bin/python kraft_title_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kraft-title

[Install]
WantedBy=multi-user.target
```

#### 4. Stock Market Bot
```bash
sudo nano /etc/systemd/system/kraft-stock-market.service
```

```ini
[Unit]
Description=KRAFT Stock Market Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=kraft_user
Group=kraft_user
WorkingDirectory=/opt/kraft_bot/kraft_system
Environment=PATH=/opt/kraft_bot/bin
ExecStart=/opt/kraft_bot/bin/python kraft_stock_market_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kraft-stock-market

[Install]
WantedBy=multi-user.target
```

### サービス有効化・開始

```bash
# systemd設定リロード
sudo systemctl daemon-reload

# 各サービス有効化
sudo systemctl enable kraft-central-bank.service
sudo systemctl enable kraft-community.service
sudo systemctl enable kraft-title.service
sudo systemctl enable kraft-stock-market.service

# 各サービス開始
sudo systemctl start kraft-central-bank.service
sudo systemctl start kraft-community.service
sudo systemctl start kraft-title.service
sudo systemctl start kraft-stock-market.service

# 状態確認
sudo systemctl status kraft-central-bank.service
sudo systemctl status kraft-community.service
sudo systemctl status kraft-title.service
sudo systemctl status kraft-stock-market.service
```

## 📊 監視・ログ設定

### 1. ログローテーション設定

```bash
sudo nano /etc/logrotate.d/kraft-bots
```

```
/opt/kraft_bot/kraft_system/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 kraft_user kraft_user
    postrotate
        sudo systemctl reload kraft-central-bank kraft-community kraft-title kraft-stock-market
    endscript
}
```

### 2. 監視スクリプト作成

```bash
nano /opt/kraft_bot/kraft_system/monitoring/health_check.py
```

```python
#!/usr/bin/env python3
import subprocess
import requests
import json
from datetime import datetime

def check_service_status():
    services = [
        'kraft-central-bank.service',
        'kraft-community.service', 
        'kraft-title.service',
        'kraft-stock-market.service'
    ]
    
    status_report = {
        'timestamp': datetime.now().isoformat(),
        'services': {}
    }
    
    for service in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', service], 
                                  capture_output=True, text=True)
            status_report['services'][service] = {
                'status': result.stdout.strip(),
                'active': result.returncode == 0
            }
        except Exception as e:
            status_report['services'][service] = {
                'status': 'error',
                'error': str(e),
                'active': False
            }
    
    return status_report

def send_webhook_alert(webhook_url, message):
    """Discord Webhookでアラート送信"""
    payload = {
        'content': f'🚨 **KRAFT Bot Alert** 🚨\n{message}',
        'username': 'KRAFT Monitor'
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Webhook送信エラー: {e}")

if __name__ == "__main__":
    report = check_service_status()
    
    # 停止しているサービスがあればアラート
    inactive_services = [
        service for service, data in report['services'].items()
        if not data['active']
    ]
    
    if inactive_services:
        message = f"以下のサービスが停止しています:\n" + "\n".join(inactive_services)
        print(message)
        
        # Webhook URL (環境変数から取得)
        webhook_url = os.getenv('MONITORING_WEBHOOK_URL')
        if webhook_url:
            send_webhook_alert(webhook_url, message)
    
    # ログ出力
    with open('/opt/kraft_bot/kraft_system/logs/health_check.log', 'a') as f:
        f.write(json.dumps(report) + '\n')
```

### 3. 監視用cron設定

```bash
# kraft_userのcrontab編集
sudo -u kraft_user crontab -e
```

```bash
# 5分間隔でヘルスチェック
*/5 * * * * /opt/kraft_bot/bin/python /opt/kraft_bot/kraft_system/monitoring/health_check.py

# 日次でログクリーンアップ
0 2 * * * find /opt/kraft_bot/kraft_system/logs -name "*.log" -mtime +30 -delete

# 週次でFirebaseバックアップ
0 3 * * 0 /opt/kraft_bot/bin/python /opt/kraft_bot/kraft_system/scripts/firebase_backup.py
```

## 💾 バックアップ戦略

### 1. Firebase データバックアップ

```python
# scripts/firebase_backup.py
import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime
import os

def backup_firestore():
    """Firestore全データのバックアップ"""
    if not firebase_admin._apps:
        cred = credentials.Certificate("config/firebase_credentials_prod.json")
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    # バックアップディレクトリ作成
    backup_dir = f"/opt/kraft_bot/backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    collections = ['users', 'personal_quests', 'transactions', 'trades', 'portfolios', 'market_data']
    
    for collection_name in collections:
        collection_ref = db.collection(collection_name)
        docs = collection_ref.stream()
        
        collection_data = {}
        for doc in docs:
            collection_data[doc.id] = doc.to_dict()
        
        # JSON形式で保存
        with open(f"{backup_dir}/{collection_name}.json", 'w', encoding='utf-8') as f:
            json.dump(collection_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"バックアップ完了: {backup_dir}")
    return backup_dir

if __name__ == "__main__":
    backup_firestore()
```

### 2. アプリケーションコード バックアップ

```bash
# scripts/app_backup.sh
#!/bin/bash

BACKUP_DIR="/opt/kraft_bot/backups/app_$(date +%Y%m%d_%H%M%S)"
SOURCE_DIR="/opt/kraft_bot/kraft_system"

# アプリケーションディレクトリをバックアップ
mkdir -p "$BACKUP_DIR"
cp -r "$SOURCE_DIR" "$BACKUP_DIR/"

# 設定ファイルをバックアップ (秘密情報は除外)
cp "$SOURCE_DIR/.env" "$BACKUP_DIR/env_backup"
cp -r "$SOURCE_DIR/config" "$BACKUP_DIR/" 2>/dev/null || true

# 圧縮
tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname $BACKUP_DIR)" "$(basename $BACKUP_DIR)"
rm -rf "$BACKUP_DIR"

echo "アプリケーションバックアップ完了: $BACKUP_DIR.tar.gz"

# 古いバックアップを削除 (30日以上)
find /opt/kraft_bot/backups -name "app_*.tar.gz" -mtime +30 -delete
```

## 🔒 セキュリティ設定

### 1. ファイアウォール設定

```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 443/tcp  # HTTPS (監視用)

# firewalld (CentOS)
sudo firewall-cmd --permanent --set-default-zone=public
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. SSL証明書設定 (Nginx + Let's Encrypt)

```bash
# Certbot インストール
sudo apt install certbot python3-certbot-nginx

# SSL証明書取得
sudo certbot --nginx -d yourdomain.com

# 自動更新設定
sudo crontab -e
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Nginx設定 (監視ダッシュボード用)

```nginx
# /etc/nginx/sites-available/kraft-monitor
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location /health {
        alias /opt/kraft_bot/kraft_system/logs;
        auth_basic "KRAFT Monitor";
        auth_basic_user_file /etc/nginx/.htpasswd;
        autoindex on;
    }
    
    location / {
        return 404;
    }
}
```

## 🔄 更新・デプロイ手順

### 1. ゼロダウンタイム更新

```bash
# scripts/update_deploy.sh
#!/bin/bash

BACKUP_DIR="/opt/kraft_bot/backups/pre_update_$(date +%Y%m%d_%H%M%S)"
APP_DIR="/opt/kraft_bot/kraft_system"

echo "🔄 KRAFT System 更新開始..."

# 1. 事前バックアップ
echo "📦 事前バックアップ作成中..."
mkdir -p "$BACKUP_DIR"
cp -r "$APP_DIR" "$BACKUP_DIR/"

# 2. 新バージョン取得
echo "📥 新バージョン取得中..."
cd "$APP_DIR"
git fetch origin
git checkout main
git pull origin main

# 3. 依存関係更新
echo "📚 依存関係更新中..."
/opt/kraft_bot/bin/pip install -r requirements.txt

# 4. 段階的再起動
echo "🔄 サービス再起動中..."
services=("kraft-central-bank" "kraft-community" "kraft-title" "kraft-stock-market")

for service in "${services[@]}"; do
    echo "  - $service 再起動中..."
    sudo systemctl restart "$service.service"
    sleep 10
    
    # ヘルスチェック
    if sudo systemctl is-active --quiet "$service.service"; then
        echo "  ✅ $service 正常起動"
    else
        echo "  ❌ $service 起動失敗 - ロールバック中..."
        # ロールバック処理
        cp -r "$BACKUP_DIR/kraft_system"/* "$APP_DIR/"
        sudo systemctl restart "$service.service"
        exit 1
    fi
done

echo "✅ 更新完了"
```

### 2. ロールバック手順

```bash
# scripts/rollback.sh
#!/bin/bash

if [ -z "$1" ]; then
    echo "使用法: $0 <backup_directory>"
    exit 1
fi

BACKUP_DIR="$1"
APP_DIR="/opt/kraft_bot/kraft_system"

echo "🔄 ロールバック開始..."

# バックアップから復元
cp -r "$BACKUP_DIR/kraft_system"/* "$APP_DIR/"

# 全サービス再起動
sudo systemctl restart kraft-central-bank.service
sudo systemctl restart kraft-community.service  
sudo systemctl restart kraft-title.service
sudo systemctl restart kraft-stock-market.service

echo "✅ ロールバック完了"
```

## 📈 パフォーマンス最適化

### 1. システムリソース監視

```bash
# scripts/resource_monitor.py
import psutil
import json
from datetime import datetime

def get_system_stats():
    stats = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'free': psutil.disk_usage('/').free,
            'percent': psutil.disk_usage('/').percent
        }
    }
    
    # ログ記録
    with open('/opt/kraft_bot/kraft_system/logs/resource_monitor.log', 'a') as f:
        f.write(json.dumps(stats) + '\n')
    
    # アラート閾値チェック
    if stats['cpu_percent'] > 80:
        print(f"⚠️ CPU使用率高: {stats['cpu_percent']}%")
    
    if stats['memory']['percent'] > 80:
        print(f"⚠️ メモリ使用率高: {stats['memory']['percent']}%")
    
    return stats

if __name__ == "__main__":
    get_system_stats()
```

## 📞 トラブルシューティング

### よくある問題と解決方法

#### 1. Bot起動失敗
```bash
# ログ確認
sudo journalctl -u kraft-central-bank.service -f

# 一般的な原因:
# - 環境変数設定ミス
# - Firebase認証ファイルの権限
# - Python仮想環境のパス
```

#### 2. Discord API制限
```bash
# レート制限対策確認
grep "rate limit" /opt/kraft_bot/kraft_system/logs/*.log

# 解決方法:
# - asyncio.sleep() の追加
# - リクエスト頻度の調整
```

#### 3. Firebase接続エラー
```bash
# 認証ファイル確認
ls -la /opt/kraft_bot/kraft_system/config/firebase_credentials_prod.json

# ネットワーク接続確認
curl -I https://firestore.googleapis.com
```

---

**🚀 本番環境でのKRAFTシステム運用を開始してください！**
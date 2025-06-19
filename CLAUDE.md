# KRAFT Bot システム情報

## プロジェクト概要
KRAFT Discord Bot システム - 4つの連携するBotで構成される経済・コミュニティシステム

## 環境情報
- **ローカル開発環境**: /Users/kenseidojima/Desktop/KRAFT/New bot
- **GitHub リポジトリ**: https://github.com/Rucolow/kraft-bot-system
- **VPS**: ubuntu@160.16.76.218
- **Pythonバージョン**: 3.12
- **主要ライブラリ**: discord.py, firebase-admin, anthropic

## VPS接続方法
```bash
# VPSに接続
ssh ubuntu@160.16.76.218

# kraftbotユーザーに切り替え
sudo su - kraftbot

# プロジェクトディレクトリへ移動
cd kraft-bot-system
```

## Bot一覧と役割

### 1. Central Bank Bot (kraft_central_bank.py)
- **役割**: 経済システムの中核、通貨管理
- **主要機能**:
  - 残高確認 (/balance)
  - 送金 (/送金)
  - 統計情報 (/stats)
  - 残高調整 (管理者専用)

### 2. Community Bot (kraft_community_bot.py)
- **役割**: クエスト・レベルシステム管理
- **主要機能**:
  - デイリークエスト (/daily)
  - パーソナルクエスト (/quest)
  - レベルシステム
  - 経験値管理

### 3. Title Bot (kraft_title_bot.py)
- **役割**: 称号システム管理
- **主要機能**:
  - 称号一覧 (/title list)
  - 称号装備 (/title equip)
  - 称号作成 (管理者専用)
  - 自動称号付与

### 4. Stock Market Bot (kraft_stock_market_bot.py)
- **役割**: 投資・株式取引システム
- **主要機能**:
  - 株価確認 (/株価)
  - 株式購入 (/株式購入)
  - 株式売却 (/株式売却)
  - ポートフォリオ (/ポートフォリオ)
  - 投資ランキング (/投資ランキング)

## systemdサービス管理

```bash
# 全Botの状態確認
systemctl status kraft-*

# 個別Bot管理
sudo systemctl start kraft-central-bank
sudo systemctl stop kraft-community
sudo systemctl restart kraft-title
sudo systemctl restart kraft-stock-market

# ログ確認
journalctl -u kraft-central-bank -f
journalctl -u kraft-community -n 50
journalctl -u kraft-title --since "1 hour ago"
journalctl -u kraft-stock-market -n 100 --no-pager
```

## デプロイメント

### 自動デプロイ (推奨)
```bash
# Macから
git add .
git commit -m "Update: 機能追加/修正内容"
git push origin main
# → GitHub Actions経由で自動的にVPSに反映
```

### 手動デプロイ
```bash
# VPS上で
cd ~/kraft-bot-system
git pull https://github.com/Rucolow/kraft-bot-system.git main
sudo systemctl restart kraft-*
```

## よく使うコマンド

### 開発時
```bash
# 構文チェック
python -m py_compile kraft_*.py

# ローカルテスト実行
python kraft_central_bank.py

# 環境変数確認
cat .env
```

### VPS管理
```bash
# リソース確認
top -u kraftbot
df -h
free -m

# プロセス確認
ps aux | grep kraft

# ファイアウォール状態
sudo ufw status
```

## トラブルシューティング

### Bot起動失敗時
1. エラーログ確認: `journalctl -u kraft-[bot-name] -n 50`
2. 手動起動でエラー詳細確認: `python kraft_[bot-name].py`
3. 環境変数確認: `.env`ファイルの設定
4. Firebase認証: `config/firebase_credentials.json`の存在確認

### よくあるエラーと対処法
- **IndentationError**: インデントの不整合 → エディタで修正
- **ImportError**: ライブラリ不足 → `pip install -r requirements.txt`
- **Firebase認証エラー**: 認証ファイルのパス確認
- **Discord Token無効**: `.env`のトークン設定確認

## 開発時の注意点

1. **環境変数**: `.env`ファイルは絶対にコミットしない
2. **Firebase認証**: 本番用と開発用を分ける
3. **テスト**: 本番環境にデプロイ前にローカルでテスト
4. **ログ**: エラー時は必ずログを確認
5. **バックアップ**: 大きな変更前はバックアップを取る

## 改善作業を始める時のテンプレート

```
KRAFT Bot システムの改善作業を行います。

【現在の環境】
- プロジェクトパス: /Users/kenseidojima/Desktop/KRAFT/New bot
- 4つのBot全て正常稼働中

【今回やりたいこと】
- [具体的な改善内容]

【関連Bot】
- [どのBotの改善か]
```

## GitHub Secrets設定
- VPS_HOST: 160.16.76.218
- VPS_USER: ubuntu
- SSH_PRIVATE_KEY: ~/.ssh/id_ed25519の内容
- DISCORD_WEBHOOK: (オプション)

## 関連ドキュメント
- docs/operation_manual.md - 運用マニュアル
- docs/developer_guide.md - 開発者ガイド
- docs/AUTO_DEPLOYMENT_SETUP.md - 自動デプロイ設定
- docs/backup_restore.md - バックアップ・リストア手順
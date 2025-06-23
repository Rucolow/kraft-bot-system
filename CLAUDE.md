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
  - 残高確認 (/残高)
  - 送金 (/送金)
  - スロットゲーム (/スロット)
  - 残高調整 (/残高調整) - 管理者専用

### 2. Community Bot (kraft_community_bot.py)
- **役割**: クエスト・レベルシステム管理
- **主要機能**:
  - プロフィール確認 (/プロフィール)
  - 寄付システム (/寄付)
  - クエスト作成 (/クエスト作成)
  - マイクエスト確認 (/マイクエスト)
  - クエスト達成報告 (/クエスト達成)
  - クエスト削除 (/クエスト削除)

### 3. Title Bot (kraft_title_bot.py)
- **役割**: 称号システム管理・自動監視
- **主要機能**:
  - 自動称号判定・付与
  - Discordロール自動管理
  - 称号強制チェック (/称号強制チェック) - 管理者専用
  - レベル・アクティビティ・経済活動の監視

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
- **スラッシュコマンド0個同期**: コマンド定義の構造問題 → 動作しているbotの構造を参考に再構築

### 🚨 重要: スラッシュコマンドが/statusに置き換わる問題（完全解決）

**症状**: 正常に起動するが、時間が経つと自動的にスラッシュコマンドが/statusのみに置き換わる、または完全に消失する

#### 💥 真の原因: bot_monitor.sh（2025-06-23完全特定）

**根本原因**: crontabで5分間隔実行される監視スクリプト
```bash
# 問題のcron設定
*/5 * * * * /home/kraftbot/bot_monitor.sh
```

**発生メカニズム**:
1. `bot_monitor.sh`が5分ごとに全Botサービスをチェック
2. 何らかの理由でサービス再起動を実行
3. Bot再起動時にコマンドツリーが一時的にクリア
4. 再同期プロセスでDiscord側との競合が発生
5. コマンドが空になったまま固着

**時系列証拠**:
- 12:21まで正常動作
- **12:26に問題発生** ← 5分間隔と完全一致
- 12:32以降コマンド完全消失

#### ✅ 完全解決方法

**1. 問題のcron削除**:
```bash
# cronを完全削除
crontab -r

# 確認
crontab -l  # "no crontab" と表示されるべき
```

**2. 効果確認**:
```bash
# 監視ログでコマンド復帰を確認
tail -f central_bank_monitor.log
# → cron削除後、コマンドが正常に復帰
```

#### 🛡️ 予防策と代替監視

**安全な監視スクリプト例**:
```bash
#!/bin/bash
# アラート専用（再起動しない）
for service in kraft-central-bank kraft-community kraft-title kraft-stock-market; do
    if ! systemctl is-active --quiet "$service"; then
        echo "[ALERT] $service is down" | logger
        # 再起動はせず、通知のみ
    fi
done
```

#### 🔍 調査・診断コマンド

**問題発生時の調査手順**:
```bash
# 1. cron確認（最優先）
crontab -l
sudo crontab -l

# 2. プロセス重複チェック
ps aux | grep kraft

# 3. Discord Token重複チェック
grep -r "DISCORD_TOKEN_CENTRAL_BANK_BOT" .

# 4. 外部プロセス確認
pm2 list
supervisorctl status 2>/dev/null
```

**修正実装**: kraft_central_bank.py（2025-06-23修正）
- コマンド定義をon_ready外に移動
- 自動監視タスクでstatusコマンド検出時の自動修正
- 詳細ログ記録（central_bank_*.log）

**重要**: この問題は複数の要因が重なって発生したため、段階的な調査が必要でした：
1. 初期仮説: プロセス重複 → 部分的に正しい
2. 中間仮説: 共有設定ファイル → 無関係
3. **最終解決**: crontab監視スクリプト → 真犯人

### Bot修正のベストプラクティス

#### 深刻な問題（スラッシュコマンド登録失敗等）の場合
1. **症状の確認**
   - ログで「0個のコマンドが同期されました」と表示
   - Discord側でスラッシュコマンドが表示されない
   - 手動実行では on_ready イベントは実行されている

2. **確実な修正方法**
   ```bash
   # 1. 動作しているbotファイルをベースとして使用
   cp kraft_stock_market_bot.py kraft_central_bank_new.py
   
   # 2. 必要な部分だけを置き換えて再構築
   # - コマンド定義部分
   # - bot設定（prefix、intents等）
   # - 環境変数名
   
   # 3. 元ファイルをバックアップしてから置き換え
   mv kraft_central_bank.py kraft_central_bank_backup.py
   mv kraft_central_bank_new.py kraft_central_bank.py
   ```

3. **重要な構造ポイント**
   - 全てのコマンドは `on_ready` イベント内で定義
   - インデントは4スペースで統一
   - コマンド同期 `await bot.tree.sync()` は `on_ready` の最後に配置
   - エラーハンドリングを含める

4. **修正後の確認**
   - ローカルで構文チェック: `python -m py_compile *.py`
   - 手動実行で「✅ X個のコマンドが同期されました」を確認
   - Git commit & push
   - VPS再起動後にDiscord側で動作確認

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
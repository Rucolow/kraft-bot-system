# GitHub Secrets設定ガイド

自動デプロイメントを有効にするため、以下のGitHub Secretsを設定する必要があります。

## 必要なSecrets

### 1. VPS_HOST
- **値**: `160.16.76.218`
- **説明**: VPSのIPアドレス

### 2. VPS_USER
- **値**: `ubuntu`
- **説明**: SSH接続時の初期ユーザー名

### 3. SSH_PRIVATE_KEY
- **値**: SSH秘密鍵の内容
- **取得方法**:
  ```bash
  # Macのターミナルで実行
  cat ~/.ssh/id_rsa
  ```
  または
  ```bash
  cat ~/.ssh/id_ed25519
  ```
- **注意**: -----BEGIN から -----END まで全て含めてコピー

### 4. DISCORD_WEBHOOK (オプション)
- **値**: Discord WebhookのURL
- **作成方法**:
  1. Discordサーバーの設定 → 連携サービス → ウェブフック
  2. 新しいウェブフックを作成
  3. URLをコピー

## 設定手順

1. GitHubリポジトリページを開く
2. Settings → Secrets and variables → Actions
3. "New repository secret"をクリック
4. 各Secretを追加:
   - Name: 上記のSecret名
   - Value: 対応する値
5. "Add secret"をクリック

## VPS側の準備

VPSで以下のコマンドを実行して、必要な設定を確認・準備します：

```bash
# kraftbotユーザーとして実行
ssh ubuntu@160.16.76.218
sudo su - kraftbot
cd kraft-bot-system

# 1. スクリプトに実行権限を付与
chmod +x scripts/check_vps_setup.sh
chmod +x scripts/deploy.sh
chmod +x scripts/rollback.sh

# 2. 現在の環境を確認
./scripts/check_vps_setup.sh

# 3. Git設定を確認
git remote -v
git branch

# 4. 必要に応じてリモートを設定
# git remote set-url origin https://github.com/[your-username]/[your-repo].git
```

## 動作確認

1. すべてのSecretsを設定後、GitHubで手動デプロイをテスト:
   - Actions → Deploy to VPS → Run workflow

2. VPSでログを確認:
   ```bash
   tail -f ~/kraft-bot-system/deploy.log
   ```

## トラブルシューティング

### SSH接続エラー
- SSH鍵が正しくコピーされているか確認
- VPSの`~/.ssh/authorized_keys`に公開鍵が登録されているか確認

### 権限エラー
- kraftbotユーザーがsudoを使えるか確認
- systemctl restart権限があるか確認

### Git pullエラー
- VPSのGitリポジトリが正しいリモートを参照しているか確認
- HTTPSまたはSSH URLを使用しているか確認
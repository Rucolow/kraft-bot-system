# KRAFT分散型Botシステム

KRAFTコミュニティ向けの分散型Discord Botシステムです。4つの専門Botが連携して、経済活動・レベリング・称号獲得・投資機能を提供します。

## 🎯 システム概要

### 4つの専門Bot
- **🏦 KRAFT中央銀行Bot** - KR通貨の管理・取引・ギャンブル
- **👥 KRAFTコミュニティBot** - XP・レベル・クエスト・寄付機能  
- **🏅 KRAFT称号Bot** - 18種類の称号獲得・自動判定・ロール付与
- **📈 KRAFT株式市場Bot** - 12社の日本企業ベース株式投資

### 主な機能
- **経済システム**: KR通貨での送金・寄付・投資・ギャンブル
- **成長システム**: メッセージでXP獲得・レベルアップ・KR報酬
- **クエストシステム**: 個人目標設定・達成でXP・KR獲得
- **称号システム**: 18種類の称号自動獲得・Discord ロール付与
- **投資システム**: リアルタイム株価変動・ポートフォリオ管理

## 🚀 セットアップ手順

### 1. 環境要件
- Python 3.9以上
- Discord Bot Token × 4個
- Firebase プロジェクト
- Claude API Key

### 2. インストール
```bash
# リポジトリクローン
git clone [repository-url]
cd kraft-distributed-bot

# 仮想環境作成・有効化
python -m venv kraft_env
source kraft_env/bin/activate  # Linux/Mac
# kraft_env\Scripts\activate  # Windows

# 依存パッケージインストール
pip install -r requirements.txt
```

### 3. 環境変数設定
`.env`ファイルを作成:
```env
# Discord Bot Tokens
DISCORD_TOKEN_CENTRAL_BANK_BOT=your_token_here
DISCORD_TOKEN_COMMUNITY_BOT=your_token_here
DISCORD_TOKEN_TITLE_BOT=your_token_here
DISCORD_TOKEN_STOCK_MARKET_BOT=your_token_here

# Firebase設定
FIREBASE_CREDENTIALS_PATH=config/firebase_credentials.json

# Claude API
CLAUDE_API_KEY=your_claude_api_key

# 管理者設定
ADMIN_USER_IDS=user_id_1,user_id_2

# チャンネルID設定
LEVELUP_CHANNEL_ID=channel_id
TITLE_NOTIFICATION_CHANNEL_ID=channel_id
INVESTMENT_NEWS_CHANNEL_ID=channel_id
DONATION_CHANNEL_ID=channel_id
```

### 4. Firebase設定
1. Firebase Console でプロジェクト作成
2. Firestore Database 有効化
3. サービスアカウント作成・秘密鍵ダウンロード
4. `config/firebase_credentials.json` に配置

### 5. Discord設定
各Botに必要な権限:
- Send Messages
- Use Slash Commands
- Manage Roles (Title Botのみ)
- Read Message History
- Embed Links

## 📖 各Botの機能詳細

### 🏦 中央銀行Bot
```
/残高          - KR残高確認
/送金 @ユーザー 金額  - KR送金
/スロット 金額     - ギャンブル (100-10,000KR)
/残高調整        - 管理者専用
```

### 👥 コミュニティBot  
```
/プロフィール @ユーザー - レベル・XP・残高・称号表示
/寄付 金額           - コミュニティに寄付してXP獲得
/クエスト作成 年 月 日   - 個人目標設定
/マイクエスト         - 作成したクエスト一覧
/クエスト達成         - 選択式でクエスト完了
/クエスト削除         - 選択式でクエスト削除
```

### 🏅 称号Bot
```
/称号強制チェック - 管理者専用 全ユーザー称号判定
```
**称号一覧 (18種類)**:
- **レベル系**: 新人冒険者(Lv5)→冒険者(Lv10)→熟練冒険者(Lv20)→探求者(Lv30)→達人(Lv50)→生きる伝説(Lv100)
- **アクティビティ系**: よく喋る人・エミネム・どこにでもいる人
- **クエスト系**: クエストマスター・どんまい・逆にすごい  
- **経済系**: 寄付マスター・聖人・投資マスター・ノーリターン・ギフトマスター・大盤振る舞い

### 📈 株式市場Bot
```
/株価            - 12銘柄の現在価格表示
/株式購入         - 選択式で株式購入
/株式売却         - 保有銘柄から選択して売却
/ポートフォリオ     - 投資状況をグラフ表示
/投資ランキング     - 収益率ランキング
```

**投資可能銘柄 (12社)**:
ハードバンク・トミタ・USJ銀行・ソミー・ドモコ・ナインイレブン・住不動産・四菱ケミカル・新目鉄・キリンジ・東京雷神・アステラサズ

## 🔧 システム仕様

### 経済設定
- **初期残高**: 1,000 KR
- **メッセージXP**: 5 XP/メッセージ (60秒クールダウン)
- **レベルアップ報酬**: レベル × 500 KR
- **寄付XP交換**: 1 KR = 0.1 XP
- **株式手数料**: 1%
- **取引制限**: 100-1,000,000 KR、日次50回まで

### バックグラウンド処理
- **株価更新**: 30分間隔 (幾何ブラウン運動)
- **投資ニュース**: 6時間間隔、30%確率で配信
- **称号チェック**: 5分間隔で自動判定
- **クエスト期限**: 1時間間隔でチェック

## 🏃‍♂️ Bot起動方法

各Botを個別に起動:
```bash
# 中央銀行Bot
python3 kraft_central_bank.py

# コミュニティBot  
python3 kraft_community_bot.py

# 称号Bot
python3 kraft_title_bot.py

# 株式市場Bot
python3 kraft_stock_market_bot.py
```

## 📊 データ構造

### Firestore コレクション
- `users` - ユーザー情報 (残高・レベル・XP・称号等)
- `personal_quests` - 個人クエストデータ
- `transactions` - KR取引履歴
- `trades` - 株式取引履歴  
- `portfolios` - 投資ポートフォリオ
- `market_data` - 株価データ・履歴

## 🔐 セキュリティ機能

- 管理者コマンドの権限チェック
- 取引上限・頻度制限
- 入力値検証
- 取引ログ記録
- レート制限対応

## 🐛 トラブルシューティング

### よくある問題

**Bot起動時にTokenエラー**
```
解決方法: .envファイルの環境変数名を確認
DISCORD_TOKEN_CENTRAL_BANK_BOT (正)
CENTRAL_BANK_TOKEN (誤)
```

**Firebaseエラー**
```
解決方法: firebase_credentials.jsonの配置確認
正しい場所: config/firebase_credentials.json
```

**コマンド同期されない**
```
解決方法: Bot再起動後、最大1時間待機
Discord側のキャッシュ更新が必要
```

**Select Menuエラー**
```
解決方法: @discord.ui.selectデコレータ使用を確認
別オブジェクト作成方式は非推奨
```

### ログ確認
各Botの起動ログで状況確認:
```
✅ コマンド同期成功時
❌ エラー時の詳細ログ
🔄 バックグラウンドタスク状況
```

## 🤝 貢献方法

1. Issue作成で機能要望・バグ報告
2. Fork→ブランチ作成→プルリクエスト  
3. コードレビュー→マージ

## 📜 ライセンス

MIT License - 詳細は LICENSE ファイルを参照

## 🙏 謝辞

- Discord.py コミュニティ
- Firebase チーム
- Anthropic Claude API
- KRAFTコミュニティメンバー

---

**🎮 KRAFTコミュニティでの経済活動をお楽しみください！**
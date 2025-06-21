#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import random

print("🏦 KRAFT中央銀行Bot - 完全版")
print("=" * 50)

# 環境変数読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN_CENTRAL_BANK_BOT")
ADMIN_USER_IDS = os.getenv("ADMIN_USER_IDS", "").split(",")

# Firebase初期化
if not firebase_admin._apps:
    cred = credentials.Certificate("config/firebase_credentials.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

print(f"Token: {'OK' if TOKEN else 'NG'}")
print(f"Admin IDs: {ADMIN_USER_IDS}")

# Intents設定
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

# Bot作成
bot = commands.Bot(command_prefix='!bank_', intents=intents)

# 起動時にコマンドツリーの状態を確認
@bot.event
async def setup_hook():
    print("🔍 既存のコマンドツリーを確認中...")
    commands_list = []
    for command in bot.tree.get_commands():
        commands_list.append(f"  - {command.name}")
    if commands_list:
        print(f"既存のコマンド: {len(commands_list)}個")
        for cmd in commands_list:
            print(cmd)
    else:
        print("既存のコマンドはありません")

# =====================================
# イベントハンドラー
# =====================================

@bot.event
async def on_ready():
    print(f"\n🏦 KRAFT中央銀行Bot起動: {bot.user}")
    print(f"接続サーバー: {[g.name for g in bot.guilds]}")
    
    # 既存のコマンドを完全にクリア
    print("\n🗑️ 既存コマンドをクリア...")
    bot.tree.clear_commands(guild=None)
    
    # 全ギルドからもコマンドをクリア
    for guild in bot.guilds:
        bot.tree.clear_commands(guild=guild)
        print(f"  - {guild.name} のコマンドをクリア")
    
    # グローバルコマンドの同期を強制
    print("\n🔄 グローバルコマンドを強制同期...")
    await bot.tree.sync()
    
    # bot_status.txtファイルを作成
    with open("bot_status.txt", "w") as f:
        f.write(f"起動時刻: {datetime.datetime.now()}\n")
        f.write(f"Bot名: {bot.user}\n")
        f.write(f"ギルド数: {len(bot.guilds)}\n")
    
    # =====================================
    # 残高確認コマンド
    # =====================================
    @bot.tree.command(name="残高", description="あなたのKR残高を確認します")
    async def balance_cmd(interaction: discord.Interaction):
        print(f"[残高] {interaction.user.name} が実行")
        await interaction.response.defer(ephemeral=True)
        
        user_id = str(interaction.user.id)
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            balance = user_doc.to_dict().get("balance", 0)
        else:
            # 新規ユーザー初期化
            user_data = {
                "user_id": user_id,
                "balance": 1000,
                "level": 1,
                "xp": 0,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            user_ref.set(user_data)
            balance = 1000
            print(f"新規ユーザー作成: {user_id}")
        
        embed = discord.Embed(
            title="💰 残高確認",
            description=f"あなたの現在の残高は **{balance:,} KR** です",
            color=discord.Color.green()
        )
        embed.set_footer(text="KRAFT中央銀行")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        print(f"残高確認成功: {balance} KR")

    # =====================================
    # 送金コマンド
    # =====================================
    @bot.tree.command(name="送金", description="他のユーザーにKRを送金します")
    async def transfer_cmd(interaction: discord.Interaction, recipient: discord.Member, 金額: int):
        print(f"[送金] {interaction.user.name} → {recipient.name}: {金額}KR")
        await interaction.response.defer()
        
        if recipient.id == interaction.user.id:
            await interaction.followup.send("自分自身への送金はできません。")
            return
        
        if 金額 <= 0:
            await interaction.followup.send("送金額は1KR以上である必要があります。")
            return
        
        if 金額 > 1000000:
            await interaction.followup.send("1回の送金上限は1,000,000KRです。")
            return
        
        sender_id = str(interaction.user.id)
        recipient_id = str(recipient.id)
        
        # 送金者の残高確認
        sender_ref = db.collection("users").document(sender_id)
        sender_doc = sender_ref.get()
        
        if not sender_doc.exists:
            await interaction.followup.send("残高が不足しています。")
            return
        
        sender_balance = sender_doc.to_dict().get("balance", 0)
        if sender_balance < 金額:
            await interaction.followup.send(f"残高が不足しています。現在の残高: {sender_balance:,} KR")
            return
        
        # 送金処理（トランザクション）
        batch = db.batch()
        
        # 送金者の残高を減額
        batch.update(sender_ref, {"balance": sender_balance - 金額})
        
        # 受取人の残高を増額
        recipient_ref = db.collection("users").document(recipient_id)
        recipient_doc = recipient_ref.get()
        
        if recipient_doc.exists:
            recipient_balance = recipient_doc.to_dict().get("balance", 0)
            batch.update(recipient_ref, {"balance": recipient_balance + 金額})
        else:
            # 新規ユーザーの場合
            batch.set(recipient_ref, {
                "user_id": recipient_id,
                "balance": 1000 + 金額,
                "level": 1,
                "xp": 0,
                "created_at": firestore.SERVER_TIMESTAMP
            })
        
        # 取引ログ
        transaction_data = {
            "type": "transfer",
            "from_user": sender_id,
            "to_user": recipient_id,
            "amount": 金額,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        batch.set(db.collection("transactions").document(), transaction_data)
        
        # バッチ実行
        batch.commit()
        
        # 送金者への確認メッセージ
        embed = discord.Embed(
            title="💸 送金完了",
            description=f"{recipient.mention} に **{金額:,} KR** を送金しました",
            color=discord.Color.green()
        )
        embed.add_field(name="送金後残高", value=f"{sender_balance - 金額:,} KR")
        embed.set_footer(text="KRAFT中央銀行")
        
        await interaction.followup.send(embed=embed)
        
        # 受取人への通知
        notification_embed = discord.Embed(
            title="💰 送金を受け取りました！",
            description=f"{interaction.user.mention} から **{金額:,} KR** を受け取りました",
            color=discord.Color.gold()
        )
        notification_embed.set_footer(text="KRAFT中央銀行")
        
        await interaction.followup.send(f"{recipient.mention}", embed=notification_embed)
        
        print(f"送金成功: {金額} KR")

    # =====================================
    # スロットコマンド
    # =====================================
    @bot.tree.command(name="スロット", description="スロットマシンで遊びます（100-10,000 KR）")
    async def slot_cmd(interaction: discord.Interaction, 金額: int):
        print(f"[スロット] {interaction.user.name}: {金額}KR")
        await interaction.response.defer()
        
        if 金額 < 100 or 金額 > 10000:
            await interaction.followup.send("ベット額は100〜10,000 KRの間で指定してください。")
            return
            
        user_id = str(interaction.user.id)
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            await interaction.followup.send("残高が不足しています。")
            return
        
        balance = user_doc.to_dict().get("balance", 0)
        if balance < 金額:
            await interaction.followup.send(f"残高が不足しています。現在の残高: {balance:,} KR")
            return
        
        # スロット結果
        symbols = ["💎", "⭐", "🍒", "🍋", "🍊", "🍇"]
        result = random.choices(symbols, k=3)
        
        # 配当計算
        multiplier = 0
        if result.count("💎") == 3:
            multiplier = 10  # 💎💎💎: 10倍
        elif result.count("⭐") == 3:
            multiplier = 5   # ⭐⭐⭐: 5倍
        elif len(set(result)) == 1:
            multiplier = 3   # その他三つ揃い: 3倍
        elif len(set(result)) == 2:
            multiplier = 1.5 # 二つ揃い: 1.5倍
        
        # 控除率5%適用
        house_edge = 0.95
        win_amount = int(金額 * multiplier * house_edge) if multiplier > 0 else 0
        
        # 残高更新
        new_balance = balance - 金額 + win_amount
        user_ref.update({"balance": new_balance})
        
        # 結果表示
        embed = discord.Embed(
            title="🎰 スロットマシン",
            description=f"結果: {' '.join(result)}",
            color=discord.Color.gold() if win_amount > 0 else discord.Color.red()
        )
        
        if win_amount > 0:
            embed.add_field(
                name="結果", 
                value=f"🎉 勝利！\n獲得: **{win_amount:,} KR**\n残高: **{new_balance:,} KR**"
            )
        else:
            embed.add_field(
                name="結果", 
                value=f"😢 残念...\n残高: **{new_balance:,} KR**"
            )
        
        embed.set_footer(text="KRAFT中央銀行")
        await interaction.followup.send(embed=embed)
        print(f"スロット結果: {win_amount} KR獲得")

    # =====================================
    # 残高調整コマンド（管理者専用）
    # =====================================
    @bot.tree.command(name="残高調整", description="管理者専用：ユーザーの残高を調整します")
    async def admin_adjust_cmd(interaction: discord.Interaction, user: discord.Member, 金額: int, 理由: str):
        print(f"[残高調整] {interaction.user.name} → {user.name}: {金額}KR ({理由})")
        try:
            await interaction.response.defer(ephemeral=True)
            
            # 管理者確認
            if str(interaction.user.id) not in ADMIN_USER_IDS:
                await interaction.followup.send("このコマンドは管理者のみ使用できます。", ephemeral=True)
                return
            
            user_id = str(user.id)
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                current_balance = user_doc.to_dict().get("balance", 0)
                new_balance = current_balance + 金額
                user_ref.update({"balance": new_balance})
            else:
                # 新規ユーザーの場合
                new_balance = 1000 + 金額
                user_ref.set({
                    "user_id": user_id,
                    "balance": new_balance,
                    "level": 1,
                    "xp": 0,
                    "created_at": firestore.SERVER_TIMESTAMP
                })
            
            embed = discord.Embed(
                title="💰 残高調整完了",
                description=f"{user.mention} の残高を調整しました",
                color=discord.Color.blue()
            )
            embed.add_field(name="調整額", value=f"{金額:,} KR")
            embed.add_field(name="新残高", value=f"{new_balance:,} KR")
            embed.add_field(name="理由", value=理由)
            embed.set_footer(text="KRAFT中央銀行")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            print(f"残高調整完了: {new_balance} KR")
            
        except Exception as e:
            print(f"残高調整エラー: {e}")
            await interaction.followup.send("残高調整中にエラーが発生しました。", ephemeral=True)
    
    # =====================================
    # コマンド同期
    # =====================================
    print("\n🔄 コマンドを同期中...")
    try:
        # グローバルコマンドの再同期
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)}個のコマンドが同期されました！")
        for cmd in synced:
            print(f"  - /{cmd.name}: {cmd.description}")
        
        # bot_status.txtに同期情報を追記
        with open("bot_status.txt", "a") as f:
            f.write(f"同期コマンド数: {len(synced)}\n")
            for cmd in synced:
                f.write(f"  - /{cmd.name}\n")
        
        print("\n🎯 利用可能なコマンド:")
        print("  /残高 - 残高確認")
        print("  /送金 - KR送金")
        print("  /スロット - スロットマシン")
        print("  /残高調整 - 管理者専用")
        
        # 警告: statusコマンドが存在する場合
        if any(cmd.name == "status" for cmd in synced):
            print("\n⚠️ 警告: 'status'コマンドが検出されました！")
            print("これは予期しないコマンドです。")
    except Exception as e:
        print(f"❌ コマンド同期失敗: {e}")
        import traceback
        traceback.print_exc()

# エラーハンドリング
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ エラー: {event}")
    import traceback
    traceback.print_exc()

print("\n🚀 KRAFT中央銀行Bot起動中...")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ TOKENが設定されていません")
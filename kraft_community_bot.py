#!/usr/bin/env python3

import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import random
import asyncio

print("👥 KRAFTコミュニティBot - 開発版")
print("=" * 50)

# 環境変数読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN_COMMUNITY_BOT")
ADMIN_USER_IDS = os.getenv("ADMIN_USER_IDS", "").split(",")

# Firebase初期化（中央銀行Botと共有）
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
intents.message_content = True  # メッセージ監視のため

# Bot作成
bot = commands.Bot(command_prefix='!community_', intents=intents)

# XPシステム設定
XP_PER_MESSAGE = 5
XP_COOLDOWN = 60  # 60秒間隔
LEVEL_UP_BASE = 100
LEVEL_UP_MULTIPLIER = 1.5

# 通知チャンネルID（設定から取得予定）
LEVELUP_CHANNEL_ID = None
DONATION_CHANNEL_ID = None

# XPシステムヘルパー関数
def calculate_xp_for_level(level):
    """指定レベルに到達するのに必要な総XP"""
    if level <= 1:
        return 0
    return int(LEVEL_UP_BASE * (LEVEL_UP_MULTIPLIER ** (level - 2)))

def calculate_level_and_xp(total_xp):
    """総XPからレベルと現在XPを計算"""
    level = 1
    while calculate_xp_for_level(level + 1) <= total_xp:
        level += 1
    
    current_level_xp = calculate_xp_for_level(level)
    current_xp = total_xp - current_level_xp
    
    return level, current_xp

# =====================================
# プロフィール確認コマンド
# =====================================
@bot.tree.command(name="プロフィール", description="あなたのプロフィール情報を確認します")
async def profile_cmd(interaction: discord.Interaction, ユーザー: discord.Member = None):
    print(f"[プロフィール] {interaction.user.name} が実行")
    await interaction.response.defer()
    
    target_user = ユーザー if ユーザー else interaction.user
    user_id = str(target_user.id)
    
    # ユーザー情報取得
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        # 新規ユーザー初期化
        user_data = {
            "user_id": user_id,
            "balance": 1000,
            "level": 1,
            "xp": 0,
            "total_xp": 0,
            "messages_count": 0,
            "donations_made": 0,
            "donations_received": 0,
            "quests_completed": 0,
            "last_message_xp": None,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        user_ref.set(user_data)
        data = user_data
        print(f"新規ユーザー作成: {user_id}")
    else:
        data = user_doc.to_dict()
    
    # レベルアップに必要なXP計算
    current_level = data.get("level", 1)
    current_xp = data.get("xp", 0)
    next_level_xp = calculate_xp_for_level(current_level + 1)
    current_level_xp = calculate_xp_for_level(current_level)
    xp_needed = next_level_xp - data.get("total_xp", 0)
    
    embed = discord.Embed(
        title=f"👤 {target_user.display_name} のプロフィール",
        color=discord.Color.blue()
    )
    
    # 称号表示
    titles = data.get("titles", [])
    if titles:
        # 最新の称号を優先表示（最大3個）
        display_titles = titles[-3:] if len(titles) > 3 else titles
        titles_text = " | ".join([f"**{title}**" for title in display_titles])
        if len(titles) > 3:
            titles_text += f" 他{len(titles) - 3}個"
        embed.add_field(
            name="🏅 称号",
            value=titles_text,
            inline=False
        )
    
    embed.add_field(
        name="💰 残高", 
        value=f"{data.get('balance', 0):,} KR", 
        inline=True
    )
    embed.add_field(
        name="⭐ レベル", 
        value=f"Lv.{current_level}", 
        inline=True
    )
    embed.add_field(
        name="✨ 経験値", 
        value=f"{current_xp}/{next_level_xp - current_level_xp} XP", 
        inline=True
    )
    embed.add_field(
        name="📈 総経験値", 
        value=f"{data.get('total_xp', 0):,} XP", 
        inline=True
    )
    embed.add_field(
        name="💬 メッセージ数", 
        value=f"{data.get('messages_count', 0):,} 回", 
        inline=True
    )
    embed.add_field(
        name="🎯 クエスト完了", 
        value=f"{data.get('quests_completed', 0)} 個", 
        inline=True
    )
    embed.add_field(
        name="💝 寄付実績", 
        value=f"送付: {data.get('donations_made', 0)} 回\n受取: {data.get('donations_received', 0)} 回", 
        inline=False
    )
    
    # レベルアップまでの進捗バー
    progress = current_xp / (next_level_xp - current_level_xp)
    progress_bar = "▓" * int(progress * 10) + "░" * (10 - int(progress * 10))
    embed.add_field(
        name="📊 次のレベルまで", 
        value=f"{progress_bar} ({xp_needed} XP)", 
        inline=False
    )
    
    embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else None)
    embed.set_footer(text="KRAFTコミュニティ")
    
    await interaction.followup.send(embed=embed)
    print(f"プロフィール表示成功: Lv.{current_level}")

# =====================================
# 寄付コマンド
# =====================================
@bot.tree.command(name="寄付", description="コミュニティに寄付してXPを獲得します")
async def donate_cmd(interaction: discord.Interaction, 金額: int):
    print(f"[寄付] {interaction.user.name}: {金額}KR")
    await interaction.response.defer()
    
    if 金額 < 100:
        await interaction.followup.send("最小寄付額は100KRです。")
        return
    
    if 金額 > 100000:
        await interaction.followup.send("1回の寄付上限は100,000KRです。")
        return
    
    user_id = str(interaction.user.id)
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        await interaction.followup.send("残高が不足しています。")
        return
    
    user_data = user_doc.to_dict()
    balance = user_data.get("balance", 0)
    
    if balance < 金額:
        await interaction.followup.send(f"残高が不足しています。現在の残高: {balance:,} KR")
        return
    
    # 寄付額に応じたXP計算（1KR = 0.1XP）
    xp_reward = int(金額 * 0.1)
    
    # ユーザー情報更新
    new_balance = balance - 金額
    current_level = user_data.get("level", 1)
    current_xp = user_data.get("xp", 0)
    current_total_xp = user_data.get("total_xp", 0)
    
    new_total_xp = current_total_xp + xp_reward
    new_level, new_xp = calculate_level_and_xp(new_total_xp)
    
    level_up = new_level > current_level
    
    # データベース更新
    update_data = {
        "balance": new_balance,
        "level": new_level,
        "xp": new_xp,
        "total_xp": new_total_xp,
        "donations_made": user_data.get("donations_made", 0) + 1
    }
    user_ref.update(update_data)
    
    # コミュニティ基金に追加
    community_ref = db.collection("community").document("fund")
    community_doc = community_ref.get()
    
    if community_doc.exists:
        current_fund = community_doc.to_dict().get("total", 0)
        community_ref.update({"total": current_fund + 金額})
    else:
        community_ref.set({"total": 金額, "created_at": firestore.SERVER_TIMESTAMP})
    
    # 寄付ログ
    donation_data = {
        "user_id": user_id,
        "amount": 金額,
        "xp_reward": xp_reward,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("donations").add(donation_data)
    
    embed = discord.Embed(
        title="💝 寄付完了",
        description=f"**{金額:,} KR** をコミュニティに寄付しました！",
        color=discord.Color.green()
    )
    embed.add_field(name="XP獲得", value=f"+{xp_reward} XP", inline=True)
    embed.add_field(name="残高", value=f"{new_balance:,} KR", inline=True)
    
    if level_up:
        embed.add_field(
            name="🎉 レベルアップ！", 
            value=f"Lv.{current_level} → Lv.{new_level}", 
            inline=False
        )
    
    embed.set_footer(text="KRAFTコミュニティ")
    
    await interaction.followup.send(embed=embed)
    print(f"寄付成功: {金額} KR, {xp_reward} XP獲得")

# =====================================
# 個人クエスト作成コマンド
# =====================================
@bot.tree.command(name="クエスト作成", description="個人の目標クエストを作成します")
async def quest_create_cmd(interaction: discord.Interaction, 目標内容: str, 年: int, 月: int, 日: int):
    print(f"[クエスト作成] {interaction.user.name}: {目標内容}")
    await interaction.response.defer(ephemeral=True)
    
    if len(目標内容) > 100:
        await interaction.followup.send("目標内容は100文字以内で入力してください。", ephemeral=True)
        return
    
    # 日付の妥当性チェック
    current_year = datetime.datetime.now().year
    if 年 < current_year or 年 > current_year + 2:
        await interaction.followup.send(f"年は{current_year}〜{current_year + 2}の範囲で設定してください。", ephemeral=True)
        return
    
    if 月 < 1 or 月 > 12:
        await interaction.followup.send("月は1〜12の範囲で設定してください。", ephemeral=True)
        return
    
    if 日 < 1 or 日 > 31:
        await interaction.followup.send("日は1〜31の範囲で設定してください。", ephemeral=True)
        return
    
    try:
        deadline = datetime.datetime(年, 月, 日, 23, 59, 59)
    except ValueError:
        await interaction.followup.send("無効な日付です。日付を正しく入力してください。", ephemeral=True)
        return
    
    # 過去の日付チェック
    now = datetime.datetime.now()
    if deadline <= now:
        await interaction.followup.send("期限は現在より未来の日付を設定してください。", ephemeral=True)
        return
    
    # 期間計算
    time_diff = deadline - now
    duration_days = time_diff.days + 1
    
    if duration_days > 365:
        await interaction.followup.send("期限は最大365日後まで設定できます。", ephemeral=True)
        return
    
    user_id = str(interaction.user.id)
    
    # 現在のアクティブクエスト数チェック
    active_quests = db.collection("personal_quests").where("user_id", "==", user_id).where("status", "==", "active").stream()
    active_count = len(list(active_quests))
    
    if active_count >= 10:
        await interaction.followup.send("アクティブなクエストが上限（10個）に達しています。", ephemeral=True)
        return
    
    # 期間に応じたXP計算（1日=10XP、最大3650XP）
    base_xp = min(duration_days * 10, 3650)
    
    # クエストデータ作成
    quest_data = {
        "user_id": user_id,
        "goal": 目標内容,
        "created_at": firestore.SERVER_TIMESTAMP,
        "deadline": deadline,
        "duration_days": duration_days,
        "reward_xp": base_xp,
        "status": "active"
    }
    
    # クエスト登録
    quest_ref = db.collection("personal_quests").add(quest_data)
    quest_id = quest_ref[1].id
    
    embed = discord.Embed(
        title="🎯 個人クエスト作成完了",
        description=f"新しい目標を設定しました！",
        color=discord.Color.green()
    )
    embed.add_field(name="目標", value=目標内容, inline=False)
    embed.add_field(name="期限", value=f"{年}/{月}/{日} まで ({duration_days}日間)", inline=False)
    embed.add_field(name="報酬XP", value=f"{base_xp} XP", inline=True)
    embed.add_field(name="クエストID", value=quest_id[:8], inline=True)
    embed.set_footer(text="KRAFTコミュニティ")
    
    await interaction.followup.send(embed=embed, ephemeral=True)
    print(f"個人クエスト作成: {quest_id}")

# =====================================
# 個人クエスト一覧コマンド
# =====================================
@bot.tree.command(name="マイクエスト", description="あなたの個人クエスト一覧を表示します")
async def my_quest_list_cmd(interaction: discord.Interaction):
    print(f"[マイクエスト] {interaction.user.name} が実行")
    await interaction.response.defer(ephemeral=True)
    
    user_id = str(interaction.user.id)
    
    # ユーザーのアクティブクエスト取得
    quests = db.collection("personal_quests").where("user_id", "==", user_id).where("status", "==", "active").stream()
    
    embed = discord.Embed(
        title="🎯 あなたの個人クエスト",
        color=discord.Color.blue()
    )
    
    quest_count = 0
    total_reward = 0
    
    for quest in quests:
        quest_data = quest.to_dict()
        quest_id = quest.id
        
        deadline = quest_data.get("deadline")
        if isinstance(deadline, str):
            deadline = datetime.datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        elif hasattr(deadline, 'to_datetime'):
            deadline = deadline.to_datetime()
        
        time_left = deadline.replace(tzinfo=None) - datetime.datetime.utcnow()
        days_left = max(0, time_left.days)
        hours_left = max(0, time_left.seconds // 3600) if days_left == 0 else 0
        
        reward_xp = quest_data.get("reward_xp", 0)
        total_reward += reward_xp
        
        time_display = f"{days_left}日" if days_left > 0 else f"{hours_left}時間"
        if days_left == 0 and hours_left == 0:
            time_display = "⚠️ まもなく期限切れ"
        
        embed.add_field(
            name=f"🎯 {quest_data.get('goal', '目標不明')[:30]}",
            value=f"⏰ 残り: {time_display}\n"
                  f"✨ 報酬: {reward_xp} XP\n"
                  f"📅 期間: {quest_data.get('duration_days', 0)}日\n"
                  f"ID: `{quest_id[:8]}`",
            inline=True
        )
        quest_count += 1
    
    if quest_count == 0:
        embed.description = "現在アクティブなクエストはありません\n`/クエスト作成` で新しい目標を設定しましょう！"
    else:
        embed.add_field(
            name="📊 概要", 
            value=f"アクティブクエスト: {quest_count}/10\n合計報酬XP: {total_reward} XP", 
            inline=False
        )
    
    embed.set_footer(text="KRAFTコミュニティ")
    
    await interaction.followup.send(embed=embed, ephemeral=True)
    print(f"マイクエスト表示: {quest_count}件")

# =====================================
# クエスト達成コマンド（選択式）
# =====================================
@bot.tree.command(name="クエスト達成", description="個人クエストの達成を報告します")
async def quest_complete_cmd(interaction: discord.Interaction):
    print(f"[クエスト達成] {interaction.user.name} が実行")
    await interaction.response.defer(ephemeral=True)
    
    user_id = str(interaction.user.id)
    
    # ユーザーのアクティブクエスト取得
    quests = list(db.collection("personal_quests").where("user_id", "==", user_id).where("status", "==", "active").stream())
    
    if not quests:
        await interaction.followup.send("達成できるアクティブなクエストがありません。", ephemeral=True)
        return
    
    # セレクトメニュー作成
    options = []
    for quest in quests[:25]:  # Discord の制限で最大25個
        quest_data = quest.to_dict()
        deadline = quest_data.get("deadline")
        
        if isinstance(deadline, str):
            deadline = datetime.datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        elif hasattr(deadline, 'to_datetime'):
            deadline = deadline.to_datetime()
        
        time_left = deadline.replace(tzinfo=None) - datetime.datetime.utcnow()
        days_left = max(0, time_left.days)
        
        options.append(discord.SelectOption(
            label=quest_data.get("goal", "目標不明")[:100],
            value=quest.id,
            description=f"報酬: {quest_data.get('reward_xp', 0)} XP | 残り: {days_left}日"
        ))
    
    select = discord.ui.Select(
        placeholder="達成したクエストを選択してください",
        options=options
    )
    
    async def select_callback(select_interaction):
        quest_id = select.values[0]
        
        # クエスト達成処理
        quest_ref = db.collection("personal_quests").document(quest_id)
        quest_doc = quest_ref.get()
        
        if not quest_doc.exists:
            await select_interaction.response.send_message("クエストが見つかりません", ephemeral=True)
            return
        
        quest_data = quest_doc.to_dict()
        
        if quest_data.get("status") != "active":
            await select_interaction.response.send_message("このクエストは既に完了または期限切れです", ephemeral=True)
            return
        
        # クエスト完了処理
        reward_xp = quest_data.get("reward_xp", 0)
        quest_ref.update({
            "status": "completed",
            "completed_at": firestore.SERVER_TIMESTAMP
        })
        
        # ユーザーのXP付与
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        level_up = False
        kr_reward = 0
        current_level = 1
        new_level = 1
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            current_level = user_data.get("level", 1)
            current_total_xp = user_data.get("total_xp", 0)
            
            new_total_xp = current_total_xp + reward_xp
            new_level, new_xp = calculate_level_and_xp(new_total_xp)
            
            level_up = new_level > current_level
            
            # クエスト完了数も更新
            quests_completed = user_data.get("quests_completed", 0) + 1
            
            user_ref.update({
                "level": new_level,
                "xp": new_xp,
                "total_xp": new_total_xp,
                "quests_completed": quests_completed
            })
            
            # レベルアップ報酬
            if level_up:
                kr_reward = new_level * 500
                current_balance = user_data.get("balance", 1000)
                user_ref.update({"balance": current_balance + kr_reward})
        
        embed = discord.Embed(
            title="🎉 クエスト達成！",
            description=f"「{quest_data.get('goal', '目標不明')}」を達成しました！",
            color=discord.Color.gold()
        )
        embed.add_field(name="獲得XP", value=f"+{reward_xp} XP", inline=True)
        
        if level_up:
            embed.add_field(name="🎉 レベルアップ！", value=f"Lv.{current_level} → Lv.{new_level}\n報酬: {kr_reward} KR", inline=False)
        
        embed.set_footer(text="KRAFTコミュニティ")
        
        await select_interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"クエスト達成: {quest_id}, XP: {reward_xp}")
    
    select.callback = select_callback
    
    view = discord.ui.View(timeout=120)
    view.add_item(select)
    
    await interaction.followup.send("達成したクエストを選択してください:", view=view, ephemeral=True)

# =====================================
# クエスト削除コマンド
# =====================================
@bot.tree.command(name="クエスト削除", description="個人クエストを削除します")
async def quest_delete_cmd(interaction: discord.Interaction):
    print(f"[クエスト削除] {interaction.user.name} が実行")
    await interaction.response.defer(ephemeral=True)
    
    user_id = str(interaction.user.id)
    
    # ユーザーのアクティブクエスト取得
    quests = list(db.collection("personal_quests").where("user_id", "==", user_id).where("status", "==", "active").stream())
    
    if not quests:
        await interaction.followup.send("削除できるアクティブなクエストがありません。", ephemeral=True)
        return
    
    # セレクトメニュー作成
    options = []
    for quest in quests[:25]:  # Discord の制限で最大25個
        quest_data = quest.to_dict()
        deadline = quest_data.get("deadline")
        
        if isinstance(deadline, str):
            deadline = datetime.datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        elif hasattr(deadline, 'to_datetime'):
            deadline = deadline.to_datetime()
        
        time_left = deadline.replace(tzinfo=None) - datetime.datetime.utcnow()
        days_left = max(0, time_left.days)
        
        options.append(discord.SelectOption(
            label=quest_data.get("goal", "目標不明")[:100],
            value=quest.id,
            description=f"残り: {days_left}日 | クエストを削除します",
            emoji="🗑️"
        ))
    
    select = discord.ui.Select(
        placeholder="削除したいクエストを選択してください",
        options=options
    )
    
    async def select_callback(select_interaction):
        quest_id = select.values[0]
        
        # クエスト削除処理
        quest_ref = db.collection("personal_quests").document(quest_id)
        quest_doc = quest_ref.get()
        
        if not quest_doc.exists:
            await select_interaction.response.send_message("クエストが見つかりません", ephemeral=True)
            return
        
        quest_data = quest_doc.to_dict()
        
        if quest_data.get("status") != "active":
            await select_interaction.response.send_message("このクエストは既に完了または期限切れです", ephemeral=True)
            return
        
        # クエスト削除
        quest_ref.update({
            "status": "deleted",
            "deleted_at": firestore.SERVER_TIMESTAMP
        })
        
        embed = discord.Embed(
            title="🗑️ クエスト削除完了",
            description=f"「{quest_data.get('goal', '目標不明')}」を削除しました",
            color=discord.Color.orange()
        )
        embed.add_field(name="ステータス", value="クエストが正常に削除されました", inline=False)
        embed.set_footer(text="KRAFTコミュニティ")
        
        await select_interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"クエスト削除: {quest_id}")
    
    select.callback = select_callback
    
    view = discord.ui.View(timeout=120)
    view.add_item(select)
    
    await interaction.followup.send("削除したいクエストを選択してください:", view=view, ephemeral=True)

@bot.event
async def on_ready():
    print(f"\n👥 KRAFTコミュニティBot起動: {bot.user}")
    print(f"接続サーバー: {[g.name for g in bot.guilds]}")
    
    # 既存のコマンドを完全にクリア
    print("\n🗑️ 既存コマンドをクリア...")
    bot.tree.clear_commands(guild=None)
    
    # =====================================
    # コマンド同期
    # =====================================
    print("\n🔄 コマンドを同期中...")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)}個のコマンドが同期されました！")
        for cmd in synced:
            print(f"  - /{cmd.name}: {cmd.description}")
        
        print("\n🎯 利用可能なコマンド:")
        print("  /プロフィール [ユーザー] - プロフィール確認")
        print("  /寄付 [金額] - コミュニティ寄付")
        print("  /クエスト作成 [目標内容] [年] [月] [日] - 個人クエスト作成")
        print("  /マイクエスト - 自分のクエスト一覧")
        print("  /クエスト達成 - クエスト達成報告（選択式）")
        print("  /クエスト削除 - クエスト削除（選択式）")
        
    except Exception as e:
        print(f"❌ コマンド同期失敗: {e}")
        import traceback
        traceback.print_exc()
    
    # バックグラウンドタスク開始
    print("\n⚙️ バックグラウンドタスク開始...")
    quest_deadline_check.start()

# バックグラウンドタスク：期限切れクエスト処理
@tasks.loop(hours=1)  # 1時間ごとに実行
async def quest_deadline_check():
    try:
        print("🕒 期限切れ個人クエストをチェック中...")
        
        # 期限切れクエスト取得
        now = datetime.datetime.utcnow()
        active_quests = db.collection("personal_quests").where("status", "==", "active").stream()
        
        expired_count = 0
        for quest in active_quests:
            quest_data = quest.to_dict()
            deadline = quest_data.get("deadline")
            
            if isinstance(deadline, str):
                deadline = datetime.datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            elif hasattr(deadline, 'to_datetime'):
                deadline = deadline.to_datetime()
            
            if deadline.replace(tzinfo=None) < now:
                # クエストを期限切れに変更
                quest.reference.update({
                    "status": "expired",
                    "expired_at": firestore.SERVER_TIMESTAMP
                })
                
                expired_count += 1
                print(f"個人クエスト期限切れ: {quest_data.get('goal', '目標不明')[:20]}... (ID: {quest.id[:8]})")
        
        if expired_count > 0:
            print(f"✅ {expired_count}件の個人クエストを期限切れに変更しました")
        else:
            print("期限切れ個人クエストはありません")
            
    except Exception as e:
        print(f"❌ 期限切れクエストチェックエラー: {e}")

@quest_deadline_check.before_loop
async def before_quest_deadline_check():
    await bot.wait_until_ready()

# メッセージ監視とXP付与
@bot.event
async def on_message(message):
    # ボットのメッセージは無視
    if message.author.bot:
        return
    
    try:
        user_id = str(message.author.id)
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        # クールダウンチェック
        now = datetime.datetime.utcnow()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            last_xp_time = user_data.get("last_message_xp")
            
            if last_xp_time:
                if isinstance(last_xp_time, str):
                    last_xp_time = datetime.datetime.fromisoformat(last_xp_time.replace('Z', '+00:00'))
                elif hasattr(last_xp_time, 'to_datetime'):
                    last_xp_time = last_xp_time.to_datetime()
                
                time_diff = (now - last_xp_time.replace(tzinfo=None)).total_seconds()
                if time_diff < XP_COOLDOWN:
                    return  # クールダウン中
        
        # XP付与
        current_level = user_data.get("level", 1) if user_doc.exists else 1
        current_xp = user_data.get("xp", 0) if user_doc.exists else 0
        current_total_xp = user_data.get("total_xp", 0) if user_doc.exists else 0
        messages_count = user_data.get("messages_count", 0) if user_doc.exists else 0
        
        new_total_xp = current_total_xp + XP_PER_MESSAGE
        new_level, new_xp = calculate_level_and_xp(new_total_xp)
        
        level_up = new_level > current_level
        
        # データベース更新
        update_data = {
            "user_id": user_id,
            "level": new_level,
            "xp": new_xp,
            "total_xp": new_total_xp,
            "messages_count": messages_count + 1,
            "last_message_xp": now,
            "balance": user_data.get("balance", 1000) if user_doc.exists else 1000
        }
        
        if not user_doc.exists:
            update_data.update({
                "donations_made": 0,
                "donations_received": 0,
                "quests_completed": 0,
                "created_at": firestore.SERVER_TIMESTAMP
            })
        
        user_ref.set(update_data, merge=True)
        
        # レベルアップ通知
        if level_up:
            print(f"レベルアップ: {message.author.name} Lv.{current_level} → Lv.{new_level}")
            
            # レベルアップ報酬計算
            kr_reward = new_level * 500  # レベル × 500 KR
            
            # 報酬付与
            current_balance = update_data.get("balance", 1000)
            user_ref.update({"balance": current_balance + kr_reward})
            
            # レベルアップ通知（同じチャンネルに送信）
            embed = discord.Embed(
                title="🎉 レベルアップ！",
                description=f"{message.author.mention} がレベル **{current_level}** から **{new_level}** になりました！",
                color=discord.Color.gold()
            )
            embed.add_field(name="報酬", value=f"{kr_reward:,} KR", inline=False)
            embed.set_footer(text="KRAFTコミュニティ")
            
            await message.channel.send(embed=embed)
    
    except Exception as e:
        print(f"メッセージ処理エラー: {e}")
    
    # コマンド処理を続行
    await bot.process_commands(message)

# エラーハンドリング
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ エラー: {event}")
    import traceback
    traceback.print_exc()

@bot.event
async def on_ready():
    print(f"\n👥 KRAFTコミュニティBot起動: {bot.user}")
    print(f"接続サーバー: {[g.name for g in bot.guilds]}")
    
    print("\n🔄 コマンドを同期中...")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)}個のコマンドが同期されました！")
        for cmd in synced:
            print(f"  - /{cmd.name}: {cmd.description}")
        
        # バックグラウンドタスク開始
        if not quest_deadline_check.is_running():
            quest_deadline_check.start()
            print("✅ クエスト期限チェックタスク開始")
    except Exception as e:
        print(f"❌ コマンド同期失敗: {e}")

print("\n👥 KRAFTコミュニティBot起動中...")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ TOKENが設定されていません")
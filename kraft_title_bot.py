# kraft_title_bot.py - KRAFT称号システムBot
# 責務: 称号条件判定・Discordロール付与・称号獲得通知・行動データ監視

import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import asyncio
from typing import Optional, Dict, Any, List, Set
import logging

# 環境変数読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN_TITLE_BOT")

print("🏅 KRAFT称号システムBot - 開発版")
print("=" * 50)
print(f"Token: {'OK' if TOKEN else 'NG'}")
if not TOKEN:
    print("❌ DISCORD_TOKEN_TITLE_BOTが設定されていません")
    exit(1)

# Firebase初期化
if not firebase_admin._apps:
    cred = credentials.Certificate("config/firebase_credentials.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 称号設定
TITLE_CONDITIONS = {
    # レベル系称号
    "新人冒険者": {
        "condition": "level >= 5",
        "description": "レベル5到達",
        "role_name": "新人冒険者",
        "category": "レベル"
    },
    "冒険者": {
        "condition": "level >= 10",
        "description": "レベル10到達",
        "role_name": "冒険者",
        "category": "レベル"
    },
    "熟練冒険者": {
        "condition": "level >= 20",
        "description": "レベル20到達",
        "role_name": "熟練冒険者",
        "category": "レベル"
    },
    "探求者": {
        "condition": "level >= 30",
        "description": "レベル30到達",
        "role_name": "探求者",
        "category": "レベル"
    },
    "達人": {
        "condition": "level >= 50",
        "description": "レベル50到達",
        "role_name": "達人",
        "category": "レベル"
    },
    "生きる伝説": {
        "condition": "level >= 100",
        "description": "レベル100到達",
        "role_name": "生きる伝説",
        "category": "レベル"
    },
    
    # アクティビティ系称号
    "よく喋る人": {
        "condition": "monthly_messages >= 500",
        "description": "月間メッセージ数500件以上",
        "role_name": "よく喋る人",
        "category": "アクティビティ"
    },
    "エミネム": {
        "condition": "monthly_messages >= 1000",
        "description": "月間メッセージ数1000件以上",
        "role_name": "エミネム",
        "category": "アクティビティ"
    },
    "どこにでもいる人": {
        "condition": "active_channels >= 10",
        "description": "月間10チャンネル以上で発言",
        "role_name": "どこにでもいる人",
        "category": "アクティビティ"
    },
    
    # クエスト系称号
    "クエストマスター": {
        "condition": "completed_quests >= 100",
        "description": "クエスト100回達成",
        "role_name": "クエストマスター",
        "category": "クエスト"
    },
    "どんまい": {
        "condition": "consecutive_quest_failures >= 2",
        "description": "クエスト2連続失敗",
        "role_name": "どんまい",
        "category": "クエスト"
    },
    "逆にすごい": {
        "condition": "consecutive_quest_failures >= 10",
        "description": "クエスト10連続失敗",
        "role_name": "逆にすごい",
        "category": "クエスト"
    },
    
    # 経済系称号
    "寄付マスター": {
        "condition": "donation_total >= 50000",
        "description": "総寄付額5万KR以上",
        "role_name": "寄付マスター",
        "category": "経済"
    },
    "聖人": {
        "condition": "became_zero_by_donation == True",
        "description": "寄付で残高0になった",
        "role_name": "聖人",
        "category": "経済"
    },
    "投資マスター": {
        "condition": "investment_profit >= 100000",
        "description": "投資利益10万KR以上",
        "role_name": "投資マスター",
        "category": "経済"
    },
    "ノーリターン": {
        "condition": "became_zero_by_investment == True",
        "description": "投資で残高0になった",
        "role_name": "ノーリターン",
        "category": "経済"
    },
    "ギフトマスター": {
        "condition": "transfer_total >= 100000",
        "description": "総送金額10万KR以上",
        "role_name": "ギフトマスター",
        "category": "経済"
    },
    "大盤振る舞い": {
        "condition": "became_zero_by_transfer == True",
        "description": "送金で残高0になった",
        "role_name": "大盤振る舞い",
        "category": "経済"
    }
}

class KraftTitleBot(commands.Bot):
    """KRAFT称号システムメインクラス"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!title_', intents=intents)
        self.title_check_queue = asyncio.Queue()
        self.notification_channel_id = 1352859030715891782  # 称号獲得のお知らせチャンネル
    
    async def on_ready(self):
        """Bot起動時処理"""
        print(f'🏅 KRAFT称号システム {self.user.name} が稼働開始しました')
        
        # コマンド登録
        self.tree.command(name="称号強制チェック", description="全ユーザーの称号を強制チェックします（管理者専用）")(force_title_check_cmd)
        
        print("\n🔄 コマンドを同期中...")
        try:
            synced = await self.tree.sync()
            print(f'✅ {len(synced)}個のコマンドが同期されました')
            for cmd in synced:
                print(f"  - /{cmd.name}: {cmd.description}")
            
            print("✅ 称号チェックコマンド同期完了")
                
        except Exception as e:
            print(f'❌ コマンド同期エラー: {e}')
            import traceback
            traceback.print_exc()
    
    # =====================================
    # 称号チェック・付与システム
    # =====================================
    
    async def check_user_titles(self, user_id: str) -> List[str]:
        """ユーザーの称号条件をチェック"""
        try:
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return []
            
            user_data = user_doc.to_dict()
            current_titles = set(user_data.get("titles", []))
            new_titles = []
            
            # 各称号の条件をチェック
            for title_name, title_info in TITLE_CONDITIONS.items():
                if title_name in current_titles:
                    continue  # 既に持っている称号はスキップ
                
                if await self.evaluate_condition(title_info["condition"], user_data):
                    current_titles.add(title_name)
                    new_titles.append(title_name)
                    logger.info(f"称号付与: {user_id} -> {title_name}")
            
            # 新しい称号があれば保存
            if new_titles:
                user_data["titles"] = list(current_titles)
                user_ref.set(user_data, merge=True)
            
            return new_titles
            
        except Exception as e:
            logger.error(f"称号チェックエラー ({user_id}): {e}")
            return []
    
    async def evaluate_condition(self, condition: str, user_data: Dict[str, Any]) -> bool:
        """称号条件の評価"""
        try:
            # 安全な評価のため、限定された変数のみ使用
            safe_vars = {
                "level": user_data.get("level", 1),
                "monthly_messages": user_data.get("monthly_messages", 0),
                "active_channels": len(user_data.get("active_channels", [])),
                "completed_quests": user_data.get("completed_quests", 0),
                "consecutive_quest_failures": user_data.get("consecutive_quest_failures", 0),
                "donation_total": user_data.get("donation_total", 0),
                "transfer_total": user_data.get("transfer_total", 0),
                "investment_profit": user_data.get("investment_profit", 0),
                "became_zero_by_donation": user_data.get("became_zero_by_donation", False),
                "became_zero_by_investment": user_data.get("became_zero_by_investment", False),
                "became_zero_by_transfer": user_data.get("became_zero_by_transfer", False)
            }
            
            # 条件評価
            return eval(condition, {"__builtins__": {}}, safe_vars)
            
        except Exception as e:
            logger.error(f"条件評価エラー: {condition} - {e}")
            return False
    
    async def assign_discord_role(self, user_id: str, title_name: str) -> bool:
        """Discordロールを付与"""
        try:
            title_info = TITLE_CONDITIONS.get(title_name)
            if not title_info:
                return False
            
            # 全ギルドでロール付与を試行
            for guild in self.guilds:
                member = guild.get_member(int(user_id))
                if member:
                    role = discord.utils.get(guild.roles, name=title_info["role_name"])
                    if role and role not in member.roles:
                        await member.add_roles(role)
                        logger.info(f"ロール付与: {member.name} -> {title_info['role_name']}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"ロール付与エラー: {e}")
            return False
    
    async def send_title_notification(self, user_id: str, title_name: str):
        """称号獲得通知を送信"""
        try:
            channel = self.get_channel(self.notification_channel_id)
            if not channel:
                return
            
            # ユーザー取得
            user = self.get_user(int(user_id))
            if not user:
                user = await self.fetch_user(int(user_id))
            
            if not user:
                return
            
            title_info = TITLE_CONDITIONS.get(title_name, {})
            description = title_info.get("description", "")
            category = title_info.get("category", "不明")
            
            embed = discord.Embed(
                title="🎉 新しい称号を獲得しました！",
                description=f"{user.mention} が称号 **『{title_name}』** を獲得しました！",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="📋 詳細",
                value=f"カテゴリ: {category}\n条件: {description}",
                inline=False
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text="KRAFT 称号システム")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"称号通知送信エラー: {e}")
    
    # =====================================
    # イベント監視システム
    # =====================================
    
    async def on_message_event(self, user_id: str, message: discord.Message):
        """メッセージイベント処理"""
        try:
            # 月間メッセージ数更新
            await self.update_monthly_activity(user_id, message.channel.id)
            
            # 称号チェックをキューに追加
            await self.title_check_queue.put(("message", user_id))
            
        except Exception as e:
            logger.error(f"メッセージイベント処理エラー: {e}")
    
    async def on_quest_complete_event(self, user_id: str):
        """クエスト完了イベント処理"""
        try:
            # 連続失敗カウンターリセット
            user_ref = db.collection("users").document(user_id)
            user_ref.update({"consecutive_quest_failures": 0})
            
            # 称号チェックをキューに追加
            await self.title_check_queue.put(("quest_complete", user_id))
            
        except Exception as e:
            logger.error(f"クエスト完了イベント処理エラー: {e}")
    
    async def on_quest_failure_event(self, user_id: str):
        """クエスト失敗イベント処理"""
        try:
            # 連続失敗カウンター増加
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            user_data = user_doc.to_dict() if user_doc.exists else {}
            
            consecutive_failures = user_data.get("consecutive_quest_failures", 0) + 1
            user_ref.update({"consecutive_quest_failures": consecutive_failures})
            
            # 称号チェックをキューに追加
            await self.title_check_queue.put(("quest_failure", user_id))
            
        except Exception as e:
            logger.error(f"クエスト失敗イベント処理エラー: {e}")
    
    async def on_economic_event(self, user_id: str, event_type: str, amount: int, resulted_in_zero: bool = False):
        """経済イベント処理（寄付・送金・投資）"""
        try:
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            user_data = user_doc.to_dict() if user_doc.exists else {}
            
            # イベントタイプ別の処理
            if event_type == "donation":
                user_data["donation_total"] = user_data.get("donation_total", 0) + amount
                if resulted_in_zero:
                    user_data["became_zero_by_donation"] = True
            elif event_type == "transfer":
                user_data["transfer_total"] = user_data.get("transfer_total", 0) + amount
                if resulted_in_zero:
                    user_data["became_zero_by_transfer"] = True
            elif event_type == "investment_profit":
                user_data["investment_profit"] = user_data.get("investment_profit", 0) + amount
            elif event_type == "investment_loss" and resulted_in_zero:
                user_data["became_zero_by_investment"] = True
            
            user_ref.set(user_data, merge=True)
            
            # 称号チェックをキューに追加
            await self.title_check_queue.put(("economic", user_id))
            
        except Exception as e:
            logger.error(f"経済イベント処理エラー: {e}")
    
    # =====================================
    # ユーティリティメソッド
    # =====================================
    
    async def update_monthly_activity(self, user_id: str, channel_id: int):
        """月間アクティビティ更新"""
        try:
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            user_data = user_doc.to_dict() if user_doc.exists else {}
            
            now = datetime.datetime.utcnow()
            last_reset = user_data.get("last_monthly_reset", "2025-01-01T00:00:00")
            
            try:
                last_reset_date = datetime.datetime.fromisoformat(last_reset)
            except ValueError:
                last_reset_date = datetime.datetime.strptime(last_reset, "%Y-%m-%dT%H:%M:%S")
            
            # 月が変わっていればリセット
            if now.month != last_reset_date.month or now.year != last_reset_date.year:
                user_data["monthly_messages"] = 0
                user_data["active_channels"] = []
                user_data["last_monthly_reset"] = now.isoformat()
            
            # 月間メッセージ数増加
            user_data["monthly_messages"] = user_data.get("monthly_messages", 0) + 1
            
            # アクティブチャンネル追加
            active_channels = set(user_data.get("active_channels", []))
            active_channels.add(str(channel_id))
            user_data["active_channels"] = list(active_channels)
            
            user_ref.set(user_data, merge=True)
            
        except Exception as e:
            logger.error(f"月間アクティビティ更新エラー: {e}")
    
    
    # =====================================
    # バックグラウンドタスク
    # =====================================
    
    @tasks.loop(minutes=5)
    async def title_check_task(self):
        """称号チェックタスク"""
        try:
            # キューからイベントを処理
            processed = 0
            while not self.title_check_queue.empty() and processed < 10:
                event_type, user_id = await self.title_check_queue.get()
                
                new_titles = await self.check_user_titles(user_id)
                
                # 新しい称号があれば処理
                for title in new_titles:
                    await self.assign_discord_role(user_id, title)
                    await self.send_title_notification(user_id, title)
                    await asyncio.sleep(1)  # レート制限対策
                
                processed += 1
                
        except Exception as e:
            logger.error(f"称号チェックタスクエラー: {e}")
    
    @tasks.loop(hours=24)
    async def monthly_reset_task(self):
        """月次リセットタスク"""
        try:
            now = datetime.datetime.utcnow()
            if now.day == 1 and now.hour == 0:  # 月初の午前0時
                logger.info("月次称号データリセット実行")
                
                # 必要に応じて月次データのリセット処理を実装
                # 現在は各ユーザーのメッセージ時に自動リセットされるため、ここでは特に処理なし
                
        except Exception as e:
            logger.error(f"月次リセットタスクエラー: {e}")
    
    @title_check_task.before_loop
    async def before_title_check_task(self):
        await self.wait_until_ready()
    
    @monthly_reset_task.before_loop
    async def before_monthly_reset_task(self):
        await self.wait_until_ready()

# =====================================
# 称号強制チェックコマンド（管理者専用）
# =====================================
async def force_title_check_cmd(interaction: discord.Interaction):
    print(f"[称号強制チェック] {interaction.user.name} が実行")
    管理者ID一覧 = ["1249582099825164312", "867343308426444801"]
    if str(interaction.user.id) not in 管理者ID一覧:
        await interaction.response.send_message("❌ 管理者専用コマンドです。", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    bot = interaction.client
    users_ref = db.collection("users")
    users = users_ref.stream()
    
    total_users = 0
    total_new_titles = 0
    
    for user_doc in users:
        user_id = user_doc.id
        new_titles = await bot.check_user_titles(user_id)
        total_users += 1
        total_new_titles += len(new_titles)
        
        # 新しい称号があればロール付与と通知
        for title in new_titles:
            await bot.assign_discord_role(user_id, title)
            await bot.send_title_notification(user_id, title)
    
    await interaction.followup.send(
        f"✅ 称号チェック完了\n"
        f"チェック対象: {total_users}人\n"
        f"新規称号付与: {total_new_titles}個"
    )

# Bot起動
if __name__ == "__main__":
    bot = KraftTitleBot()
    bot.run(TOKEN)
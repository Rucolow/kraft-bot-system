# kraft_stock_market.py - KRAFT株式市場Bot
# 責務: 株式売買・株価管理・ニュース生成・配当システム・ポートフォリオ表示

import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import random
import asyncio
from typing import Optional, Dict, Any, List
import logging
import aiohttp
import anthropic
import json
import hashlib

# 環境変数読み込み
load_dotenv()
TOKEN = os.getenv("STOCK_MARKET_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Firebase初期化
if not firebase_admin._apps:
    cred = credentials.Certificate("config/firebase_credentials.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Claude API初期化
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None

class CentralBankAPI:
    """中央銀行Bot API連携クラス"""
    
    async def subtract_kr(self, user_id: str, amount: int, reason: str) -> bool:
        """中央銀行にKR減額を依頼"""
        try:
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return False
            
            current_balance = user_doc.to_dict().get("balance", 0)
            if current_balance < amount:
                return False
            
            user_ref.update({"balance": current_balance - amount})
            logger.info(f"KR減額: {user_id} -{amount}KR ({reason})")
            return True
        except Exception as e:
            logger.error(f"KR減額エラー: {e}")
            return False
    
    async def add_kr(self, user_id: str, amount: int, reason: str) -> bool:
        """中央銀行にKR付与を依頼"""
        try:
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                current_balance = user_doc.to_dict().get("balance", 0)
                user_ref.update({"balance": current_balance + amount})
            else:
                user_ref.set({"balance": 1000 + amount}, merge=True)
            
            logger.info(f"KR付与: {user_id} +{amount}KR ({reason})")
            return True
        except Exception as e:
            logger.error(f"KR付与エラー: {e}")
            return False

class NewsGenerator:
    """ニュース生成システム"""
    
    def __init__(self):
        self.company_contexts = {
            "WICR": {
                "name": "Wicrosoft",
                "industry": "AI・Bot開発",
                "business": "Discord Bot開発・運営、AI チャットボット技術",
                "news_types": ["技術革新", "新機能リリース", "パートナーシップ"]
            },
            "QOOG": {
                "name": "Qoogle", 
                "industry": "量子コンピュータ",
                "business": "量子コンピュータ研究開発、次世代暗号化技術",
                "news_types": ["技術ブレークスルー", "研究成果発表", "政府契約"]
            },
            "RBLX": {
                "name": "Roblux",
                "industry": "ゲーム開発", 
                "business": "PCゲーム開発、モバイルゲーム運営",
                "news_types": ["新作発表", "ユーザー数増加", "大会開催"]
            },
            "NFOX": {
                "name": "Netfox",
                "industry": "動画配信",
                "business": "動画配信プラットフォーム運営、ライブストリーミング",
                "news_types": ["人気コンテンツ", "クリエイター契約", "新機能追加"]
            },
            "MOSL": {
                "name": "Mosla",
                "industry": "再生エネルギー",
                "business": "太陽光発電システム製造、風力発電設備",
                "news_types": ["大型プロジェクト受注", "技術革新", "政府支援"]
            },
            "NKDA": {
                "name": "Nikuda", 
                "industry": "物流・配送",
                "business": "国際物流サービス、倉庫管理・配送",
                "news_types": ["大手企業契約", "物流効率化", "新拠点開設"]
            },
            "FSCH": {
                "name": "Firma Schnitzel",
                "industry": "バイオテクノロジー", 
                "business": "新薬研究開発、遺伝子治療技術",
                "news_types": ["臨床試験結果", "新薬承認", "研究提携"]
            },
            "IRHA": {
                "name": "Iroha",
                "industry": "医療IT",
                "business": "電子カルテシステム、遠隔診療プラットフォーム",
                "news_types": ["医療機関導入", "AI精度向上", "遠隔医療拡大"]
            },
            "STRK": {
                "name": "Strike", 
                "industry": "デジタル決済",
                "business": "デジタル決済サービス、暗号通貨取引所",
                "news_types": ["決済提携", "規制対応", "セキュリティ強化"]
            },
            "ASST": {
                "name": "Assist",
                "industry": "銀行・金融",
                "business": "個人・法人向け銀行業務、住宅ローン・事業融資", 
                "news_types": ["業績発表", "新サービス", "金利政策影響"]
            }
        }
    
    async def generate_news(self, ticker: str) -> Optional[Dict[str, Any]]:
        """指定企業のニュースを生成"""
        if not claude_client:
            return self.get_fallback_news(ticker)
            
        company = self.company_contexts.get(ticker)
        if not company:
            return None
            
        news_type = random.choice(company["news_types"])
        
        prompt = f"""
あなたは金融ニュース記者です。以下の企業について、リアルな投資ニュースを1つ生成してください。

企業情報:
- 企業名: {company['name']} ({ticker})
- 業界: {company['industry']}
- 事業内容: {company['business']}
- ニュースタイプ: {news_type}

要件:
1. 150-250文字程度の日本語ニュース
2. 投資判断に影響する具体的な内容
3. 株価への影響度を-3から+3で評価

出力形式（JSON）:
{{
  "headline": "ニュースの見出し",
  "content": "ニュース本文",
  "impact_score": 影響度数値,
  "news_type": "{news_type}",
  "ticker": "{ticker}"
}}
"""
        
        try:
            response = await asyncio.to_thread(
                claude_client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            news_text = response.content[0].text
            news_data = json.loads(news_text)
            news_data["timestamp"] = datetime.datetime.utcnow().isoformat()
            
            return news_data
            
        except Exception as e:
            logger.error(f"ニュース生成エラー: {e}")
            return self.get_fallback_news(ticker)
    
    def get_fallback_news(self, ticker: str) -> Dict[str, Any]:
        """APIエラー時のフォールバックニュース"""
        company = self.company_contexts.get(ticker, {"name": "Unknown"})
        return {
            "headline": f"{company['name']}、堅調な業績を維持",
            "content": f"{company['name']}は事業展開を継続し、安定した成長を示している。",
            "impact_score": 0,
            "news_type": "業績",
            "ticker": ticker,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

class StockPriceManager:
    """株価管理システム"""
    
    @staticmethod
    def calculate_price_change(company: Dict[str, Any]) -> float:
        """株価変動率の計算"""
        try:
            today = datetime.datetime.utcnow()
            date_string = f"{today.year}-{today.month}-{today.day}"
            
            # 決定論的なシード生成
            combined = company['ticker'] + date_string
            hash_value = int(hashlib.sha256(combined.encode()).hexdigest()[:8], 16)
            
            # 基本変動率: -3.0%から+3.0%
            normalized = abs(hash_value) / (2**32)
            base_change_rate = (normalized * 6) - 3
            
            # ニュース影響度を加算
            news_impact = StockPriceManager.calculate_news_impact(company)
            
            # 合計変動率（最大±8%に制限）
            total_change = base_change_rate + news_impact
            return max(-8, min(8, round(total_change, 2)))
        
        except Exception as e:
            logger.error(f"株価変動計算エラー: {e}")
            return 0.0
    
    @staticmethod
    def calculate_news_impact(company: Dict[str, Any]) -> float:
        """ニュース影響度の計算"""
        try:
            one_day_ago = datetime.datetime.utcnow() - datetime.timedelta(days=1)
            
            news_ref = db.collection("market_news")
            news_docs = news_ref.where("timestamp", ">=", one_day_ago.isoformat()).get()
            
            total_impact = 0
            
            for news_doc in news_docs:
                news_data = news_doc.to_dict()
                
                if news_data.get("ticker") == company['ticker']:
                    # 企業固有ニュース
                    total_impact += news_data.get("impact_score", 0) * 0.8
                elif not news_data.get("ticker"):
                    # 市場全体ニュース
                    total_impact += news_data.get("impact_score", 0) * 0.3
            
            return max(-5, min(5, total_impact))
        
        except Exception as e:
            logger.error(f"ニュース影響計算エラー: {e}")
            return 0

class KraftStockMarket(commands.Bot):
    """KRAFT株式市場メインクラス"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!stock_', intents=intents)
        self.central_bank = CentralBankAPI()
        self.news_generator = NewsGenerator()
        self.price_manager = StockPriceManager()
    
    async def on_ready(self):
        """Bot起動時処理"""
        print(f'📈 KRAFT株式市場 {self.user.name} が稼働開始しました')
        
        try:
            synced = await self.tree.sync()
            print(f'✅ {len(synced)}個のコマンドが同期されました')
            
            # バックグラウンドタスク開始
            if not self.daily_price_update.is_running():
                self.daily_price_update.start()
                print("✅ 日次株価更新タスク開始")
                
            if not self.auto_news_generation.is_running():
                self.auto_news_generation.start()
                print("✅ 自動ニュース生成タスク開始")
                
        except Exception as e:
            print(f'❌ コマンド同期エラー: {e}')
    
    # =====================================
    # 株式売買コマンド
    # =====================================
    
    @app_commands.command(name="株式購入", description="株式を購入します")
    @app_commands.describe(銘柄="購入する銘柄", 株数="購入する株数")
    @app_commands.choices(銘柄=[
        app_commands.Choice(name="🤖 Wicrosoft (WICR)", value="WICR"),
        app_commands.Choice(name="⚛️ Qoogle (QOOG)", value="QOOG"),
        app_commands.Choice(name="🎮 Roblux (RBLX)", value="RBLX"),
        app_commands.Choice(name="📺 Netfox (NFOX)", value="NFOX"),
        app_commands.Choice(name="🌱 Mosla (MOSL)", value="MOSL"),
        app_commands.Choice(name="🚚 Nikuda (NKDA)", value="NKDA"),
        app_commands.Choice(name="🧬 Firma Schnitzel (FSCH)", value="FSCH"),
        app_commands.Choice(name="🏥 Iroha (IRHA)", value="IRHA"),
        app_commands.Choice(name="💳 Strike (STRK)", value="STRK"),
        app_commands.Choice(name="🏦 Assist (ASST)", value="ASST")
    ])
    async def buy_stock(self, interaction: discord.Interaction, 銘柄: app_commands.Choice[str], 株数: int):
        """株式購入処理"""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            ticker = 銘柄.value
            
            if 株数 <= 0:
                await interaction.followup.send("❌ 株数は1以上を指定してください。")
                return
            
            # 企業情報取得
            company_ref = db.collection("companies").document(ticker)
            company_doc = company_ref.get()
            
            if not company_doc.exists:
                await interaction.followup.send("❌ 企業データが見つかりません。")
                return
            
            company_data = company_doc.to_dict()
            current_price = company_data["current_price"]
            total_cost = current_price * 株数
            transaction_fee = int(total_cost * 0.02)  # 2%手数料
            total_payment = total_cost + transaction_fee
            
            # KR支払い処理
            if not await self.central_bank.subtract_kr(user_id, total_payment, f"stock_purchase_{ticker}"):
                await interaction.followup.send("❌ 残高不足です。")
                return
            
            # ポートフォリオ更新
            await self.update_portfolio(user_id, ticker, 株数, current_price, "buy")
            
            # 取引履歴記録
            await self.log_transaction(user_id, "buy", ticker, 株数, current_price, transaction_fee)
            
            # 成功メッセージ
            await interaction.followup.send(
                f"✅ **{company_data['name']} ({ticker})** を購入しました！\n\n"
                f"📊 **取引詳細**\n"
                f"株数: **{株数:,}株**\n"
                f"単価: **{current_price:,} KR/株**\n"
                f"株式代金: **{total_cost:,} KR**\n"
                f"手数料: **{transaction_fee:,} KR** (2.0%)\n"
                f"総支払額: **{total_payment:,} KR**"
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")
    
    @app_commands.command(name="株式売却", description="保有株式を売却します")
    @app_commands.describe(銘柄="売却する銘柄", 株数="売却する株数")
    @app_commands.choices(銘柄=[
        app_commands.Choice(name="🤖 Wicrosoft (WICR)", value="WICR"),
        app_commands.Choice(name="⚛️ Qoogle (QOOG)", value="QOOG"),
        app_commands.Choice(name="🎮 Roblux (RBLX)", value="RBLX"),
        app_commands.Choice(name="📺 Netfox (NFOX)", value="NFOX"),
        app_commands.Choice(name="🌱 Mosla (MOSL)", value="MOSL"),
        app_commands.Choice(name="🚚 Nikuda (NKDA)", value="NKDA"),
        app_commands.Choice(name="🧬 Firma Schnitzel (FSCH)", value="FSCH"),
        app_commands.Choice(name="🏥 Iroha (IRHA)", value="IRHA"),
        app_commands.Choice(name="💳 Strike (STRK)", value="STRK"),
        app_commands.Choice(name="🏦 Assist (ASST)", value="ASST")
    ])
    async def sell_stock(self, interaction: discord.Interaction, 銘柄: app_commands.Choice[str], 株数: int):
        """株式売却処理"""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            ticker = 銘柄.value
            
            # ポートフォリオ確認
            portfolio = await self.get_user_portfolio(user_id)
            if ticker not in portfolio or portfolio[ticker]["shares"] < 株数:
                await interaction.followup.send(f"❌ {ticker} の保有株数が不足しています。")
                return
            
            # 企業情報取得
            company_ref = db.collection("companies").document(ticker)
            company_data = company_ref.get().to_dict()
            current_price = company_data["current_price"]
            
            # 売却計算
            total_revenue = current_price * 株数
            transaction_fee = int(total_revenue * 0.02)
            net_revenue = total_revenue - transaction_fee
            
            # 損益計算
            cost_basis = portfolio[ticker]["avg_cost"] * 株数
            profit_loss = total_revenue - cost_basis
            
            # KR受取処理
            await self.central_bank.add_kr(user_id, net_revenue, f"stock_sale_{ticker}")
            
            # ポートフォリオ更新
            await self.update_portfolio(user_id, ticker, -株数, current_price, "sell")
            
            # 取引履歴記録
            await self.log_transaction(user_id, "sell", ticker, 株数, current_price, transaction_fee)
            
            # 損益表示
            profit_emoji = "📈" if profit_loss >= 0 else "📉"
            profit_text = f"+{profit_loss:,}" if profit_loss >= 0 else f"{profit_loss:,}"
            
            await interaction.followup.send(
                f"✅ **{company_data['name']} ({ticker})** を売却しました！\n\n"
                f"📊 **取引詳細**\n"
                f"株数: **{株数:,}株**\n"
                f"単価: **{current_price:,} KR/株**\n"
                f"売却代金: **{total_revenue:,} KR**\n"
                f"手数料: **{transaction_fee:,} KR** (2.0%)\n"
                f"受取金額: **{net_revenue:,} KR**\n\n"
                f"{profit_emoji} **損益: {profit_text} KR**"
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")
    
    @app_commands.command(name="ポートフォリオ", description="投資ポートフォリオを表示します")
    async def portfolio(self, interaction: discord.Interaction):
        """ポートフォリオ表示"""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            portfolio = await self.get_user_portfolio(user_id)
            
            if not portfolio:
                await interaction.followup.send(
                    "📊 **投資ポートフォリオ**\n\n"
                    "現在保有銘柄はありません。\n"
                    "`/株式購入` コマンドで投資を始めましょう！"
                )
                return
            
            # ポートフォリオ詳細計算
            total_value = 0
            total_cost = 0
            holdings_text = []
            
            for ticker, holding in portfolio.items():
                company_ref = db.collection("companies").document(ticker)
                company_data = company_ref.get().to_dict()
                
                current_price = company_data["current_price"]
                shares = holding["shares"]
                avg_cost = holding["avg_cost"]
                cost_basis = avg_cost * shares
                current_value = current_price * shares
                profit_loss = current_value - cost_basis
                profit_rate = (profit_loss / cost_basis) * 100
                
                total_value += current_value
                total_cost += cost_basis
                
                profit_emoji = "📈" if profit_loss >= 0 else "📉"
                profit_text = f"+{profit_loss:,}" if profit_loss >= 0 else f"{profit_loss:,}"
                rate_text = f"+{profit_rate:.1f}%" if profit_rate >= 0 else f"{profit_rate:.1f}%"
                
                holdings_text.append(
                    f"**{company_data['name']} ({ticker})**\n"
                    f"保有: {shares:,}株 | 平均: {avg_cost:,}KR → 現在: {current_price:,}KR\n"
                    f"評価額: {current_value:,}KR | {profit_emoji} {profit_text}KR ({rate_text})\n"
                )
            
            # 全体損益
            total_profit = total_value - total_cost
            total_rate = (total_profit / total_cost) * 100 if total_cost > 0 else 0
            
            portfolio_emoji = "📈" if total_profit >= 0 else "📉"
            total_profit_text = f"+{total_profit:,}" if total_profit >= 0 else f"{total_profit:,}"
            total_rate_text = f"+{total_rate:.1f}%" if total_rate >= 0 else f"{total_rate:.1f}%"
            
            embed = discord.Embed(
                title="📊 投資ポートフォリオ",
                color=discord.Color.green() if total_profit >= 0 else discord.Color.red()
            )
            
            embed.add_field(
                name="💼 総合評価",
                value=(
                    f"評価額: **{total_value:,} KR**\n"
                    f"投資元本: **{total_cost:,} KR**\n"
                    f"{portfolio_emoji} 損益: **{total_profit_text} KR ({total_rate_text})**"
                ),
                inline=False
            )
            
            embed.add_field(
                name="📈 保有銘柄",
                value="\n".join(holdings_text),
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")
    
    # =====================================
    # 内部処理メソッド
    # =====================================
    
    async def update_portfolio(self, user_id: str, ticker: str, shares_change: int, price: int, action: str):
        """ポートフォリオ更新"""
        try:
            investment_ref = db.collection("user_investments").document(user_id)
            investment_doc = investment_ref.get()
            
            if investment_doc.exists:
                investment_data = investment_doc.to_dict()
            else:
                investment_data = {"portfolio": {}, "total_invested": 0}
            
            portfolio = investment_data.get("portfolio", {})
            
            if action == "buy":
                if ticker in portfolio:
                    # 追加購入
                    existing_shares = portfolio[ticker]["shares"]
                    existing_cost = portfolio[ticker]["total_cost"]
                    new_shares = existing_shares + shares_change
                    new_total_cost = existing_cost + (price * shares_change)
                    avg_cost = new_total_cost / new_shares
                    
                    portfolio[ticker] = {
                        "shares": new_shares,
                        "avg_cost": round(avg_cost, 2),
                        "total_cost": new_total_cost
                    }
                else:
                    # 新規購入
                    portfolio[ticker] = {
                        "shares": shares_change,
                        "avg_cost": price,
                        "total_cost": price * shares_change
                    }
                
                investment_data["total_invested"] = investment_data.get("total_invested", 0) + (price * shares_change)
            
            elif action == "sell":
                if ticker in portfolio:
                    remaining_shares = portfolio[ticker]["shares"] + shares_change  # shares_changeは負数
                    if remaining_shares <= 0:
                        del portfolio[ticker]
                    else:
                        cost_per_share = portfolio[ticker]["avg_cost"]
                        portfolio[ticker]["shares"] = remaining_shares
                        portfolio[ticker]["total_cost"] = cost_per_share * remaining_shares
            
            investment_data["portfolio"] = portfolio
            investment_ref.set(investment_data)
            
        except Exception as e:
            logger.error(f"ポートフォリオ更新エラー: {e}")
    
    async def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """ユーザーポートフォリオ取得"""
        try:
            investment_ref = db.collection("user_investments").document(user_id)
            investment_doc = investment_ref.get()
            
            if investment_doc.exists:
                return investment_doc.to_dict().get("portfolio", {})
            return {}
            
        except Exception as e:
            logger.error(f"ポートフォリオ取得エラー: {e}")
            return {}
    
    async def log_transaction(self, user_id: str, transaction_type: str, ticker: str, shares: int, price: int, fee: int):
        """取引履歴記録"""
        try:
            transaction_data = {
                "user_id": user_id,
                "type": transaction_type,
                "ticker": ticker,
                "shares": shares,
                "price": price,
                "fee": fee,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            db.collection("stock_transactions").add(transaction_data)
            
        except Exception as e:
            logger.error(f"取引履歴記録エラー: {e}")
    
    # =====================================
    # バックグラウンドタスク
    # =====================================
    
    @tasks.loop(hours=24)
    async def daily_price_update(self):
        """日次株価更新"""
        try:
            companies_ref = db.collection("companies")
            companies_docs = companies_ref.get()
            
            for company_doc in companies_docs:
                company_data = company_doc.to_dict()
                ticker = company_data['ticker']
                current_price = company_data['current_price']
                
                # 株価変動計算
                price_change_percent = self.price_manager.calculate_price_change(company_data)
                new_price = max(1, int(current_price * (1 + price_change_percent / 100)))
                
                # 価格更新
                companies_ref.document(ticker).update({"current_price": new_price})
                
                # 価格履歴記録
                price_history = {
                    "ticker": ticker,
                    "date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                    "old_price": current_price,
                    "new_price": new_price,
                    "change_percent": price_change_percent,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
                db.collection("price_changes").add(price_history)
                
                logger.info(f"{ticker} 価格更新: {current_price} → {new_price} ({price_change_percent:+.1f}%)")
                
        except Exception as e:
            logger.error(f"日次株価更新エラー: {e}")
    
    @tasks.loop(hours=2)
    async def auto_news_generation(self):
        """自動ニュース生成"""
        try:
            # 平日のみ生成
            now = datetime.datetime.utcnow()
            if now.weekday() >= 5:  # 土日はスキップ
                return
            
            # 30%の確率で生成
            if random.random() < 0.3:
                tickers = list(self.news_generator.company_contexts.keys())
                selected_ticker = random.choice(tickers)
                
                news_data = await self.news_generator.generate_news(selected_ticker)
                if news_data:
                    # ニュース保存
                    db.collection("market_news").add(news_data)
                    
                    # 株価影響適用
                    if news_data["impact_score"] != 0:
                        await self.apply_news_impact(selected_ticker, news_data["impact_score"])
                    
                    logger.info(f"自動ニュース生成: {selected_ticker} - {news_data['headline']}")
                    
        except Exception as e:
            logger.error(f"自動ニュース生成エラー: {e}")
    
    async def apply_news_impact(self, ticker: str, impact_score: int):
        """ニュース影響で株価変動"""
        try:
            company_ref = db.collection("companies").document(ticker)
            company_doc = company_ref.get()
            
            if company_doc.exists:
                company_data = company_doc.to_dict()
                current_price = company_data["current_price"]
                
                # 影響度に基づく価格変動
                price_change_rate = impact_score * 0.05  # 5%ずつ
                new_price = max(1, int(current_price * (1 + price_change_rate)))
                
                # 価格更新
                company_ref.update({"current_price": new_price})
                
                # 価格履歴記録
                price_history = {
                    "ticker": ticker,
                    "date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                    "old_price": current_price,
                    "new_price": new_price,
                    "change_rate": price_change_rate,
                    "reason": "news_impact",
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
                db.collection("price_changes").add(price_history)
                
        except Exception as e:
            logger.error(f"ニュース影響適用エラー: {e}")
    
    @daily_price_update.before_loop
    async def before_daily_price_update(self):
        await self.wait_until_ready()
    
    @auto_news_generation.before_loop
    async def before_auto_news_generation(self):
        await self.wait_until_ready()

# Bot起動
if __name__ == "__main__":
    bot = KraftStockMarket()
    bot.run(TOKEN)
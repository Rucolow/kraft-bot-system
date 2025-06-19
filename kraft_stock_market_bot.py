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
import math
import json
from typing import Dict, List, Optional, Tuple, Any
import anthropic

print("📈 KRAFT株式市場Bot - 開発版")
print("=" * 50)

# 環境変数読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN_STOCK_MARKET_BOT")
ADMIN_USER_IDS = os.getenv("ADMIN_USER_IDS", "").split(",")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Anthropic クライアント初期化
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# Firebase初期化（共有）
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
bot = commands.Bot(command_prefix='!stock_', intents=intents)
STOCK_DATA = {
    "9984": {
        "name": "ハードバンク",
        "symbol": "9984",
        "sector": "テクノロジー",
        "initial_price": 1200,
        "volatility": 0.06,  # 高ボラティリティ
        "trend": 0.002,
        "description": "通信事業、IT投資、AI開発",
        "dividend": 1.5,
        "emoji": "📱"
    },
    "7203": {
        "name": "トミタ",
        "symbol": "7203",
        "sector": "自動車",
        "initial_price": 2800,
        "volatility": 0.04,
        "trend": 0.001,
        "description": "自動車製造、ハイブリッド、自動運転",
        "dividend": 2.8,
        "emoji": "🚗"
    },
    "8306": {
        "name": "USJ銀行",
        "symbol": "8306",
        "sector": "金融",
        "initial_price": 850,
        "volatility": 0.05,
        "trend": 0.0005,
        "description": "商業銀行、証券、信託銀行",
        "dividend": 4.2,
        "emoji": "🏦"
    },
    "6758": {
        "name": "ソミー",
        "symbol": "6758",
        "sector": "電機・精密機器",
        "initial_price": 1800,
        "volatility": 0.07,
        "trend": 0.003,
        "description": "ゲーム、映画、音楽、半導体",
        "dividend": 1.2,
        "emoji": "🎮"
    },
    "9432": {
        "name": "ドモコ",
        "symbol": "9432",
        "sector": "通信",
        "initial_price": 3200,
        "volatility": 0.02,  # 低ボラティリティ
        "trend": 0.0008,
        "description": "移動通信、5G、データセンター",
        "dividend": 3.8,
        "emoji": "📞"
    },
    "3382": {
        "name": "ナインイレブン",
        "symbol": "3382",
        "sector": "小売",
        "initial_price": 1400,
        "volatility": 0.03,
        "trend": 0.001,
        "description": "コンビニ、百貨店、スーパー",
        "dividend": 2.5,
        "emoji": "🏪"
    },
    "8801": {
        "name": "住不動産",
        "symbol": "8801",
        "sector": "不動産",
        "initial_price": 2600,
        "volatility": 0.04,
        "trend": 0.0005,
        "description": "オフィスビル、商業施設、住宅分譲",
        "dividend": 3.2,
        "emoji": "🏢"
    },
    "4183": {
        "name": "四菱ケミカル",
        "symbol": "4183",
        "sector": "素材・化学",
        "initial_price": 920,
        "volatility": 0.05,
        "trend": 0.0012,
        "description": "基礎化学、石油化学、機能材料",
        "dividend": 3.5,
        "emoji": "🧪"
    },
    "5401": {
        "name": "新目鉄",
        "symbol": "5401",
        "sector": "鉄鋼・重工業",
        "initial_price": 380,
        "volatility": 0.08,  # 高ボラティリティ
        "trend": 0.001,
        "description": "鉄鋼製造、エンジニアリング",
        "dividend": 4.8,
        "emoji": "⚙️"
    },
    "2503": {
        "name": "キリンジ",
        "symbol": "2503",
        "sector": "食品・飲料",
        "initial_price": 1650,
        "volatility": 0.02,  # ディフェンシブ
        "trend": 0.0008,
        "description": "ビール、清涼飲料、医薬品",
        "dividend": 2.8,
        "emoji": "🍺"
    },
    "9501": {
        "name": "東京雷神",
        "symbol": "9501",
        "sector": "電力・ガス",
        "initial_price": 680,
        "volatility": 0.03,
        "trend": 0.0005,
        "description": "電力供給、ガス、再エネ",
        "dividend": 0.0,  # 無配
        "emoji": "⚡"
    },
    "4502": {
        "name": "アステラサズ",
        "symbol": "4502",
        "sector": "医薬品",
        "initial_price": 2200,
        "volatility": 0.06,
        "trend": 0.002,
        "description": "医療用医薬品、ワクチン開発",
        "dividend": 4.5,
        "emoji": "💊"
    }
}

# 市場設定
MARKET_CONFIG = {
    "trading_fee": 0.01,        # 取引手数料 1%
    "min_trade_amount": 100,    # 最小取引額
    "max_trade_amount": 1000000, # 最大取引額
    "daily_trade_limit": 50,    # 1日の取引回数制限
    "market_hours": {           # 市場開場時間（UTC）
        "open": 0,   # 0時開場
        "close": 23  # 23時終了
    }
}

# 通知チャンネルID
INVESTMENT_NEWS_CHANNEL_ID = 1378237887446777997  # 投資ニュースチャンネル

# =====================================
# 株価情報コマンド
# =====================================
@bot.tree.command(name="株価", description="現在の株価一覧を表示します")
async def stock_prices_cmd(interaction: discord.Interaction):
    print(f"[株価] {interaction.user.name} が実行")
    await interaction.response.defer()
    
    embed = discord.Embed(
        title="📈 KRAFT株式市場 - 現在の株価",
        color=discord.Color.blue()
    )
    
    market_ref = db.collection("market_data")
    
    for symbol, stock_info in STOCK_DATA.items():
        # 現在価格取得
        price_doc = market_ref.document(f"stock_{symbol}").get()
        if price_doc.exists:
            data = price_doc.to_dict()
            current_price = data.get("current_price", stock_info["initial_price"])
            change_percent = data.get("daily_change_percent", 0)
            volume = data.get("daily_volume", 0)
        else:
            current_price = stock_info["initial_price"]
            change_percent = 0
            volume = 0
        
        # 変動表示
        if change_percent > 0:
            change_emoji = "📈"
            color_indicator = "🟢"
        elif change_percent < 0:
            change_emoji = "📉"
            color_indicator = "🔴"
        else:
            change_emoji = "➡️"
            color_indicator = "⚪"
        
        embed.add_field(
            name=f"{color_indicator} {stock_info['emoji']} {stock_info['name']}",
            value=f"**{current_price:.2f} KR** {change_emoji}\n"
                  f"変動: {change_percent:+.2f}%\n"
                  f"出来高: {volume:,}株\n"
                  f"業界: {stock_info['sector']}\n"
                  f"配当: {stock_info['dividend']:.1f}%",
            inline=True
        )
    
    embed.set_footer(text="🔄 リアルタイム更新 | 💰 KRAFT通貨で取引可能")
    
    await interaction.followup.send(embed=embed)
    
    market_ref = db.collection("market_data")
    
    for symbol, stock_info in STOCK_DATA.items():
        # 現在価格取得
        price_doc = market_ref.document(f"stock_{symbol}").get()
        if price_doc.exists:
            data = price_doc.to_dict()
            current_price = data.get("current_price", stock_info["initial_price"])
            change_percent = data.get("daily_change_percent", 0)
            volume = data.get("daily_volume", 0)
        else:
            current_price = stock_info["initial_price"]
            change_percent = 0
            volume = 0
        
        # 変動表示
        if change_percent > 0:
            change_emoji = "📈"
            color_indicator = "🟢"
        elif change_percent < 0:
            change_emoji = "📉"
            color_indicator = "🔴"
        else:
            change_emoji = "➡️"
            color_indicator = "⚪"
        
        embed.add_field(
            name=f"{color_indicator} {stock_info['emoji']} {stock_info['name']}",
            value=f"**{current_price:.2f} KR** {change_emoji}\n"
                  f"変動: {change_percent:+.2f}%\n"
                  f"出来高: {volume:,}株\n"
                  f"業界: {stock_info['sector']}\n"
                  f"配当: {stock_info['dividend']:.1f}%",
            inline=True
        )
    
    embed.set_footer(text="KRAFT株式市場")
    await interaction.followup.send(embed=embed)

# =====================================
# 株式購入コマンド
# =====================================
@bot.tree.command(name="株式購入", description="株式を購入します")
async def buy_stock_cmd(interaction: discord.Interaction):
    print(f"[株式購入] {interaction.user.name} が実行")
    try:
        # 市場開場時間チェック
        if not is_market_open():
            await interaction.response.send_message("🕒 市場は現在閉場中です。開場時間: 0:00-23:00 (UTC)", ephemeral=True)
            return
            
            # 日次取引制限チェック
            user_id = str(interaction.user.id)
            if not await check_daily_trade_limit(user_id):
                await interaction.response.send_message(f"❌ 1日の取引回数制限({MARKET_CONFIG['daily_trade_limit']}回)に達しています", ephemeral=True)
                return
            
            class StockSelectView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=60)
                
                @discord.ui.select(
                    placeholder="購入する銘柄を選択してください...",
                    options=[
                        discord.SelectOption(
                            label=f"{stock_info['emoji']} {stock_info['name']}",
                            value=symbol,
                            description=f"{stock_info['sector']} | 配当{stock_info['dividend']:.1f}%"
                        ) for symbol, stock_info in list(STOCK_DATA.items())[:25]  # Discord limit 25 options
                    ]
                )
                async def stock_select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                    selected_symbol = select.values[0]
                    stock_info = STOCK_DATA[selected_symbol]
                    current_price = await get_current_stock_price(selected_symbol)
                    
                    # 株数入力モーダル表示
                    class SharesModal(discord.ui.Modal):
                        def __init__(self):
                            super().__init__(title=f"{stock_info['name']}の購入")
                        
                        shares_input = discord.ui.TextInput(
                            label="購入株数",
                            placeholder="購入したい株数を入力してください",
                            required=True,
                            max_length=10
                        )
                        
                        async def on_submit(self, modal_interaction: discord.Interaction):
                            try:
                                shares = int(self.shares_input.value)
                                
                                if shares <= 0:
                                    await modal_interaction.response.send_message("❌ 株数は1以上である必要があります", ephemeral=True)
                                    return
                                
                                total_cost = math.ceil(current_price * shares * (1 + MARKET_CONFIG["trading_fee"]))
                                
                                # 取引制限チェック
                                if total_cost < MARKET_CONFIG["min_trade_amount"]:
                                    await modal_interaction.response.send_message(f"❌ 最小取引額: {MARKET_CONFIG['min_trade_amount']:,} KR", ephemeral=True)
                                    return
                                
                                if total_cost > MARKET_CONFIG["max_trade_amount"]:
                                    await modal_interaction.response.send_message(f"❌ 最大取引額: {MARKET_CONFIG['max_trade_amount']:,} KR", ephemeral=True)
                                    return
                                
                                # ユーザー残高確認
                                user_ref = db.collection("users").document(user_id)
                                user_doc = user_ref.get()
                                
                                if not user_doc.exists:
                                    await modal_interaction.response.send_message("❌ ユーザーデータが見つかりません", ephemeral=True)
                                    return
                                
                                user_data = user_doc.to_dict()
                                balance = user_data.get("balance", 0)
                                
                                if balance < total_cost:
                                    await modal_interaction.response.send_message(f"❌ 残高不足\n必要額: {total_cost:,} KR\n現在残高: {balance:,} KR", ephemeral=True)
                                    return
                                
                                # 取引実行
                                await execute_stock_purchase(user_id, selected_symbol, shares, current_price, total_cost)
                                
                                embed = discord.Embed(
                                    title="📈 株式購入完了",
                                    description=f"{stock_info['emoji']} {stock_info['name']} を購入しました",
                                    color=discord.Color.green()
                                )
                                
                                embed.add_field(name="購入株数", value=f"{shares:,}株", inline=True)
                                embed.add_field(name="単価", value=f"{current_price:.2f} KR", inline=True)
                                embed.add_field(name="手数料込み総額", value=f"{total_cost:,} KR", inline=True)
                                embed.add_field(name="新残高", value=f"{balance - total_cost:,} KR", inline=True)
                                
                                embed.set_footer(text="KRAFT株式市場")
                                await modal_interaction.response.send_message(embed=embed)
                                
                            except ValueError:
                                await modal_interaction.response.send_message("❌ 有効な数値を入力してください", ephemeral=True)
                            except Exception as e:
                                print(f"株式購入エラー: {e}")
                    
                    modal = SharesModal()
                    await interaction.response.send_modal(modal)
            
            view = StockSelectView()
            embed = discord.Embed(
                title="📈 株式購入",
                description="購入したい銘柄を選択してください",
                color=discord.Color.blue()
            )
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
    except Exception as e:
        print(f"株式購入コマンドエラー: {e}")

# =====================================
# 株式売却コマンド
# =====================================
@bot.tree.command(name="株式売却", description="保有している株式を売却します")
async def sell_stock_cmd(interaction: discord.Interaction):
    print(f"[株式売却] {interaction.user.name} が実行")
    try:
        # 市場開場時間チェック
        if not is_market_open():
            await interaction.response.send_message("🕒 市場は現在閉場中です。開場時間: 0:00-23:00 (UTC)", ephemeral=True)
            return
            
            # 日次取引制限チェック
            user_id = str(interaction.user.id)
            if not await check_daily_trade_limit(user_id):
                await interaction.response.send_message(f"❌ 1日の取引回数制限({MARKET_CONFIG['daily_trade_limit']}回)に達しています", ephemeral=True)
                return
            
            # ポートフォリオ取得
            portfolio = await get_user_portfolio(user_id)
            
            if not portfolio:
                await interaction.response.send_message("📊 保有株式がありません", ephemeral=True)
                return
            
            # 保有株式のみを選択肢に表示
            holdings = [(symbol, data) for symbol, data in portfolio.items() if data["shares"] > 0]
            
            if not holdings:
                await interaction.response.send_message("📊 売却可能な株式がありません", ephemeral=True)
                return
            
            # 保有銘柄の選択肢作成
            sell_options = []
            for symbol, holding in holdings:
                stock_info = STOCK_DATA[symbol]
                current_price = await get_current_stock_price(symbol)
                market_value = current_price * holding["shares"]
                profit_loss = (current_price - holding["average_cost"]) * holding["shares"]
                
                sell_options.append(
                    discord.SelectOption(
                        label=f"{stock_info['emoji']} {stock_info['name']}",
                        value=symbol,
                        description=f"保有: {holding['shares']:,}株 | 損益: {profit_loss:+.0f}KR"
                    )
                )
            
            class SellSelectView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=60)
                
                @discord.ui.select(
                    placeholder="売却する銘柄を選択してください...",
                    options=sell_options
                )
                async def sell_select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                    selected_symbol = select.values[0]
                    stock_info = STOCK_DATA[selected_symbol]
                    holding = portfolio[selected_symbol]
                    current_price = await get_current_stock_price(selected_symbol)
                    
                    # 売却株数入力モーダル表示
                    class SellSharesModal(discord.ui.Modal):
                        def __init__(self):
                            super().__init__(title=f"{stock_info['name']}の売却")
                        
                        shares_input = discord.ui.TextInput(
                            label=f"売却株数（保有: {holding['shares']:,}株）",
                            placeholder=f"1〜{holding['shares']:,}の範囲で入力してください",
                            required=True,
                            max_length=10
                        )
                        
                        async def on_submit(self, modal_interaction: discord.Interaction):
                            try:
                                shares = int(self.shares_input.value)
                                
                                if shares <= 0:
                                    await modal_interaction.response.send_message("❌ 株数は1以上である必要があります", ephemeral=True)
                                    return
                                
                                if shares > holding["shares"]:
                                    await modal_interaction.response.send_message(f"❌ 保有株数不足\n保有: {holding['shares']}株\n売却希望: {shares}株", ephemeral=True)
                                    return
                                
                                total_value = math.floor(current_price * shares * (1 - MARKET_CONFIG["trading_fee"]))
                                
                                # 取引制限チェック
                                if total_value < MARKET_CONFIG["min_trade_amount"]:
                                    await modal_interaction.response.send_message(f"❌ 最小取引額: {MARKET_CONFIG['min_trade_amount']:,} KR", ephemeral=True)
                                    return
                                
                                # 損益計算
                                avg_cost = holding["average_cost"]
                                profit_loss = (current_price - avg_cost) * shares
                                
                                # 取引実行
                                new_balance = await execute_stock_sale(user_id, selected_symbol, shares, current_price, total_value)
                                
                                embed = discord.Embed(
                                    title="📉 株式売却完了",
                                    description=f"{stock_info['emoji']} {stock_info['name']} を売却しました",
                                    color=discord.Color.orange()
                                )
                                
                                embed.add_field(name="売却株数", value=f"{shares:,}株", inline=True)
                                embed.add_field(name="単価", value=f"{current_price:.2f} KR", inline=True)
                                embed.add_field(name="手数料差引後受取額", value=f"{total_value:,} KR", inline=True)
                                
                                if profit_loss > 0:
                                    embed.add_field(name="損益", value=f"🟢 +{profit_loss:.2f} KR", inline=True)
                                elif profit_loss < 0:
                                    embed.add_field(name="損益", value=f"🔴 {profit_loss:.2f} KR", inline=True)
                                else:
                                    embed.add_field(name="損益", value="⚪ ±0 KR", inline=True)
                                
                                embed.add_field(name="新残高", value=f"{new_balance:,} KR", inline=True)
                                
                                embed.set_footer(text="KRAFT株式市場")
                                await modal_interaction.response.send_message(embed=embed)
                                
                            except ValueError:
                                await modal_interaction.response.send_message("❌ 有効な数値を入力してください", ephemeral=True)
                            except Exception as e:
                                print(f"株式売却エラー: {e}")
                    
                    modal = SellSharesModal()
                    await interaction.response.send_modal(modal)
            
            view = SellSelectView()
            embed = discord.Embed(
                title="📉 株式売却",
                description="売却したい銘柄を選択してください",
                color=discord.Color.orange()
            )
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
    except Exception as e:
        print(f"株式売却コマンドエラー: {e}")

# =====================================
# ポートフォリオ確認コマンド
# =====================================
@bot.tree.command(name="ポートフォリオ", description="あなたの保有株式を確認します")
async def portfolio_cmd(interaction: discord.Interaction):
    print(f"[ポートフォリオ] {interaction.user.name} が実行")
    await interaction.response.defer()
    
    user_id = str(interaction.user.id)
            portfolio = await get_user_portfolio(user_id)
            
            if not portfolio:
                await interaction.followup.send("📊 保有株式はありません")
                return
            
            # ポートフォリオデータ計算
            holdings_data = []
            total_value = 0
            total_cost = 0
            
            for symbol, holding in portfolio.items():
                if holding["shares"] <= 0:
                    continue
                    
                current_price = await get_current_stock_price(symbol)
                market_value = current_price * holding["shares"]
                cost_basis = holding["average_cost"] * holding["shares"]
                profit_loss = market_value - cost_basis
                profit_loss_percent = (profit_loss / cost_basis) * 100 if cost_basis > 0 else 0
                
                total_value += market_value
                total_cost += cost_basis
                
                holdings_data.append({
                    "symbol": symbol,
                    "name": STOCK_DATA[symbol]["name"],
                    "emoji": STOCK_DATA[symbol]["emoji"],
                    "sector": STOCK_DATA[symbol]["sector"],
                    "shares": holding["shares"],
                    "avg_cost": holding["average_cost"],
                    "current_price": current_price,
                    "market_value": market_value,
                    "cost_basis": cost_basis,
                    "profit_loss": profit_loss,
                    "profit_loss_percent": profit_loss_percent,
                    "weight": (market_value / total_value) * 100 if total_value > 0 else 0
                })
            
            # ソート（評価額順）
            holdings_data.sort(key=lambda x: x["market_value"], reverse=True)
            
            # メインEmbed作成
            embed = discord.Embed(
                title=f"📊 {interaction.user.display_name} のポートフォリオ",
                color=discord.Color.blue()
            )
            
            # 保有銘柄情報
            for holding in holdings_data:
                if holding["profit_loss"] > 0:
                    pl_emoji = "🟢"
                elif holding["profit_loss"] < 0:
                    pl_emoji = "🔴"
                else:
                    pl_emoji = "⚪"
                
                # 重み表示用バー
                weight_bar = "█" * int(holding["weight"] / 5) + "░" * (20 - int(holding["weight"] / 5))
                
                embed.add_field(
                    name=f"{holding['emoji']} {holding['name']}",
                    value=f"```\n"
                          f"保有株数: {holding['shares']:,}株\n"
                          f"取得価格: {holding['avg_cost']:.2f} KR\n"
                          f"現在価格: {holding['current_price']:.2f} KR\n"
                          f"評価額: {holding['market_value']:,.0f} KR\n"
                          f"構成比: {holding['weight']:.1f}%\n"
                          f"```"
                          f"{pl_emoji} **{holding['profit_loss']:+.0f} KR** ({holding['profit_loss_percent']:+.1f}%)\n"
                          f"`{weight_bar}` {holding['weight']:.1f}%",
                    inline=True
                )
            
            # ポートフォリオサマリー
            total_profit_loss = total_value - total_cost
            total_profit_loss_percent = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0
            
            # セクター分散度計算
            sector_dist = {}
            for holding in holdings_data:
                sector = holding["sector"]
                if sector in sector_dist:
                    sector_dist[sector] += holding["weight"]
                else:
                    sector_dist[sector] = holding["weight"]
            
            sector_text = "\n".join([f"• {sector}: {weight:.1f}%" for sector, weight in sorted(sector_dist.items(), key=lambda x: x[1], reverse=True)])
            
            # 損益表示
            if total_profit_loss > 0:
                summary_emoji = "📈"
                summary_color = "🟢"
            elif total_profit_loss < 0:
                summary_emoji = "📉" 
                summary_color = "🔴"
            else:
                summary_emoji = "➡️"
                summary_color = "⚪"
            
            embed.add_field(
                name=f"{summary_emoji} ポートフォリオサマリー",
                value=f"```\n"
                      f"総評価額: {total_value:,.0f} KR\n"
                      f"総取得原価: {total_cost:,.0f} KR\n"
                      f"総損益: {total_profit_loss:+.0f} KR\n"
                      f"収益率: {total_profit_loss_percent:+.1f}%\n"
                      f"銘柄数: {len(holdings_data)}社\n"
                      f"```",
                inline=False
            )
            
            embed.add_field(
                name="🏭 セクター分散",
                value=sector_text,
                inline=True
            )
            
            # パフォーマンス評価
            if total_profit_loss_percent > 10:
                performance = "🚀 優秀"
            elif total_profit_loss_percent > 5:
                performance = "📈 良好"
            elif total_profit_loss_percent > 0:
                performance = "✅ プラス"
            elif total_profit_loss_percent > -5:
                performance = "⚠️ 微減"
            elif total_profit_loss_percent > -10:
                performance = "📉 注意"
            else:
                performance = "🔴 要改善"
            
            embed.add_field(
                name="📊 パフォーマンス",
                value=f"{performance}\n{summary_color} {total_profit_loss_percent:+.1f}%",
                inline=True
            )
            
            embed.set_footer(text="KRAFT株式市場 | 構成比グラフ: █ = 5%")
            await interaction.followup.send(embed=embed)

# =====================================
# 投資ランキングコマンド
# =====================================
@bot.tree.command(name="投資ランキング", description="投資収益率ランキングを表示します")
async def investment_ranking_cmd(interaction: discord.Interaction):
    print(f"[投資ランキング] {interaction.user.name} が実行")
    await interaction.response.defer()
    
    # 全ユーザーのポートフォリオ取得
            users_ref = db.collection("users")
            users = users_ref.stream()
            
            rankings = []
            
            for user_doc in users:
                user_id = user_doc.id
                portfolio = await get_user_portfolio(user_id)
                
                if not portfolio:
                    continue
                
                total_value = 0
                total_cost = 0
                
                for symbol, holding in portfolio.items():
                    if holding["shares"] <= 0:
                        continue
                    current_price = await get_current_stock_price(symbol)
                    total_value += current_price * holding["shares"]
                    total_cost += holding["average_cost"] * holding["shares"]
                
                if total_cost > 0:
                    profit_loss = total_value - total_cost
                    profit_loss_percent = (profit_loss / total_cost) * 100
                    
                    rankings.append({
                        "user_id": user_id,
                        "total_value": total_value,
                        "total_cost": total_cost,
                        "profit_loss": profit_loss,
                        "profit_loss_percent": profit_loss_percent
                    })
            
            # 収益率でソート
            rankings.sort(key=lambda x: x["profit_loss_percent"], reverse=True)
            
            embed = discord.Embed(
                title="🏆 投資収益率ランキング TOP10",
                color=discord.Color.gold()
            )
            
            for i, ranking in enumerate(rankings[:10]):
                try:
                    user = bot.get_user(int(ranking["user_id"]))
                    if not user:
                        user = await bot.fetch_user(int(ranking["user_id"]))
                    username = user.display_name if user else "Unknown"
                except:
                    username = "Unknown"
                
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
                
                embed.add_field(
                    name=f"{medal} {username}",
                    value=f"収益率: {ranking['profit_loss_percent']:+.1f}%\n"
                          f"評価額: {ranking['total_value']:,.0f} KR\n"
                          f"損益: {ranking['profit_loss']:+.0f} KR",
                    inline=True
                )
            
            embed.set_footer(text="KRAFT株式市場")
            await interaction.followup.send(embed=embed)
        """Claude APIを使用して市場ニュースを生成"""
        if not anthropic_client:
            return "📈 KRAFT市場が活発な取引を見せています"
        
        try:
            # 現在の株価データを取得
            stock_info = []
            for symbol, data in STOCK_DATA.items():
                current_price = get_current_price(symbol)
                stock_info.append(f"{data['name']}({symbol}): {current_price:.0f}KR - {data['sector']}")
            
            stock_context = "\n".join(stock_info[:6])  # 上位6銘柄のみ
            
            prompt = f"""あなたは日本の架空の株式市場「KRAFT市場」の金融ニュース記者です。

現在の市場状況:
{stock_context}

以下の条件でリアルな市場ニュースを1つ生成してください：

1. 140文字以内の簡潔なニュース
2. 実際の株価に影響を与えそうな内容
3. 具体的な企業名や業界を含める
4. ポジティブ（上昇要因）またはネガティブ（下落要因）のトーンを選択
5. 絵文字を1-2個使用
6. 現実的で信憑性のある内容

ニュースのみを出力してください。説明は不要です。"""

            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            news = response.content[0].text.strip()
            print(f"Claude生成ニュース: {news}")
            return news
            
        except Exception as e:
            print(f"Claude API エラー: {e}")
            # フォールバック
            fallback_news = [
                "📈 KRAFT市場でテクノロジー銘柄が大幅上昇",
                "📊 金融セクターに新たな投資資金流入",
                "💼 自動車業界の決算発表が市場の注目を集める",
                "🔥 エネルギー関連株に買い注文が殺到"
            ]
            return random.choice(fallback_news)
    
    async def apply_news_market_impact(news_content, impact_strength=0.05):
        """ニュース内容に基づいて株価に影響を適用"""
        try:
            if not anthropic_client:
                return
            
            # Claude APIで影響分析
            analysis_prompt = f"""以下のニュースを分析し、どの業界・企業に影響を与えるかJSON形式で回答してください。

ニュース: {news_content}

企業リスト:
- ハードバンク(9984): テクノロジー
- トミタ(7203): 自動車
- USJ銀行(8306): 金融
- ソミー(6758): 電機・精密機器
- ドモコ(9432): 通信
- ナインイレブン(3382): 小売

回答形式:
{{"impacts": [{{"symbol": "9984", "effect": 0.03, "reason": "AI技術への投資期待"}}, ...]}}

効果値は-0.1から0.1の範囲で設定してください。"""

            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            try:
                import json
                analysis = json.loads(response.content[0].text.strip())
                
                # 株価への影響を適用
                for impact in analysis.get("impacts", []):
                    symbol = impact.get("symbol")
                    effect = float(impact.get("effect", 0))
                    reason = impact.get("reason", "市場要因")
                    
                    if symbol in STOCK_DATA and abs(effect) > 0.001:
                        # 現在価格取得
                        current_price = get_current_price(symbol)
                        
                        # 影響を適用
                        price_change = effect * impact_strength * 10  # 影響度調整
                        new_price = current_price * (1 + price_change)
                        
                        # 価格をDBに保存
                        update_stock_price(symbol, new_price)
                        
                        print(f"ニュース影響適用: {STOCK_DATA[symbol]['name']} {current_price:.0f} -> {new_price:.0f} ({price_change*100:+.1f}%) - {reason}")
                        
            except (json.JSONDecodeError, KeyError) as e:
                print(f"ニュース影響分析エラー: {e}")
                # ランダムな市場影響をフォールバック
                affected_stocks = random.sample(list(STOCK_DATA.keys()), k=random.randint(1, 3))
                for symbol in affected_stocks:
                    current_price = get_current_price(symbol)
                    price_change = random.uniform(-impact_strength, impact_strength)
                    new_price = current_price * (1 + price_change)
                    update_stock_price(symbol, new_price)
                    print(f"ランダム市場影響: {STOCK_DATA[symbol]['name']} {price_change*100:+.1f}%")
                
        except Exception as e:
            print(f"市場影響適用エラー: {e}")

# =====================================
# 手動ニュース配信コマンド（管理者専用）
# =====================================
@bot.tree.command(name="市場ニュース配信", description="管理者専用：手動でAI市場ニュースを配信します")
async def manual_news_cmd(interaction: discord.Interaction, ニュース内容: str = None):
    print(f"[市場ニュース配信] {interaction.user.name} が実行")
    await interaction.response.defer(ephemeral=True)
    
    # 管理者確認
        if str(interaction.user.id) not in ADMIN_USER_IDS:
            await interaction.followup.send("このコマンドは管理者のみ使用できます。", ephemeral=True)
            return
        
        # ニュース内容の生成または使用
        if ニュース内容:
            news = ニュース内容
        else:
            # Claude APIでニュース生成
            news = await generate_market_news()
        
        # 市場への影響を適用
        await apply_news_market_impact(news, impact_strength=0.03)
        
        # ニュースチャンネルに配信
        if INVESTMENT_NEWS_CHANNEL_ID:
            channel = bot.get_channel(INVESTMENT_NEWS_CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title="📰 KRAFT市場ニュース",
                    description=news,
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="配信情報", 
                    value=f"管理者: {interaction.user.mention}\n配信時間: {datetime.datetime.now().strftime('%H:%M')}\n🎯 市場への影響が適用されました", 
                    inline=False
                )
                embed.set_footer(text="KRAFT株式市場 • AI生成ニュース")
                await channel.send(embed=embed)
                
                await interaction.followup.send(f"✅ AI市場ニュースを配信し、株価に影響を適用しました。\n\n**配信内容:**\n{news}", ephemeral=True)
                print(f"AI市場ニュース配信: {news}")
            else:
                await interaction.followup.send("❌ 投資ニュースチャンネルが見つかりません。", ephemeral=True)
        else:
            await interaction.followup.send("❌ 投資ニュースチャンネルが設定されていません。", ephemeral=True)

# 株式・銘柄データ（日本企業ベース）
STOCK_DATA = {
    "9984": {
        "name": "ハードバンク",
        "symbol": "9984",
        "sector": "テクノロジー",
        "initial_price": 1200,
        "volatility": 0.06,  # 高ボラティリティ
        "trend": 0.002,
        "description": "通信事業、IT投資、AI開発",
        "dividend": 1.5,
        "emoji": "📱"
    },
    "7203": {
        "name": "トミタ",
        "symbol": "7203",
        "sector": "自動車",
        "initial_price": 2800,
        "volatility": 0.04,
        "trend": 0.001,
        "description": "自動車製造、ハイブリッド、自動運転",
        "dividend": 2.8,
        "emoji": "🚗"
    },
    "8306": {
        "name": "USJ銀行",
        "symbol": "8306",
        "sector": "金融",
        "initial_price": 850,
        "volatility": 0.05,
        "trend": 0.0005,
        "description": "商業銀行、証券、信託銀行",
        "dividend": 4.2,
        "emoji": "🏦"
    },
    "6758": {
        "name": "ソミー",
        "symbol": "6758",
        "sector": "電機・精密機器",
        "initial_price": 1800,
        "volatility": 0.07,
        "trend": 0.003,
        "description": "ゲーム、映画、音楽、半導体",
        "dividend": 1.2,
        "emoji": "🎮"
    },
    "9432": {
        "name": "ドモコ",
        "symbol": "9432",
        "sector": "通信",
        "initial_price": 3200,
        "volatility": 0.02,  # 低ボラティリティ
        "trend": 0.0008,
        "description": "移動通信、5G、データセンター",
        "dividend": 3.8,
        "emoji": "📞"
    },
    "3382": {
        "name": "ナインイレブン",
        "symbol": "3382",
        "sector": "小売",
        "initial_price": 1400,
        "volatility": 0.03,
        "trend": 0.001,
        "description": "コンビニ、百貨店、スーパー",
        "dividend": 2.5,
        "emoji": "🏪"
    },
    "8801": {
        "name": "住不動産",
        "symbol": "8801",
        "sector": "不動産",
        "initial_price": 2600,
        "volatility": 0.04,
        "trend": 0.0005,
        "description": "オフィスビル、商業施設、住宅分譲",
        "dividend": 3.2,
        "emoji": "🏢"
    },
    "4183": {
        "name": "四菱ケミカル",
        "symbol": "4183",
        "sector": "素材・化学",
        "initial_price": 920,
        "volatility": 0.05,
        "trend": 0.0012,
        "description": "基礎化学、石油化学、機能材料",
        "dividend": 3.5,
        "emoji": "🧪"
    },
    "5401": {
        "name": "新目鉄",
        "symbol": "5401",
        "sector": "鉄鋼・重工業",
        "initial_price": 380,
        "volatility": 0.08,  # 高ボラティリティ
        "trend": 0.001,
        "description": "鉄鋼製造、エンジニアリング",
        "dividend": 4.8,
        "emoji": "⚙️"
    },
    "2503": {
        "name": "キリンジ",
        "symbol": "2503",
        "sector": "食品・飲料",
        "initial_price": 1650,
        "volatility": 0.02,  # ディフェンシブ
        "trend": 0.0008,
        "description": "ビール、清涼飲料、医薬品",
        "dividend": 2.8,
        "emoji": "🍺"
    },
    "9501": {
        "name": "東京雷神",
        "symbol": "9501",
        "sector": "電力・ガス",
        "initial_price": 680,
        "volatility": 0.03,
        "trend": 0.0005,
        "description": "電力供給、ガス、再エネ",
        "dividend": 0.0,  # 無配
        "emoji": "⚡"
    },
    "4502": {
        "name": "アステラサズ",
        "symbol": "4502",
        "sector": "医薬品",
        "initial_price": 2200,
        "volatility": 0.06,
        "trend": 0.002,
        "description": "医療用医薬品、ワクチン開発",
        "dividend": 4.5,
        "emoji": "💊"
    }
}

# 市場設定
MARKET_CONFIG = {
    "trading_fee": 0.01,        # 取引手数料 1%
    "min_trade_amount": 100,    # 最小取引額
    "max_trade_amount": 1000000, # 最大取引額
    "daily_trade_limit": 50,    # 1日の取引回数制限
    "market_hours": {           # 市場開場時間（UTC）
        "open": 0,   # 0時開場
        "close": 23  # 23時終了
    }
}

@bot.event
async def on_ready():
    print(f"\n📈 KRAFT株式市場Bot起動: {bot.user}")
    print(f"接続サーバー: {[g.name for g in bot.guilds]}")
    
    # 既存のコマンドを完全にクリア
    print("\n🗑️ 既存コマンドをクリア...")
    bot.tree.clear_commands(guild=None)
    
    # 市場データ初期化
    await initialize_market_data()
    
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
        print("  /株価 - 株価一覧表示")
        print("  /株式購入 [銘柄] [株数] - 株式購入")
        print("  /株式売却 [銘柄] [株数] - 株式売却")
        print("  /ポートフォリオ [ユーザー] - ポートフォリオ確認")
        print("  /投資ランキング - 投資収益率ランキング")
        print("  /市場ニュース配信 [ニュース内容] - 管理者専用")
        
        # バックグラウンドタスク開始
        if not price_update_task.is_running():
            price_update_task.start()
            print("✅ 株価更新タスク開始")
        
        if not market_news_task.is_running():
            market_news_task.start()
            print("✅ 市場ニュースタスク開始")
        
    except Exception as e:
        print(f"❌ コマンド同期失敗: {e}")
        import traceback
        traceback.print_exc()

# =====================================
# ユーティリティ関数
# =====================================

async def initialize_market_data():
    """市場データの初期化"""
    try:
        market_ref = db.collection("market_data")
        
        for symbol, stock_info in STOCK_DATA.items():
            doc_ref = market_ref.document(f"stock_{symbol}")
            doc = doc_ref.get()
            
            if not doc.exists:
                initial_data = {
                    "symbol": symbol,
                    "current_price": stock_info["initial_price"],
                    "daily_change": 0,
                    "daily_change_percent": 0,
                    "daily_volume": 0,
                    "last_updated": firestore.SERVER_TIMESTAMP,
                    "price_history": [stock_info["initial_price"]]
                }
                doc_ref.set(initial_data)
                print(f"初期化: {symbol} = {stock_info['initial_price']} KR")
    
    except Exception as e:
        print(f"市場データ初期化エラー: {e}")

def is_market_open():
    """市場開場時間チェック"""
    now = datetime.datetime.utcnow()
    return MARKET_CONFIG["market_hours"]["open"] <= now.hour <= MARKET_CONFIG["market_hours"]["close"]

async def get_current_stock_price(symbol: str) -> float:
    """現在の株価取得"""
    try:
        market_ref = db.collection("market_data").document(f"stock_{symbol}")
        doc = market_ref.get()
        
        if doc.exists:
            return doc.to_dict().get("current_price", STOCK_DATA[symbol]["initial_price"])
        else:
            return STOCK_DATA[symbol]["initial_price"]
    
    except Exception as e:
        print(f"株価取得エラー ({symbol}): {e}")
        return STOCK_DATA[symbol]["initial_price"]

def get_current_price(symbol: str) -> float:
    """現在の株価取得（同期版）"""
    try:
        market_ref = db.collection("market_data").document(f"stock_{symbol}")
        doc = market_ref.get()
        
        if doc.exists:
            return doc.to_dict().get("current_price", STOCK_DATA[symbol]["initial_price"])
        else:
            return STOCK_DATA[symbol]["initial_price"]
    
    except Exception as e:
        print(f"株価取得エラー ({symbol}): {e}")
        return STOCK_DATA[symbol]["initial_price"]

def update_stock_price(symbol: str, new_price: float):
    """株価を更新"""
    try:
        market_ref = db.collection("market_data").document(f"stock_{symbol}")
        doc = market_ref.get()
        
        update_data = {
            "current_price": new_price,
            "last_updated": firestore.SERVER_TIMESTAMP
        }
        
        if doc.exists:
            # 既存の場合は価格履歴を更新
            existing_data = doc.to_dict()
            price_history = existing_data.get("price_history", [])
            
            # 新しい価格ポイントを追加
            price_history.append({
                "price": new_price,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            
            # 履歴は最新100件まで保持
            if len(price_history) > 100:
                price_history = price_history[-100:]
            
            update_data["price_history"] = price_history
            market_ref.update(update_data)
        else:
            # 新規作成
            update_data.update({
                "symbol": symbol,
                "company_name": STOCK_DATA[symbol]["name"],
                "sector": STOCK_DATA[symbol]["sector"],
                "initial_price": STOCK_DATA[symbol]["initial_price"],
                "price_history": [{
                    "price": new_price,
                    "timestamp": firestore.SERVER_TIMESTAMP
                }]
            })
            market_ref.set(update_data)
        
        print(f"株価更新完了: {symbol} = {new_price:.2f} KR")
    
    except Exception as e:
        print(f"株価更新エラー ({symbol}): {e}")

async def check_daily_trade_limit(user_id: str) -> bool:
    """日次取引制限チェック"""
    try:
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        trades_ref = db.collection("trades").where("user_id", "==", user_id).where("date", "==", today)
        trades = list(trades_ref.stream())
        
        return len(trades) < MARKET_CONFIG["daily_trade_limit"]
    
    except Exception as e:
        print(f"取引制限チェックエラー: {e}")
        return True

async def get_user_portfolio(user_id: str) -> Dict:
    """ユーザーのポートフォリオ取得"""
    try:
        portfolio_ref = db.collection("portfolios").document(user_id)
        doc = portfolio_ref.get()
        
        if doc.exists:
            return doc.to_dict().get("holdings", {})
        else:
            return {}
    
    except Exception as e:
        print(f"ポートフォリオ取得エラー: {e}")
        return {}

async def execute_stock_purchase(user_id: str, symbol: str, shares: int, price: float, total_cost: int):
    """株式購入実行"""
    try:
        # トランザクション開始
        batch = db.batch()
        
        # ユーザー残高減額
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        user_data = user_doc.to_dict()
        new_balance = user_data["balance"] - total_cost
        batch.update(user_ref, {"balance": new_balance})
        
        # ポートフォリオ更新
        portfolio_ref = db.collection("portfolios").document(user_id)
        portfolio_doc = portfolio_ref.get()
        
        if portfolio_doc.exists:
            holdings = portfolio_doc.to_dict().get("holdings", {})
        else:
            holdings = {}
        
        if symbol in holdings:
            # 平均取得価格計算
            existing_shares = holdings[symbol]["shares"]
            existing_cost = holdings[symbol]["average_cost"]
            total_shares = existing_shares + shares
            total_investment = (existing_cost * existing_shares) + (price * shares)
            new_average_cost = total_investment / total_shares
            
            holdings[symbol] = {
                "shares": total_shares,
                "average_cost": new_average_cost
            }
        else:
            holdings[symbol] = {
                "shares": shares,
                "average_cost": price
            }
        
        batch.set(portfolio_ref, {"holdings": holdings}, merge=True)
        
        # 取引ログ
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        trade_data = {
            "user_id": user_id,
            "symbol": symbol,
            "type": "buy",
            "shares": shares,
            "price": price,
            "total_amount": total_cost,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "date": today
        }
        batch.set(db.collection("trades").document(), trade_data)
        
        # 出来高更新
        market_ref = db.collection("market_data").document(f"stock_{symbol}")
        market_doc = market_ref.get()
        if market_doc.exists:
            current_volume = market_doc.to_dict().get("daily_volume", 0)
            batch.update(market_ref, {"daily_volume": current_volume + shares})
        
        # バッチ実行
        batch.commit()
        
    except Exception as e:
        print(f"株式購入実行エラー: {e}")
        raise

async def execute_stock_sale(user_id: str, symbol: str, shares: int, price: float, total_value: int) -> int:
    """株式売却実行"""
    try:
        # トランザクション開始
        batch = db.batch()
        
        # ユーザー残高増額
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        user_data = user_doc.to_dict()
        new_balance = user_data["balance"] + total_value
        batch.update(user_ref, {"balance": new_balance})
        
        # ポートフォリオ更新
        portfolio_ref = db.collection("portfolios").document(user_id)
        portfolio_doc = portfolio_ref.get()
        holdings = portfolio_doc.to_dict().get("holdings", {})
        
        holdings[symbol]["shares"] -= shares
        if holdings[symbol]["shares"] <= 0:
            del holdings[symbol]
        
        batch.set(portfolio_ref, {"holdings": holdings}, merge=True)
        
        # 取引ログ
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        trade_data = {
            "user_id": user_id,
            "symbol": symbol,
            "type": "sell",
            "shares": shares,
            "price": price,
            "total_amount": total_value,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "date": today
        }
        batch.set(db.collection("trades").document(), trade_data)
        
        # 出来高更新
        market_ref = db.collection("market_data").document(f"stock_{symbol}")
        market_doc = market_ref.get()
        if market_doc.exists:
            current_volume = market_doc.to_dict().get("daily_volume", 0)
            batch.update(market_ref, {"daily_volume": current_volume + shares})
        
        # バッチ実行
        batch.commit()
        
        return new_balance
        
    except Exception as e:
        print(f"株式売却実行エラー: {e}")
        raise

# =====================================
# バックグラウンドタスク
# =====================================

@tasks.loop(minutes=30)
async def price_update_task():
    """株価更新タスク（30分間隔）"""
    try:
        market_ref = db.collection("market_data")
        
        for symbol, stock_info in STOCK_DATA.items():
            doc_ref = market_ref.document(f"stock_{symbol}")
            doc = doc_ref.get()
            
            if not doc.exists:
                continue
            
            data = doc.to_dict()
            current_price = data.get("current_price", stock_info["initial_price"])
            
            # 価格変動計算（幾何ブラウン運動）
            dt = 0.5/24  # 30分 = 0.5時間
            random_change = random.normalvariate(0, 1)
            drift = stock_info["trend"] * dt
            volatility_change = stock_info["volatility"] * math.sqrt(dt) * random_change
            
            # 新価格計算
            price_multiplier = math.exp(drift + volatility_change)
            new_price = current_price * price_multiplier
            
            # 最小価格制限（初期価格の10%以下にはならない）
            min_price = stock_info["initial_price"] * 0.1
            new_price = max(new_price, min_price)
            
            # 変動率計算
            daily_change = new_price - current_price
            daily_change_percent = (daily_change / current_price) * 100
            
            # 価格履歴更新（最新50件まで保持）
            price_history = data.get("price_history", [])
            price_history.append(new_price)
            if len(price_history) > 50:
                price_history = price_history[-50:]
            
            # データベース更新
            update_data = {
                "current_price": new_price,
                "daily_change": daily_change,
                "daily_change_percent": daily_change_percent,
                "last_updated": firestore.SERVER_TIMESTAMP,
                "price_history": price_history
            }
            
            doc_ref.update(update_data)
            
            print(f"株価更新: {symbol} = {new_price:.2f} KR ({daily_change_percent:+.2f}%)")
            
    except Exception as e:
        print(f"株価更新エラー: {e}")

@tasks.loop(hours=6)
async def market_news_task():
    """AI市場ニュース・イベントタスク（6時間間隔）"""
    try:
        if random.random() < 0.3:  # 30%の確率でニュース配信
            # Claude APIでニュース生成
            news = await generate_market_news()
            
            # 市場への影響を適用
            await apply_news_market_impact(news, impact_strength=0.02)  # 自動配信は影響度を少し抑える
            
            # ニュースチャンネルに投稿（チャンネルIDが設定されていれば）
            if INVESTMENT_NEWS_CHANNEL_ID:
                channel = bot.get_channel(INVESTMENT_NEWS_CHANNEL_ID)
                if channel:
                    embed = discord.Embed(
                        title="📰 KRAFT市場ニュース",
                        description=news,
                        color=discord.Color.blue()
                    )
                    embed.add_field(
                        name="配信情報",
                        value=f"自動配信 • {datetime.datetime.now().strftime('%H:%M')}\n🎯 市場への影響が適用されました",
                        inline=False
                    )
                    embed.set_footer(text="KRAFT株式市場 • AI生成ニュース")
                    await channel.send(embed=embed)
            
            print(f"AI市場ニュース自動配信: {news}")
    
    except Exception as e:
        print(f"市場ニュースエラー: {e}")

@price_update_task.before_loop
async def before_price_update():
    await bot.wait_until_ready()

@market_news_task.before_loop
async def before_market_news():
    await bot.wait_until_ready()

# エラーハンドリング
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ エラー: {event}")
    import traceback
    traceback.print_exc()

print("\n🚀 KRAFT株式市場Bot起動中...")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ TOKENが設定されていません")
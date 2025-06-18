# shared/kraft_config.py - KRAFT分散Botシステム共通設定
# 責務: 全Bot共通の設定値・定数・チャンネルID管理

import os
from typing import Dict, List, Any
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# =====================================
# Discord設定
# =====================================

# Botトークン
DISCORD_TOKENS = {
    "community": os.getenv("COMMUNITY_BOT_TOKEN"),
    "central_bank": os.getenv("DISCORD_TOKEN_CENTRAL_BANK_BOT"),
    "stock_market": os.getenv("STOCK_MARKET_TOKEN"),
    "title": os.getenv("TITLE_BOT_TOKEN")
}

# チャンネルID設定
CHANNEL_IDS = {
    "level_up_notifications": 1377478794431954954,      # レベルアップ通知
    "title_announcements": 1377478794431954954,        # 称号獲得のお知らせ
    "investment_news": 1378237887446777997,             # 投資ニュース
    "donation_notifications": 1377478794431954954,      # 寄付通知
    "podcast_channel": 1369922415710179399,             # クラフトラジオ
    "general": 1377478794431954954                      # 一般お知らせ
}

# 管理者ユーザーID
ADMIN_USER_IDS = [
    "1249582099825164312",
    "867343308426444801"
]

# =====================================
# Firebase設定
# =====================================

FIREBASE_CONFIG = {
    "credentials_path": "config/firebase_credentials.json",
    "collections": {
        "users": "users",
        "quests": "quests", 
        "companies": "companies",
        "user_investments": "user_investments",
        "stock_transactions": "stock_transactions",
        "market_news": "market_news",
        "price_changes": "price_changes",
        "transactions": "transactions",
        "donation_targets": "donation_targets",
        "donations": "donations",
        "title_events": "title_events"
    }
}

# =====================================
# レベルシステム設定
# =====================================

LEVEL_SYSTEM = {
    "initial_balance": 1000,    # 初期残高
    "initial_titles": ["偉大なる一歩"],  # 初期称号
    
    # XP設定
    "message_base_xp": 10,      # メッセージ基本XP
    "message_length_bonus": 1,   # 15文字ごとのボーナスXP
    "message_length_interval": 15,  # 長文ボーナス間隔
    "message_length_max_bonus": 20,  # 長文ボーナス上限
    "continuous_message_bonus": 20,  # 連続投稿ボーナス
    "continuous_message_threshold": 10,  # 連続投稿閾値
    
    # 日次XP上限
    "daily_xp_caps": {
        "1-10": 1000,
        "11-30": 2000,
        "31-60": 3000,
        "61+": 4000
    },
    
    # クエストXP
    "quest_xp": {
        "weekly": 200,
        "monthly": 600,
        "yearly": 2000,
        "personal": 50
    },
    
    # その他XP
    "donation_xp_rate": 10,     # 100KRごとに10XP
    "transfer_xp_rate": 5,      # 100KRごとに5XP
    
    # レベルアップ報酬
    "level_rewards": {
        "base_formula": "100 * level + 50",  # 基本報酬計算式
        "milestone_rewards": {
            5: 750,
            10: 1500,
            25: 3500,
            50: 7500,
            100: 15000
        }
    }
}

# =====================================
# 経済システム設定
# =====================================

ECONOMIC_SYSTEM = {
    # KR設定
    "initial_balance": 1000,
    
    # 投資設定
    "investment": {
        "transaction_fee_rate": 0.02,  # 2%手数料
        "min_shares": 1,
        "max_shares_per_transaction": 10000,
        "companies": [
            "WICR", "QOOG", "RBLX", "NFOX", "MOSL", 
            "NKDA", "FSCH", "IRHA", "STRK", "ASST"
        ]
    },
    
    # ギャンブル設定
    "gambling": {
        "min_bet": 100,
        "max_bet": 10000,
        "house_edge": 0.05,  # 5%控除率
        "slot_payouts": {
            "💎💎💎": 10,  # ジャックポット
            "⭐⭐⭐": 5,   # 高配当
            "三つ揃い": 3,    # 通常配当
            "二つ揃い": 1.5   # 小配当
        }
    }
}

# =====================================
# 投資企業マスターデータ
# =====================================

COMPANIES_DATA = {
    "WICR": {
        "name": "Wicrosoft",
        "industry": "AI・Bot開発", 
        "initial_price": 85,
        "volatility": 0.02,
        "dividend_yield": 0.015
    },
    "QOOG": {
        "name": "Qoogle",
        "industry": "量子コンピュータ",
        "initial_price": 158,
        "volatility": 0.035,
        "dividend_yield": 0.0
    },
    "RBLX": {
        "name": "Roblux",
        "industry": "ゲーム開発",
        "initial_price": 72,
        "volatility": 0.025,
        "dividend_yield": 0.02
    },
    "NFOX": {
        "name": "Netfox",
        "industry": "動画配信",
        "initial_price": 64,
        "volatility": 0.02,
        "dividend_yield": 0.015
    },
    "MOSL": {
        "name": "Mosla",
        "industry": "再生エネルギー",
        "initial_price": 48,
        "volatility": 0.015,
        "dividend_yield": 0.03
    },
    "NKDA": {
        "name": "Nikuda",
        "industry": "物流・配送",
        "initial_price": 32,
        "volatility": 0.01,
        "dividend_yield": 0.04
    },
    "FSCH": {
        "name": "Firma Schnitzel",
        "industry": "バイオテクノロジー",
        "initial_price": 142,
        "volatility": 0.03,
        "dividend_yield": 0.0
    },
    "IRHA": {
        "name": "Iroha",
        "industry": "医療IT",
        "initial_price": 76,
        "volatility": 0.02,
        "dividend_yield": 0.01
    },
    "STRK": {
        "name": "Strike",
        "industry": "デジタル決済",
        "initial_price": 98,
        "volatility": 0.025,
        "dividend_yield": 0.0
    },
    "ASST": {
        "name": "Assist",
        "industry": "銀行・金融",
        "initial_price": 45,
        "volatility": 0.01,
        "dividend_yield": 0.05
    }
}

# =====================================
# 称号システム設定
# =====================================

TITLE_SYSTEM = {
    # レベル系称号
    "level_titles": {
        1: "偉大なる一歩",
        5: "新人冒険者", 
        10: "冒険者",
        20: "熟練冒険者",
        30: "探求者",
        40: "賢者",
        50: "達人",
        60: "英雄",
        70: "王者",
        80: "守護者",
        90: "仙人",
        100: "生きる伝説"
    },
    
    # アクティビティ系称号条件
    "activity_titles": {
        "よく喋る人": {"condition": "monthly_messages >= 500"},
        "エミネム": {"condition": "monthly_messages >= 1000"},
        "どこにでもいる人": {"condition": "active_channels >= 10"}
    },
    
    # クエスト系称号条件
    "quest_titles": {
        "クエストマスター": {"condition": "completed_quests >= 100"},
        "どんまい": {"condition": "consecutive_quest_failures >= 2"},
        "逆にすごい": {"condition": "consecutive_quest_failures >= 10"}
    },
    
    # 経済系称号条件
    "economic_titles": {
        "寄付マスター": {"condition": "donation_total >= 50000"},
        "聖人": {"condition": "became_zero_by_donation"},
        "投資マスター": {"condition": "investment_profit >= 100000"},
        "ノーリターン": {"condition": "became_zero_by_investment"},
        "ギフトマスター": {"condition": "transfer_total >= 100000"},
        "大盤振る舞い": {"condition": "became_zero_by_transfer"}
    }
}

# =====================================
# ヘルパー関数
# =====================================

def get_channel_id(channel_name: str) -> int:
    """チャンネルIDを取得"""
    return CHANNEL_IDS.get(channel_name)

def is_admin(user_id: str) -> bool:
    """管理者かどうかを判定"""
    return user_id in ADMIN_USER_IDS

def get_company_data(ticker: str) -> Dict[str, Any]:
    """企業データを取得"""
    return COMPANIES_DATA.get(ticker, {})

def get_level_reward(level: int) -> int:
    """レベルアップ報酬を計算"""
    # マイルストーン報酬の確認
    if level in LEVEL_SYSTEM["level_rewards"]["milestone_rewards"]:
        return LEVEL_SYSTEM["level_rewards"]["milestone_rewards"][level]
    
    # 基本報酬の計算
    return eval(LEVEL_SYSTEM["level_rewards"]["base_formula"], {"level": level})

def get_quest_reward(quest_type: str) -> Dict[str, int]:
    """クエスト報酬を取得"""
    return {
        "xp": LEVEL_SYSTEM["quest_xp"].get(quest_type, 0),
        "kr": 0  # 必要に応じてKR報酬も設定可能
    }

def get_daily_xp_cap(level: int) -> int:
    """日次XP上限を取得"""
    for level_range, cap in LEVEL_SYSTEM["daily_xp_caps"].items():
        start, end = map(int, level_range.split("-"))
        if start <= level <= end:
            return cap
    return LEVEL_SYSTEM["daily_xp_caps"]["61+"]  # デフォルト値 
# KRAFT経済システム パラメータ設定ファイル
# 全Bot完成後のバランス調整用設定

from typing import Dict, Any
import json
import os
from datetime import datetime

class EconomicSettings:
    """
    KRAFT経済システムの全パラメータを管理するクラス
    運用データに基づいて動的に調整可能
    """
    
    # ===========================================
    # XPシステム設定
    # ===========================================
    XP_SETTINGS = {
        # メッセージXP
        "message_xp": 5,                    # メッセージあたりのXP
        "message_cooldown": 60,             # XP獲得クールダウン(秒)
        
        # レベルアップ計算
        "level_base_xp": 100,               # レベル1→2に必要なXP
        "level_multiplier": 1.5,            # レベルアップ係数
        
        # クエストXP
        "quest_xp_per_day": 10,             # 1日あたりのクエストXP
        "quest_completion_bonus": 0,        # クエスト完了ボーナスXP
        
        # 寄付XP交換レート
        "donation_xp_rate": 0.1,            # 1KRあたりのXP (1KR=0.1XP)
    }
    
    # ===========================================
    # KR報酬システム設定
    # ===========================================
    KR_REWARDS = {
        # 初期設定
        "initial_balance": 1000,            # 新規ユーザー初期残高
        
        # レベルアップ報酬
        "levelup_kr_multiplier": 500,       # レベル×500KR
        "levelup_kr_base": 0,               # 固定ボーナス
        
        # クエスト報酬
        "quest_kr_base": 0,                 # 基本KR報酬
        "quest_kr_per_day": 0,              # 日数ボーナス
        
        # その他報酬
        "daily_login_bonus": 0,             # 日次ログインボーナス
        "weekly_bonus": 0,                  # 週次ボーナス
    }
    
    # ===========================================
    # 取引制限設定
    # ===========================================
    TRANSACTION_LIMITS = {
        # 送金制限
        "min_transfer": 1,                  # 最小送金額
        "max_transfer": 1000000,            # 最大送金額
        "daily_transfer_limit": 50,         # 日次送金回数制限
        
        # 寄付制限
        "min_donation": 100,                # 最小寄付額
        "max_donation": 100000,             # 最大寄付額
        
        # 取引頻度制限
        "transaction_window": 300,          # 制限時間枠(秒) - 5分
        "max_transactions_per_window": 8,   # 時間枠内最大取引数
    }
    
    # ===========================================
    # ギャンブル・スロット設定
    # ===========================================
    GAMBLING_SETTINGS = {
        # スロット設定
        "slot_min_bet": 100,                # 最小ベット額
        "slot_max_bet": 10000,              # 最大ベット額
        "slot_house_edge": 0.05,            # 控除率 (5%)
        
        # 配当設定
        "slot_payouts": {
            "💎💎💎": 10.0,                  # ダイヤ3つ揃い
            "⭐⭐⭐": 5.0,                   # スター3つ揃い
            "🍎🍎🍎": 3.0,                   # その他3つ揃い
            "🍊🍊🍊": 3.0,
            "🍇🍇🍇": 3.0,
            "🔔🔔🔔": 3.0,
            "🍀🍀🍀": 3.0,
            "two_match": 1.5,               # 2つ揃い
        }
    }
    
    # ===========================================
    # 投資・株式市場設定
    # ===========================================
    INVESTMENT_SETTINGS = {
        # 取引手数料
        "trading_fee_rate": 0.01,           # 取引手数料 (1%)
        
        # 取引制限
        "min_investment": 100,              # 最小投資額
        "max_investment": 1000000,          # 最大投資額
        "daily_trade_limit": 50,            # 日次取引回数制限
        
        # 市場開場時間
        "market_open_hour": 0,              # 開場時刻 (UTC)
        "market_close_hour": 23,            # 閉場時刻 (UTC)
        
        # 価格変動設定
        "price_update_interval": 30,        # 価格更新間隔(分)
        "min_price_ratio": 0.1,             # 最低価格(初期価格の10%)
        
        # ニュース配信
        "news_interval_hours": 6,           # ニュース配信間隔
        "news_probability": 0.3,            # ニュース配信確率(30%)
    }
    
    # ===========================================
    # 称号システム設定
    # ===========================================
    TITLE_SETTINGS = {
        # チェック間隔
        "title_check_interval": 5,          # 称号チェック間隔(分)
        "title_batch_size": 10,             # 一度に処理する称号数
        
        # 月次リセット
        "monthly_reset_hour": 0,            # 月次リセット時刻
        
        # 通知設定
        "notification_delay": 1,            # 通知間隔(秒)
    }
    
    # ===========================================
    # バランス調整履歴
    # ===========================================
    BALANCE_HISTORY = []
    
    @classmethod
    def load_from_file(cls, file_path: str = "config/economic_settings.json"):
        """設定ファイルから読み込み"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 各設定を更新
                if 'XP_SETTINGS' in data:
                    cls.XP_SETTINGS.update(data['XP_SETTINGS'])
                if 'KR_REWARDS' in data:
                    cls.KR_REWARDS.update(data['KR_REWARDS'])
                if 'TRANSACTION_LIMITS' in data:
                    cls.TRANSACTION_LIMITS.update(data['TRANSACTION_LIMITS'])
                if 'GAMBLING_SETTINGS' in data:
                    cls.GAMBLING_SETTINGS.update(data['GAMBLING_SETTINGS'])
                if 'INVESTMENT_SETTINGS' in data:
                    cls.INVESTMENT_SETTINGS.update(data['INVESTMENT_SETTINGS'])
                if 'TITLE_SETTINGS' in data:
                    cls.TITLE_SETTINGS.update(data['TITLE_SETTINGS'])
                if 'BALANCE_HISTORY' in data:
                    cls.BALANCE_HISTORY = data['BALANCE_HISTORY']
                    
                print(f"✅ 経済設定を読み込みました: {file_path}")
                
        except Exception as e:
            print(f"⚠️ 設定ファイル読み込みエラー: {e}")
            print("デフォルト設定を使用します")
    
    @classmethod
    def save_to_file(cls, file_path: str = "config/economic_settings.json"):
        """設定ファイルに保存"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            data = {
                "XP_SETTINGS": cls.XP_SETTINGS,
                "KR_REWARDS": cls.KR_REWARDS,
                "TRANSACTION_LIMITS": cls.TRANSACTION_LIMITS,
                "GAMBLING_SETTINGS": cls.GAMBLING_SETTINGS,
                "INVESTMENT_SETTINGS": cls.INVESTMENT_SETTINGS,
                "TITLE_SETTINGS": cls.TITLE_SETTINGS,
                "BALANCE_HISTORY": cls.BALANCE_HISTORY,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"✅ 経済設定を保存しました: {file_path}")
            
        except Exception as e:
            print(f"❌ 設定ファイル保存エラー: {e}")
    
    @classmethod
    def adjust_parameters(cls, adjustments: Dict[str, Any], reason: str = ""):
        """パラメータ調整とログ記録"""
        
        # 調整前の値を記録
        backup = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "changes": {},
            "previous_values": {}
        }
        
        # 調整実行
        for category, params in adjustments.items():
            if hasattr(cls, category):
                category_dict = getattr(cls, category)
                backup["changes"][category] = params
                backup["previous_values"][category] = {}
                
                for key, new_value in params.items():
                    if key in category_dict:
                        backup["previous_values"][category][key] = category_dict[key]
                        category_dict[key] = new_value
                        print(f"📊 {category}.{key}: {backup['previous_values'][category][key]} → {new_value}")
        
        # 履歴に追加
        cls.BALANCE_HISTORY.append(backup)
        
        # 自動保存
        cls.save_to_file()
    
    @classmethod
    def get_economic_stats(cls) -> Dict[str, Any]:
        """現在の経済設定統計"""
        return {
            "レベルアップ報酬": f"{cls.KR_REWARDS['levelup_kr_multiplier']} KR/レベル",
            "メッセージXP": f"{cls.XP_SETTINGS['message_xp']} XP/メッセージ",
            "寄付XP交換": f"1 KR = {cls.XP_SETTINGS['donation_xp_rate']} XP",
            "投資手数料": f"{cls.INVESTMENT_SETTINGS['trading_fee_rate']*100}%",
            "スロット控除率": f"{cls.GAMBLING_SETTINGS['slot_house_edge']*100}%",
            "調整履歴": len(cls.BALANCE_HISTORY)
        }

# ===========================================
# 使用例・調整シナリオ
# ===========================================

def example_balance_adjustments():
    """バランス調整の使用例"""
    
    # シナリオ1: インフレ対策
    inflation_control = {
        "KR_REWARDS": {
            "levelup_kr_multiplier": 400,  # 500→400に減額
        },
        "XP_SETTINGS": {
            "message_xp": 4,              # 5→4に減額
        }
    }
    
    # シナリオ2: 投資活性化
    investment_boost = {
        "INVESTMENT_SETTINGS": {
            "trading_fee_rate": 0.005,     # 1%→0.5%に減額
            "min_investment": 50,          # 100→50に減額
        }
    }
    
    # シナリオ3: ギャンブル規制強化
    gambling_restriction = {
        "GAMBLING_SETTINGS": {
            "slot_house_edge": 0.08,       # 5%→8%に増加
            "slot_max_bet": 5000,          # 10000→5000に減額
        }
    }
    
    return {
        "inflation_control": inflation_control,
        "investment_boost": investment_boost, 
        "gambling_restriction": gambling_restriction
    }

# ===========================================
# 初期化
# ===========================================

if __name__ == "__main__":
    # 設定ファイルから読み込み
    EconomicSettings.load_from_file()
    
    # 現在の設定表示
    print("\n📊 現在の経済設定:")
    stats = EconomicSettings.get_economic_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 調整例の表示
    print("\n🔧 調整シナリオ例:")
    scenarios = example_balance_adjustments()
    for scenario_name, adjustments in scenarios.items():
        print(f"\n  {scenario_name}:")
        for category, params in adjustments.items():
            for param, value in params.items():
                print(f"    {category}.{param} = {value}")
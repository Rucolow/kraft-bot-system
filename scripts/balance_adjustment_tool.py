#!/usr/bin/env python3
"""
KRAFT経済バランス調整ツール
運用データに基づいて経済パラメータを動的に調整するためのツール
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.economic_settings import EconomicSettings
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any
import statistics

class BalanceAnalyzer:
    """経済データ分析クラス"""
    
    def __init__(self):
        # Firebase初期化
        if not firebase_admin._apps:
            cred = credentials.Certificate("config/firebase_credentials.json")
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
    
    def analyze_kr_flow(self, days: int = 7) -> Dict[str, Any]:
        """KR流入・流出分析"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 取引履歴取得
        transactions_ref = self.db.collection("transactions")
        transactions = transactions_ref.where("timestamp", ">=", cutoff_date).stream()
        
        inflow = {"levelup": 0, "other": 0}
        outflow = {"transfer": 0, "donation": 0, "slot": 0, "investment": 0}
        
        for transaction in transactions:
            data = transaction.to_dict()
            amount = data.get("amount", 0)
            transaction_type = data.get("transaction_type", "")
            
            if amount > 0:  # 流入
                if transaction_type == "levelup":
                    inflow["levelup"] += amount
                else:
                    inflow["other"] += amount
            else:  # 流出
                amount = abs(amount)
                if transaction_type in outflow:
                    outflow[transaction_type] += amount
        
        total_inflow = sum(inflow.values())
        total_outflow = sum(outflow.values())
        
        return {
            "period_days": days,
            "inflow": inflow,
            "outflow": outflow,
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "net_flow": total_inflow - total_outflow,
            "flow_ratio": total_outflow / total_inflow if total_inflow > 0 else 0
        }
    
    def analyze_user_behavior(self) -> Dict[str, Any]:
        """ユーザー行動パターン分析"""
        users_ref = self.db.collection("users")
        users = users_ref.stream()
        
        balances = []
        levels = []
        active_users = 0
        total_users = 0
        
        for user in users:
            data = user.to_dict()
            total_users += 1
            
            balance = data.get("balance", 0)
            level = data.get("level", 1)
            last_message = data.get("last_message_xp")
            
            balances.append(balance)
            levels.append(level)
            
            # 過去7日以内にアクティブ
            if last_message:
                try:
                    if isinstance(last_message, str):
                        last_date = datetime.fromisoformat(last_message)
                    else:
                        last_date = last_message
                    
                    if (datetime.now() - last_date).days <= 7:
                        active_users += 1
                except:
                    pass
        
        if balances:
            balance_stats = {
                "average": statistics.mean(balances),
                "median": statistics.median(balances),
                "min": min(balances),
                "max": max(balances),
                "std_dev": statistics.stdev(balances) if len(balances) > 1 else 0
            }
        else:
            balance_stats = {"average": 0, "median": 0, "min": 0, "max": 0, "std_dev": 0}
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "activity_rate": active_users / total_users if total_users > 0 else 0,
            "balance_stats": balance_stats,
            "average_level": statistics.mean(levels) if levels else 0,
            "max_level": max(levels) if levels else 0
        }
    
    def analyze_investment_activity(self) -> Dict[str, Any]:
        """投資活動分析"""
        trades_ref = self.db.collection("trades")
        trades = trades_ref.stream()
        
        total_trades = 0
        total_volume = 0
        buy_trades = 0
        sell_trades = 0
        total_fees = 0
        
        for trade in trades:
            data = trade.to_dict()
            total_trades += 1
            
            action = data.get("action", "")
            total_amount = data.get("total_amount", 0)
            fee = data.get("fee", 0)
            
            total_volume += total_amount
            total_fees += fee
            
            if action == "buy":
                buy_trades += 1
            elif action == "sell":
                sell_trades += 1
        
        return {
            "total_trades": total_trades,
            "total_volume": total_volume,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "buy_sell_ratio": buy_trades / sell_trades if sell_trades > 0 else float('inf'),
            "total_fees_collected": total_fees,
            "average_trade_size": total_volume / total_trades if total_trades > 0 else 0
        }

class BalanceRecommendationEngine:
    """バランス調整推奨エンジン"""
    
    def __init__(self, analyzer: BalanceAnalyzer):
        self.analyzer = analyzer
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """調整推奨事項を生成"""
        recommendations = []
        
        # データ分析
        kr_flow = self.analyzer.analyze_kr_flow()
        user_behavior = self.analyzer.analyze_user_behavior()
        investment_activity = self.analyzer.analyze_investment_activity()
        
        # インフレ・デフレ判定
        if kr_flow["net_flow"] > 0:
            inflation_risk = kr_flow["net_flow"] / kr_flow["total_inflow"]
            if inflation_risk > 0.2:  # 20%以上の純流入
                recommendations.append({
                    "type": "inflation_control",
                    "priority": "high",
                    "reason": f"KR純流入が{inflation_risk:.1%}でインフレリスク",
                    "adjustments": {
                        "KR_REWARDS": {
                            "levelup_kr_multiplier": int(EconomicSettings.KR_REWARDS["levelup_kr_multiplier"] * 0.9)
                        },
                        "XP_SETTINGS": {
                            "message_xp": max(3, EconomicSettings.XP_SETTINGS["message_xp"] - 1)
                        }
                    }
                })
        
        elif kr_flow["net_flow"] < -kr_flow["total_inflow"] * 0.1:  # 10%以上の純流出
            recommendations.append({
                "type": "deflation_control",
                "priority": "medium", 
                "reason": "KR純流出でデフレリスク",
                "adjustments": {
                    "KR_REWARDS": {
                        "levelup_kr_multiplier": int(EconomicSettings.KR_REWARDS["levelup_kr_multiplier"] * 1.1)
                    }
                }
            })
        
        # 投資活動分析
        if investment_activity["total_trades"] > 0:
            if investment_activity["buy_sell_ratio"] > 2:  # 買いが売りの2倍以上
                recommendations.append({
                    "type": "investment_cooling",
                    "priority": "low",
                    "reason": "投資過熱気味",
                    "adjustments": {
                        "INVESTMENT_SETTINGS": {
                            "trading_fee_rate": min(0.02, EconomicSettings.INVESTMENT_SETTINGS["trading_fee_rate"] * 1.2)
                        }
                    }
                })
            elif investment_activity["buy_sell_ratio"] < 0.5:  # 売りが買いの2倍以上
                recommendations.append({
                    "type": "investment_boost",
                    "priority": "medium",
                    "reason": "投資活動低迷",
                    "adjustments": {
                        "INVESTMENT_SETTINGS": {
                            "trading_fee_rate": max(0.005, EconomicSettings.INVESTMENT_SETTINGS["trading_fee_rate"] * 0.8)
                        }
                    }
                })
        
        # ユーザーアクティビティ分析
        if user_behavior["activity_rate"] < 0.3:  # 30%未満のアクティブ率
            recommendations.append({
                "type": "activity_boost",
                "priority": "high",
                "reason": f"アクティブ率{user_behavior['activity_rate']:.1%}で低迷",
                "adjustments": {
                    "XP_SETTINGS": {
                        "message_xp": min(10, EconomicSettings.XP_SETTINGS["message_xp"] + 1)
                    },
                    "KR_REWARDS": {
                        "daily_login_bonus": 100  # デイリーボーナス導入
                    }
                }
            })
        
        return recommendations

def main():
    """メイン実行関数"""
    print("🔍 KRAFT経済バランス分析・調整ツール")
    print("=" * 50)
    
    # 設定読み込み
    EconomicSettings.load_from_file()
    
    # アナライザー初期化
    analyzer = BalanceAnalyzer()
    
    try:
        # データ分析実行
        print("\n📊 経済データ分析中...")
        kr_flow = analyzer.analyze_kr_flow()
        user_behavior = analyzer.analyze_user_behavior()
        investment_activity = analyzer.analyze_investment_activity()
        
        # 結果表示
        print(f"\n💰 KR流入・流出分析 (過去{kr_flow['period_days']}日間):")
        print(f"  総流入: {kr_flow['total_inflow']:,} KR")
        print(f"  総流出: {kr_flow['total_outflow']:,} KR")
        print(f"  純流量: {kr_flow['net_flow']:,} KR")
        print(f"  流出率: {kr_flow['flow_ratio']:.1%}")
        
        print(f"\n👥 ユーザー行動分析:")
        print(f"  総ユーザー数: {user_behavior['total_users']:,}人")
        print(f"  アクティブユーザー: {user_behavior['active_users']:,}人")
        print(f"  アクティブ率: {user_behavior['activity_rate']:.1%}")
        print(f"  平均残高: {user_behavior['balance_stats']['average']:,.0f} KR")
        print(f"  平均レベル: {user_behavior['average_level']:.1f}")
        
        print(f"\n📈 投資活動分析:")
        print(f"  総取引数: {investment_activity['total_trades']:,}件")
        print(f"  総取引量: {investment_activity['total_volume']:,} KR")
        print(f"  買い/売り比: {investment_activity['buy_sell_ratio']:.2f}")
        print(f"  手数料収入: {investment_activity['total_fees_collected']:,} KR")
        
        # 推奨事項生成
        print(f"\n🔧 バランス調整推奨事項:")
        engine = BalanceRecommendationEngine(analyzer)
        recommendations = engine.generate_recommendations()
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                print(f"\n  {i}. {priority_emoji.get(rec['priority'], '⚪')} {rec['type']}")
                print(f"     理由: {rec['reason']}")
                print(f"     調整内容:")
                for category, params in rec['adjustments'].items():
                    for key, value in params.items():
                        current = getattr(EconomicSettings, category)[key]
                        print(f"       {category}.{key}: {current} → {value}")
        else:
            print("  📊 現在のバランスは適切です")
        
        # 実行確認
        if recommendations:
            print(f"\n❓ 推奨調整を実行しますか? (y/N): ", end="")
            if input().lower() == 'y':
                for rec in recommendations:
                    EconomicSettings.adjust_parameters(
                        rec['adjustments'], 
                        f"自動調整: {rec['reason']}"
                    )
                print("✅ 調整を実行しました")
            else:
                print("⏸️ 調整をスキップしました")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
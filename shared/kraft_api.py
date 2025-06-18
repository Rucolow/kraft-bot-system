# shared/kraft_api.py - Bot間通信用共通APIライブラリ
# 責務: Bot間での統一されたAPI通信インターフェース提供

import aiohttp
import firebase_admin
from firebase_admin import firestore
import logging
from typing import Optional, Dict, Any, List
import datetime

# ロギング設定
logger = logging.getLogger(__name__)

class KraftAPI:
    """Bot間通信用統一APIクラス"""
    
    def __init__(self, db_client=None):
        """
        初期化
        Args:
            db_client: Firestoreクライアント（オプション）
        """
        self.db = db_client or firestore.client()
    
    # =====================================
    # 中央銀行API（KR管理）
    # =====================================
    
    @staticmethod
    async def add_kr(user_id: str, amount: int, reason: str) -> bool:
        """
        中央銀行にKR追加を依頼
        Args:
            user_id: ユーザーID
            amount: 追加するKR
            reason: 追加理由
        Returns:
            bool: 成功時True
        """
        try:
            db = firestore.client()
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                current_balance = user_doc.to_dict().get("balance", 0)
                user_ref.update({"balance": current_balance + amount})
            else:
                # 新規ユーザー初期化
                user_ref.set({
                    "balance": 1000 + amount,
                    "level": 1,
                    "xp": 0,
                    "titles": ["偉大なる一歩"],
                    "created_at": datetime.datetime.utcnow().isoformat()
                })
            
            # 取引ログ記録
            await KraftAPI.log_transaction(user_id, "add_kr", amount, reason=reason)
            
            logger.info(f"KR付与成功: {user_id} +{amount}KR ({reason})")
            return True
            
        except Exception as e:
            logger.error(f"KR付与エラー: {e}")
            return False
    
    @staticmethod
    async def subtract_kr(user_id: str, amount: int, reason: str) -> bool:
        """
        中央銀行にKR減額を依頼
        Args:
            user_id: ユーザーID
            amount: 減額するKR
            reason: 減額理由
        Returns:
            bool: 成功時True
        """
        try:
            db = firestore.client()
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                logger.warning(f"KR減額失敗: ユーザーが存在しません ({user_id})")
                return False
            
            current_balance = user_doc.to_dict().get("balance", 0)
            if current_balance < amount:
                logger.warning(f"KR減額失敗: 残高不足 ({user_id}, {current_balance} < {amount})")
                return False
            
            user_ref.update({"balance": current_balance - amount})
            
            # 取引ログ記録
            await KraftAPI.log_transaction(user_id, "subtract_kr", amount, reason=reason)
            
            logger.info(f"KR減額成功: {user_id} -{amount}KR ({reason})")
            return True
            
        except Exception as e:
            logger.error(f"KR減額エラー: {e}")
            return False
    
    @staticmethod
    async def get_balance(user_id: str) -> int:
        """
        残高照会（新規ユーザー自動初期化）
        Args:
            user_id: ユーザーID
        Returns:
            int: 現在の残高
        """
        try:
            db = firestore.client()
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict().get("balance", 0)
            else:
                # 新規ユーザーの初期化
                user_data = {
                    "user_id": user_id,
                    "balance": 1000,  # 初期残高
                    "level": 1,
                    "xp": 0,
                    "total_donated": 0,
                    "total_transferred": 0,
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                user_ref.set(user_data)
                logger.info(f"新規ユーザー初期化: {user_id}")
                return 1000
            
        except Exception as e:
            logger.error(f"残高照会エラー: {e}")
            return 0
    
    @staticmethod
    async def log_transaction(user_id: str, transaction_type: str, amount: int, 
                            target_user: str = None, reason: str = "") -> bool:
        """
        取引ログ記録
        Args:
            user_id: ユーザーID
            transaction_type: 取引タイプ
            amount: 金額
            target_user: 送金先ユーザー（送金時）
            reason: 取引理由
        Returns:
            bool: 成功時True
        """
        try:
            db = firestore.client()
            transaction_data = {
                "user_id": user_id,
                "type": transaction_type,
                "amount": amount,
                "target_user": target_user,
                "reason": reason,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            db.collection("transactions").add(transaction_data)
            return True
            
        except Exception as e:
            logger.error(f"取引ログ記録エラー: {e}")
            return False
    
    # =====================================
    # レベルシステムAPI（XP管理）
    # =====================================
    
    @staticmethod
    async def add_xp(user_id: str, xp_amount: int, reason: str, is_exempt: bool = False) -> Dict[str, Any]:
        """
        XP追加とレベルアップチェック
        Args:
            user_id: ユーザーID
            xp_amount: 追加するXP
            reason: 追加理由
            is_exempt: 日次上限対象外フラグ
        Returns:
            Dict: レベルアップ情報
        """
        try:
            db = firestore.client()
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                # 新規ユーザー初期化
                user_data = {
                    "level": 1,
                    "xp": xp_amount,
                    "titles": ["偉大なる一歩"],
                    "created_at": datetime.datetime.utcnow().isoformat()
                }
                user_ref.set(user_data)
                return {
                    "level_up": False,
                    "new_level": 1,
                    "old_level": 1,
                    "kr_reward": 0,
                    "new_titles": []
                }
            
            user_data = user_doc.to_dict()
            current_level = user_data.get("level", 1)
            current_xp = user_data.get("xp", 0)
            
            # 日次XP上限チェック
            if not is_exempt:
                daily_xp = user_data.get("daily_xp", 0)
                daily_xp_cap = 1000  # 基本上限
                if current_level > 10:
                    daily_xp_cap = 2000
                if current_level > 30:
                    daily_xp_cap = 3000
                if current_level > 60:
                    daily_xp_cap = 4000
                
                if daily_xp >= daily_xp_cap:
                    logger.info(f"日次XP上限到達: {user_id}")
                    return {
                        "level_up": False,
                        "new_level": current_level,
                        "old_level": current_level,
                        "kr_reward": 0,
                        "new_titles": []
                    }
                
                # 日次XP更新
                user_ref.update({"daily_xp": daily_xp + xp_amount})
            
            # XP追加
            new_xp = current_xp + xp_amount
            new_level = current_level
            
            # レベルアップ判定
            while new_xp >= new_level * 100:
                new_xp -= new_level * 100
                new_level += 1
            
            # レベルアップ報酬計算
            kr_reward = 0
            if new_level > current_level:
                kr_reward = new_level * 1000
            
            # ユーザーデータ更新
            user_ref.update({
                "level": new_level,
                "xp": new_xp
            })
            
            # レベルアップ報酬のKR付与
            if kr_reward > 0:
                await KraftAPI.add_kr(user_id, kr_reward, f"level_up_{new_level}")
            
            return {
                "level_up": new_level > current_level,
                "new_level": new_level,
                "old_level": current_level,
                "kr_reward": kr_reward,
                "new_titles": []
            }
            
        except Exception as e:
            logger.error(f"XP追加エラー: {e}")
            return {
                "level_up": False,
                "new_level": 1,
                "old_level": 1,
                "kr_reward": 0,
                "new_titles": []
            }
    
    @staticmethod
    async def get_level_info(user_id: str) -> Dict[str, Any]:
        """
        レベル情報取得
        Args:
            user_id: ユーザーID
        Returns:
            Dict: レベル情報
        """
        try:
            db = firestore.client()
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return {
                    "level": user_data.get("level", 1),
                    "xp": user_data.get("xp", 0),
                    "titles": user_data.get("titles", ["偉大なる一歩"]),
                    "balance": user_data.get("balance", 0),
                    "daily_xp": user_data.get("daily_xp", 0)
                }
            else:
                return {
                    "level": 1,
                    "xp": 0,
                    "titles": ["偉大なる一歩"],
                    "balance": 0,
                    "daily_xp": 0
                }
                
        except Exception as e:
            logger.error(f"レベル情報取得エラー: {e}")
            return {"level": 1, "xp": 0, "titles": [], "balance": 0, "daily_xp": 0}
    
    # =====================================
    # 称号システムAPI
    # =====================================
    
    @staticmethod
    async def log_title_event(user_id: str, event_type: str, data: Dict[str, Any]) -> bool:
        """
        称号Botにイベント通知
        Args:
            user_id: ユーザーID
            event_type: イベントタイプ
            data: イベントデータ
        Returns:
            bool: 成功時True
        """
        try:
            db = firestore.client()
            event_data = {
                "user_id": user_id,
                "type": event_type,
                "data": data,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            db.collection("title_events").add(event_data)
            return True
            
        except Exception as e:
            logger.error(f"称号イベント記録エラー: {e}")
            return False
    
    @staticmethod
    async def check_user_titles(user_id: str) -> List[str]:
        """
        ユーザーの称号をチェック
        Args:
            user_id: ユーザーID
        Returns:
            List[str]: 新しく獲得した称号のリスト
        """
        try:
            db = firestore.client()
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return []
            
            user_data = user_doc.to_dict()
            current_titles = set(user_data.get("titles", ["偉大なる一歩"]))
            new_titles = []
            
            # レベル系称号チェック
            level = user_data.get("level", 1)
            if level >= 5 and "新人冒険者" not in current_titles:
                new_titles.append("新人冒険者")
            if level >= 10 and "冒険者" not in current_titles:
                new_titles.append("冒険者")
            if level >= 20 and "熟練冒険者" not in current_titles:
                new_titles.append("熟練冒険者")
            if level >= 30 and "探求者" not in current_titles:
                new_titles.append("探求者")
            if level >= 40 and "賢者" not in current_titles:
                new_titles.append("賢者")
            if level >= 50 and "達人" not in current_titles:
                new_titles.append("達人")
            if level >= 60 and "英雄" not in current_titles:
                new_titles.append("英雄")
            if level >= 70 and "王者" not in current_titles:
                new_titles.append("王者")
            if level >= 80 and "守護者" not in current_titles:
                new_titles.append("守護者")
            if level >= 90 and "仙人" not in current_titles:
                new_titles.append("仙人")
            if level >= 100 and "生きる伝説" not in current_titles:
                new_titles.append("生きる伝説")
            
            # 新称号がある場合、ユーザーデータを更新
            if new_titles:
                user_ref.update({
                    "titles": list(current_titles.union(new_titles))
                })
            
            return new_titles
            
        except Exception as e:
            logger.error(f"称号チェックエラー: {e}")
            return []
    
    # =====================================
    # 投資システムAPI
    # =====================================
    
    @staticmethod
    async def get_stock_price(ticker: str) -> Optional[int]:
        """
        現在の株価取得
        Args:
            ticker: 企業ティッカー
        Returns:
            Optional[int]: 現在の株価（存在しない場合はNone）
        """
        try:
            db = firestore.client()
            company_ref = db.collection("companies").document(ticker)
            company_doc = company_ref.get()
            
            if company_doc.exists:
                return company_doc.to_dict().get("current_price")
            return None
            
        except Exception as e:
            logger.error(f"株価取得エラー: {e}")
            return None
    
    @staticmethod
    async def get_user_portfolio(user_id: str) -> Dict[str, Any]:
        """
        ユーザーの投資ポートフォリオ取得
        Args:
            user_id: ユーザーID
        Returns:
            Dict: ポートフォリオ情報
        """
        try:
            db = firestore.client()
            portfolio_ref = db.collection("user_investments").document(user_id)
            portfolio_doc = portfolio_ref.get()
            
            if portfolio_doc.exists:
                return portfolio_doc.to_dict()
            return {}
            
        except Exception as e:
            logger.error(f"ポートフォリオ取得エラー: {e}")
            return {}
    
    @staticmethod
    async def log_investment_transaction(user_id: str, transaction_type: str, ticker: str, 
                                       shares: int, price: int, fee: int) -> bool:
        """
        投資取引ログ記録
        Args:
            user_id: ユーザーID
            transaction_type: 取引タイプ（buy/sell）
            ticker: 企業ティッカー
            shares: 取引株数
            price: 取引価格
            fee: 手数料
        Returns:
            bool: 成功時True
        """
        try:
            db = firestore.client()
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
            return True
            
        except Exception as e:
            logger.error(f"投資取引ログ記録エラー: {e}")
            return False
    
    # =====================================
    # クエストシステムAPI
    # =====================================
    
    @staticmethod
    async def create_quest(user_id: str, quest_type: str, deadline: str, 
                          description: str, reward: Dict[str, int]) -> bool:
        """
        クエスト作成
        Args:
            user_id: ユーザーID
            quest_type: クエストタイプ
            deadline: 期限（YYYY-MM-DD）
            description: クエスト説明
            reward: 報酬（xp, kr）
        Returns:
            bool: 成功時True
        """
        try:
            db = firestore.client()
            quest_data = {
                "user_id": user_id,
                "type": quest_type,
                "deadline": deadline,
                "description": description,
                "reward": reward,
                "status": "active",
                "created_at": datetime.datetime.utcnow().isoformat()
            }
            db.collection("quests").add(quest_data)
            return True
            
        except Exception as e:
            logger.error(f"クエスト作成エラー: {e}")
            return False
    
    @staticmethod
    async def complete_quest(quest_id: str) -> Dict[str, Any]:
        """
        クエスト完了処理
        Args:
            quest_id: クエストID
        Returns:
            Dict: 報酬情報
        """
        try:
            db = firestore.client()
            quest_ref = db.collection("quests").document(quest_id)
            quest_doc = quest_ref.get()
            
            if not quest_doc.exists:
                return {"success": False, "error": "クエストが存在しません"}
            
            quest_data = quest_doc.to_dict()
            if quest_data["status"] != "active":
                return {"success": False, "error": "クエストは既に完了しています"}
            
            # 期限チェック
            deadline = datetime.datetime.strptime(quest_data["deadline"], "%Y-%m-%d")
            if datetime.datetime.utcnow() > deadline:
                return {"success": False, "error": "クエストの期限が切れています"}
            
            # 報酬付与
            reward = quest_data["reward"]
            user_id = quest_data["user_id"]
            
            if "xp" in reward:
                await KraftAPI.add_xp(user_id, reward["xp"], f"quest_{quest_id}")
            if "kr" in reward:
                await KraftAPI.add_kr(user_id, reward["kr"], f"quest_{quest_id}")
            
            # クエスト状態更新
            quest_ref.update({"status": "completed"})
            
            return {
                "success": True,
                "reward": reward
            }
            
        except Exception as e:
            logger.error(f"クエスト完了エラー: {e}")
            return {"success": False, "error": str(e)}
    
    # =====================================
    # ユーティリティ
    # =====================================
    
    @staticmethod
    async def get_user_data(user_id: str) -> Dict[str, Any]:
        """
        ユーザーデータ取得（ポートフォリオ評価額含む）
        Args:
            user_id: ユーザーID
        Returns:
            Dict: ユーザーデータ
        """
        try:
            db = firestore.client()
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {
                    "level": 1,
                    "xp": 0,
                    "titles": ["偉大なる一歩"],
                    "balance": 0,
                    "portfolio_value": 0
                }
            
            user_data = user_doc.to_dict()
            
            # ポートフォリオ評価額計算
            portfolio = await KraftAPI.get_user_portfolio(user_id)
            portfolio_value = 0
            
            for ticker, shares in portfolio.items():
                price = await KraftAPI.get_stock_price(ticker)
                if price:
                    portfolio_value += price * shares
            
            user_data["portfolio_value"] = portfolio_value
            return user_data
            
        except Exception as e:
            logger.error(f"ユーザーデータ取得エラー: {e}")
            return {
                "level": 1,
                "xp": 0,
                "titles": ["偉大なる一歩"],
                "balance": 0,
                "portfolio_value": 0
            }
    
    @staticmethod
    async def initialize_user(user_id: str, username: str = "") -> bool:
        """
        新規ユーザー初期化
        Args:
            user_id: ユーザーID
            username: ユーザー名（オプション）
        Returns:
            bool: 成功時True
        """
        try:
            db = firestore.client()
            user_ref = db.collection("users").document(user_id)
            
            user_data = {
                "level": 1,
                "xp": 0,
                "titles": ["偉大なる一歩"],
                "balance": 1000,
                "daily_xp": 0,
                "created_at": datetime.datetime.utcnow().isoformat()
            }
            
            if username:
                user_data["username"] = username
            
            user_ref.set(user_data)
            return True
            
        except Exception as e:
            logger.error(f"ユーザー初期化エラー: {e}")
            return False

# 便利関数エイリアス
add_kr = KraftAPI.add_kr
subtract_kr = KraftAPI.subtract_kr
get_balance = KraftAPI.get_balance
add_xp = KraftAPI.add_xp
get_level_info = KraftAPI.get_level_info
log_title_event = KraftAPI.log_title_event
check_user_titles = KraftAPI.check_user_titles
get_stock_price = KraftAPI.get_stock_price
get_user_portfolio = KraftAPI.get_user_portfolio
log_investment_transaction = KraftAPI.log_investment_transaction
create_quest = KraftAPI.create_quest
complete_quest = KraftAPI.complete_quest
get_user_data = KraftAPI.get_user_data
initialize_user = KraftAPI.initialize_user 
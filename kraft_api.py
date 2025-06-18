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
        残高照会
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
            return 0
            
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
            # level_system.py の add_xp_and_check_level_up を呼び出し
            # 実装は既存コードを参照
            level_up, new_level, old_level, kr_reward, new_titles = await add_xp_and_check_level_up(
                user_id, xp_amount, is_exempt
            )
            
            # レベルアップ報酬のKR付与
            if kr_reward > 0:
                await KraftAPI.add_kr(user_id, kr_reward, f"level_up_{new_level}")
            
            return {
                "level_up": level_up,
                "new_level": new_level,
                "old_level": old_level,
                "kr_reward": kr_reward,
                "new_titles": new_titles
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
                    "balance": user_data.get("balance", 0)
                }
            else:
                return {
                    "level": 1,
                    "xp": 0,
                    "titles": ["偉大なる一歩"],
                    "balance": 0
                }
                
        except Exception as e:
            logger.error(f"レベル情報取得エラー: {e}")
            return {"level": 1, "xp": 0, "titles": [], "balance": 0}
    
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
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            db.collection("title_events").add(event_data)
            return True
        except Exception as e:
            logger.error(f"称号イベントログ記録エラー: {e}")
            return False
    
    @staticmethod
    async def check_user_titles(user_id: str) -> List[str]:
        """
        ユーザーの称号条件をチェックし、取得した称号を返す
        Args:
            user_id: ユーザーID
        Returns:
            List[str]: 新たに獲得した称号のリスト
        """
        try:
            user_data = await KraftAPI.get_user_data(user_id)
            if not user_data:
                return []
            
            # ここで称号条件を評価するロジックを実装
            # 例: level_titles, activity_titles, economic_titles
            
            # 仮のロジック: 全ての称号条件がTITLE_SYSTEMに定義されていると仮定
            new_titles = []
            current_titles = user_data.get("titles", [])
            
            for title_type, titles_map in TITLE_SYSTEM.items():
                for title_name, condition_data in titles_map.items():
                    if title_name not in current_titles:
                        condition_met = True
                        # 条件評価ロジックをここに実装
                        # 例: eval(condition_data["condition"], {}, {"level": user_data["level"], ...})
                        
                        if condition_met:
                            new_titles.append(title_name)
                            # Firebaseに新しい称号を追加
                            user_ref = firestore.client().collection("users").document(user_id)
                            user_ref.update({"titles": firestore.ArrayUnion([title_name])})
                            logger.info(f"ユーザー {user_id} が称号 '{title_name}' を獲得しました")
            
            return new_titles

        except Exception as e:
            logger.error(f"ユーザー称号チェックエラー: {e}")
            return []
    
    # =====================================
    # 投資システムAPI
    # =====================================
    
    @staticmethod
    async def get_stock_price(ticker: str) -> Optional[int]:
        """
        指定された銘柄の現在の株価を取得
        Args:
            ticker: 銘柄
        Returns:
            Optional[int]: 株価（存在しない場合はNone）
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
        ユーザーのポートフォリオを取得
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
            transaction_type: 取引タイプ (buy/sell)
            ticker: 銘柄
            shares: 株数
            price: 単価
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
    # ユーティリティ関数
    # =====================================
    
    @staticmethod
    async def get_user_data(user_id: str) -> Dict[str, Any]:
        """
        ユーザーデータを取得し、存在しない場合は初期化
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
                # ユーザーが存在しない場合、初期化してデフォルトデータで返す
                logger.info(f"新規ユーザー初期化: {user_id}")
                await KraftAPI.initialize_user(user_id)
                user_doc = user_ref.get() # 初期化後のデータを再取得

            user_data = user_doc.to_dict()
            
            # ポートフォリオ評価額を動的に計算して追加
            portfolio = await KraftAPI.get_user_portfolio(user_id)
            total_investment_value = 0
            for ticker, shares in portfolio.items():
                if ticker in COMPANIES_DATA: # COMPANIES_DATA は kraft_config からインポートされることを想定
                    price = await KraftAPI.get_stock_price(ticker)
                    if price is not None:
                        total_investment_value += shares * price
            user_data["total_investment_value"] = total_investment_value

            return user_data

        except Exception as e:
            logger.error(f"ユーザーデータ取得エラー: {e}")
            return {}
    
    @staticmethod
    async def initialize_user(user_id: str, username: str = "") -> bool:
        """
        新規ユーザーを初期化
        Args:
            user_id: 初期化するユーザーのID
            username: ユーザー名（オプション）
        Returns:
            bool: 成功時True
        """
        try:
            db = firestore.client()
            user_ref = db.collection("users").document(user_id)
            
            initial_data = {
                "balance": ECONOMIC_SYSTEM["initial_balance"],
                "level": 1,
                "xp": 0,
                "titles": LEVEL_SYSTEM["initial_titles"],
                "created_at": datetime.datetime.utcnow().isoformat(),
                "username": username
            }
            user_ref.set(initial_data)
            return True
        except Exception as e:
            logger.error(f"ユーザー初期化エラー: {e}")
            return False

# 便利な関数のエイリアス
add_kr = KraftAPI.add_kr
subtract_kr = KraftAPI.subtract_kr
get_balance = KraftAPI.get_balance
add_xp = KraftAPI.add_xp
get_level_info = KraftAPI.get_level_info
log_title_event = KraftAPI.log_title_event
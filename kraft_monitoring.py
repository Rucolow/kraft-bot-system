# kraft_monitoring.py - KRAFT分散Botシステム監視・通知機能
# 責務: エラー通知、バックアップ、監視システムの実装

import discord
import logging
import asyncio
import datetime
import psutil
import os
from typing import Dict, List, Any, Optional
from collections import deque
import firebase_admin
from firebase_admin import firestore
import json
import shutil
from kraft_config import ERROR_NOTIFICATION, BACKUP_CONFIG, MONITORING_CONFIG

# ロギング設定
logger = logging.getLogger(__name__)

class ErrorNotifier:
    """エラー通知管理クラス"""
    
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.error_counts = deque(maxlen=ERROR_NOTIFICATION["notification_threshold"]["error_count"])
        self.last_notification = datetime.datetime.min
        self.notification_channel = None
    
    async def initialize(self):
        """通知チャンネルの初期化"""
        self.notification_channel = await self.bot.fetch_channel(
            ERROR_NOTIFICATION["channel_id"]
        )
    
    async def notify_error(self, error: Exception, context: str = ""):
        """
        エラー通知を送信
        Args:
            error: 発生したエラー
            context: エラーのコンテキスト情報
        """
        now = datetime.datetime.utcnow()
        self.error_counts.append(now)
        
        # クールダウン期間中は通知しない
        if (now - self.last_notification).total_seconds() < ERROR_NOTIFICATION["notification_threshold"]["cooldown"]:
            return
        
        # エラー数が閾値を超えた場合のみ通知
        if len(self.error_counts) >= ERROR_NOTIFICATION["notification_threshold"]["error_count"]:
            time_window = (now - self.error_counts[0]).total_seconds()
            if time_window <= ERROR_NOTIFICATION["notification_threshold"]["time_window"]:
                embed = discord.Embed(
                    title="⚠️ エラー通知",
                    description=f"短時間で多数のエラーが発生しています",
                    color=discord.Color.red(),
                    timestamp=now
                )
                embed.add_field(name="エラー内容", value=str(error))
                embed.add_field(name="コンテキスト", value=context)
                embed.add_field(name="発生回数", value=str(len(self.error_counts)))
                embed.add_field(name="時間枠", value=f"{time_window:.1f}秒")
                
                await self.notification_channel.send(embed=embed)
                self.last_notification = now

class BackupManager:
    """バックアップ管理クラス"""
    
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.db = firestore.client()
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    async def backup_firebase(self):
        """Firebaseデータのバックアップ"""
        if not BACKUP_CONFIG["firebase"]["enabled"]:
            return
        
        try:
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_data = {}
            
            # 各コレクションのバックアップ
            for collection in BACKUP_CONFIG["firebase"]["collections"]:
                docs = self.db.collection(collection).stream()
                backup_data[collection] = [doc.to_dict() for doc in docs]
            
            # バックアップファイルの保存
            backup_file = os.path.join(self.backup_dir, f"firebase_backup_{timestamp}.json")
            with open(backup_file, "w") as f:
                json.dump(backup_data, f, indent=2)
            
            # 古いバックアップの削除
            self._cleanup_old_backups("firebase_backup_", BACKUP_CONFIG["firebase"]["retention_days"])
            
            logger.info(f"Firebaseバックアップ完了: {backup_file}")
            
        except Exception as e:
            logger.error(f"Firebaseバックアップエラー: {e}")
    
    async def backup_bot_config(self):
        """Bot設定のバックアップ"""
        if not BACKUP_CONFIG["bot_config"]["enabled"]:
            return
        
        try:
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            config_files = ["kraft_config.py", ".env"]
            
            for file in config_files:
                if os.path.exists(file):
                    backup_file = os.path.join(self.backup_dir, f"{file}_{timestamp}")
                    shutil.copy2(file, backup_file)
            
            # 古いバックアップの削除
            self._cleanup_old_backups("kraft_config.py_", BACKUP_CONFIG["bot_config"]["retention_weeks"] * 7)
            self._cleanup_old_backups(".env_", BACKUP_CONFIG["bot_config"]["retention_weeks"] * 7)
            
            logger.info("Bot設定バックアップ完了")
            
        except Exception as e:
            logger.error(f"Bot設定バックアップエラー: {e}")
    
    def _cleanup_old_backups(self, prefix: str, retention_days: int):
        """古いバックアップファイルの削除"""
        try:
            cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=retention_days)
            for file in os.listdir(self.backup_dir):
                if file.startswith(prefix):
                    file_path = os.path.join(self.backup_dir, file)
                    file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < cutoff:
                        os.remove(file_path)
                        logger.info(f"古いバックアップを削除: {file}")
        except Exception as e:
            logger.error(f"バックアップクリーンアップエラー: {e}")

class SystemMonitor:
    """システム監視クラス"""
    
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.notification_channel = None
        self.last_check = datetime.datetime.utcnow()
        self.consecutive_errors = 0
        self.error_count = 0
        self.total_requests = 0
    
    async def initialize(self):
        """通知チャンネルの初期化"""
        self.notification_channel = await self.bot.fetch_channel(
            MONITORING_CONFIG["bot_status"]["notification_channel"]
        )
    
    async def check_system_health(self):
        """システム健全性チェック"""
        try:
            # メモリ使用量チェック
            memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            if memory > MONITORING_CONFIG["performance"]["memory_threshold"]:
                await self._send_alert("メモリ使用量警告", f"メモリ使用量: {memory:.1f}MB")
            
            # CPU使用率チェック
            cpu_percent = psutil.cpu_percent()
            if cpu_percent > MONITORING_CONFIG["performance"]["cpu_threshold"]:
                await self._send_alert("CPU使用率警告", f"CPU使用率: {cpu_percent}%")
            
            # エラー率チェック
            if self.total_requests > 0:
                error_rate = self.error_count / self.total_requests
                if error_rate > MONITORING_CONFIG["alerts"]["error_rate_threshold"]:
                    await self._send_alert("エラー率警告", f"エラー率: {error_rate:.1%}")
            
            # 連続エラー数チェック
            if self.consecutive_errors >= MONITORING_CONFIG["alerts"]["consecutive_errors"]:
                await self._send_alert("連続エラー警告", f"連続エラー数: {self.consecutive_errors}")
            
            self.last_check = datetime.datetime.utcnow()
            
        except Exception as e:
            logger.error(f"システム健全性チェックエラー: {e}")
    
    async def _send_alert(self, title: str, description: str):
        """アラート通知を送信"""
        try:
            embed = discord.Embed(
                title=f"⚠️ {title}",
                description=description,
                color=discord.Color.orange(),
                timestamp=datetime.datetime.utcnow()
            )
            await self.notification_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"アラート通知エラー: {e}")
    
    def log_request(self, success: bool):
        """リクエスト結果を記録"""
        self.total_requests += 1
        if not success:
            self.error_count += 1
            self.consecutive_errors += 1
        else:
            self.consecutive_errors = 0 
#!/usr/bin/env python3
"""
Health monitoring script for KRAFT Bot System
"""

import asyncio
import discord
import json
import logging
import os
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('HealthMonitor')

class HealthMonitor:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
        self.bot_processes = {
            'kraft_central_bank': None,
            'kraft_community': None,
            'kraft_title': None,
            'kraft_stock_market': None
        }
        self.last_health_check = datetime.now()
        self.health_history = []
        
    async def check_bot_process(self, bot_name: str) -> Dict:
        """Check if bot process is running"""
        try:
            # Check for Python process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['cmdline'] and f"{bot_name}.py" in ' '.join(proc.info['cmdline']):
                    return {
                        'status': 'running',
                        'pid': proc.info['pid'],
                        'memory_mb': proc.memory_info().rss / 1024 / 1024,
                        'cpu_percent': proc.cpu_percent()
                    }
            
            # Check systemd service
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', f'kraft-{bot_name.replace("_", "-")}'],
                    capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout.strip() == 'active':
                    return {'status': 'systemd_active', 'service': f'kraft-{bot_name.replace("_", "-")}'}
            except Exception:
                pass
            
            return {'status': 'not_running'}
            
        except Exception as e:
            logger.error(f"Error checking {bot_name}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def check_discord_connectivity(self) -> bool:
        """Check Discord API connectivity"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://discord.com/api/v10/gateway') as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Discord connectivity check failed: {e}")
            return False
    
    async def check_system_resources(self) -> Dict:
        """Check system resources"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': os.getloadavg()[0] if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {'error': str(e)}
    
    async def perform_health_check(self) -> Dict:
        """Perform comprehensive health check"""
        logger.info("Starting health check...")
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'bots': {},
            'system': await self.check_system_resources(),
            'discord_connectivity': await self.check_discord_connectivity(),
            'overall_status': 'healthy'
        }
        
        # Check each bot
        failed_bots = []
        for bot_name in self.bot_processes.keys():
            bot_status = await self.check_bot_process(bot_name)
            health_report['bots'][bot_name] = bot_status
            
            if bot_status['status'] not in ['running', 'systemd_active']:
                failed_bots.append(bot_name)
        
        # Determine overall status
        if failed_bots:
            health_report['overall_status'] = 'degraded' if len(failed_bots) < len(self.bot_processes) else 'critical'
            health_report['failed_bots'] = failed_bots
        
        if not health_report['discord_connectivity']:
            health_report['overall_status'] = 'critical'
        
        # Store in history
        self.health_history.append(health_report)
        if len(self.health_history) > 100:  # Keep last 100 checks
            self.health_history.pop(0)
        
        logger.info(f"Health check completed: {health_report['overall_status']}")
        return health_report
    
    async def send_alert(self, health_report: Dict):
        """Send alert to Discord webhook"""
        if not self.webhook_url:
            return
        
        try:
            status = health_report['overall_status']
            color = {
                'healthy': 0x00FF00,
                'degraded': 0xFFFF00,
                'critical': 0xFF0000
            }.get(status, 0x808080)
            
            embed = {
                'title': f'🏥 KRAFT Bot System Health Check',
                'color': color,
                'timestamp': health_report['timestamp'],
                'fields': []
            }
            
            # Overall status
            embed['fields'].append({
                'name': 'Overall Status',
                'value': f'🔴 {status.upper()}' if status == 'critical' else f'🟡 {status.upper()}' if status == 'degraded' else f'🟢 {status.upper()}',
                'inline': True
            })
            
            # Bot statuses
            bot_status_text = ""
            for bot_name, bot_info in health_report['bots'].items():
                status_emoji = "🟢" if bot_info['status'] in ['running', 'systemd_active'] else "🔴"
                bot_status_text += f"{status_emoji} {bot_name}\n"
            
            embed['fields'].append({
                'name': 'Bot Status',
                'value': bot_status_text,
                'inline': True
            })
            
            # System resources
            system = health_report['system']
            if 'error' not in system:
                embed['fields'].append({
                    'name': 'System Resources',
                    'value': f"CPU: {system.get('cpu_percent', 'N/A')}%\nMemory: {system.get('memory_percent', 'N/A')}%\nDisk: {system.get('disk_percent', 'N/A')}%",
                    'inline': True
                })
            
            # Discord connectivity
            embed['fields'].append({
                'name': 'Discord API',
                'value': '🟢 Connected' if health_report['discord_connectivity'] else '🔴 Disconnected',
                'inline': True
            })
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                await session.post(self.webhook_url, json={'embeds': [embed]})
                
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def save_health_report(self, health_report: Dict):
        """Save health report to file"""
        try:
            os.makedirs('logs/health', exist_ok=True)
            filename = f"logs/health/health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w') as f:
                json.dump(health_report, f, indent=2)
                
            # Clean up old files (keep last 7 days)
            cutoff_time = time.time() - (7 * 24 * 60 * 60)
            for file in os.listdir('logs/health'):
                if file.startswith('health_') and file.endswith('.json'):
                    file_path = os.path.join('logs/health', file)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        
        except Exception as e:
            logger.error(f"Failed to save health report: {e}")
    
    async def run_health_check(self):
        """Run a single health check cycle"""
        health_report = await self.perform_health_check()
        
        # Send alert if status is not healthy
        if health_report['overall_status'] != 'healthy':
            await self.send_alert(health_report)
        
        # Save report
        await self.save_health_report(health_report)
        
        return health_report
    
    async def continuous_monitoring(self, interval_minutes: int = 5):
        """Run continuous health monitoring"""
        logger.info(f"Starting continuous monitoring (interval: {interval_minutes} minutes)")
        
        while True:
            try:
                await self.run_health_check()
                await asyncio.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

async def main():
    import argparse
    parser = argparse.ArgumentParser(description='KRAFT Bot System Health Monitor')
    parser.add_argument('--webhook', help='Discord webhook URL for alerts')
    parser.add_argument('--interval', type=int, default=5, help='Check interval in minutes')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    
    args = parser.parse_args()
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    monitor = HealthMonitor(webhook_url=args.webhook)
    
    if args.once:
        health_report = await monitor.run_health_check()
        print(json.dumps(health_report, indent=2))
    else:
        await monitor.continuous_monitoring(args.interval)

if __name__ == "__main__":
    asyncio.run(main())
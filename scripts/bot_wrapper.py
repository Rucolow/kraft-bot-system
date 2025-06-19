#!/usr/bin/env python3
"""
Bot wrapper script with automatic restart capability
"""

import sys
import os
import time
import subprocess
import logging
from datetime import datetime
import signal
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'logs/wrapper_{os.path.basename(sys.argv[1]).replace(".py", "")}.log')
    ]
)
logger = logging.getLogger('BotWrapper')

class BotWrapper:
    def __init__(self, bot_script):
        self.bot_script = bot_script
        self.bot_name = os.path.basename(bot_script).replace('.py', '')
        self.process = None
        self.restart_count = 0
        self.max_restarts = 10
        self.restart_cooldown = 10  # seconds
        self.running = True
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
        
    def handle_signal(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                logger.warning("Process didn't terminate, killing...")
                self.process.kill()
        sys.exit(0)
    
    def start_bot(self):
        """Start the bot process"""
        logger.info(f"Starting {self.bot_name}...")
        try:
            self.process = subprocess.Popen(
                [sys.executable, self.bot_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            logger.info(f"{self.bot_name} started with PID {self.process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start {self.bot_name}: {e}")
            return False
    
    def monitor_bot(self):
        """Monitor the bot process and restart if needed"""
        while self.running:
            if self.process is None:
                if not self.start_bot():
                    time.sleep(self.restart_cooldown)
                    continue
            
            # Check if process is still running
            poll_result = self.process.poll()
            
            if poll_result is not None:
                # Process has terminated
                logger.warning(f"{self.bot_name} exited with code {poll_result}")
                
                # Read any remaining output
                stdout, stderr = self.process.communicate()
                if stdout:
                    logger.info(f"Last stdout: {stdout[-1000:]}")
                if stderr:
                    logger.error(f"Last stderr: {stderr[-1000:]}")
                
                # Check restart limit
                if self.restart_count >= self.max_restarts:
                    logger.error(f"Maximum restart limit ({self.max_restarts}) reached")
                    self.running = False
                    break
                
                # Restart the bot
                self.restart_count += 1
                logger.info(f"Restarting {self.bot_name} (attempt {self.restart_count}/{self.max_restarts})...")
                time.sleep(self.restart_cooldown)
                
                if not self.start_bot():
                    logger.error(f"Failed to restart {self.bot_name}")
                    time.sleep(self.restart_cooldown * 2)
            else:
                # Process is still running, read output
                try:
                    # Non-blocking read from stdout
                    if self.process.stdout:
                        line = self.process.stdout.readline()
                        if line:
                            logger.info(f"[{self.bot_name}] {line.strip()}")
                except Exception as e:
                    logger.debug(f"Error reading output: {e}")
                
                # Reset restart count on successful run
                if self.restart_count > 0:
                    # If bot has been running for more than 5 minutes, reset counter
                    time.sleep(1)
                    if self.process.poll() is None:
                        self.restart_count = max(0, self.restart_count - 0.01)
            
            time.sleep(0.1)  # Small delay to prevent CPU spinning
    
    def run(self):
        """Main run loop"""
        logger.info(f"Bot wrapper for {self.bot_name} started")
        try:
            self.monitor_bot()
        except Exception as e:
            logger.error(f"Unexpected error in wrapper: {e}")
            logger.error(traceback.format_exc())
        finally:
            logger.info(f"Bot wrapper for {self.bot_name} stopped")

def main():
    if len(sys.argv) != 2:
        print("Usage: python bot_wrapper.py <bot_script.py>")
        sys.exit(1)
    
    bot_script = sys.argv[1]
    if not os.path.exists(bot_script):
        print(f"Error: Bot script '{bot_script}' not found")
        sys.exit(1)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    wrapper = BotWrapper(bot_script)
    wrapper.run()

if __name__ == "__main__":
    main()
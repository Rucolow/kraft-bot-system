#!/bin/bash

echo "=== VPS Bot Environment Check ==="
echo ""

echo "1. Checking for systemd services:"
echo "--------------------------------"
systemctl list-units --type=service | grep -E "(kraft|bot)" || echo "No kraft/bot services found"
echo ""

echo "2. Checking for PM2 processes:"
echo "------------------------------"
which pm2 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    pm2 list
else
    echo "PM2 not installed"
fi
echo ""

echo "3. Checking for Python processes:"
echo "---------------------------------"
ps aux | grep -E "python.*kraft.*\.py" | grep -v grep || echo "No kraft python processes found"
echo ""

echo "4. Checking for screen/tmux sessions:"
echo "------------------------------------"
screen -ls 2>/dev/null | grep -E "(kraft|bot)" || echo "No screen sessions found"
tmux ls 2>/dev/null | grep -E "(kraft|bot)" || echo "No tmux sessions found"
echo ""

echo "5. Checking crontab:"
echo "-------------------"
crontab -l 2>/dev/null | grep -E "(kraft|bot)" || echo "No cron jobs found"
echo ""

echo "6. Checking supervisor:"
echo "----------------------"
which supervisord > /dev/null 2>&1
if [ $? -eq 0 ]; then
    supervisorctl status 2>/dev/null | grep -E "(kraft|bot)" || echo "No supervisor processes found"
else
    echo "Supervisor not installed"
fi
echo ""

echo "7. Current directory structure:"
echo "------------------------------"
pwd
ls -la
echo ""

echo "8. Checking for .env file:"
echo "-------------------------"
if [ -f .env ]; then
    echo ".env file exists"
else
    echo ".env file NOT found"
fi
echo ""

echo "9. Checking Git repository:"
echo "--------------------------"
git remote -v 2>/dev/null || echo "Not a git repository"
git branch 2>/dev/null || echo "Cannot check branches"
echo ""

echo "10. Checking for deployment scripts:"
echo "-----------------------------------"
find . -maxdepth 2 -name "*.sh" -type f | grep -E "(deploy|update|start|restart)" || echo "No deployment scripts found"
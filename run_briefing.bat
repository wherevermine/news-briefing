@echo off
cd /d "%~dp0"
echo [%date% %time%] 뉴스 브리핑 시작 >> logs\scheduler.log
python main.py --now >> logs\scheduler.log 2>&1
echo [%date% %time%] 완료 >> logs\scheduler.log

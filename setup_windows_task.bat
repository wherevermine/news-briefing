@echo off
REM Windows 작업 스케줄러에 매일 오전 6시 자동 실행 등록
REM 관리자 권한으로 실행하세요

set TASK_NAME=NewsBriefingBot
set SCRIPT_PATH=%~dp0run_briefing.bat

echo 작업 스케줄러 등록 중...
schtasks /create /tn "%TASK_NAME%" /tr "\"%SCRIPT_PATH%\"" /sc DAILY /st 06:00 /f /rl HIGHEST

if %ERRORLEVEL% == 0 (
    echo 성공! 매일 오전 6시에 자동 실행됩니다.
    echo 등록된 작업 확인:
    schtasks /query /tn "%TASK_NAME%"
) else (
    echo 실패. 관리자 권한으로 다시 실행해주세요.
)
pause

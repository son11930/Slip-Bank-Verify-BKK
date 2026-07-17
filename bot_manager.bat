@echo off
chcp 65001 >nul
setlocal

:: ==========================================================
:: Slip Verify Bot - Remote SSH Manager (Windows Batch)
:: Server: son11930@136.116.178.123
:: Path  : /home/son11930/Slip-Bank-Verify-BKK
:: Tool  : screen (Session name: bot)
:: ==========================================================

set SSH_HOST=son11930@136.116.178.123
set BOT_PATH=/home/son11930/Slip-Bank-Verify-BKK
set SCREEN_NAME=bot

:MENU
cls
echo ==============================================================
echo           SLIP VERIFY BOT - REMOTE MANAGER
echo ==============================================================
echo   Server : %SSH_HOST%
echo   Path   : %BOT_PATH%
echo   Screen : %SCREEN_NAME%
echo ==============================================================
echo.
echo   [1] Start + Update (Git Pull - Pip Install - Start Bot)
echo   [2] Stop Bot
echo   [3] Update Only (Git Pull + Pip Install without restart)
echo   [4] Restart + Update (Stop - Git Pull - Pip Install - Start)
echo   [5] Quick Restart (Stop - Start immediately without pull)
echo   [6] View Live Logs / Attach Screen (Press Ctrl+A then D to exit)
echo   [7] View Recent Screen Output (Snapshot / Snapshot Logs)
echo   [8] Check Status (Online/Offline + CPU/Memory)
echo   [9] Open SSH Terminal (cd to Bot directory)
echo   [0] Exit
echo.
echo ==============================================================
set /p CHOICE="Select option [0-9]: "

if "%CHOICE%"=="1" goto START_UPDATE
if "%CHOICE%"=="2" goto STOP_BOT
if "%CHOICE%"=="3" goto UPDATE_ONLY
if "%CHOICE%"=="4" goto RESTART_UPDATE
if "%CHOICE%"=="5" goto QUICK_RESTART
if "%CHOICE%"=="6" goto ATTACH_LOG
if "%CHOICE%"=="7" goto VIEW_LOG_SNAPSHOT
if "%CHOICE%"=="8" goto CHECK_STATUS
if "%CHOICE%"=="9" goto OPEN_TERMINAL
if "%CHOICE%"=="0" goto EXIT
goto MENU

:START_UPDATE
cls
echo [INFO] Starting Bot with Git Pull ^& Dependency Update...
echo --------------------------------------------------------------
ssh %SSH_HOST% "cd %BOT_PATH%; echo '[1/3] Pulling latest code from Git...'; git pull; echo '[2/3] Checking and updating Python dependencies...'; venv/bin/pip install -r requirements.txt -q; echo '[3/3] Starting screen session (%SCREEN_NAME%)...'; screen -dmS %SCREEN_NAME% bash -c 'cd %BOT_PATH% && source venv/bin/activate && python3 main.py'; echo '[SUCCESS] Bot started in screen session: %SCREEN_NAME%'"
echo --------------------------------------------------------------
echo Press any key to return to menu...
pause >nul
goto MENU

:STOP_BOT
cls
echo [INFO] Stopping Bot (%SCREEN_NAME%)...
echo --------------------------------------------------------------
ssh %SSH_HOST% "for s in $(screen -ls | grep -E '\.%SCREEN_NAME%[[:space:]]' | awk '{print $1}'); do screen -S \"$s\" -X quit 2>/dev/null || true; done; pkill -f 'python.*main.py' 2>/dev/null || true; echo '[SUCCESS] Screen session (%SCREEN_NAME%) and main.py processes stopped safely.'"
echo --------------------------------------------------------------
echo Press any key to return to menu...
pause >nul
goto MENU

:UPDATE_ONLY
cls
echo [INFO] Updating Code (Git Pull) and Dependencies...
echo --------------------------------------------------------------
ssh %SSH_HOST% "cd %BOT_PATH%; echo '[1/2] Pulling latest code from Git...'; git pull; echo '[2/2] Updating dependencies...'; venv/bin/pip install -r requirements.txt"
echo --------------------------------------------------------------
echo Press any key to return to menu...
pause >nul
goto MENU

:RESTART_UPDATE
cls
echo [INFO] Stopping, Updating, and Restarting Bot...
echo --------------------------------------------------------------
ssh %SSH_HOST% "echo '[1/4] Stopping current bot...'; for s in $(screen -ls | grep -E '\.%SCREEN_NAME%[[:space:]]' | awk '{print $1}'); do screen -S \"$s\" -X quit 2>/dev/null || true; done; pkill -f 'python.*main.py' 2>/dev/null || true; sleep 1; cd %BOT_PATH%; echo '[2/4] Pulling latest code from Git...'; git pull; echo '[3/4] Updating dependencies...'; venv/bin/pip install -r requirements.txt -q; echo '[4/4] Starting new screen session (%SCREEN_NAME%)...'; screen -dmS %SCREEN_NAME% bash -c 'cd %BOT_PATH% && source venv/bin/activate && python3 main.py'; echo '[SUCCESS] Bot restarted successfully.'"
echo --------------------------------------------------------------
echo Press any key to return to menu...
pause >nul
goto MENU

:QUICK_RESTART
cls
echo [INFO] Quick Restarting Bot (No Git Pull)...
echo --------------------------------------------------------------
ssh %SSH_HOST% "echo '[1/2] Stopping current bot...'; for s in $(screen -ls | grep -E '\.%SCREEN_NAME%[[:space:]]' | awk '{print $1}'); do screen -S \"$s\" -X quit 2>/dev/null || true; done; pkill -f 'python.*main.py' 2>/dev/null || true; sleep 1; echo '[2/2] Starting screen session (%SCREEN_NAME%)...'; cd %BOT_PATH%; screen -dmS %SCREEN_NAME% bash -c 'cd %BOT_PATH% && source venv/bin/activate && python3 main.py'; echo '[SUCCESS] Bot restarted immediately.'"
echo --------------------------------------------------------------
echo Press any key to return to menu...
pause >nul
goto MENU

:ATTACH_LOG
cls
echo ==============================================================
echo  IMPORTANT: To DETACH (leave bot running in background):
echo             Press  Ctrl + A  then press  D
echo.
echo  DO NOT press Ctrl + C unless you want to stop the bot!
echo ==============================================================
echo Press any key to attach to screen session '%SCREEN_NAME%'...
pause >nul
ssh -t %SSH_HOST% "screen -r %SCREEN_NAME% || (echo 'Screen session not running!' && sleep 3)"
goto MENU

:VIEW_LOG_SNAPSHOT
cls
echo [INFO] Fetching current screen buffer output (Snapshot)...
echo --------------------------------------------------------------
ssh %SSH_HOST% "screen -S %SCREEN_NAME% -X hardcopy /tmp/%SCREEN_NAME%_snapshot.log 2>/dev/null; if [ -f /tmp/%SCREEN_NAME%_snapshot.log ]; then echo '=== SCREEN SNAPSHOT ==='; cat /tmp/%SCREEN_NAME%_snapshot.log; rm -f /tmp/%SCREEN_NAME%_snapshot.log; else echo '[ERROR] Screen session (%SCREEN_NAME%) is not running or buffer empty.'; fi"
echo --------------------------------------------------------------
echo Press any key to return to menu...
pause >nul
goto MENU

:CHECK_STATUS
cls
echo [INFO] Checking Bot Status on %SSH_HOST%...
echo ==============================================================
ssh %SSH_HOST% "echo '--- SCREEN SESSION STATUS ---'; screen -ls | grep %SCREEN_NAME% || echo 'Screen session (%SCREEN_NAME%): OFFLINE'; echo ''; echo '--- PYTHON PROCESS STATUS ---'; ps aux | grep -iE 'python.*main.py' | grep -v grep || echo 'Python main.py: NOT RUNNING'; echo ''; echo '--- SYSTEM MEMORY / UP-TIME ---'; uptime; free -h | grep -E 'Mem:|Swap:'"
echo ==============================================================
echo Press any key to return to menu...
pause >nul
goto MENU

:OPEN_TERMINAL
cls
echo [INFO] Opening interactive SSH shell at %BOT_PATH%...
echo Type 'exit' to return to Manager menu.
echo --------------------------------------------------------------
ssh -t %SSH_HOST% "cd %BOT_PATH% && bash -l"
goto MENU

:EXIT
cls
echo Exiting Slip Verify Bot Manager...
exit /b 0

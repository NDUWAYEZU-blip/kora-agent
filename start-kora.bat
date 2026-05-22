@echo off
:: start-kora.bat — Run from anywhere; boots the full Kora dev stack.
:: Place this file on your PATH (e.g. C:\Windows\System32 or a custom bin dir).

setlocal

:: Adjust this path to wherever you cloned kora-agent
set AGENT_DIR=%~dp0

python "%AGENT_DIR%main.py" %*

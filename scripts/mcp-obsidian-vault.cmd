@echo off
setlocal
set "NODE=C:\Program Files\nodejs\node.exe"
set "SCRIPT=%~dp0mcp-obsidian-vault.mjs"
"%NODE%" "%SCRIPT%"

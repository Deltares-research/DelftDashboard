@echo off
set "root=%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& '%root%\_internal\_setup\setup.ps1' '%root%'"

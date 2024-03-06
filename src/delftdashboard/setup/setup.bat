@echo off
set "root=%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& './_internal/_setup/setup.ps1' '%root%'"

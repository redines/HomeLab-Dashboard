@echo off
REM HomeLab Dashboard - Quick Start Batch File for Windows
REM This is a simple wrapper to launch the PowerShell script

echo Starting HomeLab Dashboard...
powershell.exe -ExecutionPolicy Bypass -File "%~dp0scripts\start.ps1"

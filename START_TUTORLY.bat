@echo off
cd /d %~dp0
echo Starting Tutorly local environment...
docker compose up --build
pause

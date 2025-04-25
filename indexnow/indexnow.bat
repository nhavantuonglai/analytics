@echo off
for /f "delims=" %%i in ('python indexnow.py') do (
    echo %%i
)
@echo off
for /f "delims=" %%i in ('python nhavantonghop.py 2^>nul') do (
    echo %%i
)
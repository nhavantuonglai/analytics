@echo off
for /f "delims=" %%i in ('python indexnow.py 2^>nul') do (
	echo %%i
)
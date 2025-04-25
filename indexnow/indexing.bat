@echo off
setlocal EnableDelayedExpansion

set "START_TIME=%TIME%"
echo Starting.

set "RESULTS_FILE=results.json"
set "TEMP_FILE=temp.json"

set "ALL_URLS_ATTEMPTED=[]"
set "ALL_URLS_SUCCESS=[]"
set "ALL_URLS_FAILED=[]"

for %%F in (
	nhavanbatdinh.py
) do (
	echo Running %%F
	set "OUTPUT="
	for /f "delims=" %%i in ('python %%F 2^>nul') do (
		set "OUTPUT=%%i"
	)
	if defined OUTPUT (

		set "OUTPUT=!OUTPUT: =!"
		echo !OUTPUT! | find "urls_attempted" >nul
		if !ERRORLEVEL! == 0 (
			for /f "tokens=2 delims=:" %%a in ('echo !OUTPUT! ^| find "urls_attempted"') do (
				set "URLS_ATTEMPTED=%%a"
				set "URLS_ATTEMPTED=!URLS_ATTEMPTED:~1,-1!"
				if "!URLS_ATTEMPTED!" NEQ "" (
					set "ALL_URLS_ATTEMPTED=!ALL_URLS_ATTEMPTED:~0,-1!,!URLS_ATTEMPTED!]"
				)
			)
			for /f "tokens=2 delims=:" %%a in ('echo !OUTPUT! ^| find "urls_success"') do (
				set "URLS_SUCCESS=%%a"
				set "URLS_SUCCESS=!URLS_SUCCESS:~1,-1!"
				if "!URLS_SUCCESS!" NEQ "" (
					set "ALL_URLS_SUCCESS=!ALL_URLS_SUCCESS:~0,-1!,!URLS_SUCCESS!]"
				)
			)
			for /f "tokens=2 delims=:" %%a in ('echo !OUTPUT! ^| find "urls_failed"') do (
				set "URLS_FAILED=%%a"
				set "URLS_FAILED=!URLS_FAILED:~1,-1!"
				if "!URLS_FAILED!" NEQ "" (
					set "ALL_URLS_FAILED=!ALL_URLS_FAILED:~0,-1!,!URLS_FAILED!]"
				)
			)
		) else (
			echo Warning: Invalid JSON output from %%F
		)
	) else (
		echo Warning: No output from %%F
	)
)

echo Running indexnow.bat
call indexnow.bat 2>nul

set "END_TIME=%TIME%"

for /f "tokens=1-4 delims=:.," %%a in ("!START_TIME!") do (
	set "START_HOUR=0%%a"
	set "START_MIN=0%%b"
	set "START_SEC=0%%c"
	set "START_HOUR=!START_HOUR:~-2!"
	set "START_MIN=!START_MIN:~-2!"
	set "START_SEC=!START_SEC:~-2!"
)
for /f "tokens=1-4 delims=:.," %%a in ("!END_TIME!") do (
	set "END_HOUR=0%%a"
	set "END_MIN=0%%b"
	set "END_SEC=0%%c"
	set "END_HOUR=!END_HOUR:~-2!"
	set "END_MIN=!END_MIN:~-2!"
	set "END_SEC=!END_SEC:~-2!"
)

set /a "START_SECONDS=!START_HOUR!*3600+!START_MIN!*60+!START_SEC!"
set /a "END_SECONDS=!END_HOUR!*3600+!END_MIN!*60+!END_SEC!"
set /a "TOTAL_SECONDS=!END_SECONDS!-!START_SECONDS!"

if !TOTAL_SECONDS! LSS 0 set /a "TOTAL_SECONDS+=86400"
if !TOTAL_SECONDS! LSS 0 set "TOTAL_TIME=0h0m0s" & goto :skip_time_calc

set /a "HOURS=!TOTAL_SECONDS!/3600"
set /a "MINUTES=(!TOTAL_SECONDS!-!HOURS!*3600)/60"
set /a "SECONDS=!TOTAL_SECONDS!-!HOURS!*3600-!MINUTES!*60"
set "TOTAL_TIME=!HOURS!h!MINUTES!m!SECONDS!s"

:skip_time_calc

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "CURRENT_DATE=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%"

set "NEW_RECORD={\"date\":\"!CURRENT_DATE!\",\"total_time\":\"!TOTAL_TIME!\",\"urls_attempted\":!ALL_URLS_ATTEMPTED!,\"urls_success\":!ALL_URLS_SUCCESS!,\"urls_failed\":!ALL_URLS_FAILED!}"

if exist "%RESULTS_FILE%" (
	for /f "delims=" %%i in (%RESULTS_FILE%) do set "EXISTING_JSON=%%i"
	set "EXISTING_JSON=!EXISTING_JSON:[=!"
	set "EXISTING_JSON=!EXISTING_JSON:]=!"
	set "NEW_JSON=[%NEW_RECORD%,!EXISTING_JSON!]"
) else (
	set "NEW_JSON=[%NEW_RECORD%]"
)

echo !NEW_JSON! | findstr /r /c:"{" /n | find /c "{" > temp_count.txt
set /p RECORD_COUNT=<temp_count.txt
if !RECORD_COUNT! GTR 10 (
	echo !NEW_JSON! | head -n 10 > %TEMP_FILE%
	move /y %TEMP_FILE% %RESULTS_FILE%
) else (
	echo !NEW_JSON! > %RESULTS_FILE%
)

echo Executed.
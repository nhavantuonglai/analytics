@echo off
setlocal EnableDelayedExpansion

set "START_TIME=%TIME%"
echo Starting.

set "RESULTS_FILE=results.json"
set "TEMP_FILE=temp.json"

:: Initialize arrays for results
set "ALL_URLS_ATTEMPTED=[]"
set "ALL_URLS_SUCCESS=[]"
set "ALL_URLS_FAILED=[]"

:: Run Python scripts and collect results
for %%F in (
    nhavanbatdinh.py
) do (
    echo Running %%F
    set "OUTPUT="
    for /f "delims=" %%i in ('python %%F 2^>nul') do (
        set "OUTPUT=%%i"
    )
    if defined OUTPUT (
        :: Remove whitespace and check for valid JSON
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

:: Run indexnow.bat (no JSON parsing)
echo Running indexnow.bat
call indexnow.bat 2>nul

:: Calculate total time
set "END_TIME=%TIME%"
set "START_SECONDS=%START_TIME:~0,2%*3600+%START_TIME:~3,2%*60+%START_TIME:~6,2%"
set "END_SECONDS=%END_TIME:~0,2%*3600+%END_TIME:~3,2%*60+%END_TIME:~6,2%"
set /a "TOTAL_SECONDS=%END_SECONDS%-%START_SECONDS%"
set /a "HOURS=%TOTAL_SECONDS%/3600"
set /a "MINUTES=(%TOTAL_SECONDS%-%HOURS%*3600)/60"
set /a "SECONDS=%TOTAL_SECONDS%-%HOURS%*3600-%MINUTES%*60"
set "TOTAL_TIME=%HOURS%h%MINUTES%m%SECONDS%s"

:: Get current date (YYYY-MM-DD format)
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "CURRENT_DATE=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%"

:: Create new record
set "NEW_RECORD={\"date\":\"%CURRENT_DATE%\",\"total_time\":\"%TOTAL_TIME%\",\"urls_attempted\":!ALL_URLS_ATTEMPTED!,\"urls_success\":!ALL_URLS_SUCCESS!,\"urls_failed\":!ALL_URLS_FAILED!}"

:: Read existing JSON (if exists)
if exist "%RESULTS_FILE%" (
    for /f "delims=" %%i in (%RESULTS_FILE%) do set "EXISTING_JSON=%%i"
    set "EXISTING_JSON=!EXISTING_JSON:[=!"
    set "EXISTING_JSON=!EXISTING_JSON:]=!"
    set "NEW_JSON=[%NEW_RECORD%,!EXISTING_JSON!]"
) else (
    set "NEW_JSON=[%NEW_RECORD%]"
)

:: Limit to 10 records
echo !NEW_JSON! | findstr /r /c:"{" /n | find /c "{" > temp_count.txt
set /p RECORD_COUNT=<temp_count.txt
if !RECORD_COUNT! GTR 10 (
    echo !NEW_JSON! | head -n 10 > %TEMP_FILE%
    move /y %TEMP_FILE% %RESULTS_FILE%
) else (
    echo !NEW_JSON! > %RESULTS_FILE%
)

echo Executed.
@echo off
setlocal EnableDelayedExpansion

set "START_TIME=%TIME%"
echo Starting.

set "RESULTS_FILE=results.json"
set "TEMP_FILE=temp.json"

:: Khởi tạo mảng tạm thời để lưu kết quả
set "ALL_URLS_ATTEMPTED="
set "ALL_URLS_SUCCESS="
set "ALL_URLS_FAILED="

:: Chạy các tệp Python và thu thập kết quả
for %%F in (
    nhavantuonglai.py
	nhavanvietnam.py
	nhavantinhtu.py
	nhavantinhhoa.py
    nhavantinhban.py
	nhavantinhyeu.py
	nhavandautien.py
	nhavanduynhat.py
    nhavanthiensu.py
	nhavantrietgia.py
	nhavanhiendai.py
	nhavanquakhu.py
    nhavandocsach.py
	nhavanvietlach.py
	nhavankhongten.py
	nhavanbatdinh.py
    nhavanhuvo.py
	nhavancodien.py
	nhavanyentinh.py
	nhavanhocduong.py
    nhavantinhtao.py
	nhavantinhcam.py
	nhavantinhthan.py
) do (
    echo Running %%F
    for /f "delims=" %%i in ('python %%F') do (
        set "OUTPUT=%%i"
        :: Phân tích JSON từ OUTPUT
        for /f "tokens=2 delims=:" %%a in ('echo !OUTPUT! ^| find "urls_attempted"') do (
            set "URLS_ATTEMPTED=%%a"
            set "URLS_ATTEMPTED=!URLS_ATTEMPTED:~2,-2!"
            set "ALL_URLS_ATTEMPTED=!ALL_URLS_ATTEMPTED!,!URLS_ATTEMPTED!"
        )
        for /f "tokens=2 delims=:" %%a in ('echo !OUTPUT! ^| find "urls_success"') do (
            set "URLS_SUCCESS=%%a"
            set "URLS_SUCCESS=!URLS_SUCCESS:~2,-2!"
            set "ALL_URLS_SUCCESS=!ALL_URLS_SUCCESS!,!URLS_SUCCESS!"
        )
        for /f "tokens=2 delims=:" %%a in ('echo !OUTPUT! ^| find "urls_failed"') do (
            set "URLS_FAILED=%%a"
            set "URLS_FAILED=!URLS_FAILED:~2,-2!"
            set "ALL_URLS_FAILED=!ALL_URLS_FAILED!,!URLS_FAILED!"
        )
    )
)

:: Chạy indexnow.bat
echo Running indexnow.bat
for /f "delims=" %%i in ('call indexnow.bat') do (
    set "OUTPUT=%%i"
    for /f "tokens=2 delims=:" %%a in ('echo !OUTPUT! ^| find "urls_attempted"') do (
        set "URLS_ATTEMPTED=%%a"
        set "URLS_ATTEMPTED=!URLS_ATTEMPTED:~2,-2!"
        set "ALL_URLS_ATTEMPTED=!ALL_URLS_ATTEMPTED!,!URLS_ATTEMPTED!"
    )
    for /f "tokens=2 delims=:" %%a in ('echo !OUTPUT! ^| find "urls_success"') do (
        set "URLS_SUCCESS=%%a"
        set "URLS_SUCCESS=!URLS_SUCCESS:~2,-2!"
        set "ALL_URLS_SUCCESS=!ALL_URLS_SUCCESS!,!URLS_SUCCESS!"
    )
    for /f "tokens=2 delims=:" %%a in ('echo !OUTPUT! ^| find "urls_failed"') do (
        set "URLS_FAILED=%%a"
        set "URLS_FAILED=!URLS_FAILED:~2,-2!"
        set "ALL_URLS_FAILED=!ALL_URLS_FAILED!,!URLS_FAILED!"
    )
)

:: Tính tổng thời gian
set "END_TIME=%TIME%"
set "START_SECONDS=%START_TIME:~0,2%*3600+%START_TIME:~3,2%*60+%START_TIME:~6,2%"
set "END_SECONDS=%END_TIME:~0,2%*3600+%END_TIME:~3,2%*60+%END_TIME:~6,2%"
set /a "TOTAL_SECONDS=%END_SECONDS%-%START_SECONDS%"
set /a "HOURS=%TOTAL_SECONDS%/3600"
set /a "MINUTES=(%TOTAL_SECONDS%-%HOURS%*3600)/60"
set /a "SECONDS=%TOTAL_SECONDS%-%HOURS%*3600-%MINUTES%*60"
set "TOTAL_TIME=%HOURS%h%MINUTES%m%SECONDS%s"

:: Lấy ngày hiện tại (định dạng YYYY-MM-DD)
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "CURRENT_DATE=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%"

:: Tạo bản ghi mới
set "NEW_RECORD={\"date\":\"%CURRENT_DATE%\",\"total_time\":\"%TOTAL_TIME%\",\"urls_attempted\":[!ALL_URLS_ATTEMPTED!],\"urls_success\":[!ALL_URLS_SUCCESS!],\"urls_failed\":[!ALL_URLS_FAILED!]}"

:: Đọc tệp JSON hiện có (nếu tồn tại)
if exist "%RESULTS_FILE%" (
    for /f "delims=" %%i in (%RESULTS_FILE%) do set "EXISTING_JSON=%%i"
    set "EXISTING_JSON=!EXISTING_JSON:[=!"
    set "EXISTING_JSON=!EXISTING_JSON:]=!"
    set "NEW_JSON=[%NEW_RECORD%,!EXISTING_JSON!]"
) else (
    set "NEW_JSON=[%NEW_RECORD%]"
)

:: Giới hạn tối đa 10 bản ghi
echo !NEW_JSON! | findstr /r /c:"{" /n | find /c "{" > temp_count.txt
set /p RECORD_COUNT=<temp_count.txt
if !RECORD_COUNT! GTR 10 (
    echo !NEW_JSON! | head -n 10 > %TEMP_FILE%
    move /y %TEMP_FILE% %RESULTS_FILE%
) else (
    echo !NEW_JSON! > %RESULTS_FILE%
)

echo Executed.
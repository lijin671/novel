@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 《半岛：雨季未命名》自动化跑批脚本 (Batch版)
REM 从第31章开始批量生成到第1000章

set PROJECT_ROOT=C:\ITS\MuMuAINovel
set USER_ID=local_21232f297a57a5a7
set ARTIFACT_DIR=tmp\bandao-original-rainseason-20260601
set BASE_OUTPUT_DIR=tmp\bandao-original-rainseason-20260601
set TARGET_WORD_COUNT=10000
set BATCH_SIZE=10
set START_CHAPTER=31
set END_CHAPTER=1000

echo ==========================================
echo 《半岛：雨季未命名》自动化跑批
echo ==========================================
echo 起始章节: %START_CHAPTER%
echo 结束章节: %END_CHAPTER%
echo 批次大小: %BATCH_SIZE%
echo.

cd /d "%PROJECT_ROOT%"

REM 创建日志目录
if not exist "logs" mkdir "logs"

REM 计算批次并执行
set /a CURRENT=%START_CHAPTER%

:LOOP
if %CURRENT% gtr %END_CHAPTER% goto DONE

set /a BATCH_END=%CURRENT% + %BATCH_SIZE% - 1
if %BATCH_END% gtr %END_CHAPTER% set /a BATCH_END=%END_CHAPTER%

REM 格式化批次号
set PADDED_START=00%CURRENT%
set PADDED_START=%PADDED_START:~-3%
set PADDED_END=00%BATCH_END%
set PADDED_END=%PADDED_END:~-3%

set OUTPUT_DIR=%BASE_OUTPUT_DIR%\real_ai_pack_%PADDED_START%_%PADDED_END%
set BATCH_NUM=%PADDED_START%-%PADDED_END%

echo ------------------------------------------
echo 开始批次: %BATCH_NUM%
echo 输出目录: %OUTPUT_DIR%
echo.

REM 运行生成脚本
python -m backend.scripts.generate_original_novel_full_pack ^
    --user-id "%USER_ID%" ^
    --artifact-dir "%ARTIFACT_DIR%" ^
    --output-dir "%OUTPUT_DIR%" ^
    --start-chapter %CURRENT% ^
    --end-chapter %BATCH_END% ^
    --target-word-count %TARGET_WORD_COUNT% ^
    --max-segments-per-chapter 8 ^
    --retry-delay-seconds 2

if %errorlevel% equ 0 (
    echo [SUCCESS] 批次 %BATCH_NUM% 完成
) else (
    echo [ERROR] 批次 %BATCH_NUM% 失败，退出码: %errorlevel%
    echo 继续执行下一批次...
)

echo.

REM 更新进度
set /a CURRENT=%BATCH_END% + 1
goto LOOP

:DONE
echo ==========================================
echo 跑批完成
echo ==========================================
echo.

REM 检查是否需要合并
if %CURRENT% gtr %END_CHAPTER% (
    echo 所有批次执行完毕，开始合并...
    echo.

    set MERGED_PATH=%BASE_OUTPUT_DIR%\半岛：雨季未命名_001-1000.txt

    python -m backend.scripts.generate_original_novel_full_pack ^
        --user-id "%USER_ID%" ^
        --artifact-dir "%ARTIFACT_DIR%" ^
        --output-dir "%BASE_OUTPUT_DIR%\final_pack" ^
        --start-chapter 1 ^
        --end-chapter 1000 ^
        --merge-txt ^
        --merged-path "%MERGED_PATH%" ^
        --normalize-headings

    if %errorlevel% equ 0 (
        echo [SUCCESS] 合并完成: %MERGED_PATH%
    ) else (
        echo [ERROR] 合并失败
    )
)

echo.
echo 脚本执行完毕
pause

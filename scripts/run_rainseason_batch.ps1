# 《半岛：雨季未命名》自动化跑批脚本
# 从第31章开始批量生成到第1000章，每批10章

param(
    [int]$StartChapter = 31,
    [int]$EndChapter = 1000,
    [int]$BatchSize = 10,
    [string]$UserId = "local_21232f297a57a5a7",
    [string]$ArtifactDir = "tmp/bandao-original-rainseason-20260601",
    [string]$BaseOutputDir = "tmp/bandao-original-rainseason-20260601",
    [int]$TargetWordCount = 10000,
    [int]$MaxSegmentsPerChapter = 8,
    [int]$RetryDelaySeconds = 2,
    [switch]$DryRun,
    [switch]$MergeOnly
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\ITS\MuMuAINovel"

# 日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path "$ProjectRoot\logs\rainseason_batch.log" -Value $logEntry -Encoding UTF8
}

# 创建日志目录
if (-not (Test-Path "$ProjectRoot\logs")) {
    New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
}

# 计算批次
$batches = @()
$current = $StartChapter
while ($current -le $EndChapter) {
    $batchEnd = [Math]::Min($current + $BatchSize - 1, $1000)
    $batches += @{
        Start = $current
        End = $batchEnd
        OutputDir = "$BaseOutputDir\real_ai_pack_{0:D3}_{1:D3}" -f $current, $batchEnd
    }
    $current = $batchEnd + 1
}

Write-Log "=========================================="
Write-Log "《半岛：雨季未命名》自动化跑批开始"
Write-Log "=========================================="
Write-Log "起始章节: $StartChapter"
Write-Log "结束章节: $EndChapter"
Write-Log "批次大小: $BatchSize"
Write-Log "总批次数: $($batches.Count)"
Write-Log "目标字数: $TargetWordCount"
Write-Log "用户ID: $UserId"

if ($DryRun) {
    Write-Log "DRY RUN 模式 - 不会实际生成" "WARN"
    foreach ($batch in $batches) {
        Write-Log "批次: $($batch.Start)-$($batch.End) -> $($batch.OutputDir)"
    }
    exit 0
}

# 进度跟踪文件
$progressFile = "$BaseOutputDir\batch_progress.json"
$progress = @{
    start_chapter = $StartChapter
    end_chapter = $EndChapter
    batch_size = $BatchSize
    started_at = (Get-Date -Format "o")
    completed_batches = @()
    failed_batches = @()
    current_batch = $null
    total_chapters_generated = 0
}

# 保存进度函数
function Save-Progress {
    $progress | ConvertTo-Json -Depth 10 | Set-Content -Path $progressFile -Encoding UTF8
}

# 初始化进度文件
Save-Progress

$totalGenerated = 0
$totalFailed = 0
$startTime = Get-Date

foreach ($batch in $batches) {
    $batchStart = $batch.Start
    $batchEnd = $batch.End
    $outputDir = $batch.OutputDir
    $batchNum = "$batchStart-$batchEnd"

    Write-Log "------------------------------------------"
    Write-Log "开始批次: $batchNum"
    Write-Log "输出目录: $outputDir"

    $progress.current_batch = @{
        start = $batchStart
        end = $batchEnd
        output_dir = $outputDir
        started_at = (Get-Date -Format "o")
    }
    Save-Progress

    # 构建命令
    $cmd = @(
        "-m", "backend.scripts.generate_original_novel_full_pack",
        "--user-id", $UserId,
        "--artifact-dir", $ArtifactDir,
        "--output-dir", $outputDir,
        "--start-chapter", $batchStart,
        "--end-chapter", $batchEnd,
        "--target-word-count", $TargetWordCount,
        "--max-segments-per-chapter", $MaxSegmentsPerChapter,
        "--retry-delay-seconds", $RetryDelaySeconds
    )

    try {
        # 运行生成脚本
        $process = Start-Process -FilePath "python" -ArgumentList $cmd -WorkingDirectory $ProjectRoot -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$ProjectRoot\logs\batch_${batchNum}_stdout.log" -RedirectStandardError "$ProjectRoot\logs\batch_${batchNum}_stderr.log"

        if ($process.ExitCode -eq 0) {
            Write-Log "批次 $batchNum 完成" "SUCCESS"

            # 读取审计结果
            $auditFile = "$outputDir\original_novel_audit_report.json"
            if (Test-Path $auditFile) {
                $audit = Get-Content $auditFile -Raw | ConvertFrom-Json
                if ($audit.passed) {
                    Write-Log "审计通过: $($audit.chapter_count) 章节, 最短字数: $($audit.chapters | ForEach-Object { $_.word_count } | Measure-Object -Minimum | Select-Object -ExpandProperty Minimum)"
                    $totalGenerated += $audit.chapter_count
                    $progress.completed_batches += $batchNum
                } else {
                    Write-Log "审计失败: $($audit.failed_chapter_count) 章节未通过" "ERROR"
                    $totalFailed += $audit.failed_chapter_count
                    $progress.failed_batches += $batchNum
                }
            }
        } else {
            Write-Log "批次 $batchNum 失败，退出码: $($process.ExitCode)" "ERROR"
            $progress.failed_batches += $batchNum

            # 读取错误日志
            $stderrLog = "$ProjectRoot\logs\batch_${batchNum}_stderr.log"
            if (Test-Path $stderrLog) {
                $errorContent = Get-Content $stderrLog -Raw
                if ($errorContent) {
                    Write-Log "错误信息: $errorContent" "ERROR"
                }
            }
        }
    } catch {
        Write-Log "批次 $batchNum 异常: $_" "ERROR"
        $progress.failed_batches += $batchNum
    }

    $progress.total_chapters_generated = $totalGenerated
    $progress.current_batch = $null
    Save-Progress

    # 计算进度
    $elapsed = (Get-Date) - $startTime
    $percentComplete = [Math]::Round(($batchEnd - $StartChapter + 1) / ($EndChapter - $StartChapter + 1) * 100, 2)
    $chaptersRemaining = $EndChapter - $batchEnd
    $avgTimePerChapter = if ($totalGenerated -gt 0) { $elapsed.TotalMinutes / $totalGenerated } else { 0 }
    $estimatedRemaining = if ($avgTimePerChapter -gt 0) { [Math]::Round($avgTimePerChapter * $chaptersRemaining / 60, 2) } else { "未知" }

    Write-Log "进度: $percentComplete% | 已生成: $totalGenerated | 失败: $totalFailed | 剩余: $chaptersRemaining 章 | 预计剩余: $estimatedRemaining 小时"
}

# 最终汇总
$endTime = Get-Date
$totalTime = $endTime - $startTime

Write-Log "=========================================="
Write-Log "跑批完成"
Write-Log "=========================================="
Write-Log "总耗时: $($totalTime.Hours)小时 $($totalTime.Minutes)分钟"
Write-Log "成功章节: $totalGenerated"
Write-Log "失败章节: $totalFailed"
Write-Log "完成批次: $($progress.completed_batches.Count)"
Write-Log "失败批次: $($progress.failed_batches.Count)"

$progress.completed_at = (Get-Date -Format "o")
$progress.total_time_seconds = [Math]::Round($totalTime.TotalSeconds, 2)
Save-Progress

# 如果全部完成，自动合并
if ($totalFailed -eq 0 -and $totalGenerated -ge ($EndChapter - $StartChapter + 1)) {
    Write-Log "所有章节生成成功，开始合并..."

    $mergedPath = "$BaseOutputDir\半岛：雨季未命名_001-1000.txt"
    $mergeCmd = @(
        "-m", "backend.scripts.generate_original_novel_full_pack",
        "--user-id", $UserId,
        "--artifact-dir", $ArtifactDir,
        "--output-dir", "$BaseOutputDir\final_pack",
        "--start-chapter", "1",
        "--end-chapter", "1000",
        "--merge-txt",
        "--merged-path", $mergedPath,
        "--normalize-headings"
    )

    try {
        $mergeProcess = Start-Process -FilePath "python" -ArgumentList $mergeCmd -WorkingDirectory $ProjectRoot -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$ProjectRoot\logs\merge_stdout.log" -RedirectStandardError "$ProjectRoot\logs\merge_stderr.log"

        if ($mergeProcess.ExitCode -eq 0) {
            Write-Log "合并完成: $mergedPath" "SUCCESS"

            # 计算文件信息
            if (Test-Path $mergedPath) {
                $fileInfo = Get-Item $mergedPath
                $hash = Get-FileHash $mergedPath -Algorithm SHA256
                Write-Log "文件大小: $([Math]::Round($fileInfo.Length / 1MB, 2)) MB"
                Write-Log "SHA256: $($hash.Hash)"
            }
        } else {
            Write-Log "合并失败" "ERROR"
        }
    } catch {
        Write-Log "合并异常: $_" "ERROR"
    }
}

Write-Log "=========================================="
Write-Log "脚本执行完毕"
Write-Log "=========================================="

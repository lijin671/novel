# 《半岛：雨季未命名》断点续跑脚本
# 自动检测已完成章节，从断点继续生成

param(
    [string]$UserId = "local_21232f297a57a5a7",
    [string]$ArtifactDir = "tmp/bandao-original-rainseason-20260601",
    [string]$BaseOutputDir = "tmp/bandao-original-rainseason-20260601",
    [int]$TargetWordCount = 10000,
    [int]$BatchSize = 10,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\ITS\MuMuAINovel"

# 日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path "$ProjectRoot\logs\rainseason_resume.log" -Value $logEntry -Encoding UTF8
}

# 创建日志目录
if (-not (Test-Path "$ProjectRoot\logs")) {
    New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
}

Write-Log "=========================================="
Write-Log "《半岛：雨季未命名》断点续跑检测"
Write-Log "=========================================="

# 扫描已完成的章节
$completedChapters = @()
$missingChapters = @()

for ($i = 1; $i -le 1000; $i++) {
    $padded = "{0:D4}" -f $i
    $found = $false

    # 检查所有可能的输出目录
    $possibleDirs = @(
        "$BaseOutputDir\real_ai_pack_001_020",
        "$BaseOutputDir\real_ai_pack_021_030",
        "$BaseOutputDir\real_ai_pack_031_040",
        "$BaseOutputDir\real_ai_pack_041_050",
        "$BaseOutputDir\real_ai_pack_051_060",
        "$BaseOutputDir\real_ai_pack_061_070",
        "$BaseOutputDir\real_ai_pack_071_080",
        "$BaseOutputDir\real_ai_pack_081_090",
        "$BaseOutputDir\real_ai_pack_091_100",
        "$BaseOutputDir\real_ai_pack_101_110",
        "$BaseOutputDir\real_ai_pack_111_120",
        "$BaseOutputDir\real_ai_pack_121_130",
        "$BaseOutputDir\real_ai_pack_131_140",
        "$BaseOutputDir\real_ai_pack_141_150",
        "$BaseOutputDir\real_ai_pack_151_160",
        "$BaseOutputDir\real_ai_pack_161_170",
        "$BaseOutputDir\real_ai_pack_171_180",
        "$BaseOutputDir\real_ai_pack_181_190",
        "$BaseOutputDir\real_ai_pack_191_200",
        "$BaseOutputDir\real_ai_pack_201_210",
        "$BaseOutputDir\real_ai_pack_211_220",
        "$BaseOutputDir\real_ai_pack_221_230",
        "$BaseOutputDir\real_ai_pack_231_240",
        "$BaseOutputDir\real_ai_pack_241_250",
        "$BaseOutputDir\real_ai_pack_251_260",
        "$BaseOutputDir\real_ai_pack_261_270",
        "$BaseOutputDir\real_ai_pack_271_280",
        "$BaseOutputDir\real_ai_pack_281_290",
        "$BaseOutputDir\real_ai_pack_291_300",
        "$BaseOutputDir\real_ai_pack_301_310",
        "$BaseOutputDir\real_ai_pack_311_320",
        "$BaseOutputDir\real_ai_pack_321_330",
        "$BaseOutputDir\real_ai_pack_331_340",
        "$BaseOutputDir\real_ai_pack_341_350",
        "$BaseOutputDir\real_ai_pack_351_360",
        "$BaseOutputDir\real_ai_pack_361_370",
        "$BaseOutputDir\real_ai_pack_371_380",
        "$BaseOutputDir\real_ai_pack_381_390",
        "$BaseOutputDir\real_ai_pack_391_400",
        "$BaseOutputDir\real_ai_pack_401_410",
        "$BaseOutputDir\real_ai_pack_411_420",
        "$BaseOutputDir\real_ai_pack_421_430",
        "$BaseOutputDir\real_ai_pack_431_440",
        "$BaseOutputDir\real_ai_pack_441_450",
        "$BaseOutputDir\real_ai_pack_451_460",
        "$BaseOutputDir\real_ai_pack_461_470",
        "$BaseOutputDir\real_ai_pack_471_480",
        "$BaseOutputDir\real_ai_pack_481_490",
        "$BaseOutputDir\real_ai_pack_491_500",
        "$BaseOutputDir\real_ai_pack_501_510",
        "$BaseOutputDir\real_ai_pack_511_520",
        "$BaseOutputDir\real_ai_pack_521_530",
        "$BaseOutputDir\real_ai_pack_531_540",
        "$BaseOutputDir\real_ai_pack_541_550",
        "$BaseOutputDir\real_ai_pack_551_560",
        "$BaseOutputDir\real_ai_pack_561_570",
        "$BaseOutputDir\real_ai_pack_571_580",
        "$BaseOutputDir\real_ai_pack_581_590",
        "$BaseOutputDir\real_ai_pack_591_600",
        "$BaseOutputDir\real_ai_pack_601_610",
        "$BaseOutputDir\real_ai_pack_611_620",
        "$BaseOutputDir\real_ai_pack_621_630",
        "$BaseOutputDir\real_ai_pack_631_640",
        "$BaseOutputDir\real_ai_pack_641_650",
        "$BaseOutputDir\real_ai_pack_651_660",
        "$BaseOutputDir\real_ai_pack_661_670",
        "$BaseOutputDir\real_ai_pack_671_680",
        "$BaseOutputDir\real_ai_pack_681_690",
        "$BaseOutputDir\real_ai_pack_691_700",
        "$BaseOutputDir\real_ai_pack_701_710",
        "$BaseOutputDir\real_ai_pack_711_720",
        "$BaseOutputDir\real_ai_pack_721_730",
        "$BaseOutputDir\real_ai_pack_731_740",
        "$BaseOutputDir\real_ai_pack_741_750",
        "$BaseOutputDir\real_ai_pack_751_760",
        "$BaseOutputDir\real_ai_pack_761_770",
        "$BaseOutputDir\real_ai_pack_771_780",
        "$BaseOutputDir\real_ai_pack_781_790",
        "$BaseOutputDir\real_ai_pack_791_800",
        "$BaseOutputDir\real_ai_pack_801_810",
        "$BaseOutputDir\real_ai_pack_811_820",
        "$BaseOutputDir\real_ai_pack_821_830",
        "$BaseOutputDir\real_ai_pack_831_840",
        "$BaseOutputDir\real_ai_pack_841_850",
        "$BaseOutputDir\real_ai_pack_851_860",
        "$BaseOutputDir\real_ai_pack_861_870",
        "$BaseOutputDir\real_ai_pack_871_880",
        "$BaseOutputDir\real_ai_pack_881_890",
        "$BaseOutputDir\real_ai_pack_891_900",
        "$BaseOutputDir\real_ai_pack_901_910",
        "$BaseOutputDir\real_ai_pack_911_920",
        "$BaseOutputDir\real_ai_pack_921_930",
        "$BaseOutputDir\real_ai_pack_931_940",
        "$BaseOutputDir\real_ai_pack_941_950",
        "$BaseOutputDir\real_ai_pack_951_960",
        "$BaseOutputDir\real_ai_pack_961_970",
        "$BaseOutputDir\real_ai_pack_971_980",
        "$BaseOutputDir\real_ai_pack_981_990",
        "$BaseOutputDir\real_ai_pack_991_1000"
    )

    foreach ($dir in $possibleDirs) {
        $chapterFile = "$dir\chapter_$padded.txt"
        if (Test-Path $chapterFile) {
            $fileInfo = Get-Item $chapterFile
            if ($fileInfo.Length -gt 1000) {
                $completedChapters += $i
                $found = $true
                break
            }
        }
    }

    if (-not $found) {
        $missingChapters += $i
    }
}

Write-Log "已完成章节: $($completedChapters.Count)"
Write-Log "缺失章节: $($missingChapters.Count)"

if ($missingChapters.Count -eq 0) {
    Write-Log "所有章节已完成！" "SUCCESS"
    Write-Log "可以运行合并脚本生成最终TXT"
    exit 0
}

# 找出第一个缺失章节
$firstMissing = $missingChapters[0]
Write-Log "第一个缺失章节: $firstMissing"

# 计算需要生成的批次
$batches = @()
$current = $firstMissing
while ($current -le 1000) {
    # 检查这个章节是否需要生成
    if ($current -in $missingChapters) {
        $batchEnd = [Math]::Min($current + $BatchSize - 1, 1000)

        # 检查这个批次中是否有缺失章节
        $hasMissing = $false
        for ($i = $current; $i -le $batchEnd; $i++) {
            if ($i -in $missingChapters) {
                $hasMissing = $true
                break
            }
        }

        if ($hasMissing) {
            $paddedStart = "{0:D3}" -f $current
            $paddedEnd = "{0:D3}" -f $batchEnd
            $batches += @{
                Start = $current
                End = $batchEnd
                OutputDir = "$BaseOutputDir\real_ai_pack_${paddedStart}_${paddedEnd}"
            }
        }
    }
    $current += $BatchSize
}

Write-Log "需要生成的批次: $($batches.Count)"

if ($DryRun) {
    Write-Log "DRY RUN 模式 - 不会实际生成" "WARN"
    foreach ($batch in $batches) {
        Write-Log "批次: $($batch.Start)-$($batch.End) -> $($batch.OutputDir)"
    }
    exit 0
}

# 开始生成
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

    # 构建命令
    $cmd = @(
        "-m", "backend.scripts.generate_original_novel_full_pack",
        "--user-id", $UserId,
        "--artifact-dir", $ArtifactDir,
        "--output-dir", $outputDir,
        "--start-chapter", $batchStart,
        "--end-chapter", $batchEnd,
        "--target-word-count", $TargetWordCount,
        "--max-segments-per-chapter", "8",
        "--retry-delay-seconds", "2"
    )

    try {
        $process = Start-Process -FilePath "python" -ArgumentList $cmd -WorkingDirectory $ProjectRoot -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$ProjectRoot\logs\resume_${batchNum}_stdout.log" -RedirectStandardError "$ProjectRoot\logs\resume_${batchNum}_stderr.log"

        if ($process.ExitCode -eq 0) {
            Write-Log "批次 $batchNum 完成" "SUCCESS"

            # 读取审计结果
            $auditFile = "$outputDir\original_novel_audit_report.json"
            if (Test-Path $auditFile) {
                $audit = Get-Content $auditFile -Raw | ConvertFrom-Json
                if ($audit.passed) {
                    Write-Log "审计通过: $($audit.chapter_count) 章节"
                    $totalGenerated += $audit.chapter_count
                } else {
                    Write-Log "审计失败: $($audit.failed_chapter_count) 章节未通过" "ERROR"
                    $totalFailed += $audit.failed_chapter_count
                }
            }
        } else {
            Write-Log "批次 $batchNum 失败，退出码: $($process.ExitCode)" "ERROR"
            $totalFailed += ($batchEnd - $batchStart + 1)
        }
    } catch {
        Write-Log "批次 $batchNum 异常: $_" "ERROR"
        $totalFailed += ($batchEnd - $batchStart + 1)
    }

    # 计算进度
    $elapsed = (Get-Date) - $startTime
    $percentComplete = [Math]::Round(($batchEnd - $firstMissing + 1) / (1000 - $firstMissing + 1) * 100, 2)
    Write-Log "进度: $percentComplete% | 已生成: $totalGenerated | 失败: $totalFailed"
}

# 最终汇总
$endTime = Get-Date
$totalTime = $endTime - $startTime

Write-Log "=========================================="
Write-Log "续跑完成"
Write-Log "=========================================="
Write-Log "总耗时: $($totalTime.Hours)小时 $($totalTime.Minutes)分钟"
Write-Log "成功章节: $totalGenerated"
Write-Log "失败章节: $totalFailed"

# 检查是否全部完成
$finalMissing = @()
for ($i = 1; $i -le 1000; $i++) {
    $padded = "{0:D4}" -f $i
    $found = $false

    foreach ($dir in $possibleDirs) {
        $chapterFile = "$dir\chapter_$padded.txt"
        if (Test-Path $chapterFile) {
            $fileInfo = Get-Item $chapterFile
            if ($fileInfo.Length -gt 1000) {
                $found = $true
                break
            }
        }
    }

    if (-not $found) {
        $finalMissing += $i
    }
}

if ($finalMissing.Count -eq 0) {
    Write-Log "所有章节已完成！可以运行合并脚本生成最终TXT" "SUCCESS"
} else {
    Write-Log "仍有 $($finalMissing.Count) 个章节未完成" "WARN"
    Write-Log "第一个缺失章节: $($finalMissing[0])"
}

Write-Log "=========================================="
Write-Log "脚本执行完毕"
Write-Log "=========================================="

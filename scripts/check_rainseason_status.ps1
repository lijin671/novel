# 《半岛：雨季未命名》状态检查脚本
# 快速查看当前生成进度

param(
    [string]$BaseOutputDir = "tmp/bandao-original-rainseason-20260601"
)

$ErrorActionPreference = "SilentlyContinue"
$ProjectRoot = "C:\ITS\MuMuAINovel"

Write-Host "=========================================="
Write-Host "《半岛：雨季未命名》生成状态"
Write-Host "=========================================="
Write-Host ""

# 扫描已完成的章节
$completedChapters = @()
$chapterDetails = @()

for ($i = 1; $i -le 1000; $i++) {
    $padded = "{0:D4}" -f $i
    $found = $false

    # 检查所有可能的输出目录
    $dirs = Get-ChildItem -Path "$ProjectRoot\$BaseOutputDir" -Directory -Filter "real_ai_pack_*" -ErrorAction SilentlyContinue

    foreach ($dir in $dirs) {
        $chapterFile = "$($dir.FullName)\chapter_$padded.txt"
        if (Test-Path $chapterFile) {
            $fileInfo = Get-Item $chapterFile
            if ($fileInfo.Length -gt 1000) {
                $completedChapters += $i
                $wordCount = (Get-Content $chapterFile -Raw -ErrorAction SilentlyContinue).Split("`n").Count * 5  # 估算字数
                $chapterDetails += @{
                    Chapter = $i
                    File = $chapterFile
                    Size = $fileInfo.Length
                    WordCount = $wordCount
                }
                $found = $true
                break
            }
        }
    }
}

# 统计信息
$totalCompleted = $completedChapters.Count
$totalMissing = 1000 - $totalCompleted
$percentComplete = [Math]::Round($totalCompleted / 1000 * 100, 2)

Write-Host "总进度: $percentComplete% ($totalCompleted / 1000)"
Write-Host ""

if ($totalCompleted -gt 0) {
    # 按批次分组
    $batches = @{}
    foreach ($ch in $completedChapters) {
        $batchNum = [Math]::Ceiling($ch / 10) * 10
        if (-not $batches.ContainsKey($batchNum)) {
            $batches[$batchNum] = @()
        }
        $batches[$batchNum] += $ch
    }

    Write-Host "已完成批次:"
    foreach ($batch in ($batches.Keys | Sort-Object)) {
        $chapters = $batches[$batch]
        $start = ($chapters | Measure-Object -Minimum).Minimum
        $end = ($chapters | Measure-Object -Maximum).Maximum
        $count = $chapters.Count
        Write-Host "  $start-$end`: $count 章节"
    }

    Write-Host ""
    Write-Host "最近生成的章节:"
    $recent = $completedChapters | Select-Object -Last 5
    foreach ($ch in $recent) {
        $detail = $chapterDetails | Where-Object { $_.Chapter -eq $ch } | Select-Object -First 1
        if ($detail) {
            $sizeKB = [Math]::Round($detail.Size / 1KB, 2)
            Write-Host "  第$ch章`: $sizeKB KB"
        }
    }
}

Write-Host ""

# 找出第一个缺失章节
$firstMissing = $null
for ($i = 1; $i -le 1000; $i++) {
    if ($i -notin $completedChapters) {
        $firstMissing = $i
        break
    }
}

if ($firstMissing) {
    Write-Host "第一个缺失章节: 第$firstMissing章"
    Write-Host ""
    Write-Host "继续生成命令:"
    Write-Host "  powershell -File scripts\resume_rainseason.ps1"
    Write-Host ""
    Write-Host "或指定起始章节:"
    Write-Host "  powershell -File scripts\run_rainseason_batch.ps1 -StartChapter $firstMissing"
} else {
    Write-Host "所有章节已完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "合并命令:"
    Write-Host "  python -m backend.scripts.generate_original_novel_full_pack --merge-txt --merged-path `"$BaseOutputDir\半岛：雨季未命名_001-1000.txt`""
}

Write-Host ""
Write-Host "=========================================="

# 检查进度文件
$progressFile = "$ProjectRoot\$BaseOutputDir\batch_progress.json"
if (Test-Path $progressFile) {
    Write-Host ""
    Write-Host "上次跑批进度:"
    $progress = Get-Content $progressFile -Raw | ConvertFrom-Json
    Write-Host "  开始时间: $($progress.started_at)"
    if ($progress.completed_at) {
        Write-Host "  完成时间: $($progress.completed_at)"
    }
    Write-Host "  已生成章节: $($progress.total_chapters_generated)"
    Write-Host "  完成批次: $($progress.completed_batches.Count)"
    Write-Host "  失败批次: $($progress.failed_batches.Count)"
}

# 检查审计报告
Write-Host ""
Write-Host "审计报告:"
$auditFiles = Get-ChildItem -Path "$ProjectRoot\$BaseOutputDir" -Recurse -Filter "original_novel_audit_report.json" -ErrorAction SilentlyContinue
foreach ($auditFile in $auditFiles) {
    $audit = Get-Content $auditFile.FullName -Raw | ConvertFrom-Json
    if ($audit.passed) {
        Write-Host "  $($auditFile.Directory.Name): 通过 ($($audit.chapter_count) 章节)" -ForegroundColor Green
    } else {
        Write-Host "  $($auditFile.Directory.Name): 失败 ($($audit.failed_chapter_count) 章节)" -ForegroundColor Red
    }
}

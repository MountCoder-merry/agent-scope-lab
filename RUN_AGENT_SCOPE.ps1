<#
.SYNOPSIS
  Bounded, resumable Codex autonomy test for an isolated AgentScope project.
.DESCRIPTION
  Starts one Codex exec session; if it exits before verified completion,
  resumes the latest session up to MaxHours/MaxTurns. Never bypasses sandbox.
  This does not prevent OS/process interruption; it only resumes across turns.
.NOTES
  Read AGENTS.md and the plan before running. Tested statically; requires
  installed compatible Codex CLI, local auth, and optional GitHub auth.
#>
param(
    [ValidateRange(1,24)][int]$MaxHours = 6,
    [ValidateRange(1,30)][int]$MaxTurns = 12
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $project

foreach ($file in @('AGENTS.md','CODEX_MASTER_PROMPT.md','AgentScope_全自主开发计划书.md')) {
    if (-not (Test-Path -LiteralPath (Join-Path $project $file))) {
        throw "Missing required file: $file. Copy the entire starter kit to this new project folder."
    }
}
foreach ($command in @('git','codex')) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "$command is unavailable. Install/login before running unattended."
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $project '.git'))) {
    & git init -b main
    if ($LASTEXITCODE -ne 0) { throw 'git init failed' }
}

$runDir = Join-Path $project '.codex-run'
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$ignoreFile = Join-Path $project '.gitignore'
$ignoreText = if (Test-Path $ignoreFile) { Get-Content -LiteralPath $ignoreFile -Raw } else { '' }
if ($ignoreText -notmatch '(?m)^\.codex-run/?\s*$') {
    Add-Content -LiteralPath $ignoreFile -Value "`n.codex-run/" -Encoding UTF8
}

$statePath = Join-Path $project 'docs/AUTONOMOUS_STATE.json'
$stopPath = Join-Path $runDir 'STOP'
$runStarted = Get-Date
$deadline = $runStarted.AddHours($MaxHours)
$markerFile = Join-Path $runDir 'started.flag'

function Read-State {
    if (-not (Test-Path -LiteralPath $statePath)) { return $null }
    try { return (Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json) }
    catch {
        Write-Warning "State JSON cannot be parsed yet: $($_.Exception.Message)"
        return $null
    }
}

function Get-ProgressMarker {
    $st = Read-State
    $phase = if ($null -ne $st) { [string]$st.phase } else { '' }
    $milestone = if ($null -ne $st) { [string]$st.last_completed_milestone } else { '' }
    $next = if ($null -ne $st) { [string]$st.next_action } else { '' }
    $gitHead = (& git rev-parse --verify --quiet HEAD)
    $workingSet = (& git status --porcelain 2>$null | Out-String).Trim()
    return "$phase|$milestone|$next|$gitHead|$workingSet"
}

function Test-VerifiedCompletion {
    $st = Read-State
    if ($null -eq $st) { return $false }
    if ([string]$st.overall_status -ne 'completed') { return $false }
    if ($st.quality_gates_passed -ne $true) { return $false }
    $url = [string]$st.verified_demo_url
    if ($url -notmatch '^https://') {
        Write-Warning 'Completion claimed without a verified HTTPS demo URL.'
        return $false
    }
    try {
        $res = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing -TimeoutSec 25
        if ([int]$res.StatusCode -eq 200) {
            Write-Host "VERIFIED: The published Demo responds HTTP 200 at $url" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Warning "Demo URL was not reachable from this machine: $($_.Exception.Message)"
    }
    return $false
}

Write-Host "AgentScope unattended run in $project" -ForegroundColor Cyan
Write-Host "Budget: $MaxHours hours, $MaxTurns turns. UTC start: $($runStarted.ToUniversalTime().ToString('o'))"
Write-Host "No --yolo or sandbox bypass is used. GitHub authentication/permissions may still block release."
Write-Host 'To stop after the current Codex turn: create .codex-run/STOP. Ctrl+C stops immediately.'

$round = 0
$stagnation = 0
while ((Get-Date) -lt $deadline -and $round -lt $MaxTurns) {
    if (Test-Path -LiteralPath $stopPath) {
        Write-Warning 'STOP file found; exiting without starting another Codex turn.'
        break
    }
    if (Test-VerifiedCompletion) { break }
    $st = Read-State
    if ($null -ne $st -and [string]$st.overall_status -eq 'blocked') {
        Write-Warning 'Codex marked all remaining tasks blocked; check docs/BLOCKERS.md. No unsafe retries.'
        break
    }

    $round++
    $before = Get-ProgressMarker
    $baseName = 'turn-{0:D2}-{1}' -f $round,(Get-Date -Format 'yyyyMMdd-HHmmss')
    $logPath = Join-Path $runDir "$baseName.jsonl"
    $lastMessage = Join-Path $runDir "$baseName.last.md"
    Write-Host "`n=== Starting Codex turn $round/$MaxTurns at $(Get-Date) ===" -ForegroundColor Yellow
    $exitCode = 1
    try {
        if (-not (Test-Path -LiteralPath $markerFile)) {
            # The complete task is in repository files; use an ASCII bootstrap
            # instruction for compatibility with older Windows shell encodings.
            $bootstrap = 'Read AGENTS.md and CODEX_MASTER_PROMPT.md in this workspace, then execute the full project-scoped autonomous development task continuously. Do not pause at ordinary milestones. Maintain docs/AUTONOMOUS_STATE.json. Respect all safety and release gates.'
            & codex exec --approve-for-me --json --output-last-message $lastMessage $bootstrap 2>&1 |
                Tee-Object -FilePath $logPath
            $exitCode = $LASTEXITCODE
            # Record that a session was attempted; if it was not persisted,
            # the next resume may fail and the script will stop after bounded retries.
            if ($exitCode -eq 0) {
                Set-Content -LiteralPath $markerFile -Value 'Started a persisted Codex execution session.' -Encoding UTF8
            }
        } else {
            $continuation = 'Continue from docs/AUTONOMOUS_STATE.json, docs/WORKLOG.md and the Git history. Execute the next safe incomplete milestone without asking for routine confirmation. Repair failures, verify honestly, preserve security boundaries, and keep progress files current.'
            & codex exec --approve-for-me --json resume --last $continuation 2>&1 |
                Tee-Object -FilePath $logPath
            $exitCode = $LASTEXITCODE
        }
    } catch {
        Write-Warning "Codex launch/continue exception: $($_.Exception.Message)"
    }

    Write-Host "Codex turn $round exited with code $exitCode. Raw transcript: $logPath" -ForegroundColor Cyan
    if (Test-VerifiedCompletion) { break }
    $after = Get-ProgressMarker
    if ($before -eq $after) { $stagnation++ } else { $stagnation = 0 }
    if ($stagnation -ge 3) {
        Write-Warning 'No recorded milestone/Git progress over three turns. Stopping rather than looping indefinitely.'
        break
    }
    if ((Get-Date) -ge $deadline) { break }
    Start-Sleep -Seconds 2
}

$finalState = Read-State
Write-Host "`n=== AgentScope experiment ended ===" -ForegroundColor Cyan
Write-Host "Turns attempted: $round of $MaxTurns"
Write-Host "Elapsed: $([math]::Round(((Get-Date)-$runStarted).TotalMinutes,1)) min"
if ($null -ne $finalState) {
    Write-Host "Phase: $($finalState.phase) | Overall: $($finalState.overall_status)"
    Write-Host "Next task: $($finalState.next_action)"
    if ($finalState.blockers) { Write-Host "Blockers: $($finalState.blockers -join '; ')" }
} else {
    Write-Warning 'No valid docs/AUTONOMOUS_STATE.json found. Inspect the most recent .codex-run log.'
}
Write-Host 'Review docs/WORKLOG.md, docs/BLOCKERS.md, and docs/release-report.md if present.'
Write-Host 'After resolving blockers, rerun this script from the same folder. Do not delete session data.'

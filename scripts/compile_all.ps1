# PharmaClear - Compile All Smart Contracts
# This script works around Windows App Execution Alias issues with Python

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  PharmaClear Smart Contract Compilation" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Create output directory
$outputDir = "smart_contracts\artifacts"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
Write-Host "📁 Output directory: $outputDir`n" -ForegroundColor Yellow

# List of contracts to compile
$contracts = @(
    "layer0_ingestion.py",
    "layer0_enhanced.py",
    "layer1_rebate.py",
    "layer2 _escrow.py",
    "layer3_audit.py",
    "layer4_governance.py",
    "layer5_crossborder.py"
)

$compiled = 0
$failed = 0

foreach ($contract in $contracts) {
    $contractPath = "smart_contracts\$contract"

    if (Test-Path $contractPath) {
        Write-Host "🔨 Compiling: $contract..." -ForegroundColor White

        # Use AlgoKit compile with output directory
        $result = algokit compile python $contractPath --out-dir $outputDir 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Success`n" -ForegroundColor Green
            $compiled++
        } else {
            Write-Host "   ❌ Failed" -ForegroundColor Red
            Write-Host "   Error: $result`n" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host "⚠️  Skipping: $contract (not found)`n" -ForegroundColor Yellow
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Compilation Summary" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Compiled: $compiled" -ForegroundColor Green
Write-Host "❌ Failed: $failed" -ForegroundColor Red

if ($failed -gt 0) {
    Write-Host "`n⚠️  Some contracts failed to compile." -ForegroundColor Yellow
    Write-Host "This may be due to Windows App Execution Alias issues.`n" -ForegroundColor Yellow
    Write-Host "To fix:" -ForegroundColor Cyan
    Write-Host "1. Open Windows Settings" -ForegroundColor White
    Write-Host "2. Search for 'App execution aliases'" -ForegroundColor White
    Write-Host "3. Disable 'python.exe' and 'python3.exe' aliases" -ForegroundColor White
    Write-Host "4. Re-run this script`n" -ForegroundColor White
} else {
    Write-Host "`n🎉 All contracts compiled successfully!" -ForegroundColor Green
    Write-Host "📁 TEAL files are in: $outputDir`n" -ForegroundColor Yellow
}

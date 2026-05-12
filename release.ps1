# release.ps1 - GitHub Release 创建脚本
param(
    [string]$version = "v1.0.0",
    [string]$exePath = "dist\DL_Function_Helper.exe"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    $ghPath = "C:\Program Files\GitHub CLI\gh.exe"
    if (Test-Path $ghPath) {
        Set-Alias gh $ghPath
    } else {
        Write-Host "请先安装 GitHub CLI: winget install GitHub.cli" -ForegroundColor Red
        exit 1
    }
}

if (-not $env:GH_TOKEN) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "  需要 GitHub Token 来创建 Release" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. 打开 https://github.com/settings/tokens"
    Write-Host "2. 点击 'Generate new token (classic)'"
    Write-Host "3. 勾选 'repo' 权限"
    Write-Host "4. 生成后复制 token"
    Write-Host ""
    $token = Read-Host -Prompt "请输入 GitHub Token"
    $env:GH_TOKEN = $token
}

if (-not (Test-Path $exePath)) {
    Write-Host "错误: 没有找到 $exePath ，请先运行 pyinstaller 打包" -ForegroundColor Red
    exit 1
}

Write-Host "正在创建 Release $version ..." -ForegroundColor Cyan

gh release create $version `
    --title "$version - Deep Learning Function Helper" `
    --notes "## 下载

点击下方 **DL_Function_Helper.exe** 下载，双击即可运行（无需安装 Python）。

## 功能

- 覆盖 PyTorch / NumPy / Matplotlib / OpenCV / Sklearn / Pandas 共 196 个函数
- 语义搜索，支持按功能描述查找函数
- IDE 风格语法高亮
- 桌面快捷方式支持
- 暗色主题 UI

## 源码

详见 [README](https://github.com/lucky-money-account/Deep-Learning-Function-Helper)" `
    --repo lucky-money-account/Deep-Learning-Function-Helper `
    $exePath

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Release 创建成功！" -ForegroundColor Green
    Write-Host "查看: https://github.com/lucky-money-account/Deep-Learning-Function-Helper/releases" -ForegroundColor Cyan
} else {
    Write-Host "Release 创建失败，请检查 Token 权限" -ForegroundColor Red
}

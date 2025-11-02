# Windows安全配置实用指南

## 快速配置检查清单

### 1. 基础安全设置

#### 1.1 启用BitLocker加密
```powershell
# 检查BitLocker状态
Get-BitLockerVolume

# 启用BitLocker（需要管理员权限）
Enable-BitLocker -MountPoint "C:" -EncryptionMethod Aes256 -RecoveryPasswordProtector -RecoveryKeyProtector

# 验证BitLocker状态
Get-BitLockerVolume -MountPoint "C:"
```

#### 1.2 配置Windows防火墙
```powershell
# 启用所有防火墙配置文件
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

# 创建基本入站规则
New-NetFirewallRule -DisplayName "Allow ICMP" -Direction Inbound -Protocol ICMPv4 -Action Allow
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# 创建基本出站规则
New-NetFirewallRule -DisplayName "Allow DNS" -Direction Outbound -Protocol UDP -RemotePort 53 -Action Allow
New-NetFirewallRule -DisplayName "Allow HTTP Out" -Direction Outbound -Protocol TCP -RemotePort 80 -Action Allow
New-NetFirewallRule -DisplayName "Allow HTTPS Out" -Direction Outbound -Protocol TCP -RemotePort 443 -Action Allow
```

#### 1.3 配置UAC（用户账户控制）
```powershell
# 检查UAC设置
$UACSettings = @{
    "ConsentPromptBehaviorAdmin" = (Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System).ConsentPromptBehaviorAdmin
    "ConsentPromptBehaviorUser" = (Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System).ConsentPromptBehaviorUser
    "EnableLUA" = (Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System).EnableLUA
}

# 配置UAC（推荐设置）
Set-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name ConsentPromptBehaviorAdmin -Value 2
Set-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name ConsentPromptBehaviorUser -Value 3
Set-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name EnableLUA -Value 1
Set-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name PromptOnSecureDesktop -Value 1
```

### 2. 身份认证配置

#### 2.1 配置Windows Hello
```powershell
# 检查Windows Hello状态
Get-WmiObject -Namespace "root\cimv2" -Class Win32_OptionalFeature | Where-Object {$_.Name -like "*Hello*"}

# 启用Windows Hello生物识别功能
Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Windows-Hello-For-Business" -All

# 配置Windows Hello策略
$HelloPolicy = @{
    "BiometricsEnabled" = 1
    "UseBiometrics" = 1
    "UsePIN" = 1
}
```

#### 2.2 配置多因素认证
```powershell
# 检查MFA配置状态
Get-MsolUser -UserPrincipalName "user@domain.com" | Select-Object StrongAuthenticationRequirements

# 启用MFA（需要Azure AD模块）
# Install-Module AzureAD
# Connect-MsolService
# Set-MsolUser -UserPrincipalName "user@domain.com" -StrongAuthenticationRequirements @(@{RelyingParty="*";State="Enabled"})
```

### 3. 应用程序安全

#### 3.1 配置Smart App Control
```powershell
# 检查Smart App Control状态
Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\CI\Config -Name "VulnerableDriverBlocklistEnable" -ErrorAction SilentlyContinue

# 启用Smart App Control
Set-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\CI\Config -Name "VulnerableDriverBlocklistEnable" -Value 1
```

#### 3.2 配置应用程序控制策略
```powershell
# 创建基本AppLocker策略
$AppLockerPolicy = @"
<?xml version="1.0" encoding="utf-8"?>
<AppLockerPolicy Version="1">
  <RuleCollection Type="Exe" EnforcementMode="AuditOnly">
    <FilePathRule Id="a61c36b8-2b4b-4b91-a5c5-1125c3d8b7c8" Name="All files" Description="" Action="Allow">
      <FilePath>%ProgramFiles%\*</FilePath>
    </FilePathRule>
    <FilePathRule Id="f3e675e6-2d4b-4b5d-a1e1-1c2b3e4d5f6a" Name="Windows files" Description="" Action="Allow">
      <FilePath>%SystemRoot%\*</FilePath>
    </FilePathRule>
  </RuleCollection>
</AppLockerPolicy>
"@

# 保存AppLocker策略
$AppLockerPolicy | Out-File -FilePath "C:\AppLockerPolicy.xml" -Encoding UTF8
```

### 4. 网络安全配置

#### 4.1 配置TLS设置
```powershell
# 检查TLS版本状态
Get-TlsCipherSuite | Where-Object {$_.Name -like "*TLS*"}

# 禁用旧版TLS（可选）
# Disable-TlsVersion -Version "1.0" -ErrorAction SilentlyContinue
# Disable-TlsVersion -Version "1.1" -ErrorAction SilentlyContinue
```

#### 4.2 配置DNS安全
```powershell
# 启用DNS over HTTPS
Set-DnsClientDohServerAddress -ServerAddress "8.8.8.8" -DohTemplate "https://dns.google/dns-query" -AllowFallbackToUdp $true -AutoUpgrade $true

# 配置DNS over TLS
Set-DnsClientDohServerAddress -ServerAddress "8.8.8.8" -DohTemplate "dot://dns.google" -AllowFallbackToUdp $true -AutoUpgrade $true
```

### 5. 系统安全强化

#### 5.1 配置安全策略
```powershell
# 导入安全模板
secedit /configure /cfg %windir%\inf\defltbase.inf /db defltbase.sdb /verbose

# 配置密码策略
net accounts /minpwlen:12 /maxpwage:90 /minpwage:1 /uniquepw:5 /complexity:on

# 配置账户锁定策略
net accounts /lockoutthreshold:5 /lockoutduration:30 /lockoutwindow:30 /reset
```

#### 5.2 启用安全审计
```powershell
# 启用基本审计策略
auditpol /set /category:"账户登录" /success:enable /failure:enable
auditpol /set /category:"账户管理" /success:enable /failure:enable
auditpol /set /category:"登录事件" /success:enable /failure:enable
auditpol /set /category:"对象访问" /success:enable /failure:enable
auditpol /set /category:"策略更改" /success:enable /failure:enable
auditpol /set /category:"系统事件" /success:enable /failure:enable
auditpol /set /category:"详细跟踪" /success:enable /failure:enable
auditpol /set /category:"特权使用" /success:enable /failure:enable
```

### 6. 监控和日志配置

#### 6.1 配置事件日志
```powershell
# 配置日志大小和保留策略
wevtutil sl Security /ms:104857600 /rt:true /max:100
wevtutil sl System /ms:52428800 /rt:true /max:50
wevtutil sl Application /ms:52428800 /rt:true /max:50

# 清除旧日志（谨慎使用）
# wevtutil cl Security
# wevtutil cl System
# wevtutil cl Application
```

#### 6.2 配置Windows Defender
```powershell
# 检查Windows Defender状态
Get-MpComputerStatus

# 启用实时保护
Set-MpPreference -DisableRealtimeMonitoring $false

# 配置扫描选项
Set-MpPreference -ScanAvgCPULoadFactor 50
Set-MpPreference -CheckForSignaturesBeforeRunningScan $true
Set-MpPreference -ScanRemovableDrives $true
Set-MpPreference -ScanOnlyAvailableIdle $true
```

### 7. 远程管理配置

#### 7.1 配置PowerShell远程处理
```powershell
# 启用PowerShell远程处理
Enable-PSRemoting -Force

# 配置防火墙例外
New-NetFirewallRule -DisplayName "PowerShell Remoting" -Direction Inbound -Protocol TCP -LocalPort 5985 -Action Allow

# 配置信任主机（谨慎使用）
# Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "LocalAccountTokenFilterPolicy" -Value 1
```

#### 7.2 配置远程桌面
```powershell
# 启用远程桌面
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0

# 配置网络级别身份验证
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "SecurityLayer" -Value 2

# 配置防火墙例外
New-NetFirewallRule -DisplayName "Remote Desktop - User Mode (TCP-In)" -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow
```

### 8. 自动化脚本

#### 8.1 一键安全加固脚本
```powershell
# Windows安全加固脚本
param(
    [switch]$EnableBitLocker,
    [switch]$EnableFirewall,
    [switch]$EnableUAC,
    [switch]$EnableAudit,
    [switch]$EnableDefender,
    [switch]$All
)

Write-Host "开始Windows安全加固..." -ForegroundColor Green

if ($All -or $EnableBitLocker) {
    Write-Host "启用BitLocker..." -ForegroundColor Yellow
    try {
        Enable-BitLocker -MountPoint "C:" -EncryptionMethod Aes256 -RecoveryPasswordProtector -RecoveryKeyProtector -ErrorAction Stop
        Write-Host "BitLocker启用成功" -ForegroundColor Green
    }
    catch {
        Write-Host "BitLocker启用失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

if ($All -or $EnableFirewall) {
    Write-Host "配置Windows防火墙..." -ForegroundColor Yellow
    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
    Write-Host "防火墙配置完成" -ForegroundColor Green
}

if ($All -or $EnableUAC) {
    Write-Host "配置UAC..." -ForegroundColor Yellow
    Set-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name ConsentPromptBehaviorAdmin -Value 2
    Set-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name ConsentPromptBehaviorUser -Value 3
    Set-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name EnableLUA -Value 1
    Write-Host "UAC配置完成" -ForegroundColor Green
}

if ($All -or $EnableAudit) {
    Write-Host "启用安全审计..." -ForegroundColor Yellow
    auditpol /set /category:"账户登录" /success:enable /failure:enable
    auditpol /set /category:"登录事件" /success:enable /failure:enable
    auditpol /set /category:"对象访问" /success:enable /failure:enable
    Write-Host "审计策略配置完成" -ForegroundColor Green
}

if ($All -or $EnableDefender) {
    Write-Host "配置Windows Defender..." -ForegroundColor Yellow
    Set-MpPreference -DisableRealtimeMonitoring $false
    Set-MpPreference -ScanAvgCPULoadFactor 50
    Write-Host "Defender配置完成" -ForegroundColor Green
}

Write-Host "安全加固完成！" -ForegroundColor Green
```

### 9. 验证检查清单

#### 9.1 安全状态检查
```powershell
# 检查BitLocker状态
Write-Host "=== BitLocker状态 ===" -ForegroundColor Cyan
Get-BitLockerVolume | Select-Object MountPoint,EncryptionPercentage,ProtectionStatus

# 检查防火墙状态
Write-Host "=== 防火墙状态 ===" -ForegroundColor Cyan
Get-NetFirewallProfile | Select-Object Name,Enabled

# 检查UAC状态
Write-Host "=== UAC状态 ===" -ForegroundColor Cyan
$UAC = Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
Write-Host "EnableLUA: $($UAC.EnableLUA)"
Write-Host "ConsentPromptBehaviorAdmin: $($UAC.ConsentPromptBehaviorAdmin)"

# 检查Windows Defender状态
Write-Host "=== Windows Defender状态 ===" -ForegroundColor Cyan
Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,BehaviorMonitorEnabled

# 检查审计策略
Write-Host "=== 审计策略 ===" -ForegroundColor Cyan
auditpol /get /category:"账户登录"
auditpol /get /category:"登录事件"
```

#### 9.2 漏洞扫描
```powershell
# 使用Windows内置工具检查基本安全设置
Write-Host "=== 安全基线检查 ===" -ForegroundColor Cyan

# 检查是否启用了安全功能
$SecurityChecks = @{
    "BitLocker" = (Get-BitLockerVolume -MountPoint "C:").ProtectionStatus -eq "On"
    "Firewall" = (Get-NetFirewallProfile -Name Domain).Enabled
    "UAC" = (Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System).EnableLUA -eq 1
    "Defender" = (Get-MpComputerStatus).AntivirusEnabled
    "SmartScreen" = (Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer -Name SmartScreenEnabled -ErrorAction SilentlyContinue).SmartScreenEnabled -ne "Off"
}

foreach ($Check in $SecurityChecks.GetEnumerator()) {
    $Status = if ($Check.Value) { "✓ 已启用" } else { "✗ 未启用" }
    Write-Host "$($Check.Key): $Status" -ForegroundColor $(if ($Check.Value) { "Green" } else { "Red" })
}
```

### 10. 故障排除

#### 10.1 常见问题解决

```powershell
# 问题1: BitLocker无法启用
# 解决方案: 检查TPM状态和硬件要求
Get-Tpm | Select-Object TpmPresent,TpmEnabled,TpmActivated

# 问题2: 防火墙规则不生效
# 解决方案: 重置防火墙配置
netsh advfirewall reset

# 问题3: UAC提示过于频繁
# 解决方案: 调整UAC设置
Set-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name ConsentPromptBehaviorAdmin -Value 5

# 问题4: Windows Defender被禁用
# 解决方案: 重新启用实时保护
Set-MpPreference -DisableRealtimeMonitoring $false
```

### 11. 维护和更新

#### 11.1 定期维护任务
```powershell
# 每日检查任务
$DailyTasks = @{
    "检查安全更新" = { Get-WUList | Where-Object {$_.IsDownloaded -eq $false} }
    "检查防火墙状态" = { Get-NetFirewallProfile | Where-Object {$_.Enabled -eq $false} }
    "检查BitLocker状态" = { Get-BitLockerVolume | Where-Object {$_.ProtectionStatus -eq "Off"} }
    "检查事件日志" = { Get-EventLog -LogName Security -Newest 10 | Where-Object {$_.EntryType -eq "FailureAudit"} }
}

# 每周检查任务
$WeeklyTasks = @{
    "安全基线检查" = { & "$env:SystemRoot\System32\sc.exe" query }
    "磁盘空间检查" = { Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID,FreeSpace,Size }
    "网络连接检查" = { Get-NetTCPConnection | Where-Object {$_.State -eq "Established"} }
}
```

#### 11.2 自动化报告
```powershell
# 生成安全状态报告
function Get-SecurityStatusReport {
    param(
        [string]$OutputPath = "C:\SecurityReport.html"
    )
    
    $Report = @"
<!DOCTYPE html>
<html>
<head>
    <title>Windows安全状态报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 10px; }
        .section { margin: 20px 0; }
        .success { color: green; }
        .warning { color: orange; }
        .error { color: red; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Windows安全状态报告</h1>
        <p>生成时间: $(Get-Date)</p>
    </div>
    
    <div class="section">
        <h2>BitLocker状态</h2>
        <table>
            <tr><th>驱动器</th><th>加密百分比</th><th>保护状态</th></tr>
"@
    
    # 添加BitLocker信息
    $BitLockerVolumes = Get-BitLockerVolume
    foreach ($Volume in $BitLockerVolumes) {
        $Status = if ($Volume.ProtectionStatus -eq "On") { "success" } else { "error" }
        $Report += "<tr><td>$($Volume.MountPoint)</td><td>$($Volume.EncryptionPercentage)%</td><td class='$Status'>$($Volume.ProtectionStatus)</td></tr>"
    }
    
    $Report += @"
        </table>
    </div>
    
    <div class="section">
        <h2>防火墙状态</h2>
        <table>
            <tr><th>配置文件</th><th>状态</th></tr>
"@
    
    # 添加防火墙信息
    $FirewallProfiles = Get-NetFirewallProfile
    foreach ($Profile in $FirewallProfiles) {
        $Status = if ($Profile.Enabled) { "success" } else { "error" }
        $StatusText = if ($Profile.Enabled) { "已启用" } else { "已禁用" }
        $Report += "<tr><td>$($Profile.Name)</td><td class='$Status'>$StatusText</td></tr>"
    }
    
    $Report += @"
        </table>
    </div>
</body>
</html>
"@
    
    $Report | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Host "安全状态报告已生成: $OutputPath" -ForegroundColor Green
}

# 生成报告
Get-SecurityStatusReport -OutputPath "C:\SecurityReport.html"
```

---

## 使用说明

1. **以管理员身份运行PowerShell**
2. **根据需要执行相应的配置命令**
3. **使用验证脚本检查配置结果**
4. **定期运行维护任务**
5. **生成安全状态报告进行审计**

## 注意事项

- ⚠️ 在生产环境中执行前请先在测试环境验证
- ⚠️ 某些配置可能需要重启才能生效
- ⚠️ 建议在执行前创建系统还原点
- ⚠️ 某些企业策略可能限制某些配置的更改

---

*此指南提供了Windows安全配置的基本框架，实际部署时请根据组织具体需求进行调整。*
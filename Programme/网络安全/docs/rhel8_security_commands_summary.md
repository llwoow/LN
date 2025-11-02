# RHEL 8 安全加固关键命令速查

## 核心安全配置命令

### 系统更新与基础安全
```bash
# 更新系统安全修复
yum update

# 启用防火墙
systemctl start firewalld && systemctl enable firewalld

# 禁用不必要服务
systemctl disable [service_name]

# 查看活动服务
systemctl list-units | grep service
```

### FIPS模式配置
```bash
# 启用FIPS模式
fips-mode-setup --enable

# 验证FIPS状态
fips-mode-setup --check

# 安装时启用FIPS（内核参数）
fips=1
```

### 加密策略管理
```bash
# 查看当前策略
update-crypto-policies --show

# 设置策略
update-crypto-policies --set FUTURE

# 重启应用策略
systemctl restart sshd
```

### 文件完整性检查（AIDE）
```bash
# 安装AIDE
yum install aide

# 初始化数据库
aide --init

# 重命名数据库
mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz

# 执行完整性检查
aide --check

# 更新数据库
aide --update
```

### 系统审计配置
```bash
# 启动auditd服务
systemctl start auditd && systemctl enable auditd

# 添加审计规则
auditctl -w /etc/passwd -p wa -k passwd_changes

# 查看审计日志
ausearch -k passwd_changes

# 生成审计报告
aureport -t
```

### LUKS磁盘加密
```bash
# 加密现有设备
cryptsetup luksFormat /dev/sdb

# 打开加密设备
cryptsetup luksOpen /dev/sdb encrypted_disk

# 格式化文件系统
mkfs.ext4 /dev/mapper/encrypted_disk

# 更改密码
cryptsetup luksChangeKey /dev/sdb
```

### USB设备保护（USBGuard）
```bash
# 安装USBGuard
yum install usbguard

# 生成初始策略
usbguard generate-policy > /etc/usbguard/rules.conf

# 启动服务
systemctl enable usbguard && systemctl start usbguard

# 允许特定设备
usbguard allow-device <device-id>

# 阻止USB设备
usbguard block-device <device-id>
```

### OpenSCAP合规扫描
```bash
# 安装OpenSCAP工具
yum install openscap-scanner scap-security-guide

# 查看可用配置文件
oscap info /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml

# 执行合规扫描
oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_ospp --report report.html /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml

# 自动修复
oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_ospp --remediate /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
```

### 漏洞扫描
```bash
# 下载RHSA OVAL定义
wget https://www.redhat.com/security/data/oval/v2/RHEL8/rhel-8.oval.xml.bz2

# 执行漏洞扫描
oscap oval eval --report vulnerability.html rhel-8.oval.xml
```

### 内核完整性（IMA/EVM）
```bash
# 检查TPM支持
cat /sys/class/tpm/tpm0/tpm_version_major

# 启用IMA/EVM（内核参数）
ima_policy=appraise_tcb ima_appraise=fix evm=fix

# 创建EVM密钥
keyctl add user evm-key "evm-key" @u
```

## 配置文件位置

| 功能 | 配置文件位置 |
|------|-------------|
| AIDE配置 | `/etc/aide.conf` |
| 审计配置 | `/etc/audit/auditd.conf` |
| 审计规则 | `/etc/audit/rules.d/` |
| USBGuard配置 | `/etc/usbguard/usbguard-daemon.conf` |
| USBGuard规则 | `/etc/usbguard/rules.conf` |
| 加密策略 | `/etc/crypto-policies/` |

## 关键日志文件

| 功能 | 日志文件位置 |
|------|-------------|
| 审计日志 | `/var/log/audit/audit.log` |
| 系统日志 | `/var/log/messages` |
| 安全日志 | `/var/log/secure` |

## 常用服务管理

```bash
# 启用并启动服务
systemctl enable --now [service_name]

# 检查服务状态
systemctl status [service_name]

# 重启服务
systemctl restart [service_name]
```

## 安全检查清单

- [ ] 系统已更新到最新安全补丁
- [ ] 防火墙已启用并配置
- [ ] 不必要的服务已禁用
- [ ] FIPS模式已启用（如需要）
- [ ] 加密策略已配置
- [ ] 文件完整性监控已设置
- [ ] 系统审计已启用
- [ ] 磁盘加密已配置
- [ ] USB设备保护已启用
- [ ] 合规性扫描已完成
- [ ] 漏洞扫描已执行
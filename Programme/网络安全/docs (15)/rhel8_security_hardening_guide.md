# Red Hat Enterprise Linux 8 安全加固技术指南

## 概述

本指南基于Red Hat官方Enterprise Linux 8安全加固文档，详细介绍了Linux系统的安全机制配置，包括SELinux、AppArmor、文件系统权限、用户管理等核心技术，以及具体的配置命令和策略示例。

## 目录

1. [安装期间和安装后安全配置](#1-安装期间和安装后安全配置)
2. [FIPS模式配置](#2-fips模式配置)
3. [系统范围加密策略](#3-系统范围加密策略)
4. [内核完整性子系统](#4-内核完整性子系统)
5. [系统审计](#5-系统审计)
6. [配置合规性和漏洞扫描](#6-配置合规性和漏洞扫描)
7. [AIDE文件完整性检查](#7-aide文件完整性检查)
8. [LUKS磁盘加密](#8-luks磁盘加密)
9. [USB设备保护](#9-usb设备保护)

---

## 1. 安装期间和安装后安全配置

### 1.1 磁盘分区策略

**安全分区建议：**
- 为裸机安装创建独立分区：`/boot`、`/`、`/home`、`/tmp`、`/var/tmp/`
- 虚拟/云环境中，分区是可选的，因为虚拟磁盘可以扩展

**关键安全考虑：**
- `/boot`分区不应加密，因为包含启动加载程序和内核镜像
- 如果`/boot`包含在加密的`/`分区中且不可用，系统无法启动
- 独立`/home`分区防止根分区损坏时的数据丢失
- 临时目录分离防止存储空间耗尽导致系统不稳定

### 1.2 网络安全配置

**安装期间网络限制：**
- 始终限制暴露在最近必要的网络区域
- 最安全选择：'no network'区域（断开连接的机器）
- 如果需要网络，优先选择LAN/Intranet而非Internet连接

### 1.3 最小化安装原则

**安装策略：**
- 仅安装需要的软件包，每个软件组件都可能包含漏洞
- 必要时可以后续添加软件包

### 1.4 后安装安全程序

**系统更新：**
```bash
# 更新系统安全修复
yum update
```

**防火墙服务管理：**
```bash
# 启用并启动firewalld
systemctl start firewalld
systemctl enable firewalld
```

**服务硬化：**
```bash
# 禁用不必要服务
systemctl disable [service_name]
# 示例：禁用打印机服务（如果未安装打印机）
systemctl disable cups
```

**活动服务审查：**
```bash
# 监控活动服务
systemctl list-units | grep service
```

**SMT禁用（CPU安全）：**
- 通过Web控制台禁用同步多线程(SMT)
- 缓解CPU安全漏洞如L1TF和MDS攻击
- 权衡：禁用SMT可能降低系统性能但提供增强的安全性

---

## 2. FIPS模式配置

### 2.1 FIPS 140标准概述

FIPS 140确保加密工具正确实现算法并通过运行时自检。

### 2.2 安装时启用FIPS

**内核参数：**
```bash
# 在RHEL安装期间添加内核参数
fips=1
```

### 2.3 安装后切换到FIPS模式

**命令配置：**
```bash
# 启用FIPS模式
fips-mode-setup --enable

# 验证FIPS模式状态
fips-mode-setup --check

# 配置更改后需要重启系统
```

### 2.4 容器中的FIPS支持

**版本差异：**
- RHEL 8.1-8.2：需要手动策略更新
- RHEL 8.4+：自动支持

**重要限制：**
- FIPS策略影响加密算法选择（例如：不允许ChaCha20）
- 一旦启用FIPS模式，无法在不重新安装系统的情况下禁用
- 主机系统必须处于FIPS模式，容器FIPS功能才能工作

### 2.5 非FIPS兼容应用程序

文档列出了使用不符合FIPS 140-2标准的加密的应用程序（如FreeRADIUS、Ghostscript等）。

---

## 3. 系统范围加密策略

### 3.1 预定义策略级别

**四种预定义策略：**
1. **DEFAULT**：安全的当前设置
2. **LEGACY**：与RHEL 5及更早版本的最大兼容性
3. **FUTURE**：更严格的面向未来的安全性
4. **FIPS**：FIPS 140合规性

**策略支持差异：**
- **LEGACY**：允许TLS 1.0/1.1、DSA、3DES、RC4
- **FUTURE**：在签名中不允许SHA-1，要求最小3072位RSA/DH密钥
- **FIPS:OSPP**：为通用标准认证提供额外限制

### 3.2 命令行工具配置

**策略管理命令：**
```bash
# 显示当前策略
update-crypto-policies --show

# 设置策略
update-crypto-policies --set <POLICY>
# 示例：update-crypto-policies --set FUTURE

# 策略更改后需要重启系统
```

### 3.3 Web控制台配置

通过Web控制台概述页面中的配置卡进行配置：
- 下拉选择策略
- 应用并重启按钮

### 3.4 子策略自定义

**作用域策略允许对特定协议和算法进行细粒度控制：**
```bash
# NO-SHA1策略模块（从RHEL 8.3开始）
# 在签名算法中禁用SHA-1，同时保留HMAC使用
```

### 3.5 自定义策略创建

**策略文件位置：**
- `/etc/crypto-policies/policies/`目录
- 从预定义模板复制

### 3.6 RHEL系统角色自动化

**crypto_policies RHEL系统角色：**
- 使用Ansible playbook自动化策略配置
- 启用策略配置的标准化方法

---

## 4. 内核完整性子系统

### 4.1 IMA和EVM概述

**内核完整性子系统包括：**
- **IMA（完整性测量架构）**：检测文件篡改和收集访问日志
- **EVM（扩展验证模块）**：保护文件元数据

### 4.2 IMA功能

**IMA提供三个功能：**
1. **IMA-Measurement**：哈希/签名收集
2. **IMA-Appraisal**：文件完整性验证
3. **IMA-Audit**：审计日志存储

### 4.3 EVM保护

**EVM保护：**
- 保护包括security.ima和security.selinux在内的扩展属性
- 通过在security.evm中存储参考哈希来保护文件元数据

### 4.4 密钥类型

**可信密钥：**
- 需要TPM硬件
- 使用TPM的存储根密钥进行加密

**加密密钥：**
- 使用内核AES加密
- 不需要TPM，速度更快但可能安全性较低

### 4.5 启用IMA和EVM

**TPM 2.0支持验证：**
```bash
# 检查TPM支持
cat /sys/class/tpm/tpm0/tpm_version_major
```

**内核参数配置：**
```bash
# 必须一起启用IMA和EVM
ima_policy=appraise_tcb ima_appraise=fix evm=fix
```

**EVM密钥要求：**
- EVM需要名为'evm-key'的特定加密密钥才能正常工作

### 4.6 系统重新标记

启用IMA/EVM后需要重新标记系统以确保正确功能。

---

## 5. 系统审计

### 5.1 Linux审计系统架构

**系统组成：**
- 内核端系统调用处理
- 用户空间应用程序和工具

### 5.2 auditd配置

**配置文件：**
```bash
# 主要配置文件
/etc/audit/auditd.conf
```

**关键参数：**
- 日志文件管理
- 磁盘空间处理

### 5.3 审计规则定义

**auditctl命令：**
```bash
# 定义和执行审计规则
auditctl [选项] 规则
```

**规则文件位置：**
- `/etc/audit/rules.d/`目录中的文件
- 通过`augenrules`编译为`/etc/audit/audit.rules`

### 5.4 持久化规则

**augenrules管理：**
```bash
# 编译规则
augenrules

# 禁用augenrules（如果需要）
```

### 5.5 预配置规则

**合规标准规则文件：**
```bash
# 位置
/usr/share/audit/sample-rules/

# 包含的合规标准
# OSPP, PCI DSS, STIG等
```

### 5.6 审计日志分析

**分析工具：**
- `ausearch`：搜索审计日志
- `aureport`：生成审计报告
- `aulast`：显示最后登录信息

**日志文件位置：**
```bash
/var/log/audit/audit.log
```

### 5.7 监控用例

**具体用例包括：**
- 监控文件访问
- 系统调用
- 用户命令
- 登录时间

---

## 6. 配置合规性和漏洞扫描

### 6.1 OpenSCAP工具套件

**工具组件：**
- **SCAP Workbench**：图形界面
- **OpenSCAP库**：oscap命令行工具
- **SCAP Security Guide (SSG)**：安全指南
- **Script Check Engine (SCE)**：脚本检查引擎

### 6.2 漏洞扫描

**本地漏洞扫描：**
```bash
oscap oval eval --report vulnerability.html rhel-8.oval.xml
```

**远程漏洞扫描：**
```bash
oscap-ssh <username>@<hostname> <port> oval eval --report <scan-report.html> rhel-8.oval.xml
```

### 6.3 配置合规性扫描

**查看配置文件：**
```bash
oscap info /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
```

**合规性评估：**
```bash
oscap xccdf eval --report <scan-report.html> --profile <profileID> /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
```

### 6.4 系统修复

**自动修复：**
```bash
oscap xccdf eval --profile <profileID> --remediate /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
```

**Ansible Playbook修复：**
```bash
ANSIBLE_COLLECTIONS_PATH=/usr/share/rhc-worker-playbook/ansible/collections/ansible_collections/ ansible-playbook -i "localhost," -c local /usr/share/scap-security-guide/ansible/rhel8-playbook-<profileID>.yml
```

### 6.5 自定义修复脚本

**创建Ansible修复：**
```bash
oscap xccdf generate fix --fix-type ansible --result-id <result-id> --output <profile-remediations.yml> <profile-results.xml>
```

**创建Bash修复脚本：**
```bash
oscap xccdf generate fix --fix-type bash --result-id <result-id> --output <profile-remediations.sh> <profile-results.xml>
```

### 6.6 容器扫描

**容器漏洞扫描：**
```bash
oscap-podman <container-id> oval eval --report vulnerability.html rhel-8.oval.xml
```

**容器合规性扫描：**
```bash
oscap-podman <ID> xccdf eval --report <scan-report.html> --profile <profileID> /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
```

### 6.7 支持的配置文件

**包含的配置文件：**
- CIS
- HIPAA
- OSPP
- PCI-DSS
- DISA STIG
- 其他特定版本兼容性配置文件

---

## 7. AIDE文件完整性检查

### 7.1 AIDE概述

**AIDE（高级入侵检测环境）：**
- 创建系统文件数据库
- 用于确保文件完整性和检测系统入侵

### 7.2 AIDE安装

**安装命令：**
```bash
# 启用AppStream仓库
yum install aide
```

### 7.3 数据库初始化

**初始数据库生成：**
```bash
# 创建初始数据库
aide --init

# 数据库位置
/var/lib/aide/aide.db.new.gz

# 重命名数据库
mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
```

### 7.4 配置文件

**配置文件位置：**
```bash
/etc/aide.conf
```

### 7.5 完整性检查

**执行检查：**
```bash
aide --check
```

**计划检查：**
```bash
# 通过cron每日或每周检查
05 4 * * * root /usr/sbin/aide --check
```

### 7.6 数据库更新

**更新数据库：**
```bash
aide --update
```

### 7.7 安全考虑

**安全存储：**
- 数据库、配置和二进制文件应存储在只读媒体上

### 7.8 AIDE与IMA比较

**差异：**
- **IMA**：提供检测和预防，而AIDE仅检测修改
- **AIDE**：在本地系统上工作，而IMA可以在本地和远程系统上工作
- **AIDE**：使用基于规则的比较，而IMA使用文件哈希值进行验证

---

## 8. LUKS磁盘加密

### 8.1 LUKS概述

**LUKS（Linux统一密钥设置）：**
- 提供块设备加密
- 多个用户密钥解密主密钥进行批量加密

### 8.2 默认加密设置

**默认密码：**
- aes-xts-plain64
- 512位密钥大小（LUKS和Anaconda XTS模式）

**可用密码：**
- AES
- Twofish
- Serpent

### 8.3 LUKS版本差异

**LUKS1与LUKS2：**
- **LUKS2**：RHEL 8中的默认格式
- **LUKS1**：为兼容性保持支持

**功能差异：**
- **LUKS2**：支持在线重新加密，LUKS1不支持
- **LUKS1**：提供8个密钥槽
- **LUKS2**：提供最多32个密钥槽

### 8.4 LUKS2重新加密选项

**三种弹性模式：**
1. **checksum**：默认模式
2. **journal**：最安全
3. **none**：最快

### 8.5 现有数据加密

**现有数据加密要求：**
- 卸载文件系统
- 为LUKS头创建空间

### 8.6 分离头

**分离头提供额外安全性：**
- 将头与加密数据分开存储

### 8.7 密码短语管理

**管理方法：**
- Web控制台
- 命令行

### 8.8 Ansible自动化

**Ansible存储角色：**
- 可以自动化LUKS2卷创建与加密

### 8.9 cryptsetup工具

**LUKS操作工具：**
- 用于大多数LUKS操作
- LUKS1与LUKS2的不同命令

---

## 9. USB设备保护

### 9.1 USBGuard框架

**组件：**
- 具有IPC接口的系统服务
- 命令行工具
- 策略规则语言
- C++ API

### 9.2 USBGuard安装

**安装过程：**
```bash
# 安装USBGuard
yum install usbguard

# 生成初始策略
usbguard generate-policy

# 启用并启动服务
systemctl enable usbguard
systemctl start usbguard
```

### 9.3 CLI设备管理

**设备管理命令：**
```bash
# 列出设备
usbguard list-devices

# 允许设备
usbguard allow-device

# 阻止设备
usbguard block-device

# 拒绝设备
usbguard reject-device
```

### 9.4 永久设备授权

**永久授权选项：**
```bash
# 使用-p选项进行永久授权
usbguard allow-device -p <device-id>
usbguard block-device -p <device-id>
usbguard reject-device -p <device-id>
```

### 9.5 自定义策略创建

**策略生成：**
```bash
# 生成无哈希策略
usbguard generate-policy --no-hashes

# 编辑策略文件
/etc/usbguard/rules.conf
```

### 9.6 结构化策略组织

**策略目录：**
```bash
# 按字母顺序组织的.conf文件
/etc/usbguard/rules.d/
```

### 9.7 用户和组授权

**IPC接口授权：**
```bash
# 通过配置文件配置
/etc/usbguard/usbguard-daemon.conf

# 使用IPCAllowGroups或IPCAllowedUsers
```

**高级用户权限：**
```bash
# 使用usbguard add-user命令
usbguard add-user --devices --policy --exceptions
```

### 9.8 审计日志集成

**审计后端配置：**
```bash
# 在守护进程配置中更改AuditBackend
# 从FileAudit更改为LinuxAudit
```

### 9.9 SELinux配置

**SELinux布尔值：**
```bash
# 确保启用usbguard_daemon_write_rules布尔值
# 用于规则管理
```

### 9.10 设备授权术语

**授权类型：**
- **block**：暂时不交互
- **reject**：完全忽略设备

### 9.11 策略规则示例

**规则示例：**
```bash
# 允许大容量存储设备
allow with-interface equals { 08:*:* }
```

---

## 总结

本指南涵盖了Red Hat Enterprise Linux 8的全面安全加固技术，包括：

1. **安装安全**：磁盘分区、网络安全、最小化安装
2. **加密合规**：FIPS模式、加密策略
3. **系统完整性**：内核完整性子系统、文件完整性检查
4. **审计监控**：Linux审计系统配置和管理
5. **合规扫描**：OpenSCAP工具、漏洞扫描、合规评估
6. **数据保护**：LUKS磁盘加密、USB设备保护

每个章节都提供了具体的配置命令和策略示例，可用于实际的安全加固实施。建议根据具体的安全需求和合规要求选择相应的配置选项。

---

**文档来源：** Red Hat Enterprise Linux 8 Security Hardening Documentation  
**版本：** RHEL 8  
**更新日期：** 2025年11月2日
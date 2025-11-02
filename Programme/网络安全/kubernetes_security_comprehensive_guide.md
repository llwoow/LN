# Kubernetes安全机制综合指南

## 概述

本指南基于Kubernetes官方安全文档，全面介绍了Kubernetes的安全机制，包括RBAC配置、网络策略、Pod安全策略、Secrets管理、准入控制和审计等关键技术细节。

## 1. Kubernetes安全机制概览

### 1.1 核心安全组件

Kubernetes提供了多层次的安全控制机制：

- **控制平面保护**：API访问控制、TLS加密、静态数据加密
- **Secrets管理**：敏感数据的安全存储和管理
- **工作负载保护**：Pod安全标准、运行时类、网络策略
- **准入控制**：API请求验证和变更
- **审计日志**：集群活动的安全相关记录
- **安全策略**：网络策略和验证准入策略

## 2. RBAC（基于角色的访问控制）

### 2.1 核心原则

**最小权限原则**：
- 分配最少的RBAC权限
- 使用命名空间级别的权限和RoleBindings而不是ClusterRoleBindings
- 避免通配符权限，特别是对所有资源的权限

### 2.2 安全配置示例

```yaml
# 最小权限的Role示例
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

# RoleBinding示例
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: "jane"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### 2.3 权限提升风险

**高风险动词**：
- `escalate`：绕过内置RBAC保护
- `bind`：创建角色绑定
- `impersonate`：模拟其他用户

**危险操作**：
- 列出Secrets
- 创建工作负载
- 创建持久卷
- 访问代理子资源

### 2.4 安全最佳实践

```bash
# 避免使用cluster-admin账户
# 错误示例：不要这样做
kubectl create clusterrolebinding cluster-admin-binding \
  --clusterrole=cluster-admin --user=admin

# 使用模拟权限替代
kubectl auth can-i get pods --as=admin --as-group=system:masters

# 定期审查RBAC设置
kubectl auth can-i --list --as=system:serviceaccount:default:default
```

## 3. 网络策略（Network Policies）

### 3.1 网络策略概述

网络策略控制Pod之间的网络流量，支持TCP、UDP和SCTP协议。

### 3.2 基本配置示例

```yaml
# 拒绝所有入口流量的默认策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress

# 允许特定命名空间的入口流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-namespace
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: frontend

# 允许特定Pod的出口流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-to-pods
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          role: backend
    ports:
    - protocol: TCP
      port: 5432
```

### 3.3 高级配置示例

```yaml
# 使用IP块的网络策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-external
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 172.17.0.0/16
        except:
        - 172.17.1.0/24

# 多端口网络策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: multiport-egress
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          role: database
    ports:
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 3306
```

### 3.4 网络策略特性

- **策略是累加的**：多个策略可以同时生效
- **双向控制**：连接需要源Pod的出口策略和目标Pod的入口策略都允许
- **端口范围支持**：使用endPort字段（Kubernetes v1.25+）
- **命名空间选择**：通过标签选择命名空间

## 4. Pod安全策略（Pod Security Standards）

### 4.1 安全级别

**三个安全级别**：
- **Privileged**：无限制
- **Baseline**：最小限制，防止已知权限提升
- **Restricted**：严格限制，强制执行当前Pod硬化最佳实践

### 4.2 命名空间标签配置

```yaml
# 配置命名空间为baseline级别
apiVersion: v1
kind: Namespace
metadata:
  name: secure-namespace
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/warn: baseline

# 配置命名空间为restricted级别
apiVersion: v1
kind: Namespace
metadata:
  name: strict-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 4.3 Pod安全配置示例

```yaml
# 符合baseline标准的Pod
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  containers:
  - name: app
    image: nginx
    securityContext:
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
  # 禁止特权容器
  # 禁止主机路径挂载
  # 禁止主机网络命名空间

# 符合restricted标准的Pod
apiVersion: v1
kind: Pod
metadata:
  name: very-secure-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
  containers:
  - name: app
    image: nginx
    securityContext:
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

### 4.4 Pod安全准入控制器

```yaml
# 启用Pod安全准入控制器
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: PodSecurity
  configuration:
    apiVersion: pod-security.admission.k8s.io/v1
    kind: PodSecurityConfiguration
    defaults:
      enforce: "baseline"
      enforce-version: "latest"
      audit: "baseline"
      audit-version: "latest"
      warn: "baseline"
      warn-version: "latest"
    exemptions:
      usernames: ["admin"]
      runtimeClassNames: ["*"]
      namespaces: ["kube-system"]
```

## 5. Secrets管理

### 5.1 Secrets类型

**内置Secret类型**：
- **Opaque**：任意用户定义数据
- **ServiceAccount Token**：服务账户令牌
- **Docker Config**：Docker配置
- **Basic Auth**：基本认证
- **SSH Auth**：SSH认证
- **TLS**：TLS证书
- **Bootstrap Token**：引导令牌

### 5.2 创建Secrets

```bash
# 使用kubectl创建Secret
kubectl create secret generic my-secret \
  --from-literal=username=admin \
  --from-literal=password=secret123

# 使用配置文件创建Secret
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: YWRtaW4=
  password: c2VjcmV0MTIz
EOF

# 使用Kustomize创建Secret
kubectl apply -k .
```

### 5.3 使用Secrets

```yaml
# 作为环境变量使用
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
  - name: app
    image: nginx
    env:
    - name: USERNAME
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: username
    - name: PASSWORD
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: password

# 作为挂载卷使用
apiVersion: v1
kind: Pod
metadata:
  name: secret-volume-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: secret-volume
      mountPath: "/etc/secrets"
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: my-secret
```

### 5.4 Secrets最佳实践

```yaml
# 启用静态加密
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64-encoded-32-byte-key>
  - identity: {}

# 限制Secret访问的RBAC
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["my-secret"]
  verbs: ["get"]

# 不可变Secret
apiVersion: v1
kind: Secret
metadata:
  name: immutable-secret
type: Opaque
immutable: true
data:
  username: YWRtaW4=
```

## 6. 准入控制

### 6.1 Pod安全准入

```yaml
# 命名空间配置示例
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/version: v1.25

# 豁免配置
apiVersion: v1
kind: Namespace
metadata:
  name: privileged
  labels:
    pod-security.kubernetes.io/enforce: privileged
    pod-security.kubernetes.io/audit: privileged
    pod-security.kubernetes.io/warn: privileged
```

### 6.2 验证准入策略

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: validatingadmissionpolicies.example.com
spec:
  group: example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              key:
                type: string
  scope: Namespaced
  names:
    plural: validatingadmissionpolicies
    singular: validatingadmissionpolicy
    kind: ValidatingAdmissionPolicy
    shortNames:
    - vwp

---
apiVersion: example.com/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: "example-policy.example.com"
spec:
  matchConstraints:
    resourceRules:
    - apiGroups: ["apps"]
      apiVersions: ["v1"]
      operations: ["CREATE", "UPDATE"]
      resources: ["deployments"]
  validations:
  - expression: "object.spec.replicas <= 10"
    message: "不能创建超过10个副本的部署"
```

## 7. 审计日志

### 7.1 审计策略配置

```yaml
# 审计策略文件
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# 记录所有请求的元数据
- level: Metadata
  omitStages:
  - RequestReceived
  resources:
  - group: ""
    resources: ["pods", "services", "configmaps"]

# 记录所有配置更改的完整信息
- level: RequestResponse
  omitStages:
  - RequestReceived
  resources:
  - group: ""
    resources: ["secrets", "serviceaccounts"]

# 记录所有认证和授权决策
- level: Request
  omitStages:
  - RequestReceived
  resources:
  - group: "rbac.authorization.k8s.io"
    resources: ["roles", "rolebindings", "clusterroles", "clusterrolebindings"]
```

### 7.2 API服务器配置

```bash
# 启用审计日志
kube-apiserver \
  --audit-policy-file=/etc/kubernetes/audit-policy.yaml \
  --audit-log-path=/var/log/kubernetes/audit.log \
  --audit-log-maxage=30 \
  --audit-log-maxbackup=10 \
  --audit-log-maxsize=100 \
  --audit-webhook-config-file=/etc/kubernetes/audit-webhook.yaml \
  --audit-webhook-initial-backoff=10s \
  --audit-webhook-batch-buffer-size=30000 \
  --audit-webhook-batch-max-size=1000 \
  --audit-webhook-batch-max-wait=5s
```

### 7.3 Webhook后端配置

```yaml
# Webhook配置
apiVersion: v1
kind: Config
clusters:
- cluster:
    server: https://audit.example.com/webhook
  name: audit
contexts:
- context:
    cluster: audit
    user: audit
  name: audit
current-context: audit
kind: Config
preferences: {}
users:
- name: audit
  user:
    tokenFile: /var/run/secrets/kubernetes.io/serviceaccount/token
```

## 8. 云提供商安全

### 8.1 AWS安全

- IAM角色和服务账户
- VPC CNI网络策略
- EKS安全组
- Secrets Manager集成

### 8.2 Google Cloud安全

- Workload Identity
- GKE安全功能
- Cloud KMS集成
- VPC防火墙规则

### 8.3 Azure安全

- Azure AD集成
- AKS网络安全组
- Key Vault集成
- Azure Policy

## 9. 安全检查清单

### 9.1 集群安全检查

```bash
# 检查API服务器安全配置
kubectl get configmap -n kube-system apiserver-config -o yaml

# 检查RBAC配置
kubectl auth can-i --list

# 检查Pod安全标准
kubectl get namespace -o jsonpath='{range .items[?(@.metadata.labels.pod-security\.kubernetes\.io/enforce)]}{.metadata.name}{"\t"}{.metadata.labels.pod-security\.kubernetes\.io/enforce}{"\n"}{end}'

# 检查网络策略
kubectl get networkpolicy --all-namespaces

# 检查静态加密
kubectl get secret -o jsonpath='{.items[*].metadata.annotations.kubernetes\.io/encryption}'
```

### 9.2 应用安全检查

```bash
# 检查容器安全上下文
kubectl get pod -o jsonpath='{range .items[*].spec.containers[*].securityContext}{.runAsNonRoot}{"\t"}{.allowPrivilegeEscalation}{"\t"}{.capabilities\.drop}{"\n"}{end}'

# 检查Secrets使用
kubectl get pod -o jsonpath='{range .items[*].spec.volumes[*].secret}{.secretName}{"\n"}{end}'

# 检查镜像拉取策略
kubectl get pod -o jsonpath='{range .items[*].spec.containers[*].imagePullPolicy}{.}{"\n"}{end}'
```

## 10. 总结

Kubernetes安全是一个多层次的体系，需要从以下方面进行综合考虑：

1. **身份验证和授权**：使用RBAC实现最小权限原则
2. **网络隔离**：通过NetworkPolicy控制Pod间通信
3. **工作负载安全**：使用Pod安全标准保护容器
4. **敏感数据保护**：正确使用和管理Secrets
5. **准入控制**：实施策略验证和变更控制
6. **审计监控**：配置审计日志进行安全监控
7. **云安全集成**：利用云提供商的安全功能

通过正确配置这些安全机制，可以构建一个安全、可靠的Kubernetes集群环境。

---

**参考链接**：
- [Kubernetes官方安全文档](https://kubernetes.io/docs/concepts/security/)
- [RBAC最佳实践](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [网络策略](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Pod安全标准](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Secrets管理](https://kubernetes.io/docs/concepts/configuration/secret/)
- [审计日志](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
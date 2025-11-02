# Linux内核I/O调度器技术摘要

## 核心技术架构

### blk-mq多队列机制
- **双层队列架构**: 软件分段队列(blk_mq_ctx) + 硬件调度队列(blk_mq_hw_ctx)
- **并行处理**: 每CPU/NUMA节点独立队列，显著降低锁争用
- **标签机制**: 基于唯一标签的完成机制，避免线性搜索
- **核心API**: `blk_mq_submit_bio()`, `blk_mq_run_hw_queue()`, `blk_mq_complete_request()`

## I/O调度算法实现

### BFQ调度器
- **算法基础**: B-WF2Q+算法，增强型红黑树实现O(log N)复杂度
- **比例份额**: 基于权重公平分配设备带宽
- **低延迟模式**: 优先处理交互式应用，支持权重提升
- **早期队列合并**: EQM机制合并交错I/O为顺序I/O
- **关键参数**: `slice_idle`, `low_latency`, `max_budget`, `timeout_sync`

### Deadline调度器
- **截止时间机制**: 读/写请求设置超时时间
- **批处理策略**: 按扇区顺序处理请求批次
- **读写平衡**: 优先读请求，通过`writes_starved`避免写饥饿
- **关键参数**: `read_expire`, `write_expire`, `fifo_batch`, `front_merges`

### Kyber调度器
- **极简设计**: 仅两个目标延迟参数
- **延迟控制**: `read_lat_nsec`, `write_lat_nsec`
- **现代优化**: 专为SSD设计，专注延迟优化

## 核心数据结构

### blk-mq关键结构
```c
struct blk_mq_ctx {
    spinlock_t lock;
    struct list_head dispatch;
    struct request_queue *queue;
    unsigned int cpu;
};

struct blk_mq_hw_ctx {
    spinlock_t lock;
    struct list_head dispatch;
    struct request_queue *queue;
    cpumask_t cpumask;
    sbitmap ctx_map;
    struct delayed_work run_work;
};

struct blk_mq_ops {
    void (*queue_rq)(struct blk_mq_hw_ctx *hctx, 
                    const struct blk_mq_queue_data *bd);
    void (*complete)(struct request *rq);
    bool (*get_budget)(struct request_queue *q);
    void (*put_budget)(struct request_queue *q, int tag);
    // ... 更多回调函数
};
```

### BFQ队列结构
```c
struct bfq_queue {
    struct rb_node rb_node;
    struct request *next_rq;
    struct list_head fifo;
    unsigned int bfqq;
    unsigned int flags;
    unsigned int max_budget;
    unsigned int budget_timeout;
    unsigned int budget_slice;
    unsigned short ioprio;
    unsigned short ioprio_class;
    pid_t pid;
    u64 start_time;
    unsigned long slice_end;
    long long vdisktime;
    // ... 更多字段
};
```

## I/O优先级系统

### 优先级类别
- **RT(实时)**: 最高优先级，8个级别，需谨慎使用
- **BE(尽力而为)**: 默认类别，0-7级别，对应CPU nice值
- **IDLE(空闲)**: 最低优先级，仅在无其他I/O时获得访问

### 编码格式
```c
/* 32位编码格式 */
#define IOPRIO_CLASS_SHIFT 13
ioprio = (ioprio_class << IOPRIO_CLASS_SHIFT) | ioprio_data
```

### 系统调用
```c
long sys_ioprio_set(int which, int who, int ioprio);
long sys_ioprio_get(int which, int who);
```

## biovecs迭代器机制

### 不可变设计
- **核心变化**: `bi_sector`, `bi_size`, `bi_idx`, `bi_bvec_done`移至`struct bvec_iter`
- **优势**: 简化迭代、支持bio拆分、biovec共享、部分完成安全

### 核心API
```c
/* 获取biovec数据 */
struct bio_vec bio_iovec(struct bio *bio);
struct bio_vec bio_iter_iovec(struct bio *bio, struct bvec_iter iter);

/* 遍历bio段 */
#define bio_for_each_segment(bvl, bio, iter)

/* 推进迭代器 */
void bio_advance_iter(struct bio *bio, struct bvec_iter *iter, unsigned int bytes);
void bio_advance(struct bio *bio, unsigned int bytes);
```

## 数据完整性控制

### 缓存控制机制
- **REQ_PREFLUSH**: 强制缓存刷新
- **REQ_FUA**: 强制单元访问
- **驱动支持**: 通过`BLK_FEAT_WRITE_CACHE`和`BLK_FEAT_FUA`标志声明支持

### 驱动实现差异
**基于bio的驱动**
- 直接处理`REQ_PREFLUSH`和`REQ_FUA`位
- 必须设置`BLK_FEAT_WRITE_CACHE`标志

**blk-mq驱动**
- `REQ_OP_WRITE | REQ_PREFLUSH`自动转换为`REQ_OP_FLUSH` + 写入请求
- `REQ_FUA`位直接传递给`REQ_OP_WRITE`请求

## 用户空间驱动(ublk)

### 架构设计
- **控制平面**: `/dev/ublk-control`接口
- **数据平面**: 专用I/O线程 + io_uring
- **通信机制**: io_uring透传命令

### 关键命令
```c
/* 控制命令 */
UBLK_CMD_ADD_DEV, UBLK_CMD_START_DEV, UBLK_CMD_STOP_DEV
UBLK_CMD_SET_PARAMS, UBLK_CMD_GET_PARAMS

/* 数据通信命令 */
UBLK_IO_FETCH_REQ, UBLK_IO_COMMIT_AND_FETCH_REQ
UBLK_IO_REGISTER_IO_BUF, UBLK_IO_UNREGISTER_IO_BUF
```

### 零拷贝支持
- 依赖io_uring固定内核缓冲区API
- 自动缓冲区注册简化实现
- 需要`CAP_SYS_ADMIN`权限

## 基准测试工具(null_blk)

### 工作模式
- **Multi-queue**: 请求导向模式
- **No block-layer**: bio导向模式

### 配置参数
- 设备数量、大小、块大小
- 队列深度、提交队列数量
- I/O完成机制(irqmode)
- 内存支持、带宽限制
- 分区域设备支持

## 统计监控(/sys/block/<dev>/stat)

### 17项统计指标
- **读统计**: I/O数、合并数、扇区数、等待时间
- **写统计**: I/O数、合并数、扇区数、等待时间
- **丢弃统计**: I/O数、合并数、扇区数、等待时间
- **刷新统计**: I/O数、等待时间
- **其他**: in_flight, io_ticks, time_in_queue

## 分区管理(blkdevparts)

### 命令行格式
```
blkdevparts=<blkdev-def>[;<blkdev-def>]
<blkdev-id>:<partdef>[,<partdef>]
<size>[@<offset>](part-name)[ro]
```

### 应用场景
- 嵌入式设备(eMMC等固定块设备)
- 节省MBR存储空间
- 简化引导加载程序访问

## 持久预留机制

### 预留类型
```c
PR_WRITE_EXCLUSIVE           /* 独占写 */
PR_EXCLUSIVE_ACCESS          /* 独占访问 */
PR_WRITE_EXCLUSIVE_REG_ONLY  /* 注册者独占写 */
PR_EXCLUSIVE_ACCESS_REG_ONLY /* 注册者独占访问 */
PR_WRITE_EXCLUSIVE_ALL_REGS  /* 所有注册者写 */
PR_EXCLUSIVE_ACCESS_ALL_REGS /* 所有注册者访问 */
```

### 控制命令
```c
IOC_PR_REGISTER    /* 注册密钥 */
IOC_PR_RESERVE     /* 预留设备 */
IOC_PR_RELEASE     /* 释放预留 */
IOC_PR_PREEMPT     /* 抢占预留 */
IOC_PR_PREEMPT_ABORT  /* 抢占并中止 */
IOC_PR_CLEAR       /* 清除所有预留 */
```

## 性能优化要点

### blk-mq优化
- 利用CPU局部性，减少缓存失效
- 软件队列请求合并减少I/O操作次数
- 硬件队列dispatch列表保证公平性
- 标签机制避免线性搜索

### 调度器选择
- **BFQ**: 适合桌面应用，需要低延迟和公平性
- **Deadline**: 适合数据库等需要延迟保证的应用
- **Kyber**: 适合现代SSD，专注延迟控制
- **none**: 适合高性能NVMe设备，最小开销

### 系统调优
- 根据工作负载选择合适的调度器
- 调整I/O优先级优化关键应用性能
- 启用适当的缓存控制标志保证数据完整性
- 使用统计信息监控和调优系统性能

## 发展趋势

### 技术演进
- 向多队列架构统一发展
- 更多的用户空间驱动支持
- 增强的数据完整性和可靠性特性
- 更好的NUMA感知和优化

### 应用场景扩展
- 云存储和容器环境
- 边缘计算设备
- 实时和嵌入式系统
- 高性能计算集群

这些技术构成了现代Linux存储栈的核心，为各种应用场景提供了高性能、可靠的I/O服务基础。
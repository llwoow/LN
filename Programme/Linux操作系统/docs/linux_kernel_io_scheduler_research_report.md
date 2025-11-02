# Linux内核I/O调度器深入研究报告

## 报告概述

本报告深入分析了Linux内核I/O调度器的相关技术文档，重点关注多队列块设备(MQ)、I/O调度算法、blk-mq子系统等核心组件。通过对官方内核文档的系统性研究，提取了详细的I/O调度机制和源码实现信息。

## 目录

1. [多队列块I/O队列机制(blk-mq)](#1-多队列块io队列机制blk-mq)
2. [I/O调度器实现](#2-io调度器实现)
3. [I/O优先级系统](#3-io优先级系统)
4. [biovecs和迭代器机制](#4-biovecs和迭代器机制)
5. [数据完整性与缓存控制](#5-数据完整性与缓存控制)
6. [用户空间块设备驱动](#6-用户空间块设备驱动)
7. [基准测试工具](#7-基准测试工具)
8. [统计与监控](#8-统计与监控)
9. [分区管理](#9-分区管理)
10. [持久预留机制](#10-持久预留机制)

## 1. 多队列块I/O队列机制(blk-mq)

### 1.1 架构设计

blk-mq是Linux内核中用于现代快速存储设备（如SSD和NVMe）的关键I/O调度和排队机制，采用双层队列架构：

**软件分段队列（`struct blk_mq_ctx`）**
- 通常每CPU或每NUMA节点一个
- 负责请求的初步处理和调度
- 各自拥有独立的锁，减少锁竞争
- 执行请求合并（plugging）和I/O调度

**硬件调度队列（`struct blk_mq_hw_ctx`）**
- 映射到物理设备的提交队列
- 包含`dispatch`列表处理因硬件资源不足而延迟的请求
- 确保公平调度机制

### 1.2 核心数据结构

```c
struct blk_mq_ctx {
    spinlock_t		lock;
    struct list_head	dispatch;
    struct request_queue	*queue;
    unsigned int		cpu;
};

struct blk_mq_hw_ctx {
    spinlock_t		lock;
    struct list_head	dispatch;
    struct request_queue	*queue;
    unsigned int		nr_ctx;
    struct blk_mq_ctx	**ctxs;
    cpumask_t		cpumask;
    sbitmap		ctx_map;
    struct delayed_work	run_work;
};

struct blk_mq_ops {
    void (*queue_rq)(struct blk_mq_hw_ctx *hctx, const struct blk_mq_queue_data *bd);
    void (*commit_rq)(struct blk_mq_hw_ctx *hctx, struct request *rq);
    void (*queue_rqs)(struct list_rq *list);
    bool (*get_budget)(struct request_queue *q);
    void (*put_budget)(struct request_queue *q, int tag);
    void (*prepare_request)(struct request *rq);
    void (*finish_request)(struct request *rq);
    bool (*insert_requests)(struct blk_mq_hw_ctx *hctx, struct list_head *list,
                            bool from_scsi);
    bool (*requeue_request)(struct request *rq);
    void (*requeue_list)(struct list_head *list);
    void (*timeout)(struct request *req, bool reserved);
    bool (*poll)(struct blk_mq_hw_ctx *hctx);
    void (*complete)(struct request *rq);
    int (*init_hctx)(struct blk_mq_hw_ctx *hctx, void *data, unsigned int hctx_idx);
    void (*exit_hctx)(struct blk_mq_hw_ctx *hctx, unsigned int hctx_idx);
    void (*init_request)(void *data, struct request *rq, unsigned int hctx_idx,
                         unsigned int numa_node);
    void (*exit_request)(void *data, struct request *rq, unsigned int hctx_idx);
    void (*cleanup_request)(struct request *rq);
    bool (*busy)(struct request_queue *q);
    void (*map_queues)(struct blk_mq_queue_map *map);
    int (*set_affinity)(struct blk_mq_hw_ctx *hctx, const struct cpumask *cpumask);
    bool (*allow_merge)(struct request_queue *q, struct request *rq, struct bio *bio);
    bool (*bio_merge)(struct request_queue *q, struct bio *bio, unsigned int nr_segs);
    int (*req_merge)(struct request *rq, struct request *next);
    unsigned int (*req_gap_to_prev)(struct request *rq, struct request *next);
    void (*prepare_dispatch)(struct request *rq);
    void (*finish_dispatch)(struct request *rq);
    bool (*has_work)(struct blk_mq_hw_ctx *hctx);
    void (*enable_rq)(struct request_queue *q, struct request *rq);
    void (*disable_rq)(struct request_queue *q, struct request *rq);
    int (*dispatch_rq)(struct request *rq);
    int (*queue_rqs)(struct list_head *list);
};
```

### 1.3 算法原理

**多队列并行处理**
- 通过每CPU/节点软件队列和多个硬件队列实现高度并行
- 显著降低锁争用，提高I/O吞吐量

**基于标签的完成机制**
- 每个请求分配唯一整数标签
- 完成时通过标签快速识别并处理已完成的I/O请求
- 避免线性搜索，提高性能

**请求合并与调度**
- 软件队列尝试合并相邻扇区的请求
- 可插拔的I/O调度器在软件队列内对请求进行重排序
- 优化公平性或性能，避免全局锁

### 1.4 关键API函数

```c
void blk_mq_submit_bio(struct bio *bio);
void blk_mq_run_hw_queue(struct blk_mq_hw_ctx *hctx, bool async);
void blk_mq_complete_request(struct request *rq);
void blk_mq_start_request(struct request *rq);
void blk_mq_end_request(struct request *rq, blk_status_t error);
```

## 2. I/O调度器实现

### 2.1 BFQ (Budget Fair Queueing)调度器

#### 2.1.1 算法原理

BFQ是基于B-WF2Q+算法的比例份额I/O调度器，主要特点：

**比例份额调度机制**
- 根据进程或组的权重，公平分配设备带宽
- 每个I/O进程关联一个`bfq_queue`结构
- 队列通过预算机制控制设备访问权

**B-WF2Q+调度算法**
- 使用增强型红黑树实现O(log N)复杂度
- 确保每个队列获得与其权重成比例的设备吞吐量
- 服务平滑，与设备参数、当前工作负载和预算无关

**低延迟启发式**
- 默认启用低延迟模式
- 通过"权重提升"等启发式算法优先处理交互式应用
- 为音视频播放器等提供更多设备吞吐量份额

**早期队列合并(EQM)**
- 与CFQ不同，采用更具响应性的EQM机制
- 合并执行交错I/O的队列，使其变为顺序I/O
- 提高吞吐量的统一机制

#### 2.1.2 核心数据结构

```c
struct bfq_queue {
    struct rb_node rb_node;
    struct rb_root *root;
    struct bfq_entity *entity;
    struct bfq_group *bfqg;
    struct bfq_data *bfqd;
    struct request *next_rq;
    struct list_head fifo;
    struct hlist_node burst_list_node;
    unsigned int bfqq;
    unsigned int flags;
    unsigned int burst_size;
    unsigned int max_budget;
    unsigned int budget_timeout;
    unsigned int budget_slice;
    unsigned int orig_budget_slice;
    unsigned int slice_dispatch;
    unsigned int slice_left;
    unsigned int dispatch_slice;
    unsigned int next_rq_pos;
    unsigned int seek_samples;
    sector_t seek_total;
    sector_t seek_mean;
    unsigned int in_large_burst:1;
    unsigned int in_service:1;
    unsigned int queued[2];
    unsigned int dispatched;
    unsigned int allocated;
    unsigned int ref;
    unsigned short ioprio;
    unsigned short ioprio_class;
    unsigned short new_ioprio;
    unsigned short new_ioprio_class;
    pid_t pid;
    u64 start_time;
    u64 start_time_bic;
    u64 start_time_when;
    u64 finish_time;
    unsigned long slice_end;
    long long vdisktime;
    unsigned int weight_counter;
    unsigned short tunning;
    unsigned int first_IO_time;
    unsigned int last_IO_time;
    unsigned long IO_start_time_when;
    unsigned long IO_allocation;
    unsigned long IO_bound;
    unsigned long IO_bound_time;
    unsigned int in_thrashing:1;
    unsigned long in_thrashing_end;
    unsigned int was_in_burst_list_at_end:1;
    unsigned int saved_large_slowness;
    unsigned int saved_idling_window;
    unsigned int saved_IO_bound;
    unsigned int saved_in_large_burst;
    unsigned int was_in_burst_list;
    unsigned int saved_close_to_system;
    unsigned int was_save_bound;
    unsigned int was_in_burst_list_at_beginning;
    unsigned int burst_at_end;
    unsigned int was_in_burst_list_at_end;
    unsigned int large_budget_increased;
    unsigned int was_in_burst_list_at_end;
    unsigned int was_in_burst_list;
    unsigned int saved_large_slowness;
    unsigned int saved_idling_window;
    unsigned int saved_IO_bound;
    unsigned int saved_in_large_burst;
    unsigned int was_in_burst_list_at_beginning;
    unsigned int burst_at_end;
    unsigned int was_in_burst_list_at_end;
    unsigned int large_budget_increased;
};
```

#### 2.1.3 可调参数

- `slice_idle`: 控制设备空闲时间
- `strict_guarantees`: 确保严格服务保障，可能影响吞吐量
- `back_seek_max`和`back_seek_penalty`: 优化磁盘寻道
- `fifo_expire_async`和`fifo_expire_sync`: 控制异步/同步请求超时
- `low_latency`: 低延迟模式开关
- `timeout_sync`: 任务最大设备时间
- `max_budget`: 队列最大服务扇区数，支持自动调整

### 2.2 Deadline调度器

#### 2.2.1 核心目标与原理

Deadline调度器的主要目标是尝试为I/O请求提供一个保证的起始服务时间，特别关注优化读请求的延迟。

**截止时间机制**
- 读请求截止时间：`read_expire`参数（毫秒）
- 写请求截止时间：`write_expire`参数（毫秒）
- 请求进入调度器时被赋予截止时间

**请求批处理机制**
- 按数据方向（读或写）分组为"批次"
- 按扇区递增顺序进行服务
- 只在批次之间检查截止时间

**读写优先级平衡**
- 总是优先处理读请求
- `writes_starved`参数控制读请求被连续优先派发的次数
- 避免写请求无限期饥饿

#### 2.2.2 可调参数

- `fifo_batch`: 控制每个批次的最大请求数量
- `front_merges`: 控制是否尝试前向合并
- `read_expire`: 读请求截止时间（毫秒）
- `write_expire`: 写请求截止时间（毫秒）
- `writes_starved`: 读请求连续优先次数限制

### 2.3 Kyber调度器

Kyber调度器是专为现代SSD设计的高性能调度器，具有极简的接口：

**核心机制**
- 只有两个可调参数：`read_lat_nsec`和`write_lat_nsec`
- 通过限制请求来满足设定的目标延迟
- 专注于延迟控制而非吞吐量优化

**目标延迟设置**
- `read_lat_nsec`: 设置读请求的目标延迟（纳秒）
- `write_lat_nsec`: 设置同步写请求的目标延迟（纳秒）

## 3. I/O优先级系统

### 3.1 优先级类别

Linux内核提供三种I/O调度类别：

**IOPRIO_CLASS_RT (实时类)**
- 具有最高优先级，每次都优先获得磁盘访问权
- 8个优先级级别（class data）
- 需谨慎使用，单个RT进程可能导致系统饥饿

**IOPRIO_CLASS_BE (尽力而为类)**
- 默认的调度类别
- 优先级级别0为最高BE优先级，7为最低
- 与CPU nice级别粗略对应：io_nice = (cpu_nice + 20) / 5

**IOPRIO_CLASS_IDLE (空闲类)**
- 优先级最低，仅当没有其他进程需要磁盘I/O时才能获得I/O时间
- 没有优先级级别（class data）

### 3.2 优先级编码

I/O优先级值是一个32位整数，编码格式：
- 高位：优先级类别（`ioprio_class << IOPRIO_CLASS_SHIFT`）
- 低位：优先级级别（`ioprio & 0xff`）

```c
enum {
    IOPRIO_CLASS_NONE = 0,
    IOPRIO_CLASS_RT = 1,
    IOPRIO_CLASS_BE = 2,
    IOPRIO_CLASS_IDLE = 3,
};

enum {
    IOPRIO_WHO_PROCESS = 1,
    IOPRIO_WHO_PGRP = 2,
    IOPRIO_WHO_USER = 3,
};
```

### 3.3 系统调用接口

```c
/* 系统调用号因架构而异 */
#define __NR_ioprio_set 289  /* i386 */
#define __NR_ioprio_get 290  /* i386 */
#define __NR_ioprio_set 251  /* x86_64 */
#define __NR_ioprio_get 252  /* x86_64 */

long sys_ioprio_set(int which, int who, int ioprio);
long sys_ioprio_get(int which, int who);
```

## 4. biovecs和迭代器机制

### 4.1 不可变biovecs设计

自Linux内核3.13版本起，biovecs在bio提交后不应再被修改。引入了`struct bvec_iter`来封装可变状态：

**核心变化**
- 所有必须随bio部分完成而发生变化的状态移至`struct bvec_iter`
- 包括`bi_sector`、`bi_size`、`bi_idx`和`bi_bvec_done`
- biovec本身成为不可变结构

**主要优势**
- 简化迭代逻辑
- biovec数据持久化
- 支持高效的bio拆分和biovec共享
- 支持部分完成的bio提交

### 4.2 核心API

```c
/* 获取biovec数据 */
struct bio_vec bio_iovec(struct bio *bio);
struct bio_vec bio_iter_iovec(struct bio *bio, struct bvec_iter iter);

/* 遍历bio段 */
#define bio_for_each_segment(bvl, bio, iter) \
    for (iter = (bio)->bi_iter; \
         (iter).bi_size && \
         ((bvl = bio_iter_iovec((bio), (iter))), 1); \
         bio_advance_iter((bio), &(iter), (bvl).bv_len))

/* 推进迭代器 */
void bio_advance_iter(struct bio *bio, struct bvec_iter *iter, unsigned int bytes);
void bio_advance(struct bio *bio, unsigned int bytes);
void bvec_iter_advance(struct bio_vec *bv, struct bvec_iter *iter, unsigned int bytes);
```

### 4.3 辅助宏

**`_all`后缀宏**
- `bio_for_each_segment_all()`, `bio_for_each_bvec_all()`
- `bio_first_bvec_all()`, `bio_first_page_all()`
- `bio_first_folio_all()`, `bio_last_bvec_all()`
- 仅用于非`BIO_CLONED`的bio

**单页段迭代器**
- `bio_for_each_segment()`, `bio_for_each_segment_all()`
- 传入的`struct bio_vec`包含一个单页I/O向量

**多页bvec迭代器**
- `bio_for_each_bvec()`, `bio_for_each_bvec_all()`, `rq_for_each_bvec()`
- 传入的`struct bio_vec`包含一个多页I/O向量

## 5. 数据完整性与缓存控制

### 5.1 易失性回写缓存问题

许多存储设备使用易失性回写缓存，在数据实际写入非易失性存储前即报告I/O完成。这加速了工作负载，但在执行fsync、sync或umount等数据完整性操作时需要特殊处理。

### 5.2 核心机制

**强制缓存刷新（REQ_PREFLUSH）**
- 确保在当前I/O操作开始前，存储设备的易失性缓存已被刷新
- 可与bio的r/w标志进行OR操作
- 可用于空的bio结构，推荐使用`blkdev_issue_flush()`辅助函数

**强制单元访问（REQ_FUA）**
- 确保只有在数据已提交到非易失性存储后，才发出I/O完成信号
- 可与bio的r/w标志进行OR操作

### 5.3 驱动程序实现

**基于bio的块驱动**
- 设置`BLK_FEAT_WRITE_CACHE`标志告知块层支持缓存刷新
- 设置`BLK_FEAT_FUA`标志告知块层支持FUA位
- 需要处理`REQ_PREFLUSH`和`REQ_FUA`位

**blk-mq驱动**
- 设置`BLK_FEAT_WRITE_CACHE`时，带有效载荷的`REQ_OP_WRITE | REQ_PREFLUSH`请求自动转换为`REQ_OP_FLUSH`请求
- 设置`BLK_FEAT_FUA`时，`REQ_FUA`位直接传递给`REQ_OP_WRITE`请求
- 未设置`BLK_FEAT_FUA`但bio带有`REQ_FUA`位时，写入完成后发送`REQ_OP_FLUSH`请求

## 6. 用户空间块设备驱动

### 6.1 ublk框架概述

ublk是Linux内核中一个通用的框架，旨在将虚拟块设备驱动的逻辑迁移到用户空间实现：

**核心优势**
- 多语言支持
- 使用用户空间库
- 易于调试
- 隔离内核崩溃风险
- 独立更新

### 6.2 架构设计

**控制平面**
- 通过`/dev/ublk-control`提供接口
- 使用一系列控制命令进行操作

**数据平面**
- ublk服务器创建专用的I/O处理线程
- 每个线程拥有自己的io_uring实例
- 专注于I/O处理，不处理控制和管理任务

### 6.3 控制命令

```c
UBLK_CMD_ADD_DEV      /* 添加ublk字符设备 */
UBLK_CMD_SET_PARAMS   /* 设置设备参数 */
UBLK_CMD_GET_PARAMS   /* 获取设备参数 */
UBLK_CMD_START_DEV    /* 启动设备 */
UBLK_CMD_STOP_DEV     /* 停止设备 */
UBLK_CMD_DEL_DEV      /* 删除设备 */
UBLK_CMD_GET_QUEUE_AFFINITY  /* 获取队列亲和性 */
UBLK_CMD_GET_DEV_INFO  /* 获取设备信息 */
UBLK_CMD_START_USER_RECOVERY  /* 启动用户恢复 */
UBLK_CMD_END_USER_RECOVERY    /* 结束用户恢复 */
```

### 6.4 数据通信命令

```c
UBLK_IO_FETCH_REQ              /* 获取I/O请求 */
UBLK_IO_COMMIT_AND_FETCH_REQ   /* 提交结果并获取下一请求 */
UBLK_IO_NEED_GET_DATA          /* 需要获取数据 */
UBLK_IO_REGISTER_IO_BUF        /* 注册I/O缓冲区 */
UBLK_IO_UNREGISTER_IO_BUF      /* 注销I/O缓冲区 */
```

### 6.5 零拷贝机制

- 依赖io_uring的固定内核缓冲区API
- 通过`UBLK_IO_REGISTER_IO_BUF`注册客户端请求缓冲区
- ublk服务器需要`CAP_SYS_ADMIN`权限
- 自动缓冲区注册功能简化实现

## 7. 基准测试工具

### 7.1 null_blk驱动

null_blk是用于Linux内核块层基准测试的虚拟块设备驱动：

**核心原理**
- 不执行实际的读写操作
- 仅将传入的I/O请求标记为完成
- 用于模拟块层交互和性能测试

**支持模式**
- Multi-queue（请求导向）
- No block-layer（bio导向）

**可配置参数**
- 设备数量（`nr_devices`）
- 设备总大小（`gb`）
- 块大小（`bs`）
- 硬件队列深度（`hw_queue_depth`）
- 提交队列数量（`submit_queues`）
- I/O完成机制（`irqmode`）
- 内存支持（`memory_backed`）
- 带宽限制（`mbps`）

### 7.2 分区域块设备支持

支持宿主管理的分区域块设备（Host-managed Zoned Block Device）：
- 区域大小（`zone_size`）
- 常规区域数量（`zone_nr_conv`）

## 8. 统计与监控

### 8.1 /sys/block/<dev>/stat文件

提供17个块层统计信息的单一快照：

**读统计**
- 读I/O数量
- 读合并数量
- 读的扇区数
- 读请求总等待时间（read ticks）

**写统计**
- 写I/O数量
- 写合并数量
- 写的扇区数
- 写请求总等待时间（write ticks）

**丢弃统计**
- 丢弃I/O数量
- 丢弃合并数量
- 丢弃的扇区数
- 丢弃请求总等待时间（discard ticks）

**刷新统计**
- 刷新I/O数量
- 刷新请求总等待时间（flush ticks）

**其他指标**
- `in_flight`: 已发出但未完成的I/O数量
- `io_ticks`: 设备有I/O请求排队的总时间
- `time_in_queue`: 所有请求的总等待时间

## 9. 分区管理

### 9.1 命令行分区解析

`blkdevparts`命令行选项用于从内核命令行读取块设备分区表：

**典型应用场景**
- 固定块设备（如eMMC）的嵌入式设备
- 节省存储空间（无需MBR）
- 通过绝对地址轻松访问引导加载程序

**命令行格式**
```
blkdevparts=<blkdev-def>[;<blkdev-def>]
```

**块设备定义格式**
```
<blkdev-id>:<partdef>[,<partdef>]
```

**分区定义格式**
```
<size>[@<offset>](part-name)[ro]
```

**示例**
```
blkdevparts=mmcblk0:1G(data0),1G(data1),-;mmcblk0boot0:1m(boot)ro,-(kernel)
```

## 10. 持久预留机制

### 10.1 持久预留目的

允许在共享存储环境中，将块设备的访问权限限制给特定的发起者。

### 10.2 预留类型

```c
PR_WRITE_EXCLUSIVE           /* 只有拥有预留的发起者可以写入设备 */
PR_EXCLUSIVE_ACCESS          /* 只有拥有预留的发起者可以访问设备 */
PR_WRITE_EXCLUSIVE_REG_ONLY  /* 只有拥有注册密钥的发起者可以写入设备 */
PR_EXCLUSIVE_ACCESS_REG_ONLY /* 只有拥有注册密钥的发起者可以访问设备 */
PR_WRITE_EXCLUSIVE_ALL_REGS  /* 拥有注册密钥的发起者可以写入设备 */
PR_EXCLUSIVE_ACCESS_ALL_REGS /* 拥有注册密钥的发起者可以访问设备 */
```

### 10.3 ioctl命令

```c
IOC_PR_REGISTER    /* 注册新的预留密钥 */
IOC_PR_RESERVE     /* 预留设备 */
IOC_PR_RELEASE     /* 释放预留 */
IOC_PR_PREEMPT     /* 抢占预留 */
IOC_PR_PREEMPT_ABORT  /* 抢占并中止未决命令 */
IOC_PR_CLEAR       /* 清除所有预留 */
```

## 结论

Linux内核的I/O调度器系统是一个复杂而精密的架构，通过多队列设计、多种调度算法、优先级控制和数据完整性机制，为现代存储设备提供了高性能、可靠的I/O服务。blk-mq作为核心机制，通过双层队列架构和基于标签的完成机制，显著提升了多核系统上对SSD和NVMe等高速存储设备的I/O并行处理能力。

各种I/O调度器（BFQ、Deadline、Kyber）针对不同的应用场景和性能需求提供了优化的解决方案，而biovecs迭代器机制、缓存控制、用户空间驱动支持等特性则进一步完善了整个块层系统的功能和性能。

这些技术的结合使Linux内核能够高效地处理各种I/O工作负载，从实时系统到高性能计算，从嵌入式设备到企业级存储解决方案，为现代计算环境提供了坚实可靠的基础。
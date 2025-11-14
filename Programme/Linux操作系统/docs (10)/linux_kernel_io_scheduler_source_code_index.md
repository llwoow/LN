# Linux内核I/O调度器源码实现索引

## 主要源码文件路径

### blk-mq核心实现
```
block/blk-mq.c              # blk-mq核心实现
block/blk-mq-tag.c          # 标签管理
block/blk-mq-sched.c        # 调度器接口
include/linux/blk-mq.h      # blk-mq头文件
include/linux/blk-mq-tag.h  # 标签相关头文件
```

### I/O调度器实现
```
block/bfq-iosched.c         # BFQ调度器实现
block/deadline-iosched.c    # Deadline调度器实现
block/kyber-iosched.c       # Kyber调度器实现
block/noop-iosched.c        # Noop调度器实现
block/elevator.c            # 通用调度器框架
include/linux/elevator.h    # 调度器框架头文件
```

### bio和biovec实现
```
block/bio.c                 # bio操作实现
block/bio-integrity.c       # bio完整性
block/bvec.c                # biovec操作
include/linux/bio.h         # bio头文件
include/linux/bvec.h        # biovec头文件
```

### 用户空间驱动
```
drivers/block/ublk.c        # ublk驱动实现
include/uapi/linux/ublk_cmd.h  # ublk命令定义
```

### 基准测试驱动
```
drivers/block/null_blk.c    # null_blk驱动
drivers/block/null_blk_main.c # null_blk主模块
drivers/block/null_blk.h    # null_blk头文件
```

### 统计和监控
```
block/genhd.c               # 通用磁盘设备
block/partitions/           # 分区处理
include/linux/genhd.h       # 通用磁盘头文件
```

## 核心数据结构定义

### blk-mq关键结构

#### blk_mq_ctx (软件队列)
```c
// include/linux/blk-mq.h
struct blk_mq_ctx {
    struct request_queue *queue;      // 所属请求队列
    unsigned int cpu;                 // CPU编号
    spinlock_t lock;                  // 保护队列的锁
    struct list_head dispatch;        // 分发队列
    struct list_head request_list;    // 请求列表
    struct blk_mq_hw_ctx *hctx;       // 关联的硬件上下文
    cpumask_t cpumask;                // CPU掩码
    unsigned int *map_queues;         // 队列映射
};
```

#### blk_mq_hw_ctx (硬件队列)
```c
// include/linux/blk-mq.h
struct blk_mq_hw_ctx {
    struct request_queue *queue;      // 所属请求队列
    unsigned int queue_num;           // 队列编号
    cpumask_t cpumask;                // CPU掩码
    spinlock_t lock;                  // 保护队列的锁
    struct list_head dispatch;        // 分发队列
    struct blk_mq_ctx **ctxs;         // 软件队列数组
    unsigned int nr_ctx;              // 软件队列数量
    struct blk_mq_queue_map map;      // 队列映射
    struct delayed_work run_work;     // 延迟工作项
    sbitmap ctx_map;                  // 上下文映射位图
    struct blk_mq_tag_set *tag_set;   // 标签集合
    void *driver_data;                // 驱动私有数据
    unsigned long state;              // 队列状态
};
```

#### blk_mq_ops (驱动操作接口)
```c
// include/linux/blk-mq.h
struct blk_mq_ops {
    // 请求排队
    void (*queue_rq)(struct blk_mq_hw_ctx *hctx,
                     const struct blk_mq_queue_data *bd);
    
    // 请求完成
    void (*complete)(struct request *rq);
    
    // 预算管理
    bool (*get_budget)(struct request_queue *q);
    void (*put_budget)(struct request_queue *q, int tag);
    
    // 硬件上下文管理
    int (*init_hctx)(struct blk_mq_hw_ctx *hctx, void *data,
                     unsigned int hctx_idx);
    void (*exit_hctx)(struct blk_mq_hw_ctx *hctx, unsigned int hctx_idx);
    
    // 请求管理
    void (*prepare_request)(struct request *rq);
    void (*finish_request)(struct request *rq);
    void (*cleanup_request)(struct request *rq);
    
    // 队列管理
    bool (*busy)(struct request_queue *q);
    void (*map_queues)(struct blk_mq_queue_map *map);
    
    // 超时处理
    void (*timeout)(struct request *req, bool reserved);
    
    // 轮询支持
    bool (*poll)(struct blk_mq_hw_ctx *hctx);
    
    // 请求合并
    bool (*allow_merge)(struct request_queue *q, struct request *rq,
                       struct bio *bio);
    bool (*bio_merge)(struct request_queue *q, struct bio *bio,
                     unsigned int nr_segs);
    int (*req_merge)(struct request *rq, struct request *next);
    unsigned int (*req_gap_to_prev)(struct request *rq,
                                   struct request *next);
};
```

### BFQ调度器结构

#### bfq_queue (BFQ队列)
```c
// block/bfq-iosched.h
struct bfq_queue {
    struct rb_node rb_node;           // 红黑树节点
    struct request *next_rq;          // 下一个请求
    struct list_head fifo;            // FIFO队列
    struct bfq_group *bfqg;           // 所属组
    struct bfq_data *bfqd;            // 调度器数据
    unsigned int bfqq;                // 队列ID
    unsigned int flags;               // 队列标志
    
    // 预算管理
    unsigned int max_budget;          // 最大预算
    unsigned int budget_timeout;      // 预算超时
    unsigned int budget_slice;        // 预算切片
    unsigned int orig_budget_slice;   // 原始预算切片
    
    // 优先级
    unsigned short ioprio;            // I/O优先级
    unsigned short ioprio_class;      // I/O优先级类别
    pid_t pid;                        // 进程ID
    
    // 时间统计
    u64 start_time;                   // 开始时间
    unsigned long slice_end;          // 切片结束时间
    long long vdisktime;              // 虚拟磁盘时间
    
    // 寻道统计
    unsigned int seek_samples;        // 寻道样本数
    sector_t seek_total;              // 寻道总距离
    sector_t seek_mean;               // 平均寻道距离
    
    // 状态标志
    unsigned int in_service:1;        // 是否在服务中
    unsigned int in_thrashing:1;      // 是否在抖动
    unsigned int in_large_burst:1;    // 是否在大突发中
};
```

#### bfq_group (BFQ组)
```c
// block/bfq-iosched.h
struct bfq_group {
    struct bfq_entity *entity;        // 实体结构
    struct bfq_data *bfqd;            // 调度器数据
    
    // 权重管理
    struct rb_root rb;                // 红黑树根
    struct rb_node rb_node;           // 红黑树节点
    unsigned int weight;              // 权重
    unsigned int new_weight;          // 新权重
    unsigned int orig_weight;         // 原始权重
    
    // 预算管理
    unsigned int budget;              // 当前预算
    unsigned int max_budget;          // 最大预算
    unsigned int budget_timeout;      // 预算超时
    
    // 服务统计
    unsigned int served;              // 已服务字节数
    unsigned int service_from_root;   // 从根服务字节数
    unsigned long total_service_time; // 总服务时间
    unsigned long start_at_first_request; // 第一个请求开始时间
    unsigned long first_request_time; // 第一个请求时间
    
    // cgroups支持
    unsigned int entity;              // 实体ID
    struct rcu_head rcu_head;         // RCU头
};
```

### bio和biovec结构

#### bio (块I/O)
```c
// include/linux/bio.h
struct bio {
    struct bio *bi_next;              // 下一个bio
    struct block_device *bi_bdev;     // 块设备
    int bi_error;                     // 错误码
    atomic_t __bi_remaining;          // 剩余bio计数
    
    // I/O向量
    struct bvec_iter bi_iter;         // 迭代器
    unsigned short bi_io_vec;         // I/O向量索引
    
    // 完整性
    struct bio_integrity_payload *bi_integrity;
    
    // 标志
    unsigned short bi_flags;          // bio标志
    unsigned short bi_ioprio;         // I/O优先级
    
    // 物理和虚拟地址
    struct bvec_iter bi_iter;
    unsigned int bi_max_vecs;         // 最大向量数
    unsigned int bi_vcnt;             // 向量计数
    unsigned int bi_size;             // 总大小
    
    // 提交和完成
    bio_end_io_t *bi_end_io;          // 完成回调
    void *bi_private;                 // 私有数据
    
    // 合并和拆分
    struct bio_set *bi_pool;          // bio集合
    struct bio_vec bi_inline_vecs[0]; // 内联向量
};
```

#### bvec_iter (向量迭代器)
```c
// include/linux/bvec.h
struct bvec_iter {
    sector_t bi_sector;               // 扇区号
    unsigned int bi_size;             // 剩余大小
    unsigned int bi_idx;              // 当前向量索引
    unsigned int bi_bvec_done;        // 当前向量完成字节数
};
```

#### bio_vec (向量)
```c
// include/linux/bvec.h
struct bio_vec {
    struct page *bv_page;             // 页面
    unsigned int bv_len;              // 长度
    unsigned int bv_offset;           // 偏移
};
```

## 关键函数实现

### blk-mq核心函数

#### blk_mq_submit_bio
```c
// block/blk-mq.c
void blk_mq_submit_bio(struct bio *bio)
{
    struct request_queue *q = bio->bi_bdev->bd_disk->queue;
    struct blk_mq_hw_ctx *hctx;
    struct blk_mq_ctx *ctx;
    unsigned int cpu;
    
    // 获取CPU和上下文
    cpu = get_cpu();
    ctx = blk_mq_get_ctx(q);
    hctx = blk_mq_map_queue(q, cpu);
    
    // 提交bio
    blk_mq_bio_to_request(rq, bio);
    blk_mq_insert_request(hctx, rq, false, true);
    
    put_cpu();
}
```

#### blk_mq_run_hw_queue
```c
// block/blk-mq.c
void blk_mq_run_hw_queue(struct blk_mq_hw_ctx *hctx, bool async)
{
    if (unlikely(blk_mq_hctx_stopped(hctx) || blk_mq_queue_stopped(hctx->queue)))
        return;
    
    if (!async && !(hctx->flags & BLK_MQ_F_BLOCKING)) {
        int srcu_idx;
        struct request_queue *q = hctx->queue;
        
        if (!test_and_set_bit(BLK_MQ_S_START_ON_RUN, &hctx->state))
            return;
        
        hctx->run_work.data = &srcu_idx;
        blk_mq_hctx_clear_pending(hctx);
        blk_mq_run_work_fn(&hctx->run_work);
    } else {
        queue_delayed_work_on(smp_processor_id(), hctx->queue->mq_poll_wq,
                             &hctx->run_work, 0);
    }
}
```

### BFQ调度器函数

#### bfq_insert_request
```c
// block/bfq-iosched.c
static void bfq_insert_request(struct blk_mq_hw_ctx *hctx, struct request *rq,
                              bool at_head)
{
    struct request_queue *q = hctx->queue;
    struct bfq_data *bfqd = q->elevator->elevator_data;
    struct bfq_queue *bfqq = RQ_BFQQ(rq);
    
    // 验证请求
    if (at_head || !bfqq)
        list_add(&rq->queuelist, &bfqd->dispatch);
    else {
        // 插入到队列末尾
        list_add_tail(&rq->queuelist, &bfqq->fifo);
        
        // 更新队列状态
        bfqq->queued[rq_data_dir(rq)]++;
        bfq_update_queues(bfqd, bfqq);
    }
}
```

#### bfq_dispatch_request
```c
// block/bfq-iosched.c
static struct request *bfq_dispatch_request(struct blk_mq_hw_ctx *hctx)
{
    struct bfq_data *bfqd = hctx->queue->elevator->elevator_data;
    struct request *rq;
    
    // 检查是否有请求需要调度
    if (!bfq_has_work(bfqd))
        return NULL;
    
    // 获取下一个请求
    rq = bfq_next_request(bfqd);
    if (!rq)
        return NULL;
    
    // 验证预算
    if (!bfq_serv_allowed(rq, bfqd))
        return NULL;
    
    // 标记为在服务中
    bfq_clear_bfqq_wait_request(bfqq);
    bfq_mark_bfqq_in_service(bfqq);
    
    // 更新统计
    bfqd->in_service_queue = bfqq;
    
    return rq;
}
```

### Deadline调度器函数

#### deadline_insert_request
```c
// block/deadline-iosched.c
static void deadline_insert_request(struct blk_mq_hw_ctx *hctx,
                                   struct request *rq, bool at_head)
{
    struct request_queue *q = hctx->queue;
    struct deadline_data *dd = q->elevator->elevator_data;
    const int data_dir = rq_data_dir(rq);
    
    if (at_head) {
        list_add(&rq->queuelist, &dd->dispatch);
    } else {
        // 添加到相应队列的末尾
        if (data_dir == REQ_OP_READ)
            list_add_tail(&rq->queuelist, &dd->read_fifo);
        else
            list_add_tail(&rq->queuelist, &dd->write_fifo);
    }
}
```

#### deadline_dispatch_request
```c
// block/deadline-iosched.c
static struct request *deadline_dispatch_request(struct blk_mq_hw_ctx *hctx)
{
    struct deadline_data *dd = hctx->queue->elevator->elevator_data;
    struct request *rq;
    bool read;
    
    // 检查是否有请求需要调度
    if (!list_empty(&dd->dispatch))
        return list_first_entry(&dd->dispatch, struct request, queuelist);
    
    // 检查读请求
    if (!list_empty(&dd->read_fifo)) {
        rq = list_first_entry(&dd->read_fifo, struct request, queuelist);
        read = true;
    }
    // 检查写请求
    else if (!list_empty(&dd->write_fifo)) {
        rq = list_first_entry(&dd->write_fifo, struct request, queuelist);
        read = false;
    }
    else
        return NULL;
    
    // 检查截止时间
    if (deadline_check_fifo(dd, read))
        dd->fifo_expire[data_dir] = jiffies + dd->fifo_expire[data_dir];
    
    return rq;
}
```

### bio操作函数

#### bio_advance
```c
// block/bio.c
void bio_advance(struct bio *bio, unsigned int bytes)
{
    if (bio_integrity(bio))
        bio_integrity_advance(bio, bytes);
    
    bio_advance_iter(bio, &bio->bi_iter, bytes);
    
    if (bio->bi_end_io)
        bio_crypt_free_ctx(bio);
}
```

#### bio_for_each_segment
```c
// include/linux/bio.h
#define bio_for_each_segment(bvl, bio, iter) \
    for (iter = (bio)->bi_iter; \
         (iter).bi_size && \
         ((bvl = bio_iter_iovec((bio), (iter))), 1); \
         bio_advance_iter((bio), &(iter), (bvl).bv_len))
```

### ublk驱动函数

#### ublk_add_dev
```c
// drivers/block/ublk.c
static int ublk_add_dev(struct ublk_device *ub, unsigned int dev_id,
                       unsigned int nr_hw_queues, unsigned int queue_depth,
                       unsigned int max_io_size)
{
    struct request_queue *q;
    struct gendisk *disk;
    int ret;
    
    // 创建设备
    ret = ublk_ch_dev_setup(ub, nr_hw_queues, queue_depth);
    if (ret)
        return ret;
    
    // 创建请求队列
    q = blk_mq_alloc_queue(&ub->tag_set);
    if (IS_ERR(q))
        return PTR_ERR(q);
    
    // 设置队列参数
    blk_queue_flag_set(QUEUE_FLAG_MQ_DEFAULT, q);
    blk_queue_max_hw_sectors(q, max_io_size >> 9);
    blk_queue_max_segments(q, USHRT_MAX);
    
    // 创建设备节点
    disk = ublk_disk_alloc(ub);
    if (!disk) {
        blk_mq_free_queue(q);
        return -ENOMEM;
    }
    
    return 0;
}
```

## 调试和性能分析

### 调试接口
```
/sys/block/<dev>/queue/scheduler    # 当前调度器
/sys/block/<dev>/queue/iosched/     # 调度器参数
/sys/block/<dev>/stat               # 设备统计
/proc/<pid>/io                      # 进程I/O统计
```

### 内核调试选项
```
CONFIG_BLK_DEV_IO_TRACE            # I/O跟踪
CONFIG_BLK_DEV_THROTTLING          # I/O限流
CONFIG_BLK_CGROUP                  # cgroups支持
CONFIG_BFQ_CGROUP_DEBUG            # BFQ调试
```

### 性能分析工具
- **iostat**: I/O统计监控
- **iotop**: 实时I/O监控
- **blktrace**: 块I/O跟踪
- **bpftrace**: BPF跟踪工具

## 编译配置

### 内核配置选项
```
CONFIG_BLOCK=y                     # 块层支持
CONFIG_MQ_DEADLINE=y               # mq-deadline调度器
CONFIG_BFQ_CGROUP_IOSCHED=y        # BFQ调度器
CONFIG_KYBER_CUBIC_IOSCHED=y       # Kyber调度器
CONFIG_BLK_DEV_NULL_BLK=y          # null_blk驱动
CONFIG_BLK_DEVUBLK=y               # ublk驱动
CONFIG_BLK_DEV_ZONED=y             # 分区域设备支持
CONFIG_BLK_DEV_INTEGRITY=y         # 数据完整性支持
```

### 模块参数
```
# blk-mq参数
blk_mq_nr_hw_queues                # 硬件队列数量
blk_mq_queue_depth                 # 队列深度

# ublk参数
ublk_nr_devices                    # 设备数量
ublk_queue_depth                   # 队列深度
ublk_io_uring_depth                # io_uring深度

# null_blk参数
null_blk_nr_devices                # 设备数量
null_blk_queue_depth               # 队列深度
null_blk_submit_queues             # 提交队列数量
```

这个索引为Linux内核I/O调度器的源码实现提供了完整的导航指南，帮助开发者快速定位相关代码和理解实现细节。
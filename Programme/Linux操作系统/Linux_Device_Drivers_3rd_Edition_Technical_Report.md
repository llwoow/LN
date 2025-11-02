# Linux Device Drivers 第三版深入技术报告

## 文档概述

本报告深入分析了《Linux Device Drivers, Third Edition》这本经典教材的核心内容，特别关注设备驱动架构、字符设备驱动、块设备驱动、PCI驱动、DMA技术、中断处理等关键技术章节。

**文档信息：**
- 书名：Linux Device Drivers, Third Edition
- 作者：Jonathan Corbet, Alessandro Rubini, and Greg Kroah-Hartman
- 版本：第三版（2005年2月）
- 覆盖内核版本：Linux 2.6.10
- 总页数：630页
- 提取页数：前50页 + 核心章节307页

## 1. 设备驱动架构

### 1.1 设备驱动的角色

设备驱动在Linux内核中扮演着特殊的角色：

- **黑盒机制**：设备驱动是独立的"黑盒"，使特定硬件响应定义良好的内部编程接口
- **硬件抽象**：完全隐藏设备工作细节，提供标准化的调用接口
- **模块化设计**：可以独立于内核构建，在运行时"插入"

### 1.2 内核架构分解

Linux内核可以分为以下几个主要部分：

#### 进程管理
- 创建和销毁进程
- 处理进程与外部世界的连接（输入/输出）
- 进程间通信（信号、管道、IPC原语）
- 调度器控制进程如何共享CPU

#### 内存管理
- 构建虚拟地址空间
- 管理有限的物理资源
- 提供从简单malloc/free到复杂功能的函数调用

#### 文件系统
- 基于文件系统概念构建
- 在非结构化硬件上构建结构化文件系统
- 支持多种文件系统类型（ext3、FAT等）

#### 设备控制
- 每个外设都需要特定于设备的驱动程序代码
- 设备驱动程序处理所有设备控制操作

#### 网络
- 网络操作是异步事件
- 收集、识别和分派数据包
- 控制程序执行和网络活动

### 1.3 设备类型分类

Linux将设备分为三种基本类型：

#### 字符设备（Character Devices）
- 可以作为字节流访问的设备
- 实现open、close、read、write系统调用
- 示例：控制台（/dev/console）、串口（/dev/ttyS0）
- 通过文件系统节点访问：/dev/tty1、/dev/lp0

#### 块设备（Block Devices）
- 可以承载文件系统的设备（如磁盘）
- 只能处理传输整个块的I/O操作（通常512字节或2的幂）
- Linux允许像字符设备一样读写块设备
- 通过文件系统节点访问

#### 网络接口（Network Interfaces）
- 能够与其他主机交换数据的设备
- 可以是硬件设备或纯软件设备（如loopback接口）
- 负责发送和接收数据包
- 不容易映射到文件系统节点

### 1.4 机制与策略分离

Linux设计的一个重要原则是机制与策略的分离：

- **机制（Mechanism）**：提供什么能力
- **策略（Policy）**：如何使用这些能力

驱动程序应该：
- 提供机制（访问硬件能力）
- 不强制特定策略
- 让用户空间应用程序决定如何使用硬件

## 2. 字符设备驱动

### 2.1 字符设备驱动概述

字符设备驱动是最容易理解的设备驱动类型，适合大多数简单硬件设备。

#### scull设备设计
scull（Simple Character Utility for Loading Localities）是一个字符驱动示例：

**设备类型：**
- **scull0-scull3**：全局持久内存设备
- **scullpipe0-scullpipe3**：FIFO管道设备
- **scullsingle**：单进程设备
- **scullpriv**：每个虚拟控制台私有
- **sculluid/scullwuid**：用户控制的设备

### 2.2 主次设备号

#### 设备号表示
- **dev_t类型**：32位数值，12位主设备号，20位次设备号
- **宏操作**：
  ```c
  MAJOR(dev_t dev);    // 获取主设备号
  MINOR(dev_t dev);    // 获取次设备号
  MKDEV(int major, int minor);  // 构建设备号
  ```

#### 设备号分配
```c
// 静态分配
int register_chrdev_region(dev_t first, unsigned int count, char *name);

// 动态分配
int alloc_chrdev_region(dev_t *dev, unsigned int firstminor, 
                       unsigned int count, char *name);

// 释放设备号
void unregister_chrdev_region(dev_t first, unsigned int count);
```

### 2.3 重要数据结构

#### file_operations结构
```c
struct file_operations scull_fops = {
    .owner = THIS_MODULE,
    .llseek = scull_llseek,
    .read = scull_read,
    .write = scull_write,
    .ioctl = scull_ioctl,
    .open = scull_open,
    .release = scull_release,
};
```

#### inode结构
inode结构包含设备信息：
```c
dev_t i_rdev;  // 设备号
struct cdev *i_cdev;  // 字符设备指针
```

### 2.4 设备注册

#### 字符设备注册
```c
struct cdev *cdev_alloc(void);
void cdev_init(struct cdev *cdev, struct file_operations *fops);
int cdev_add(struct cdev *p, dev_t dev, unsigned count);
void cdev_del(struct cdev *p);
```

#### 设备结构体
```c
struct scull_dev {
    struct scull_qset *data;  // 指向数据区域的指针
    int quantum;              // 当前量子大小
    int qset;                 // 量子集大小
    unsigned int size;        // 设备中的数据总量
    struct semaphore sem;     // 并发控制信号量
    struct cdev cdev;         // 字符设备结构
};
```

### 2.5 核心操作函数

#### open函数
```c
static int scull_open(struct inode *inode, struct file *filp)
{
    struct scull_dev *dev;
    
    dev = container_of(inode->i_cdev, struct scull_dev, cdev);
    filp->private_data = dev;
    
    // 检查文件标志
    if ((filp->f_flags & O_ACCMODE) == O_WRONLY) {
        // 写入模式处理
    }
    
    return 0;
}
```

#### release函数
```c
static int scull_release(struct inode *inode, struct file *filp)
{
    // 清理资源
    return 0;
}
```

#### read函数
```c
static ssize_t scull_read(struct file *filp, char __user *buf, size_t count,
                         loff_t *f_pos)
{
    struct scull_dev *dev = filp->private_data;
    struct scull_qset *dptr;
    int quantum = dev->quantum;
    int qset = dev->qset;
    int itemsize = quantum * qset;
    
    // 计算位置
    if (*f_pos >= dev->size)
        return 0;
    
    if (*f_pos + count > dev->size)
        count = dev->size - *f_pos;
    
    // 复制数据到用户空间
    if (copy_to_user(buf, /* 源指针 */, count))
        return -EFAULT;
    
    *f_pos += count;
    return count;
}
```

#### write函数
```c
static ssize_t scull_write(struct file *filp, const char __user *buf, size_t count,
                          loff_t *f_pos)
{
    struct scull_dev *dev = filp->private_data;
    
    // 检查和扩展设备
    if (*f_pos >= dev->size)
        return -ENOSPC;
    
    if (*f_pos + count > dev->size)
        count = dev->size - *f_pos;
    
    // 从用户空间复制数据
    if (copy_from_user(/* 目标指针 */, buf, count))
        return -EFAULT;
    
    *f_pos += count;
    return count;
}
```

## 3. 内核模块编程

### 3.1 Hello World模块

最简单的内核模块示例：
```c
#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

static int hello_init(void)
{
    printk(KERN_ALERT "Hello, world\n");
    return 0;
}

static void hello_exit(void)
{
    printk(KERN_ALERT "Goodbye, cruel world\n");
}

module_init(hello_init);
module_exit(hello_exit);
```

### 3.2 模块构建

#### Makefile示例
```makefile
obj-m := hello.o

# 如果从内核构建系统调用
ifneq ($(KERNELRELEASE),)
    obj-m := hello.o
else
    KERNELDIR ?= /lib/modules/$(shell uname -r)/build
    PWD := $(shell pwd)
    
default:
    $(MAKE) -C $(KERNELDIR) M=$(PWD) modules
endif
```

#### 编译和加载
```bash
make
insmod ./hello.ko
rmmod hello
```

### 3.3 模块参数

#### 参数声明
```c
static char *whom = "world";
static int howmany = 1;

module_param(howmany, int, S_IRUGO);
module_param(whom, charp, S_IRUGO);
```

#### 支持的参数类型
- `bool`/`invbool`：布尔值
- `charp`：字符指针
- `int`/`long`/`short`：整数类型
- `uint`/`ulong`/`ushort`：无符号整数类型
- 数组参数：`module_param_array(name, type, num, perm)`

### 3.4 内核符号表

#### 导出符号
```c
EXPORT_SYMBOL(symbol);
EXPORT_SYMBOL_GPL(symbol);
```

#### 模块堆叠
- 模块可以堆叠在其他模块之上
- 使用`modprobe`自动加载依赖模块
- 示例：USB设备模块堆叠在usbcore和input模块上

## 4. 并发与竞态条件

### 4.1 并发来源

Linux内核中的并发来源：
- 多进程同时访问设备
- 硬件中断（异步）
- 内核定时器和其他软件抽象
- 对称多处理器（SMP）系统
- 2.6内核的抢占性

### 4.2 内核同步原语

#### 信号量（Semaphores）
```c
struct semaphore sem;
void sema_init(struct semaphore *sem, int val);

void down(struct semaphore *sem);      // 不可中断
int down_interruptible(struct semaphore *sem);  // 可中断
void up(struct semaphore *sem);        // 释放信号量
```

#### 互斥体（Mutexes）
```c
struct mutex mutex;
void mutex_init(struct mutex *mutex);
void mutex_lock(struct mutex *mutex);
int mutex_lock_interruptible(struct mutex *mutex);
void mutex_unlock(struct mutex *mutex);
```

#### 自旋锁（Spinlocks）
```c
spinlock_t lock;
spin_lock_init(&lock);
spin_lock(&lock);      // 获取锁
spin_unlock(&lock);    // 释放锁

// 读写自旋锁
rwlock_t rwlock;
read_lock(&rwlock);
read_unlock(&rwlock);
write_lock(&rwlock);
write_unlock(&rwlock);
```

#### 完成机制（Completions）
```c
struct completion done;
init_completion(&done);

// 等待完成
wait_for_completion(&done);

// 标记完成
complete(&done);
```

### 4.3 竞态条件处理

#### 错误处理模式
```c
int __init my_init_function(void)
{
    int err;
    
    err = register_this(ptr1, "skull");
    if (err) goto fail_this;
    
    err = register_that(ptr2, "skull");
    if (err) goto fail_that;
    
    err = register_those(ptr3, "skull");
    if (err) goto fail_those;
    
    return 0;
    
fail_those:
    unregister_that(ptr2, "skull");
fail_that:
    unregister_this(ptr1, "skull");
fail_this:
    return err;
}
```

## 5. 中断处理

### 5.1 中断处理基础

#### 中断处理程序特点
- 执行时间应尽可能短
- 不能调用可能阻塞的函数
- 必须快速处理并返回

#### 中断处理流程
1. **上半部（Top Half）**：快速处理，标记需要延迟的工作
2. **下半部（Bottom Half）**：处理耗时的操作

### 5.2 中断处理程序注册

#### 请求中断
```c
int request_irq(unsigned int irq, 
               irq_handler_t handler,
               unsigned long flags,
               const char *name,
               void *dev_id);

void free_irq(unsigned int irq, void *dev_id);
```

#### 中断标志
- `IRQF_SHARED`：共享中断
- `IRQF_ONESHOT`：一次性中断
- `IRQF_TRIGGER_RISING/FALLING/LOW/HIGH`：触发方式

#### 中断处理程序示例
```c
static irqreturn_t intr_handler(int irq, void *dev_id)
{
    struct my_device *dev = dev_id;
    
    // 读取设备状态
    unsigned long flags;
    
    spin_lock_irqsave(&dev->lock, flags);
    
    // 处理中断
    if (device_has_interrupt(dev)) {
        // 处理中断逻辑
        intr = 1;
        wake_up_interruptible(&dev->wait_queue);
    }
    
    spin_unlock_irqrestore(&dev->lock, flags);
    
    return IRQ_HANDLED;  // 或 IRQ_NONE
}
```

### 5.3 中断共享

#### 共享中断处理
```c
static irqreturn_t intr_handler(int irq, void *dev_id)
{
    struct my_device *dev = dev_id;
    
    // 检查是否是本设备的中断
    if (!device_has_interrupt(dev))
        return IRQ_NONE;  // 不是本设备的中断
    
    // 处理中断
    // ...
    
    return IRQ_HANDLED;
}

// 注册共享中断
request_irq(dev->irq, intr_handler, IRQF_SHARED, "my_device", dev);
```

### 5.4 下半部机制

#### 软中断（Softirqs）
```c
struct softirq_action {
    void (*action)(struct softirq_action *);
};

void open_softirq(int nr, void (*action)(struct softirq_action *));
void raise_softirq(unsigned int nr);
```

#### Tasklets
```c
struct tasklet_struct {
    void (*func)(unsigned long);
    unsigned long data;
};

void tasklet_init(struct tasklet_struct *t,
                  void (*func)(unsigned long),
                  unsigned long data);

void tasklet_schedule(struct tasklet_struct *t);
void tasklet_disable(struct tasklet_struct *t);
void tasklet_enable(struct tasklet_struct *t);
```

#### 工作队列
```c
struct work_struct {
    void (*func)(void *);
    void *data;
};

DECLARE_WORK(name, func, data);

schedule_work(&work);
schedule_delayed_work(&work, delay);
```

## 6. 内存管理

### 6.1 内核内存分配

#### kmalloc/kfree
```c
void *kmalloc(size_t size, gfp_t flags);
void kfree(const void *objp);

// 标志位
GFP_KERNEL    // 进程上下文，可以睡眠
GFP_ATOMIC    // 中断上下文，不能睡眠
GFP_USER      // 用户空间分配
```

#### vmalloc/vfree
```c
void *vmalloc(unsigned long size);
void vfree(const void *addr);
```

#### 页面分配
```c
struct page *alloc_pages(gfp_t gfp_mask, unsigned int order);
void __free_pages(struct page *page, unsigned int order);

// 获取页面地址
void *page_address(struct page *page);
```

### 6.2 内存池

#### mempool_t
```c
mempool_t *mempool_create(int min_nr, 
                         mempool_alloc_t *alloc_fn,
                         mempool_free_t *free_fn,
                         void *pool_data);

void mempool_destroy(mempool_t *pool);

void *mempool_alloc(mempool_t *pool, gfp_t gfp_mask);
void mempool_free(void *element, mempool_t *pool);
```

### 6.3 缓存分配器

#### Slab分配器
```c
struct kmem_cache *kmem_cache_create(const char *name, size_t size,
                                    size_t align, unsigned long flags,
                                    void (*ctor)(void *));

void *kmem_cache_alloc(struct kmem_cache *cachep, gfp_t flags);
void kmem_cache_free(struct kmem_cache *cachep, void *objp);
void kmem_cache_destroy(struct kmem_cache *cachep);
```

## 7. 硬件通信

### 7.1 I/O端口

#### 端口操作
```c
// 字节端口
u8 inb(unsigned long port);
void outb(u8 value, unsigned long port);

// 字端口
u16 inw(unsigned long port);
void outw(u16 value, unsigned long port);

// 长端口
u32 inl(unsigned long port);
void outl(u32 value, unsigned long port);

// 字符串操作
void insb(unsigned long port, void *addr, unsigned long count);
void outsb(unsigned long port, const void *addr, unsigned long count);
```

#### 端口分配
```c
struct resource *request_region(unsigned long start, unsigned long len,
                               const char *name);
void release_region(unsigned long start, unsigned long len);
int check_region(unsigned long start, unsigned long len);
```

### 7.2 I/O内存

#### 内存映射
```c
void __iomem *ioremap(unsigned long phys_addr, unsigned long size);
void iounmap(volatile void __iomem *addr);

// 新版本
void __iomem *ioremap_cache(unsigned long phys_addr, unsigned long size);
void __iomem *ioremap_wc(unsigned long phys_addr, unsigned long size);
```

#### 内存访问
```c
u8 readb(const volatile void __iomem *addr);
u16 readw(const volatile void __iomem *addr);
u32 readl(const volatile void __iomem *addr);

void writeb(u8 value, volatile void __iomem *addr);
void writew(u16 value, volatile void __iomem *addr);
void writel(u32 value, volatile void __iomem *addr);
```

#### 内存分配
```c
struct resource *request_mem_region(unsigned long start, unsigned long len,
                                   const char *name);
void release_mem_region(unsigned long start, unsigned long len);
```

## 8. PCI设备驱动

### 8.1 PCI设备枚举

#### PCI设备结构
```c
struct pci_dev {
    struct pci_bus *bus;          // 父总线
    struct pci_driver *driver;    // 驱动绑定
    unsigned int devfn;           // 设备功能号
    unsigned short vendor;        // 厂商ID
    unsigned short device;        // 设备ID
    unsigned int class;           // 设备类
    // ... 更多字段
};
```

#### 扫描PCI设备
```c
struct pci_dev *pci_get_device(unsigned int vendor, unsigned int device,
                              struct pci_dev *from);

struct pci_dev *pci_get_class(unsigned int class, struct pci_dev *from);

int pci_read_config_byte(struct pci_dev *dev, int where, u8 *val);
int pci_read_config_word(struct pci_dev *dev, int where, u16 *val);
int pci_read_config_dword(struct pci_dev *dev, int where, u32 *val);
```

### 8.2 PCI驱动注册

#### 驱动结构
```c
struct pci_driver {
    const char *name;
    const struct pci_device_id *id_table;
    int (*probe)(struct pci_dev *dev, const struct pci_device_id *id);
    void (*remove)(struct pci_dev *dev);
    int (*suspend)(struct pci_dev *dev, pm_message_t state);
    int (*resume)(struct pci_dev *dev);
    // ... 更多字段
};
```

#### 驱动注册
```c
int pci_register_driver(struct pci_driver *driver);
void pci_unregister_driver(struct pci_driver *driver);
```

#### 设备ID表
```c
static struct pci_device_id my_pci_table[] = {
    { PCI_VENDOR_ID_INTEL, PCI_DEVICE_ID_INTEL_82559,
      PCI_ANY_ID, PCI_ANY_ID, 0, 0, 0 },
    { 0, }
};

MODULE_DEVICE_TABLE(pci, my_pci_table);
```

### 8.3 设备初始化

#### 设备探测
```c
static int __devinit my_pci_probe(struct pci_dev *dev,
                                 const struct pci_device_id *id)
{
    int err;
    
    // 启用设备
    err = pci_enable_device(dev);
    if (err)
        return err;
    
    // 请求内存区域
    err = pci_request_regions(dev, "my_driver");
    if (err)
        goto err_disable;
    
    // 映射设备内存
    void __iomem *bar0 = pci_iomap(dev, 0, 0);
    if (!bar0) {
        err = -ENOMEM;
        goto err_release;
    }
    
    // 设置驱动数据
    pci_set_drvdata(dev, my_dev);
    
    return 0;
    
err_release:
    pci_release_regions(dev);
err_disable:
    pci_disable_device(dev);
    return err;
}
```

#### 设备移除
```c
static void __devexit my_pci_remove(struct pci_dev *dev)
{
    struct my_device *my_dev = pci_get_drvdata(dev);
    
    // 取消映射
    pci_iounmap(dev, my_dev->bar0);
    
    // 释放资源
    pci_release_regions(dev);
    pci_disable_device(dev);
    
    // 清理驱动数据
    pci_set_drvdata(dev, NULL);
}
```

## 9. DMA技术

### 9.1 DMA基础概念

#### DMA优势
- 减少CPU负担
- 提高数据传输效率
- 支持大数据块传输

#### DMA类型
- **Bus Mastering DMA**：设备控制总线进行DMA传输
- **Fly-by DMA**：DMA控制器在内存和设备间传输数据

### 9.2 DMA映射

#### 单页映射
```c
struct page *dma_alloc_coherent(struct device *dev, size_t size,
                               dma_addr_t *dma_handle, gfp_t flag);
void dma_free_coherent(struct device *dev, size_t size,
                      void *cpu_addr, dma_addr_t dma_handle);
```

#### 流式DMA映射
```c
dma_addr_t dma_map_single(struct device *dev, void *cpu_addr, size_t size,
                         enum dma_data_direction direction);
void dma_unmap_single(struct device *dev, dma_addr_t dma_addr, size_t size,
                     enum dma_data_direction direction);

// 方向
enum dma_data_direction {
    DMA_BIDIRECTIONAL = 0,
    DMA_TO_DEVICE = 1,
    DMA_FROM_DEVICE = 2,
    DMA_NONE = 3,
};
```

#### 分散/聚集映射
```c
struct scatterlist {
    struct page *page;
    unsigned int offset;
    unsigned int length;
};

int dma_map_sg(struct device *dev, struct scatterlist *sg,
               int nents, enum dma_data_direction direction);
void dma_unmap_sg(struct device *dev, struct scatterlist *sg,
                  int nents, enum dma_data_direction direction);
```

### 9.3 DMA同步

#### 同步操作
```c
void dma_sync_single_for_cpu(struct device *dev, dma_addr_t dma_handle,
                            size_t size, enum dma_data_direction dir);
void dma_sync_single_for_device(struct device *dev, dma_addr_t dma_handle,
                               size_t size, enum dma_data_direction dir);

void dma_sync_sg_for_cpu(struct device *dev, struct scatterlist *sg,
                        int nents, enum dma_data_direction dir);
void dma_sync_sg_for_device(struct device *dev, struct scatterlist *sg,
                           int nents, enum dma_data_direction dir);
```

### 9.4 DMA缓冲区分配

#### 缓冲区分配
```c
void *dma_alloc_noncoherent(struct device *dev, size_t size,
                           dma_addr_t *dma_handle, gfp_t flag);
void dma_free_noncoherent(struct device *dev, size_t size,
                         void *cpu_addr, dma_addr_t dma_handle);

// 连续内存分配
void *dma_alloc_writecombine(struct device *dev, size_t size,
                            dma_addr_t *dma_handle, gfp_t flag);
```

## 10. 块设备驱动

### 10.1 块设备特点

#### 块设备vs字符设备
- 块设备以块为单位传输数据
- 支持随机访问
- 可以缓存数据
- 有更复杂的请求队列

### 10.2 块设备注册

#### 块设备结构
```c
struct block_device {
    struct inode *bd_inode;       // 设备文件inode
    dev_t bd_dev;                 // 设备号
    int bd_openers;               // 打开计数
    struct mutex bd_mutex;        // 互斥锁
    // ... 更多字段
};
```

#### 通用磁盘结构
```c
struct gendisk {
    int major;                    // 主设备号
    int first_minor;              // 第一个次设备号
    int minors;                   // 次设备号数量
    struct request_queue *queue;  // 请求队列
    struct block_device_operations *fops;
    struct device *driverfs_dev;
    // ... 更多字段
};
```

#### 磁盘注册
```c
struct gendisk *alloc_disk(int minors);
void add_disk(struct gendisk *disk);
void del_gdisk(struct gendisk *disk);
void put_disk(struct gendisk *disk);
```

### 10.3 请求队列

#### 请求队列结构
```c
struct request_queue {
    struct request *last_merge;
    struct elevator_queue *elevator;
    struct request_list root_rl;
    struct request *next_rq;
    // ... 更多字段
};
```

#### 请求结构
```c
struct request {
    struct list_head queuelist;
    struct request_queue *q;
    struct bio *bio;
    struct bio *biotail;
    sector_t sector;              // 扇区号
    unsigned long nr_sectors;     // 扇区数
    unsigned int current_nr_sectors;
    int tag;
    int rq_flags;
    // ... 更多字段
};
```

### 10.4 块设备操作

#### 设备操作结构
```c
struct block_device_operations {
    int (*open) (struct block_device *, fmode_t);
    int (*release) (struct block_device *, fmode_t);
    int (*ioctl) (struct block_device *, fmode_t, unsigned, unsigned long);
    int (*compat_ioctl) (struct block_device *, fmode_t, unsigned, unsigned long);
    int (*direct_access) (struct block_device *, sector_t, void **, unsigned long *);
    int (*media_changed) (struct gendisk *);
    unsigned long (*revalidate_disk) (struct gendisk *);
    // ... 更多字段
};
```

#### 设备初始化
```c
static int __init my_block_init(void)
{
    struct gendisk *disk;
    
    // 分配磁盘结构
    disk = alloc_disk(16);  // 16个分区
    if (!disk)
        return -ENOMEM;
    
    // 设置设备号
    disk->major = MY_BLOCK_MAJOR;
    disk->first_minor = 0;
    disk->minors = 16;
    
    // 设置操作函数
    disk->fops = &my_block_ops;
    
    // 初始化请求队列
    disk->queue = blk_init_queue(my_request_fn, &my_lock);
    if (!disk->queue)
        goto out_put_disk;
    
    // 添加磁盘
    add_disk(disk);
    
    return 0;
    
out_put_disk:
    put_disk(disk);
    return -ENOMEM;
}
```

### 10.5 请求处理

#### 请求函数
```c
static void my_request_fn(struct request_queue *q)
{
    struct request *req;
    
    // 循环处理请求
    while ((req = blk_fetch_request(q)) != NULL) {
        // 处理请求
        if (!blk_end_request(req, 0, blk_rq_bytes(req))) {
            // 请求完成
        }
    }
}
```

#### 简单请求处理
```c
static void simple_request_fn(struct request_queue *q)
{
    struct request *req;
    
    while ((req = blk_peek_request(q)) != NULL) {
        // 跳过分区请求
        if (blk_rq_is_passthrough(req)) {
            __blk_end_request_all(req, -EIO);
            continue;
        }
        
        // 处理读写请求
        if (req->cmd_type == REQ_TYPE_FS) {
            process_fs_request(req);
        }
        
        blk_start_request(req);
        __blk_end_request(req, 0, blk_rq_bytes(req));
    }
}
```

## 11. 关键源码示例

### 11.1 字符设备驱动完整示例

```c
/*
 * scull字符设备驱动示例
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/semaphore.h>
#include <linux/uaccess.h>

#define SCULL_MAJOR 0          // 动态分配主设备号
#define SCULL_MINOR 0          // 起始次设备号
#define SCULL_NR_DEVS 4        // 设备数量
#define SCULL_QUANTUM 4000     // 量子大小
#define SCULL_QSET 1000        // 量子集大小

struct scull_dev {
    struct scull_qset *data;   // 指向数据区域的指针
    int quantum;               // 当前量子大小
    int qset;                  // 量子集大小
    unsigned int size;         // 设备中的数据总量
    unsigned int access_key;   // 访问控制密钥
    struct semaphore sem;      // 并发控制信号量
    struct cdev cdev;          // 字符设备结构
};

struct scull_qset {
    void **data;
    struct scull_qset *next;
};

static int scull_major = SCULL_MAJOR;
static int scull_minor = SCULL_MINOR;
static int scull_nr_devs = SCULL_NR_DEVS;
static int scull_quantum = SCULL_QUANTUM;
static int scull_qset = SCULL_QSET;

module_param(scull_major, int, S_IRUGO);
module_param(scull_minor, int, S_IRUGO);
module_param(scull_nr_devs, int, S_IRUGO);
module_param(scull_quantum, int, S_IRUGO);
module_param(scull_qset, int, S_IRUGO);

MODULE_LICENSE("Dual BSD/GPL");
MODULE_AUTHOR("Linux Device Drivers 3rd Edition");
MODULE_DESCRIPTION("SCULL char device driver");

static struct scull_dev *scull_devices;  // 设备数组

static struct scull_qset *scull_follow(struct scull_dev *dev, int n)
{
    struct scull_qset *qs = dev->data;
    struct scull_qset *prev;
    
    // 查找或创建第n个量子集
    while (n--) {
        if (!qs) {
            qs = kmalloc(sizeof(struct scull_qset), GFP_KERNEL);
            if (!qs)
                return NULL;
            memset(qs, 0, sizeof(struct scull_qset));
            if (prev)
                prev->next = qs;
            if (!dev->data)
                dev->data = qs;
        }
        prev = qs;
        qs = qs->next;
    }
    return qs;
}

static int scull_trim(struct scull_dev *dev)
{
    struct scull_qset *next, *dptr;
    int qset = dev->qset;
    int i;
    
    for (dptr = dev->data; dptr; dptr = next) {
        if (dptr->data) {
            for (i = 0; i < qset; i++)
                kfree(dptr->data[i]);
            kfree(dptr->data);
        }
        next = dptr->next;
        kfree(dptr);
    }
    dev->size = 0;
    dev->quantum = scull_quantum;
    dev->qset = scull_qset;
    dev->data = NULL;
    return 0;
}

static int scull_open(struct inode *inode, struct file *filp)
{
    struct scull_dev *dev;
    
    dev = container_of(inode->i_cdev, struct scull_dev, cdev);
    filp->private_data = dev;
    
    // 非阻塞访问检查
    if ((filp->f_flags & O_ACCMODE) == O_WRONLY) {
        if (down_interruptible(&dev->sem))
            return -ERESTARTSYS;
        scull_trim(dev);
        up(&dev->sem);
    }
    
    return 0;
}

static int scull_release(struct inode *inode, struct file *filp)
{
    return 0;
}

static loff_t scull_llseek(struct file *filp, loff_t off, int whence)
{
    struct scull_dev *dev = filp->private_data;
    loff_t newpos;
    
    switch (whence) {
    case 0: /* SEEK_SET */
        newpos = off;
        break;
    case 1: /* SEEK_CUR */
        newpos = filp->f_pos + off;
        break;
    case 2: /* SEEK_END */
        newpos = dev->size + off;
        break;
    default:
        return -EINVAL;
    }
    
    if (newpos < 0)
        return -EINVAL;
    
    filp->f_pos = newpos;
    return newpos;
}

static ssize_t scull_read(struct file *filp, char __user *buf, size_t count,
                         loff_t *f_pos)
{
    struct scull_dev *dev = filp->private_data;
    struct scull_qset *dptr;
    int quantum = dev->quantum, qset = dev->qset;
    int itemsize = quantum * qset;
    int s_pos, q_pos, rest;
    ssize_t retval = 0;
    
    if (down_interruptible(&dev->sem))
        return -ERESTARTSYS;
    
    if (*f_pos >= dev->size)
        goto out;
    
    if (*f_pos + count > dev->size)
        count = dev->size - *f_pos;
    
    // 查找起始量子集
    dptr = scull_follow(dev, *f_pos / itemsize);
    if (!dptr || !dptr->data)
        goto out;
    
    s_pos = *f_pos % itemsize;
    q_pos = s_pos / quantum;
    rest = s_pos % quantum;
    
    while (count > 0) {
        // 计算要复制的字节数
        unsigned long n = quantum - rest;
        if (n > count)
            n = count;
        
        // 确保量子存在
        if (!dptr->data) {
            dptr->data = kzalloc(qset * sizeof(void *), GFP_KERNEL);
            if (!dptr->data)
                goto out;
        }
        
        if (!dptr->data[q_pos]) {
            dptr->data[q_pos] = kzalloc(quantum, GFP_KERNEL);
            if (!dptr->data[q_pos])
                goto out;
        }
        
        // 复制数据到用户空间
        if (copy_to_user(buf, dptr->data[q_pos] + rest, n)) {
            retval = -EFAULT;
            goto out;
        }
        
        rest = (rest + n) % quantum;
        q_pos = rest / quantum;
        
        if (q_pos) {
            dptr = dptr->next;
            if (!dptr) {
                dptr = scull_follow(dev, 0);
                if (!dptr)
                    break;
            }
        }
        
        buf += n;
        count -= n;
        retval += n;
        *f_pos += n;
    }
    
out:
    up(&dev->sem);
    return retval;
}

static ssize_t scull_write(struct file *filp, const char __user *buf, size_t count,
                          loff_t *f_pos)
{
    struct scull_dev *dev = filp->private_data;
    struct scull_qset *dptr;
    int quantum = dev->quantum, qset = dev->qset;
    int itemsize = quantum * qset;
    int s_pos, q_pos, rest;
    ssize_t retval = -ENOMEM;
    
    if (down_interruptible(&dev->sem))
        return -ERESTARTSYS;
    
    // 查找起始量子集
    dptr = scull_follow(dev, *f_pos / itemsize);
    if (!dptr)
        goto out;
    
    s_pos = *f_pos % itemsize;
    q_pos = s_pos / quantum;
    rest = s_pos % quantum;
    
    while (count > 0) {
        // 计算要复制的字节数
        unsigned long n = quantum - rest;
        if (n > count)
            n = count;
        
        // 确保数据存在
        if (!dptr->data) {
            dptr->data = kzalloc(qset * sizeof(void *), GFP_KERNEL);
            if (!dptr->data)
                goto out;
        }
        
        if (!dptr->data[q_pos]) {
            dptr->data[q_pos] = kzalloc(quantum, GFP_KERNEL);
            if (!dptr->data[q_pos])
                goto out;
        }
        
        // 从用户空间复制数据
        if (copy_from_user(dptr->data[q_pos] + rest, buf, n)) {
            retval = -EFAULT;
            goto out;
        }
        
        rest = (rest + n) % quantum;
        q_pos = rest / quantum;
        
        if (q_pos) {
            dptr = dptr->next;
            if (!dptr) {
                dptr = scull_follow(dev, 0);
                if (!dptr)
                    goto out;
            }
        }
        
        buf += n;
        count -= n;
        retval += n;
        *f_pos += n;
    }
    
    dev->size += retval;
    
out:
    up(&dev->sem);
    return retval;
}

static struct file_operations scull_fops = {
    .owner = THIS_MODULE,
    .llseek = scull_llseek,
    .read = scull_read,
    .write = scull_write,
    .open = scull_open,
    .release = scull_release,
};

static void scull_cleanup_module(void)
{
    int i;
    dev_t devno = MKDEV(scull_major, scull_minor);
    
    if (scull_devices) {
        for (i = 0; i < scull_nr_devs; i++) {
            scull_trim(scull_devices + i);
            cdev_del(&scull_devices[i].cdev);
        }
        kfree(scull_devices);
    }
    
    unregister_chrdev_region(devno, scull_nr_devs);
}

static int __init scull_init_module(void)
{
    int result, i;
    dev_t dev = 0;
    
    // 分配设备号
    if (scull_major) {
        dev = MKDEV(scull_major, scull_minor);
        result = register_chrdev_region(dev, scull_nr_devs, "scull");
    } else {
        result = alloc_chrdev_region(&dev, scull_minor, scull_nr_devs, "scull");
        scull_major = MAJOR(dev);
    }
    
    if (result < 0) {
        printk(KERN_WARNING "scull: can't get major %d\n", scull_major);
        return result;
    }
    
    // 分配设备结构
    scull_devices = kmalloc(scull_nr_devs * sizeof(struct scull_dev), GFP_KERNEL);
    if (!scull_devices) {
        result = -ENOMEM;
        goto fail;
    }
    memset(scull_devices, 0, scull_nr_devs * sizeof(struct scull_dev));
    
    // 初始化设备
    for (i = 0; i < scull_nr_devs; i++) {
        scull_devices[i].quantum = scull_quantum;
        scull_devices[i].qset = scull_qset;
        sema_init(&scull_devices[i].sem, 1);
        cdev_init(&scull_devices[i].cdev, &scull_fops);
        scull_devices[i].cdev.owner = THIS_MODULE;
        scull_devices[i].cdev.ops = &scull_fops;
        
        result = cdev_add(&scull_devices[i].cdev, dev + i, 1);
        if (result)
            printk(KERN_NOTICE "Error %d adding scull%d", result, i);
    }
    
    return 0;
    
fail:
    scull_cleanup_module();
    return result;
}

module_init(scull_init_module);
module_exit(scull_cleanup_module);
```

### 11.2 中断处理示例

```c
/*
 * 并行端口中断处理示例
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/interrupt.h>
#include <linux/ioport.h>
#include <linux/delay.h>
#include <linux/errno.h>
#include <linux/slab.h>

#define LPT_BASE 0x378  // 并行端口基地址
#define LPT_STATUS (LPT_BASE + 1)  // 状态端口
#define LPT_CONTROL (LPT_BASE + 2) // 控制端口

#define IRQ 7  // 并行端口中断号

struct my_device {
    unsigned long base;
    int irq;
    struct tasklet_struct tasklet;
    spinlock_t lock;
    unsigned char status;
};

static struct my_device *my_dev;

static irqreturn_t my_interrupt(int irq, void *dev_id)
{
    struct my_device *dev = dev_id;
    unsigned long flags;
    
    // 读取设备状态
    spin_lock_irqsave(&dev->lock, flags);
    dev->status = inb(LPT_STATUS);
    spin_unlock_irqrestore(&dev->lock, flags);
    
    // 调度下半部处理
    tasklet_schedule(&dev->tasklet);
    
    return IRQ_HANDLED;
}

static void my_tasklet_handler(unsigned long data)
{
    struct my_device *dev = (struct my_device *)data;
    unsigned long flags;
    
    printk(KERN_INFO "my_device: processing interrupt, status=0x%02x\n", dev->status);
    
    // 在这里处理耗时的中断后工作
    spin_lock_irqsave(&dev->lock, flags);
    // 执行具体的中断后处理逻辑
    spin_unlock_irqrestore(&dev->lock, flags);
}

static int __init my_init(void)
{
    int ret;
    
    // 分配设备结构
    my_dev = kmalloc(sizeof(struct my_device), GFP_KERNEL);
    if (!my_dev)
        return -ENOMEM;
    
    // 初始化设备
    my_dev->base = LPT_BASE;
    my_dev->irq = IRQ;
    spin_lock_init(&my_dev->lock);
    tasklet_init(&my_dev->tasklet, my_tasklet_handler, (unsigned long)my_dev);
    
    // 请求I/O端口
    if (!request_region(LPT_BASE, 3, "my_device")) {
        ret = -EBUSY;
        goto err_free_dev;
    }
    
    // 请求中断
    ret = request_irq(IRQ, my_interrupt, IRQF_SHARED, "my_device", my_dev);
    if (ret) {
        printk(KERN_ERR "my_device: can't get assigned IRQ %d\n", IRQ);
        goto err_release_region;
    }
    
    // 启用并行端口中断
    outb(inb(LPT_CONTROL) | 0x10, LPT_CONTROL);
    
    printk(KERN_INFO "my_device: initialized successfully\n");
    return 0;
    
err_release_region:
    release_region(LPT_BASE, 3);
err_free_dev:
    kfree(my_dev);
    return ret;
}

static void __exit my_exit(void)
{
    // 禁用中断
    outb(inb(LPT_CONTROL) & ~0x10, LPT_CONTROL);
    
    // 释放中断
    free_irq(IRQ, my_dev);
    
    // 释放端口
    release_region(LPT_BASE, 3);
    
    // 清理任务队列
    tasklet_kill(&my_dev->tasklet);
    
    // 释放设备结构
    kfree(my_dev);
    
    printk(KERN_INFO "my_device: unloaded\n");
}

module_init(my_init);
module_exit(my_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Linux Device Drivers 3rd Edition");
```

## 12. 总结与建议

### 12.1 核心概念总结

1. **设备驱动架构**
   - 机制与策略分离
   - 模块化设计
   - 设备分类（字符、块、网络）

2. **字符设备驱动**
   - 主次设备号管理
   - file_operations结构
   - 设备注册与注销

3. **并发控制**
   - 信号量和互斥体
   - 自旋锁
   - 完成机制

4. **中断处理**
   - 上半部和下半部
   - 中断共享
   - 软中断和任务队列

5. **内存管理**
   - 内核内存分配
   - DMA映射
   - 缓存分配器

6. **硬件通信**
   - I/O端口操作
   - I/O内存映射
   - 资源管理

7. **PCI设备驱动**
   - 设备枚举
   - 配置空间访问
   - 设备驱动注册

8. **DMA技术**
   - DMA映射类型
   - 缓冲区分配
   - 同步操作

9. **块设备驱动**
   - 请求队列管理
   - 块设备操作
   - 数据传输处理

### 12.2 编程最佳实践

1. **错误处理**
   - 始终检查返回值
   - 使用goto进行错误恢复
   - 资源分配失败时的清理

2. **并发安全**
   - 使用适当的锁机制
   - 避免死锁
   - 考虑中断上下文限制

3. **性能优化**
   - 减少中断处理时间
   - 合理使用缓存
   - 批量处理请求

4. **代码质量**
   - 遵循内核编码风格
   - 添加适当的注释
   - 使用MODULE_*宏

### 12.3 进一步学习建议

1. **深入内核源码**
   - 学习现有驱动实现
   - 理解内核API变化
   - 关注内核邮件列表

2. **实践项目**
   - 编写简单设备驱动
   - 参与开源项目
   - 硬件平台移植

3. **相关技术**
   - USB驱动开发
   - 网络设备驱动
   - 嵌入式Linux开发

这份报告提供了Linux设备驱动开发的核心技术内容和实用示例，为深入学习Linux内核和设备驱动开发提供了全面的技术指导。

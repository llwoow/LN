# Linux Device Drivers 第三版源码示例集

## 文档说明

本文件包含了从《Linux Device Drivers, Third Edition》PDF文档中提取的实际源码示例，涵盖了设备驱动开发的核心技术点。

## 1. 基础模块示例

### 1.1 Hello World模块

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

### 1.2 带参数的模块

```c
static char *whom = "world";
static int howmany = 1;

module_param(howmany, int, S_IRUGO);
module_param(whom, charp, S_IRUGO);

MODULE_PARM_DESC(howmany, "How many times to say hello");
MODULE_PARM_DESC(whom, "Whom to say hello to");
```

### 1.3 模块参数示例（hellop）

```c
static int __init hellop_init(void)
{
    int i;
    
    for (i = 0; i < howmany; i++)
        printk(KERN_ALERT "Hello, %s\n", whom);
    
    return 0;
}

static void __exit hellop_exit(void)
{
    printk(KERN_ALERT "Goodbye, %s\n", whom);
}

module_init(hellop_init);
module_exit(hellop_exit);
```

## 2. 字符设备驱动核心代码

### 2.1 设备结构体定义

```c
struct scull_dev {
    struct scull_qset *data;  /* Pointer to first quantum set */
    int quantum;              /* The current allocation size */
    int qset;                 /* The current array size */
    unsigned int size;        /* Amount of data stored here */
    unsigned int access_key;  /* Used by sculluid and scullpriv */
    struct semaphore sem;     /* Mutual exclusion */
    struct cdev cdev;         /* Char device structure */
};

struct scull_qset {
    void **data;
    struct scull_qset *next;
};
```

### 2.2 file_operations结构

```c
struct file_operations scull_fops = {
    .owner =    THIS_MODULE,
    .llseek =   scull_llseek,
    .read =     scull_read,
    .write =    scull_write,
    .ioctl =    scull_ioctl,
    .open =     scull_open,
    .release =  scull_release,
};
```

### 2.3 设备号分配代码

```c
if (scull_major) {
    dev = MKDEV(scull_major, scull_minor);
    result = register_chrdev_region(dev, scull_nr_devs, "scull");
} else {
    result = alloc_chrdev_region(&dev, scull_minor, scull_nr_devs, "scull");
    scull_major = MAJOR(dev);
}
```

### 2.4 字符设备注册

```c
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
```

### 2.5 设备初始化

```c
static int __init scull_init_module(void)
{
    int result, i;
    dev_t dev = 0;

    /*
     * Get a range of minor numbers to work with, asking for a dynamic
     * major unless directed otherwise at load time.
     */
    if (scull_major) {
        dev = MKDEV(scull_major, scull_minor);
        result = register_chrdev_region(dev, scull_nr_devs, "scull");
    } else {
        result = alloc_chrdev_region(&dev, scull_minor, scull_nr_devs,
                                     "scull");
        scull_major = MAJOR(dev);
    }
    if (result < 0) {
        printk(KERN_WARNING "scull: can't get major %d\n", scull_major);
        return result;
    }

    /*
     * allocate the devices -- we can't have them static, as the number
     * can be specified at load time
     */
    scull_devices = kmalloc(scull_nr_devs * sizeof(struct scull_dev), GFP_KERNEL);
    if (!scull_devices) {
        result = -ENOMEM;
        goto fail;
    }
    memset(scull_devices, 0, scull_nr_devs * sizeof(struct scull_dev));

    /* Initialize each device. */
    for (i = 0; i < scull_nr_devs; i++) {
        scull_devices[i].quantum = scull_quantum;
        scull_devices[i].qset = scull_qset;
        sema_init(&scull_devices[i].sem, 1);
        cdev_init(&scull_devices[i].cdev, &scull_fops);
        scull_devices[i].cdev.owner = THIS_MODULE;
        scull_devices[i].cdev.ops = &scull_fops;
        result = cdev_add(&scull_devices[i].cdev, dev + i, 1);
        /* Fail gracefully if need be */
        if (result)
            printk(KERN_NOTICE "Error %d adding scull%d", result, i);
    }

    return 0; /* success */

fail:
    scull_cleanup_module();
    return result;
}
```

## 3. 设备操作函数

### 3.1 open函数

```c
static int scull_open(struct inode *inode, struct file *filp)
{
    struct scull_dev *dev; /* device information */

    dev = container_of(inode->i_cdev, struct scull_dev, cdev);
    filp->private_data = dev; /* for other methods */

    /* now trim to 0 the length of the device if open was write-only */
    if ((filp->f_flags & O_ACCMODE) == O_WRONLY) {
        if (down_interruptible(&dev->sem))
            return -ERESTARTSYS;
        scull_trim(dev); /* ignore errors */
        up(&dev->sem);
    }
    return 0;          /* success */
}
```

### 3.2 release函数

```c
static int scull_release(struct inode *inode, struct file *filp)
{
    /* nothing to do, because we don't keep any state in scull */
    return 0;
}
```

### 3.3 read函数

```c
static ssize_t scull_read(struct file *filp, char __user *buf, size_t count,
                         loff_t *f_pos)
{
    struct scull_dev *dev = filp->private_data; 
    struct scull_qset *dptr;    /* the first listitem */
    int quantum = dev->quantum, qset = dev->qset;
    int itemsize = quantum * qset; /* how many bytes in the listitem */
    int s_pos, q_pos, rest;     /* which part of which item */

    ssize_t retval = 0;

    if (down_interruptible(&dev->sem))
        return -ERESTARTSYS;

    if (*f_pos >= dev->size)
        goto out;

    if (*f_pos + count > dev->size)
        count = dev->size - *f_pos;

    /* find listitem, qset index and offset in the quantum */
    dptr = scull_follow(dev, *f_pos / itemsize);
    if (!dptr)
        goto out;
    if (!dptr->data)
        goto out;
    s_pos = *f_pos % itemsize;
    q_pos = s_pos / quantum;
    rest = s_pos % quantum;

    /* read only up to the end of this quantum */
    if (count > quantum - q_pos)
        count = quantum - q_pos;

    /* copy data to user space */
    if (copy_to_user(buf, dptr->data[q_pos] + q_pos, count)) {
        retval = -EFAULT;
        goto out;
    }

    *f_pos += count;
    retval = count;

  out:
    up(&dev->sem);
    return retval;
}
```

### 3.4 write函数

```c
static ssize_t scull_write(struct file *filp, const char __user *buf, size_t count,
                          loff_t *f_pos)
{
    struct scull_dev *dev = filp->private_data;
    struct scull_qset *dptr;
    int quantum = dev->quantum, qset = dev->qset;
    int itemsize = quantum * qset;
    int s_pos, q_pos, rest;
    ssize_t retval = -ENOMEM; /* value used in "goto out" statements */

    if (down_interruptible(&dev->sem))
        return -ERESTARTSYS;

    /* find listitem, qset index and offset in the quantum */
    dptr = scull_follow(dev, *f_pos / itemsize);
    if (!dptr)
        goto out;

    s_pos = *f_pos % itemsize;
    q_pos = s_pos / quantum;
    rest = s_pos % quantum;

    /* write only up to the end of this quantum */
    if (count > quantum - q_pos)
        count = quantum - q_pos;

    if (!dptr->data) {
        dptr->data = kmalloc(qset * sizeof(void *), GFP_KERNEL);
        if (!dptr->data)
            goto out;
        memset(dptr->data, 0, qset * sizeof(char *));
    }

    if (!dptr->data[q_pos]) {
        dptr->data[q_pos] = kmalloc(quantum, GFP_KERNEL);
        if (!dptr->data[q_pos])
            goto out;
    }

    /* if copying from user space, do it in safe way */
    if (copy_from_user(dptr->data[q_pos] + q_pos, buf, count)) {
        retval = -EFAULT;
        goto out;
    }

    *f_pos += count;
    retval = count;

        /* update the size */
    if (dev->size < *f_pos)
        dev->size = *f_pos;

  out:
    up(&dev->sem);
    return retval;
}
```

### 3.5 llseek函数

```c
static loff_t scull_llseek(struct file *filp, loff_t off, int whence)
{
    struct scull_dev *dev = filp->private_data;
    loff_t newpos;

    switch(whence) {
    case 0: /* SEEK_SET */
        newpos = off;
        break;
    case 1: /* SEEK_CUR */
        newpos = filp->f_pos + off;
        break;
    case 2: /* SEEK_END */
        newpos = dev->size + off;
        break;
    default: /* invalid */
        return -EINVAL;
    }
    if (newpos < 0)
        return -EINVAL;
    filp->f_pos = newpos;
    return newpos;
}
```

## 4. 并发控制示例

### 4.1 信号量使用

```c
struct scull_dev {
    /* ... other fields ... */
    struct semaphore sem;     /* mutual exclusion semaphore */
};

sema_init(&dev->sem, 1);  /* 初始化为1，表示可用 */

if (down_interruptible(&dev->sem))
    return -ERESTARTSYS;

/* 临界区代码 */

up(&dev->sem);  /* 释放信号量 */
```

### 4.2 自旋锁使用

```c
struct my_device {
    spinlock_t lock;
    unsigned char status;
};

spin_lock_init(&dev->lock);

/* 在中断上下文中使用 */
spin_lock(&dev->lock);
/* 临界区代码 */
spin_unlock(&dev->lock);

/* 在中断上下文中使用（保存标志） */
unsigned long flags;
spin_lock_irqsave(&dev->lock, flags);
/* 临界区代码 */
spin_unlock_irqrestore(&dev->lock, flags);
```

### 4.3 完成机制

```c
struct my_device {
    struct completion done;
    int busy;
};

init_completion(&dev->done);

/* 在等待完成的代码中 */
wait_for_completion(&dev->done);

/* 在完成操作的代码中 */
complete(&dev->done);
```

## 5. 中断处理示例

### 5.1 中断处理程序

```c
static irqreturn_t intr_handler(int irq, void *dev_id)
{
    struct my_device *dev = dev_id;
    unsigned long flags;

    spin_lock_irqsave(&dev->lock, flags);

    /* read the device status */
    if (device_has_interrupt(dev)) {
        dev->status = inb(dev->base + STATUS);
        intr = 1;  /* we received an interrupt */
        wake_up_interruptible(&dev->wait_queue);
    }

    spin_unlock_irqrestore(&dev->lock, flags);
    return IRQ_HANDLED;      /* we handled the interrupt */
}
```

### 5.2 中断共享

```c
static irqreturn_t intr_handler(int irq, void *dev_id)
{
    struct my_device *dev = dev_id;
    int status, handled = 0;

    status = inb(dev->base + STATUS);
    if (status & DEVICE_INTERRUPT) {
        handled = 1;
        /* real interrupt handling here */
    }

    return IRQ_RETVAL(handled);
}

/* 注册共享中断 */
request_irq(dev->irq, intr_handler, IRQF_SHARED, "my_device", dev);
```

### 5.3 任务队列

```c
static struct work_struct my_work;

static void my_work_handler(struct work_struct *work)
{
    struct my_device *dev = container_of(work, struct my_device, work);
    
    /* 耗时的中断后处理工作 */
    printk(KERN_INFO "Processing interrupt work\n");
}

static irqreturn_t my_interrupt(int irq, void *dev_id)
{
    struct my_device *dev = dev_id;

    /* 快速处理 */
    schedule_work(&dev->work);
    
    return IRQ_HANDLED;
}

/* 初始化 */
INIT_WORK(&dev->work, my_work_handler);
```

## 6. 内存管理示例

### 6.1 内核内存分配

```c
/* 分配内存 */
char *buffer = kmalloc(1024, GFP_KERNEL);
if (!buffer) {
    return -ENOMEM;
}

/* 使用内存 */
memset(buffer, 0, 1024);

/* 释放内存 */
kfree(buffer);

/* 页面分配 */
struct page *page = alloc_pages(GFP_KERNEL, 0);
if (!page) {
    return -ENOMEM;
}

void *addr = page_address(page);

/* 释放页面 */
__free_pages(page, 0);
```

### 6.2 缓存分配器

```c
struct kmem_cache *my_cachep;

static int __init my_init(void)
{
    my_cachep = kmem_cache_create("my_driver_cache", 
                                  sizeof(struct my_data),
                                  0, 0, NULL);
    if (!my_cachep)
        return -ENOMEM;
    return 0;
}

static void __exit my_exit(void)
{
    if (my_cachep)
        kmem_cache_destroy(my_cachep);
}

/* 使用缓存 */
struct my_data *data = kmem_cache_alloc(my_cachep, GFP_KERNEL);
if (data) {
    /* 使用data */
    kmem_cache_free(my_cachep, data);
}
```

### 6.3 DMA映射

```c
/* 单页DMA映射 */
dma_addr_t dma_handle;
void *cpu_addr = dma_alloc_coherent(dev, size, &dma_handle, GFP_KERNEL);
if (!cpu_addr) {
    return -ENOMEM;
}

/* 使用DMA */
memcpy_toio((void __iomem *)cpu_addr, source, size);

/* 同步 */
dma_sync_single_for_device(dev, dma_handle, size, DMA_TO_DEVICE);

/* 清理 */
dma_free_coherent(dev, size, cpu_addr, dma_handle);

/* 流式DMA映射 */
dma_addr_t dma_handle;
void *cpu_addr = kmalloc(size, GFP_KERNEL);
dma_handle = dma_map_single(dev, cpu_addr, size, DMA_TO_DEVICE);

/* 使用DMA */

/* 同步和清理 */
dma_unmap_single(dev, dma_handle, size, DMA_TO_DEVICE);
kfree(cpu_addr);
```

## 7. PCI设备驱动示例

### 7.1 PCI设备ID表

```c
static struct pci_device_id my_pci_table[] = {
    { PCI_VENDOR_ID_INTEL, PCI_DEVICE_ID_INTEL_82559,
      PCI_ANY_ID, PCI_ANY_ID, 0, 0, 0 },
    { 0, }
};

MODULE_DEVICE_TABLE(pci, my_pci_table);
```

### 7.2 PCI驱动结构

```c
static struct pci_driver my_pci_driver = {
    .name = "my_driver",
    .id_table = my_pci_table,
    .probe = my_pci_probe,
    .remove = my_pci_remove,
    .suspend = my_pci_suspend,
    .resume = my_pci_resume,
};
```

### 7.3 设备探测

```c
static int __devinit my_pci_probe(struct pci_dev *dev,
                                 const struct pci_device_id *id)
{
    int err;
    void __iomem *bar0;

    /* 启用设备 */
    err = pci_enable_device(dev);
    if (err)
        return err;

    /* 请求内存区域 */
    err = pci_request_regions(dev, "my_driver");
    if (err)
        goto err_disable;

    /* 映射设备内存 */
    bar0 = pci_iomap(dev, 0, 0);
    if (!bar0) {
        err = -ENOMEM;
        goto err_release;
    }

    /* 设置驱动数据 */
    pci_set_drvdata(dev, bar0);

    /* 启用DMA */
    pci_set_master(dev);

    return 0;

err_release:
    pci_release_regions(dev);
err_disable:
    pci_disable_device(dev);
    return err;
}
```

### 7.4 设备移除

```c
static void __devexit my_pci_remove(struct pci_dev *dev)
{
    void __iomem *bar0 = pci_get_drvdata(dev);

    /* 取消映射 */
    pci_iounmap(dev, bar0);

    /* 释放资源 */
    pci_release_regions(dev);
    pci_disable_device(dev);

    /* 清理驱动数据 */
    pci_set_drvdata(dev, NULL);
}
```

## 8. I/O端口和内存示例

### 8.1 I/O端口操作

```c
/* 端口分配 */
struct resource *port_resource;
port_resource = request_region(LPT_BASE, 3, "my_lpt");
if (!port_resource) {
    return -EBUSY;
}

/* 端口操作 */
u8 status = inb(LPT_STATUS);
outb(data, LPT_DATA);

/* 释放端口 */
release_region(LPT_BASE, 3);
```

### 8.2 I/O内存映射

```c
/* 内存区域分配 */
struct resource *mem_resource;
mem_resource = request_mem_region(0xA0000, 0x20000, "vga");
if (!mem_resource) {
    return -EBUSY;
}

/* 映射内存 */
void __iomem *vga_mem = ioremap(0xA0000, 0x20000);
if (!vga_mem) {
    release_mem_region(0xA0000, 0x20000);
    return -ENOMEM;
}

/* 访问内存 */
u8 value = readb(vga_mem + 0x1234);
writew(value, vga_mem + 0x1234);

/* 清理 */
iounmap(vga_mem);
release_mem_region(0xA0000, 0x20000);
```

## 9. 错误处理模式

### 9.1 初始化错误处理

```c
static int __init my_init(void)
{
    int err;

    /* 注册设备 */
    err = register_device(dev1);
    if (err) goto fail_dev1;

    err = register_device(dev2);
    if (err) goto fail_dev2;

    err = request_irq(irq, handler, IRQF_SHARED, "my_driver", dev);
    if (err) goto fail_irq;

    err = enable_device(dev);
    if (err) goto fail_enable;

    return 0;

fail_enable:
    free_irq(irq, dev);
fail_irq:
    unregister_device(dev2);
fail_dev2:
    unregister_device(dev1);
fail_dev1:
    return err;
}
```

### 9.2 使用goto的错误处理

```c
int __init my_init_function(void)
{
    int err;
    /* registration takes a pointer and a name */
    err = register_this(ptr1, "skull");
    if (err) goto fail_this;
    err = register_that(ptr2, "skull");
    if (err) goto fail_that;
    err = register_those(ptr3, "skull");
    if (err) goto fail_those;
    return 0; /* success */
fail_those:
    unregister_that(ptr2, "skull");
fail_that:
    unregister_this(ptr1, "skull");
fail_this:
    return err; /* propagate the error */
}
```

## 10. 模块加载脚本

### 10.1 设备节点创建脚本

```bash
#!/bin/sh
module="scull"
device="scull"
mode="664"

# invoke insmod with all arguments we got
# and use a pathname, as newer modutils don't look in . by default
/sbin/insmod ./$module.ko $* || exit 1

# remove stale nodes
rm -f /dev/${device}[0-3]

# get the major number
major=$(awk "\\$2==\"$module\" {print \\$1}" /proc/devices)

# create the nodes
mknod /dev/${device}0 c $major 0
mknod /dev/${device}1 c $major 1
mknod /dev/${device}2 c $major 2
mknod /dev/${device}3 c $major 3

# give appropriate group/permissions
group="staff"
grep -q '^staff:' /etc/group || group="wheel"
chgrp $group /dev/${device}[0-3]
chmod $mode /dev/${device}[0-3]
```

### 10.2 设备清理脚本

```bash
#!/bin/sh
module="scull"

# invoke rmmod with all arguments we got
/sbin/rmmod $module $* || exit 1

# remove stale nodes
rm -f /dev/${device}[0-3]
```

## 11. Makefile示例

### 11.1 简单模块Makefile

```makefile
obj-m := hello.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

### 11.2 多文件模块Makefile

```makefile
obj-m := scull.o
scull-objs := main.o pipe.o access.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

### 11.3 复杂项目Makefile

```makefile
# If KERNELRELEASE is defined, we've been invoked from the
# kernel build system and can use its language.
ifneq ($(KERNELRELEASE),)
    obj-m := scull.o
    scull-objs := main.o pipe.o access.o
    scull-pipe-objs := pipe.o
    scull-single-objs := single.o
    scull-uid-objs := uid.o
    scull-wuid-objs := wuid.o

# Otherwise we were called directly from the command
# line; invoke the kernel build system.
else
    KERNELDIR ?= /lib/modules/$(shell uname -r)/build
    PWD := $(shell pwd)

default:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) clean

help:
	@echo "Building scull modules:"
	@echo "  make clean       - remove generated files"
	@echo "  make             - build all modules"
	@echo "  make install     - install modules"
	@echo "  make uninstall   - remove installed modules"

install: default
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules_install

uninstall:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules_uninstall

endif
```

这些源码示例展示了Linux设备驱动开发的核心模式和最佳实践，为深入理解设备驱动编程提供了宝贵的参考。

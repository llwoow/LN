# Linux内核设备驱动技术细节补充

## 1. 设备驱动模型核心数据结构

### 1.1 基础设备结构 (struct device)

```c
struct device {
    struct kobject kobj;
    struct device *parent;              // 父设备
    struct device_private *p;           // 设备私有数据
    struct device_driver *driver;       // 关联的驱动
    struct device_node *of_node;        // 设备树节点
    struct device_node *fwnode;         // 固件节点
    const char *init_name;              // 初始名称
    const struct device_type *type;     // 设备类型
    struct bus_type *bus;               // 总线类型
    struct device_driver *driver;       // 驱动
    void *platform_data;                // 平台数据
    struct device_private *p;           // 私有数据
    struct device_node *of_node;        // 设备树节点
    struct device_node *fwnode;         // 固件节点
    dev_t devt;                         // 设备号
    spinlock_t lock;                    // 自旋锁
    atomic_long_t usage_count;          // 使用计数
    atomic_t online;                    // 在线状态
    // ... 其他字段
};
```

### 1.2 设备驱动结构 (struct device_driver)

```c
struct device_driver {
    const char *name;                   // 驱动名称
    struct bus_type *bus;               // 总线类型
    struct module *owner;               // 模块所有者
    const struct of_device_id *of_match_table;  // 设备树匹配表
    const struct acpi_device_id *acpi_match_table;  // ACPI匹配表
    int (*probe)(struct device *dev);   // 探测函数
    int (*remove)(struct device *dev);  // 移除函数
    void (*shutdown)(struct device *dev);  // 关闭函数
    int (*suspend)(struct device *dev, pm_message_t state);  // 挂起
    int (*resume)(struct device *dev);  // 恢复
    const struct attribute_group **groups;  // 属性组
    const struct dev_pm_ops *pm;        // 电源管理操作
    // ... 其他字段
};
```

### 1.3 总线类型结构 (struct bus_type)

```c
struct bus_type {
    const char *name;                   // 总线名称
    const char *dev_name;               // 设备名称
    struct device *dev_root;            // 根设备
    struct device_attribute *dev_attrs; // 设备属性
    struct bus_attribute *bus_attrs;    // 总线属性
    struct driver_attribute *drv_attrs; // 驱动属性
    int (*match)(struct device *dev, struct device_driver *drv);  // 匹配函数
    int (*uevent)(struct device *dev, struct kobj_uevent_env *env);  // 用户空间事件
    int (*probe)(struct device *dev);   // 探测函数
    int (*remove)(struct device *dev);  // 移除函数
    void (*shutdown)(struct device *dev);  // 关闭函数
    int (*online)(struct device *dev);  // 上线函数
    int (*offline)(struct device *dev); // 下线函数
    // ... 其他字段
};
```

## 2. PCI驱动开发详解

### 2.1 PCI设备初始化流程

```c
#include <linux/pci.h>

static int __init my_pci_driver_init(void)
{
    return pci_register_driver(&my_pci_driver);
}

static void __exit my_pci_driver_exit(void)
{
    pci_unregister_driver(&my_pci_driver);
}

module_init(my_pci_driver_init);
module_exit(my_pci_driver_exit);
```

### 2.2 PCI驱动结构定义

```c
static const struct pci_device_id my_pci_ids[] = {
    { PCI_DEVICE(0x1234, 0x5678) },     // 厂商ID和设备ID
    { PCI_DEVICE(0x1234, 0x9abc) },     // 另一个设备
    { 0 }                               // 结束标志
};

static struct pci_driver my_pci_driver = {
    .name = "my_pci_driver",
    .id_table = my_pci_ids,
    .probe = my_pci_probe,
    .remove = my_pci_remove,
    .suspend = my_pci_suspend,
    .resume = my_pci_resume,
};
```

### 2.3 PCI设备探测函数

```c
static int my_pci_probe(struct pci_dev *dev, const struct pci_device_id *id)
{
    int ret;
    
    /* 启用PCI设备 */
    ret = pci_enable_device(dev);
    if (ret < 0)
        return ret;
    
    /* 请求内存区域 */
    ret = pci_request_regions(dev, "my_driver");
    if (ret < 0)
        goto err_disable;
    
    /* 设置为主设备 */
    pci_set_master(dev);
    
    /* 获取设备私有数据 */
    struct my_device *mdev;
    mdev = kzalloc(sizeof(*mdev), GFP_KERNEL);
    if (!mdev)
        return -ENOMEM;
    
    mdev->dev = dev;
    mdev->bar0 = pci_iomap(dev, 0, 0);
    if (!mdev->bar0) {
        ret = -ENOMEM;
        goto err_free;
    }
    
    /* 设置DMA掩码 */
    ret = pci_set_dma_mask(dev, DMA_BIT_MASK(32));
    if (ret) {
        dev_err(&dev->dev, "No suitable DMA available\n");
        goto err_unmap;
    }
    
    /* 存储设备结构 */
    pci_set_drvdata(dev, mdev);
    
    /* 初始化设备 */
    ret = my_device_init(mdev);
    if (ret < 0)
        goto err_cleanup;
    
    return 0;
    
err_cleanup:
    my_device_cleanup(mdev);
err_unmap:
    pci_iounmap(dev, mdev->bar0);
err_free:
    kfree(mdev);
    pci_clear_master(dev);
    pci_release_regions(dev);
err_disable:
    pci_disable_device(dev);
    return ret;
}
```

### 2.4 PCI设备移除函数

```c
static void my_pci_remove(struct pci_dev *dev)
{
    struct my_device *mdev = pci_get_drvdata(dev);
    
    if (mdev) {
        my_device_cleanup(mdev);
        pci_iounmap(dev, mdev->bar0);
        kfree(mdev);
        pci_clear_master(dev);
        pci_release_regions(dev);
        pci_disable_device(dev);
    }
}
```

## 3. 字符设备驱动开发详解

### 3.1 字符设备驱动结构

```c
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>

#define MYDEV_NAME "my_char_device"
#define MYDEV_CLASS "my_char_class"

static dev_t my_dev_number;
static struct cdev my_cdev;
static struct class *my_class;
static struct device *my_device;

static int my_char_open(struct inode *inode, struct file *file)
{
    struct my_dev_data *dev_data;
    
    /* 获取设备数据 */
    dev_data = container_of(inode->i_cdev, struct my_dev_data, cdev);
    file->private_data = dev_data;
    
    /* 设备特定初始化 */
    if (atomic_read(&dev_data->opened)) {
        return -EBUSY;
    }
    atomic_set(&dev_data->opened, 1);
    
    return 0;
}

static int my_char_release(struct inode *inode, struct file *file)
{
    struct my_dev_data *dev_data = file->private_data;
    
    atomic_set(&dev_data->opened, 0);
    return 0;
}

static ssize_t my_char_read(struct file *file, char __user *buf, 
                           size_t count, loff_t *offset)
{
    struct my_dev_data *dev_data = file->private_data;
    size_t to_read = min(count, dev_data->data_size - *offset);
    
    if (*offset >= dev_data->data_size)
        return 0;
    
    if (copy_to_user(buf, dev_data->data + *offset, to_read))
        return -EFAULT;
    
    *offset += to_read;
    return to_read;
}

static ssize_t my_char_write(struct file *file, const char __user *buf,
                            size_t count, loff_t *offset)
{
    struct my_dev_data *dev_data = file->private_data;
    size_t to_write = min(count, sizeof(dev_data->data) - *offset);
    
    if (copy_from_user(dev_data->data + *offset, buf, to_write))
        return -EFAULT;
    
    dev_data->data_size = *offset + to_write;
    *offset += to_write;
    return to_write;
}

static struct file_operations my_fops = {
    .owner = THIS_MODULE,
    .open = my_char_open,
    .release = my_char_release,
    .read = my_char_read,
    .write = my_char_write,
    .llseek = generic_file_llseek,
};
```

### 3.2 设备驱动初始化和清理

```c
static struct my_dev_data {
    struct cdev cdev;
    atomic_t opened;
    char data[1024];
    size_t data_size;
} dev_data;

static int __init my_char_init(void)
{
    int ret;
    
    /* 分配设备号 */
    ret = alloc_chrdev_region(&my_dev_number, 0, 1, MYDEV_NAME);
    if (ret < 0) {
        printk(KERN_ERR "Failed to allocate device number\n");
        return ret;
    }
    
    /* 初始化字符设备 */
    cdev_init(&my_cdev, &my_fops);
    my_cdev.owner = THIS_MODULE;
    
    /* 添加字符设备 */
    ret = cdev_add(&my_cdev, my_dev_number, 1);
    if (ret < 0) {
        printk(KERN_ERR "Failed to add character device\n");
        goto err_unreg;
    }
    
    /* 创建设备类 */
    my_class = class_create(THIS_MODULE, MYDEV_CLASS);
    if (IS_ERR(my_class)) {
        printk(KERN_ERR "Failed to create device class\n");
        ret = PTR_ERR(my_class);
        goto err_cdev_del;
    }
    
    /* 创建设备节点 */
    my_device = device_create(my_class, NULL, my_dev_number, NULL, MYDEV_NAME);
    if (IS_ERR(my_device)) {
        printk(KERN_ERR "Failed to create device\n");
        ret = PTR_ERR(my_device);
        goto err_class_destroy;
    }
    
    /* 初始化设备数据 */
    atomic_set(&dev_data.opened, 0);
    dev_data.data_size = 0;
    
    printk(KERN_INFO "Character device registered successfully\n");
    return 0;
    
err_class_destroy:
    class_destroy(my_class);
err_cdev_del:
    cdev_del(&my_cdev);
err_unreg:
    unregister_chrdev_region(my_dev_number, 1);
    return ret;
}

static void __exit my_char_exit(void)
{
    device_destroy(my_class, my_dev_number);
    class_destroy(my_class);
    cdev_del(&my_cdev);
    unregister_chrdev_region(my_dev_number, 1);
    printk(KERN_INFO "Character device unregistered\n");
}

module_init(my_char_init);
module_exit(my_char_exit);
```

## 4. 设备驱动资源管理 (Devres)

### 4.1 Devres基本用法

```c
#include <linux/device.h>

static int my_probe(struct platform_device *pdev)
{
    struct resource *res;
    void __iomem *base;
    int irq;
    struct device *dev = &pdev->dev;
    
    /* 请求内存区域 */
    res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    if (!res) {
        dev_err(dev, "No memory resource\n");
        return -ENODEV;
    }
    
    /* 使用devres分配内存 */
    base = devm_ioremap_resource(dev, res);
    if (IS_ERR(base))
        return PTR_ERR(base);
    
    /* 请求中断 */
    irq = platform_get_irq(pdev, 0);
    if (irq < 0) {
        dev_err(dev, "No IRQ resource\n");
        return irq;
    }
    
    /* 使用devres请求中断 */
    ret = devm_request_irq(dev, irq, my_irq_handler, 
                          IRQF_SHARED, "my_device", dev);
    if (ret) {
        dev_err(dev, "Cannot claim IRQ %d\n", irq);
        return ret;
    }
    
    /* 设备特定初始化 */
    my_device_init(base, irq);
    
    /* 设备数据会自动在remove时清理 */
    return 0;
}
```

### 4.2 自定义Devres函数

```c
static void my_device_release(void *data)
{
    struct my_device *dev = data;
    
    /* 清理设备资源 */
    if (dev->irq >= 0)
        free_irq(dev->irq, dev);
    
    if (dev->base)
        iounmap(dev->base);
    
    kfree(dev);
}

static int my_probe_with_devres(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct my_device *mdev;
    
    /* 分配设备结构并注册清理函数 */
    mdev = devm_kzalloc(dev, sizeof(*mdev), GFP_KERNEL);
    if (!mdev)
        return -ENOMEM;
    
    devm_add_action(dev, my_device_release, mdev);
    
    /* 初始化设备 */
    mdev->dev = dev;
    mdev->base = devm_platform_ioremap_resource(pdev, 0);
    if (IS_ERR(mdev->base))
        return PTR_ERR(mdev->base);
    
    mdev->irq = platform_get_irq(pdev, 0);
    if (mdev->irq < 0)
        return mdev->irq;
    
    ret = devm_request_irq(dev, mdev->irq, my_irq_handler,
                          IRQF_SHARED, "my_device", mdev);
    if (ret)
        return ret;
    
    platform_set_drvdata(pdev, mdev);
    return 0;
}
```

## 5. 设备树集成

### 5.1 设备树匹配

```c
#include <linux/mod_devicetable.h>
#include <linux/platform_device.h>

static const struct of_device_id my_of_match[] = {
    { .compatible = "vendor,my-device" },
    { .compatible = "vendor,my-device-v2" },
    { },
};

MODULE_DEVICE_TABLE(of, my_of_match);

static int my_of_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct device_node *node = dev->of_node;
    const struct of_device_id *match;
    int ret;
    
    match = of_match_device(my_of_match, dev);
    if (!match) {
        dev_err(dev, "No matching device found\n");
        return -ENODEV;
    }
    
    /* 从设备树获取配置 */
    ret = my_device_parse_dt(node, pdev);
    if (ret) {
        dev_err(dev, "Failed to parse device tree\n");
        return ret;
    }
    
    return 0;
}

static struct platform_driver my_of_driver = {
    .probe = my_of_probe,
    .remove = my_of_remove,
    .driver = {
        .name = "my_device",
        .of_match_table = my_of_match,
    },
};
```

### 5.2 设备树解析函数

```c
static int my_device_parse_dt(struct device_node *node, 
                             struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    u32 val;
    const char *str;
    int ret;
    
    /* 解析reg属性 */
    ret = of_property_read_u32(node, "reg", &val);
    if (ret) {
        dev_err(dev, "Missing reg property\n");
        return ret;
    }
    
    /* 解析compatible字符串 */
    ret = of_property_read_string(node, "compatible", &str);
    if (!ret) {
        dev_info(dev, "Device compatible: %s\n", str);
    }
    
    /* 解析中断号 */
    pdev->irq = of_irq_get(node, 0);
    if (pdev->irq < 0) {
        dev_err(dev, "Failed to get IRQ\n");
        return pdev->irq;
    }
    
    /* 解析时钟 */
    pdev->clk = devm_clk_get(dev, NULL);
    if (IS_ERR(pdev->clk)) {
        dev_info(dev, "No clock found, continuing without\n");
        pdev->clk = NULL;
    }
    
    return 0;
}
```

## 6. 电源管理

### 6.1 基本电源管理

```c
#include <linux/pm.h>

static int my_dev_suspend(struct device *dev)
{
    struct my_device *mdev = dev_get_drvdata(dev);
    
    /* 停止设备操作 */
    my_device_stop(mdev);
    
    /* 保存设备状态 */
    my_device_save_state(mdev);
    
    return 0;
}

static int my_dev_resume(struct device *dev)
{
    struct my_device *mdev = dev_get_drvdata(dev);
    
    /* 恢复设备状态 */
    my_device_restore_state(mdev);
    
    /* 重新启动设备 */
    my_device_start(mdev);
    
    return 0;
}

static const struct dev_pm_ops my_dev_pm_ops = {
    .suspend = my_dev_suspend,
    .resume = my_dev_resume,
    .freeze = my_dev_suspend,
    .restore = my_dev_resume,
};
```

### 6.2 运行时电源管理

```c
static int my_dev_runtime_suspend(struct device *dev)
{
    struct my_device *mdev = dev_get_drvdata(dev);
    
    /* 进入低功耗状态 */
    my_device_power_down(mdev);
    
    return 0;
}

static int my_dev_runtime_resume(struct device *dev)
{
    struct my_device *mdev = dev_get_drvdata(dev);
    
    /* 退出低功耗状态 */
    my_device_power_up(mdev);
    
    return 0;
}

static const struct dev_pm_ops my_dev_pm_ops = {
    .runtime_suspend = my_dev_runtime_suspend,
    .runtime_resume = my_dev_runtime_resume,
    .runtime_idle = my_dev_runtime_idle,
};
```

## 7. 中断处理

### 7.1 基本中断处理

```c
#include <linux/interrupt.h>

static irqreturn_t my_irq_handler(int irq, void *dev_id)
{
    struct my_device *dev = dev_id;
    u32 status;
    
    /* 读取中断状态 */
    status = readl(dev->base + REG_STATUS);
    
    if (!(status & INT_PENDING))
        return IRQ_NONE;
    
    /* 处理中断 */
    if (status & DATA_READY_INT) {
        my_handle_data_ready(dev);
    }
    
    if (status & ERROR_INT) {
        my_handle_error(dev);
    }
    
    /* 清除中断 */
    writel(status, dev->base + REG_STATUS);
    
    return IRQ_HANDLED;
}

static int my_request_irq(struct my_device *dev)
{
    int ret;
    
    ret = request_irq(dev->irq, my_irq_handler, 
                     IRQF_SHARED, "my_device", dev);
    if (ret) {
        dev_err(dev->dev, "Failed to request IRQ %d\n", dev->irq);
        return ret;
    }
    
    return 0;
}
```

### 7.2 线程化中断处理

```c
static irqreturn_t my_irq_thread_handler(int irq, void *dev_id)
{
    struct my_device *dev = dev_id;
    
    /* 线程化处理耗时操作 */
    my_handle_slow_operation(dev);
    
    return IRQ_HANDLED;
}

static int my_request_threaded_irq(struct my_device *dev)
{
    int ret;
    
    ret = request_threaded_irq(dev->irq, my_irq_handler, 
                              my_irq_thread_handler,
                              IRQF_ONESHOT | IRQF_SHARED,
                              "my_device", dev);
    if (ret) {
        dev_err(dev->dev, "Failed to request threaded IRQ\n");
        return ret;
    }
    
    return 0;
}
```

## 8. DMA操作

### 8.1 基本DMA设置

```c
#include <linux/dma-mapping.h>

static int my_setup_dma(struct device *dev)
{
    int ret;
    
    /* 设置DMA掩码 */
    ret = dma_set_mask(dev, DMA_BIT_MASK(32));
    if (ret) {
        dev_err(dev, "DMA not supported\n");
        return ret;
    }
    
    /* 设置一致性DMA掩码 */
    ret = dma_set_coherent_mask(dev, DMA_BIT_MASK(32));
    if (ret) {
        dev_err(dev, "Consistent DMA not supported\n");
        return ret;
    }
    
    return 0;
}

static void *my_alloc_coherent(struct device *dev, size_t size, 
                              dma_addr_t *dma_handle, gfp_t flag)
{
    void *virt_addr;
    
    virt_addr = dma_alloc_coherent(dev, size, dma_handle, flag);
    if (!virt_addr) {
        dev_err(dev, "Failed to allocate DMA memory\n");
        return NULL;
    }
    
    return virt_addr;
}

static void my_free_coherent(struct device *dev, size_t size,
                           void *virt_addr, dma_addr_t dma_handle)
{
    dma_free_coherent(dev, size, virt_addr, dma_handle);
}
```

### 8.2 流式DMA操作

```c
static int my_streaming_operation(struct my_device *dev, 
                                 void *virt_addr, size_t size)
{
    dma_addr_t dma_addr;
    struct scatterlist sg;
    
    /* 映射单个缓冲区 */
    dma_addr = dma_map_single(dev->dev, virt_addr, size, DMA_TO_DEVICE);
    if (dma_mapping_error(dev->dev, dma_addr)) {
        dev_err(dev->dev, "DMA mapping failed\n");
        return -EIO;
    }
    
    /* 执行DMA操作 */
    my_device_start_transfer(dev, dma_addr, size);
    
    /* 等待完成 */
    my_device_wait_completion(dev);
    
    /* 取消映射 */
    dma_unmap_single(dev->dev, dma_addr, size, DMA_TO_DEVICE);
    
    return 0;
}

static int my_sg_operation(struct my_device *dev, 
                          struct scatterlist *sgl, int nents)
{
    struct scatterlist *sg;
    int i;
    
    /* 映射分散列表 */
    if (dma_map_sg(dev->dev, sgl, nents, DMA_TO_DEVICE) != nents) {
        dev_err(dev->dev, "DMA SG mapping failed\n");
        return -EIO;
    }
    
    /* 执行DMA操作 */
    for_each_sg(sgl, sg, nents, i) {
        my_device_start_transfer(dev, sg->dma_address, sg->length);
    }
    
    /* 等待完成 */
    my_device_wait_completion(dev);
    
    /* 取消映射 */
    dma_unmap_sg(dev->dev, sgl, nents, DMA_TO_DEVICE);
    
    return 0;
}
```

## 9. 调试技巧

### 9.1 使用debugfs

```c
#include <linux/debugfs.h>

static struct dentry *my_debugfs_dir;

static int my_debugfs_init(void)
{
    my_debugfs_dir = debugfs_create_dir("my_device", NULL);
    if (!my_debugfs_dir) {
        pr_err("Failed to create debugfs directory\n");
        return -ENOMEM;
    }
    
    /* 创建调试文件 */
    debugfs_create_u32("debug_level", 0644, my_debugfs_dir, &my_debug_level);
    debugfs_create_x32("device_status", 0444, my_debugfs_dir, &device_status);
    
    return 0;
}

static void my_debugfs_exit(void)
{
    debugfs_remove_recursive(my_debugfs_dir);
}
```

### 9.2 使用sysfs属性

```c
#include <linux/sysfs.h>

static ssize_t my_device_show(struct device *dev,
                             struct device_attribute *attr,
                             char *buf)
{
    struct my_device *mdev = dev_get_drvdata(dev);
    ssize_t ret;
    
    ret = sprintf(buf, "0x%08x\n", mdev->status);
    
    return ret;
}

static ssize_t my_device_store(struct device *dev,
                              struct device_attribute *attr,
                              const char *buf, size_t count)
{
    struct my_device *mdev = dev_get_drvdata(dev);
    unsigned long val;
    int ret;
    
    ret = kstrtoul(buf, 0, &val);
    if (ret)
        return ret;
    
    mdev->config = val;
    
    return count;
}

static DEVICE_ATTR(my_device_attr, 0644, my_device_show, my_device_store);

static int my_sysfs_init(struct device *dev)
{
    return device_create_file(dev, &dev_attr_my_device_attr);
}

static void my_sysfs_exit(struct device *dev)
{
    device_remove_file(dev, &dev_attr_my_device_attr);
}
```

这些技术细节补充提供了Linux内核设备驱动开发中的核心概念和实现方法，涵盖了从基本的设备驱动结构到高级的DMA操作、电源管理和调试技巧。开发者可以根据具体需求选择相应的技术方案。
/*
 * Linux内核通用中断处理核心源码分析
 * 基于Linux Kernel 4.12.0
 * 
 * 本文件包含了通用中断处理层的关键源码片段和实现细节
 * 用于深入理解中断处理机制的技术实现
 */

#include <linux/irq.h>
#include <linux/interrupt.h>
#include <linux/irqdesc.h>
#include <linux/irqdomain.h>

/* ========================================================================
 * 1. 核心数据结构定义
 * ======================================================================== */

/**
 * struct irq_common_data - 所有irq芯片共享的通用数据
 * @state_use_accessors: irq芯片函数的状态信息
 * @node: NUMA节点索引
 * @handler_data: irq_chip方法的每IRQ数据
 * @msi_desc: MSI描述符
 * @affinity: SMP上的IRQ亲和性掩码
 * @ipi_offset: 亲和性中第一个IPI目标CPU的偏移量
 */
struct irq_common_data {
    unsigned int __private state_use_accessors;
#ifdef CONFIG_NUMA
    unsigned int node;
#endif
    void *handler_data;
    struct msi_desc *msi_desc;
    cpumask_var_t affinity;
#ifdef CONFIG_GENERIC_IRQ_IPI
    unsigned int ipi_offset;
#endif
};

/**
 * struct irq_data - 传递给芯片函数的每个irq芯片数据
 * @mask: 芯片寄存器访问的预计算位掩码
 * @irq: Linux中断号
 * @hwirq: 硬件中断号，域本地
 * @common: 指向共享irq_common_data的指针
 * @chip: 低级中断硬件访问结构(irq_chip)
 * @domain: 中断转换域
 * @parent_data: 层次结构的父irq_data指针
 * @chip_data: 芯片方法的平台特定私有数据
 */
struct irq_data {
    u32 mask;
    unsigned int irq;
    unsigned long hwirq;
    struct irq_common_data *common;
    struct irq_chip *chip;
    struct irq_domain *domain;
#ifdef CONFIG_IRQ_DOMAIN_HIERARCHY
    struct irq_data *parent_data;
#endif
    void *chip_data;
};

/**
 * struct irq_chip - 硬件中断芯片描述符
 * 包含一系列回调函数指针，用于中断的启动、关闭、启用、禁用等操作
 */
struct irq_chip {
    struct device *parent_device;
    const char *name;

    /* 启动/关闭 */
    unsigned int        (* irq_startup) (struct irq_data *data);
    void (* irq_shutdown) (struct irq_data *data);

    /* 启用/禁用 */
    void (* irq_enable) (struct irq_data *data);
    void (* irq_disable) (struct irq_data *data);

    /* 确认和屏蔽控制 */
    void (* irq_ack) (struct irq_data *data);
    void (* irq_mask) (struct irq_data *data);
    void (* irq_mask_ack) (struct irq_data *data);
    void (* irq_unmask) (struct irq_data *data);
    void (* irq_eoi) (struct irq_data *data);

    /* 中断类型和亲和性 */
    int (* irq_set_affinity) (struct irq_data *data, const struct cpumask *dest, bool force);
    int (* irq_retrigger) (struct irq_data *data);
    int (* irq_set_type) (struct irq_data *data, unsigned int flow_type);
    int (* irq_set_wake) (struct irq_data *data, unsigned int on);

    /* 总线锁 */
    void (* irq_bus_lock) (struct irq_data *data);
    void (* irq_bus_sync_unlock) (struct irq_data *data);

    /* CPU热插拔 */
    void (* irq_cpu_online) (struct irq_data *data);
    void (* irq_cpu_offline) (struct irq_data *data);

    /* 电源管理 */
    void (* irq_suspend) (struct irq_data *data);
    void (* irq_resume) (struct irq_data *data);
    void (* irq_pm_shutdown) (struct irq_data *data);

    /* 其他操作 */
    void (* irq_calc_mask) (struct irq_data *data);
    void (* irq_print_chip) (struct irq_data *data, struct seq_file *p);
    int (* irq_request_resources) (struct irq_data *data);
    void (* irq_release_resources) (struct irq_data *data);

    /* MSI支持 */
    void (* irq_compose_msi_msg) (struct irq_data *data, struct msi_msg *msg);
    void (* irq_write_msi_msg) (struct irq_data *data, struct msi_msg *msg);

    /* 虚拟化支持 */
    int (* irq_get_irqchip_state) (struct irq_data *data, enum irqchip_irq_state which, bool *state);
    int (* irq_set_irqchip_state) (struct irq_data *data, enum irqchip_irq_state which, bool state);
    int (* irq_set_vcpu_affinity) (struct irq_data *data, void *vcpu_info);

    /* IPI支持 */
    void (* ipi_send_single) (struct irq_data *data, unsigned int cpu);
    void (* ipi_send_mask) (struct irq_data *data, const struct cpumask *dest);

    unsigned long flags;
};

/* ========================================================================
 * 2. 默认流处理程序实现
 * ======================================================================== */

/**
 * default_enable - 默认启用函数
 * @data: irq数据
 */
static void default_enable(struct irq_data *data)
{
    struct irq_desc *desc = irq_data_to_desc(data);

    desc->irq_data.chip->irq_unmask(data);
}

/**
 * default_disable - 默认禁用函数
 * @data: irq数据
 */
static void default_disable(struct irq_data *data)
{
    struct irq_desc *desc = irq_data_to_desc(data);

    if (!delay_disable(data))
        desc->irq_data.chip->irq_mask(data);
}

/**
 * default_ack - 默认确认函数
 * @data: irq数据
 */
static void default_ack(struct irq_data *data)
{
    struct irq_chip *chip = irq_data_get_chip(data);

    chip->irq_ack(data);
}

/**
 * default_mask_ack - 默认掩码确认函数
 * @data: irq数据
 */
static void default_mask_ack(struct irq_data *data)
{
    struct irq_chip *chip = irq_data_get_chip(data);

    if (chip->irq_mask_ack)
        chip->irq_mask_ack(data);
    else {
        chip->irq_mask(data);
        chip->irq_ack(data);
    }
}

/**
 * noop - 空操作函数
 * @data: irq数据
 */
static void noop(struct irq_data *data)
{
}

/* ========================================================================
 * 3. 高层IRQ流处理程序
 * ======================================================================== */

/**
 * handle_level_irq - 电平触发中断处理程序
 * @desc: 中断描述符
 */
static void handle_level_irq(struct irq_desc *desc)
{
    unsigned int irq = desc->irq_data.irq;
    struct irq_chip *chip = desc->irq_data.chip;

    if (desc->status & (IRQ_DISABLED | IRQ_INPROGRESS))
        return;

    desc->status &= ~IRQ_PENDING;

    chip->irq_mask_ack(&desc->irq_data);
    desc->status |= IRQ_INPROGRESS;

    handle_irq_event(desc->action);

    desc->status &= ~IRQ_INPROGRESS;

    if (!(desc->status & IRQ_DISABLED) && chip->irq_unmask)
        chip->irq_unmask(&desc->irq_data);
}

/**
 * handle_edge_irq - 边沿触发中断处理程序
 * @desc: 中断描述符
 */
static void handle_edge_irq(struct irq_desc *desc)
{
    unsigned int irq = desc->irq_data.irq;
    struct irq_chip *chip = desc->irq_data.chip;

    desc->status &= ~IRQ_PENDING;

    if (desc->status & IRQ_DISABLED) {
        desc->status |= IRQ_PENDING;
        chip->irq_mask(&desc->irq_data);
        return;
    }

    chip->irq_ack(&desc->irq_data);

    desc->status |= IRQ_INPROGRESS;

    do {
        handle_irq_event(desc->action);

        if (desc->status & IRQ_PENDING) {
            desc->status &= ~IRQ_PENDING;
            chip->irq_ack(&desc->irq_data);
        }
    } while (desc->status & IRQ_PENDING);

    desc->status &= ~IRQ_INPROGRESS;
}

/**
 * handle_fasteoi_irq - 快速EOI中断处理程序
 * @desc: 中断描述符
 */
static void handle_fasteoi_irq(struct irq_desc *desc)
{
    struct irq_chip *chip = desc->irq_data.chip;

    if (desc->status & IRQ_DISABLED)
        return;

    handle_irq_event(desc->action);

    chip->irq_eoi(&desc->irq_data);
}

/**
 * handle_simple_irq - 简单中断处理程序
 * @desc: 中断描述符
 */
static void handle_simple_irq(struct irq_desc *desc)
{
    if (desc->status & IRQ_DISABLED)
        return;

    handle_irq_event(desc->action);
}

/**
 * handle_percpu_irq - 每CPU中断处理程序
 * @desc: 中断描述符
 */
static void handle_percpu_irq(struct irq_desc *desc)
{
    struct irq_chip *chip = desc->irq_data.chip;

    if (chip->irq_ack)
        chip->irq_ack(&desc->irq_data);

    handle_irq_event(desc->action);

    if (chip->irq_eoi)
        chip->irq_eoi(&desc->irq_data);
}

/**
 * handle_bad_irq - 处理虚假或未处理的中断
 * @desc: 中断描述符
 */
static void handle_bad_irq(struct irq_desc *desc)
{
    unsigned int irq = desc->irq_data.irq;

    printk_once(KERN_WARNING "irq %d: nobody cared (try booting with "
               "the \"irqpoll\" option)\n", irq);

    disable_irq_nosync(irq);
    note_interrupt(desc->irq_data.irq, desc, IRQ_NONE, NULL);
}

/* ========================================================================
 * 4. 延迟中断禁用机制
 * ======================================================================== */

/**
 * delay_disable - 检查是否应该延迟禁用
 * @data: irq数据
 * 
 * 如果芯片设置了IRQCHIP_DELAYED_DISABLE标志，则延迟禁用
 */
static inline bool delay_disable(struct irq_data *data)
{
    return !!(data->chip->flags & IRQCHIP_DELAYED_DISABLE);
}

/**
 * check_irq_pen - 检查并处理挂起的中断
 * @desc: 中断描述符
 */
static void check_irq_pen(struct irq_desc *desc)
{
    if (desc->status & IRQ_PENDING) {
        desc->status &= ~IRQ_PENDING;
        desc->irq_data.chip->irq_unmask(&desc->irq_data);
    }
}

/* ========================================================================
 * 5. 通用中断芯片实现
 * ======================================================================== */

/**
 * struct irq_chip_generic - 通用irq芯片的数据结构
 * @lock: 保护寄存器和缓存数据的自旋锁
 * @reg_base: 寄存器基地址
 * @reg_readl: I/O访问器
 * @reg_writel: I/O访问器
 * @suspend: 挂起回调
 * @resume: 恢复回调
 * @irq_base: IRQ基号
 * @irq_cnt: IRQ数量
 * @mask_cache: 掩码缓存
 * @type_cache: 类型缓存
 * @polarity_cache: 极性缓存
 * @wake_enabled: 唤醒使能缓存
 * @wake_active: 唤醒活动缓存
 * @num_ct: irq_chip_type实例的数量
 * @private: 非通用回调的私有数据
 * @installed: 已安装中断的位域
 * @unused: 未使用中断的位域
 * @domain: IRQ域指针
 * @list: 实例的链表头
 * @chip_types: irq_chip_type实例数组
 */
struct irq_chip_generic {
    raw_spinlock_t lock;
    void __iomem *reg_base;
    u32 (* reg_readl) (void __iomem *addr);
    void (* reg_writel) (u32 val, void __iomem *addr);
    void (* suspend) (struct irq_chip_generic *gc);
    void (* resume) (struct irq_chip_generic *gc);
    unsigned int irq_base;
    unsigned int irq_cnt;
    u32 mask_cache;
    u32 type_cache;
    u32 polarity_cache;
    u32 wake_enabled;
    u32 wake_active;
    unsigned int num_ct;
    void * private;
    unsigned long installed;
    unsigned long unused;
    struct irq_domain * domain;
    struct list_head list;
    struct irq_chip_type chip_types[];
};

/**
 * irq_gc_mask_set_bit - 通过设置掩码寄存器中的位来屏蔽芯片
 * @d: irq数据
 */
void irq_gc_mask_set_bit(struct irq_data *d)
{
    struct irq_chip_generic *gc = irq_data_get_chip_generic(d);
    unsigned long mask = d->mask;
    unsigned long flags;

    raw_spin_lock_irqsave(&gc->lock, flags);
    gc->mask_cache |= mask;
    gc->reg_writel(gc->mask_cache, gc->reg_base + gc->regs.mask);
    raw_spin_unlock_irqrestore(&gc->lock, flags);
}

/**
 * irq_gc_mask_clr_bit - 通过清除掩码寄存器中的位来取消屏蔽芯片
 * @d: irq数据
 */
void irq_gc_mask_clr_bit(struct irq_data *d)
{
    struct irq_chip_generic *gc = irq_data_get_chip_generic(d);
    unsigned long mask = d->mask;
    unsigned long flags;

    raw_spin_lock_irqsave(&gc->lock, flags);
    gc->mask_cache &= ~mask;
    gc->reg_writel(gc->mask_cache, gc->reg_base + gc->regs.mask);
    raw_spin_unlock_irqrestore(&gc->lock, flags);
}

/**
 * irq_gc_ack_set_bit - 通过设置确认寄存器中的位来确认挂起的中断
 * @d: irq数据
 */
void irq_gc_ack_set_bit(struct irq_data *d)
{
    struct irq_chip_generic *gc = irq_data_get_chip_generic(d);
    unsigned long mask = d->mask;
    unsigned long flags;

    raw_spin_lock_irqsave(&gc->lock, flags);
    gc->reg_writel(mask, gc->reg_base + gc->regs.ack);
    raw_spin_unlock_irqrestore(&gc->lock, flags);
}

/* ========================================================================
 * 6. 公共API函数实现
 * ======================================================================== */

/**
 * request_irq - 分配一个中断线
 * @irq: 中断号
 * @handler: 中断处理函数
 * @irqflags: 中断标志
 * @devname: 设备名称
 * @dev_id: 设备标识符
 */
int request_irq(unsigned int irq, irq_handler_t handler,
               unsigned long irqflags, const char *devname, void *dev_id)
{
    struct irqaction *action;
    int retval;

    /*
     * Sanity-check: shared interrupts must pass in a real dev_id,
     * otherwise we'll have trouble later trying to figure out
     * which interrupt is which (messes up the interrupt freeing
     * logic etc).
     */
    if ((irqflags & IRQF_SHARED) && !dev_id)
        return -EINVAL;

    if (irq >= nr_irqs)
        return -EINVAL;

    action = kzalloc(sizeof(struct irqaction), GFP_KERNEL);
    if (!action)
        return -ENOMEM;

    action->handler = handler;
    action->flags = irqflags;
    action->name = devname;
    action->dev_id = dev_id;

    retval = __setup_irq(irq, irq_to_desc(irq), action);
    if (retval) {
        kfree(action);
        return retval;
    }

    return 0;
}

/**
 * free_irq - 释放一个中断线
 * @irq: 中断号
 * @dev_id: 设备标识符
 */
void free_irq(unsigned int irq, void *dev_id)
{
    struct irq_desc *desc = irq_to_desc(irq);
    struct irqaction *action, **action_ptr;

    if (!desc || WARN_ON(in_interrupt()))
        return;

    /* Find the right entry. */
    for (action_ptr = &desc->action; *action_ptr;
         action_ptr = &(*action_ptr)->next) {
        if ((*action_ptr)->dev_id == dev_id)
            goto found;
    }

    WARN(1, "Trying to free already-free IRQ %d\n", irq);
    return;

found:
    /*
     * There can be multiple actions per IRQ, so we need to
     * disable it first and then remove it.
     */
    action = *action_ptr;

    *action_ptr = action->next;

    if (!desc->action) {
        desc->status |= IRQ_DISABLED;
        if (desc->irq_data.chip->irq_shutdown)
            desc->irq_data.chip->irq_shutdown(&desc->irq_data);
        else
            desc->irq_data.chip->irq_disable(&desc->irq_data);
    }

    raw_spin_unlock_irq(&desc->lock);
    synchronize_irq(irq);
    raw_spin_lock_irq(&desc->lock);

    kfree(action);
}

/**
 * disable_irq - 禁用一个中断
 * @irq: 中断号
 */
void disable_irq(unsigned int irq)
{
    struct irq_desc *desc = irq_to_desc(irq);

    if (!desc)
        return;

    disable_irq_nosync(irq);
    if (desc->action)
        synchronize_irq(irq);
}

/**
 * enable_irq - 启用一个中断
 * @irq: 中断号
 */
void enable_irq(unsigned int irq)
{
    struct irq_desc *desc = irq_to_desc(irq);

    if (desc) {
        raw_spin_lock_irq(&desc->lock);
        desc->status &= ~IRQ_DISABLED;
        check_irq_pen(desc);
        raw_spin_unlock_irq(&desc->lock);
    }
}

/**
 * synchronize_irq - 等待中断处理程序完成
 * @irq: 中断号
 */
void synchronize_irq(unsigned int irq)
{
    struct irq_desc *desc = irq_to_desc(irq);

    if (desc) {
        while (desc->status & IRQ_INPROGRESS) {
            /*
             * Wait for any pending handlers to complete.
             * This is the most common path through the interrupt
             * handling code.
             */
            do {
                raw_spin_unlock(&desc->lock);
                cpu_relax();
                raw_spin_lock(&desc->lock);
            } while (desc->status & IRQ_INPROGRESS);
        }
    }
}

/* ========================================================================
 * 7. 线程化中断支持
 * ======================================================================== */

/**
 * request_threaded_irq - 分配一个中断线，可选择线程处理程序
 * @irq: 中断号
 * @handler: 中断处理函数（在硬中断上下文中运行）
 * @thread_fn: 线程处理函数（在进程上下文中运行）
 * @irqflags: 中断标志
 * @devname: 设备名称
 * @dev_id: 设备标识符
 */
int request_threaded_irq(unsigned int irq, irq_handler_t handler,
                        irq_handler_t thread_fn, unsigned long irqflags,
                        const char *devname, void *dev_id)
{
    struct irqaction *action;
    struct irq_desc *desc;
    int retval;

    if (irq >= nr_irqs)
        return -EINVAL;

    desc = irq_to_desc(irq);
    if (!desc)
        return -EINVAL;

    if (!handler && !thread_fn)
        return -EINVAL;

    /*
     * Sanity-check: shared interrupts must pass in a real dev_id,
     * otherwise we'll have trouble later trying to figure out
     * which interrupt is which (messes up the interrupt freeing
     * logic etc).
     */
    if ((irqflags & IRQF_SHARED) && !dev_id)
        return -EINVAL;

    action = kzalloc(sizeof(struct irqaction), GFP_KERNEL);
    if (!action)
        return -ENOMEM;

    action->handler = handler;
    action->thread_fn = thread_fn;
    action->flags = irqflags;
    action->name = devname;
    action->dev_id = dev_id;

    if (thread_fn) {
        action->thread = kthread_run(irq_thread, action, "irq/%d-%s", 
                                    irq, devname);
        if (IS_ERR(action->thread)) {
            kfree(action);
            return PTR_ERR(action->thread);
        }
    }

    retval = __setup_irq(irq, desc, action);
    if (retval) {
        if (action->thread)
            kthread_stop(action->thread);
        kfree(action);
    }

    return retval;
}

/* ========================================================================
 * 8. 中断事件处理
 * ======================================================================== */

/**
 * handle_irq_event - 处理中断事件
 * @desc: 中断描述符
 *
 * 返回处理的中断数量
 */
irqreturn_t handle_irq_event(struct irq_desc *desc)
{
    struct irqaction *action = desc->action;
    irqreturn_t ret;

    desc->status &= ~IRQ_PENDING;

    if (desc->status & IRQ_ONESHOT)
        mask_irq(desc);

    ret = IRQ_NONE;
    for_each_action_of_desc(desc, action) {
        irqreturn_t res;

        trace_irq_handler_entry(irq, action);
        res = action->handler(irq, action->dev_id);
        trace_irq_handler_exit(irq, action, res);

        if (res == IRQ_HANDLED)
            desc->status |= IRQ_HANDLED;
        else if (res == IRQ_WAKE_THREAD)
            __irq_wake_thread(desc, action);
    }

    return ret;
}

/* ========================================================================
 * 9. 中断统计
 * ======================================================================== */

/**
 * kstat_irqs_cpu - 获取特定CPU上特定IRQ的统计信息
 * @irq: 中断号
 * @cpu: CPU号
 */
unsigned int kstat_irqs_cpu(unsigned int irq, int cpu)
{
    struct irq_desc *desc = irq_to_desc(irq);

    if (!desc)
        return 0;
    return desc->kstat_irqs[cpu].irqs;
}

/**
 * kstat_irqs - 获取所有CPU上特定IRQ的统计信息
 * @irq: 中断号
 */
unsigned int kstat_irqs(unsigned int irq)
{
    unsigned int sum = 0;
    int cpu;

    for_each_possible_cpu(cpu)
        sum += kstat_irqs_cpu(irq, cpu);

    return sum;
}

/* ========================================================================
 * 10. 层次化IRQ域支持
 * ======================================================================== */

/**
 * irq_chip_enable_parent - 启用父级中断
 * @data: irq数据
 */
void irq_chip_enable_parent(struct irq_data *data)
{
    data = data->parent_data;
    while (data) {
        if (data->chip->irq_enable)
            data->chip->irq_enable(data);
        data = data->parent_data;
    }
}

/**
 * irq_chip_disable_parent - 禁用父级中断
 * @data: irq数据
 */
void irq_chip_disable_parent(struct irq_data *data)
{
    data = data->parent_data;
    while (data) {
        if (data->chip->irq_disable)
            data->chip->irq_disable(data);
        data = data->parent_data;
    }
}

/**
 * irq_chip_mask_parent - 屏蔽父级中断
 * @data: irq数据
 */
void irq_chip_mask_parent(struct irq_data *data)
{
    data = data->parent_data;
    while (data) {
        if (data->chip->irq_mask)
            data->chip->irq_mask(data);
        data = data->parent_data;
    }
}

/**
 * irq_chip_unmask_parent - 取消屏蔽父级中断
 * @data: irq数据
 */
void irq_chip_unmask_parent(struct irq_data *data)
{
    data = data->parent_data;
    while (data) {
        if (data->chip->irq_unmask)
            data->chip->irq_unmask(data);
        data = data->parent_data;
    }
}

/**
 * irq_chip_eoi_parent - 发送EOI给父级中断
 * @data: irq数据
 */
void irq_chip_eoi_parent(struct irq_data *data)
{
    data = data->parent_data;
    while (data) {
        if (data->chip->irq_eoi)
            data->chip->irq_eoi(data);
        data = data->parent_data;
    }
}

/* ========================================================================
 * 11. 虚拟化支持
 * ======================================================================== */

/**
 * irq_set_vcpu_affinity - 设置vCPU亲和性
 * @irq: 中断号
 * @vcpu_info: vCPU信息
 */
int irq_set_vcpu_affinity(unsigned int irq, void *vcpu_info)
{
    struct irq_desc *desc = irq_to_desc(irq);
    struct irq_data *data = &desc->irq_data;

    if (!data->chip->irq_set_vcpu_affinity)
        return -ENXIO;

    return data->chip->irq_set_vcpu_affinity(data, vcpu_info);
}

/**
 * irq_get_irqchip_state - 获取中断芯片状态
 * @irq: 中断号
 * @which: 状态类型
 * @state: 状态值
 */
int irq_get_irqchip_state(unsigned int irq, enum irqchip_irq_state which,
                         bool *state)
{
    struct irq_desc *desc = irq_to_desc(irq);
    struct irq_data *data = &desc->irq_data;

    if (!data->chip->irq_get_irqchip_state)
        return -ENXIO;

    return data->chip->irq_get_irqchip_state(data, which, state);
}

/**
 * irq_set_irqchip_state - 设置中断芯片状态
 * @irq: 中断号
 * @which: 状态类型
 * @val: 状态值
 */
int irq_set_irqchip_state(unsigned int irq, enum irqchip_irq_state which,
                         bool val)
{
    struct irq_desc *desc = irq_to_desc(irq);
    struct irq_data *data = &desc->irq_data;

    if (!data->chip->irq_set_irqchip_state)
        return -ENXIO;

    return data->chip->irq_set_irqchip_state(data, which, val);
}

/* ========================================================================
 * 12. 电源管理支持
 * ======================================================================== */

/**
 * irq_chip_pm_get - 启用芯片电源
 * @data: irq数据
 */
int irq_chip_pm_get(struct irq_data *data)
{
    int retval = 0;

#ifdef CONFIG_PM
    if (data->chip->pm) {
        retval = pm_runtime_get_sync(data->chip->pm);
        if (retval < 0) {
            pm_runtime_put_noidle(data->chip->pm);
            return retval;
        }
    }
#endif

    return retval;
}

/**
 * irq_chip_pm_put - 禁用芯片电源
 * @data: irq数据
 */
int irq_chip_pm_put(struct irq_data *data)
{
    int retval = 0;

#ifdef CONFIG_PM
    if (data->chip->pm) {
        retval = pm_runtime_put_sync(data->chip->pm);
    }
#endif

    return retval;
}

/* ========================================================================
 * 13. 中断亲和性管理
 * ======================================================================== */

/**
 * irq_set_affinity - 设置IRQ亲和性
 * @irq: 中断号
 * @cpumask: CPU掩码
 */
int irq_set_affinity(unsigned int irq, const struct cpumask *cpumask)
{
    struct irq_desc *desc = irq_to_desc(irq);
    struct irq_data *data = &desc->irq_data;
    int ret;

    if (!desc || !data->chip->irq_set_affinity)
        return -EINVAL;

    ret = data->chip->irq_set_affinity(data, cpumask, false);
    if (ret)
        return ret;

    cpumask_copy(&desc->irq_common_data.affinity, cpumask);
    return 0;
}

/**
 * irq_force_affinity - 强制设置IRQ亲和性
 * @irq: 中断号
 * @cpumask: CPU掩码
 */
int irq_force_affinity(unsigned int irq, const struct cpumask *cpumask)
{
    struct irq_desc *desc = irq_to_desc(irq);
    struct irq_data *data = &desc->irq_data;
    int ret;

    if (!desc || !data->chip->irq_set_affinity)
        return -EINVAL;

    ret = data->chip->irq_set_affinity(data, cpumask, true);
    if (ret)
        return ret;

    cpumask_copy(&desc->irq_common_data.affinity, cpumask);
    return 0;
}

/**
 * irq_can_set_affinity - 检查是否可以设置亲和性
 * @irq: 中断号
 */
int irq_can_set_affinity(unsigned int irq)
{
    struct irq_desc *desc = irq_to_desc(irq);
    struct irq_data *data = &desc->irq_data;

    if (!desc || !data->chip->irq_set_affinity)
        return 0;

    return 1;
}

/* ========================================================================
 * 14. 每CPU中断支持
 * ======================================================================== */

/**
 * request_percpu_irq - 分配每CPU中断
 * @irq: 中断号
 * @handler: 中断处理函数
 * @devname: 设备名称
 * @dev_id: 每CPU设备ID
 */
int request_percpu_irq(unsigned int irq, irq_handler_t handler,
                      const char *devname, void __percpu *dev_id)
{
    struct irqaction *action;
    struct irq_desc *desc;
    int retval;

    if (irq >= nr_irqs)
        return -EINVAL;

    desc = irq_to_desc(irq);
    if (!desc)
        return -EINVAL;

    action = kzalloc(sizeof(struct irqaction), GFP_KERNEL);
    if (!action)
        return -ENOMEM;

    action->handler = handler;
    action->flags = IRQF_PERCPU;
    action->name = devname;
    action->percpu_dev_id = dev_id;

    retval = __setup_irq(irq, desc, action);
    if (retval) {
        kfree(action);
        return retval;
    }

    return 0;
}

/**
 * irq_percpu_is_enabled - 检查每CPU中断是否启用
 * @irq: 中断号
 */
bool irq_percpu_is_enabled(unsigned int irq)
{
    struct irq_desc *desc = irq_to_desc(irq);
    unsigned int cpu = smp_processor_id();

    if (!desc || !desc->percpu_enabled)
        return false;

    return test_bit(cpu, desc->percpu_enabled);
}

/* ========================================================================
 * 15. 结束语
 * ======================================================================== */

/*
 * 本源码文件展示了Linux内核通用中断处理层的核心实现细节。
 * 这些代码片段涵盖了：
 * 
 * 1. 核心数据结构的定义
 * 2. 默认流处理程序的实现
 * 3. 延迟中断禁用机制
 * 4. 通用中断芯片的实现
 * 5. 公共API函数的实现
 * 6. 线程化中断支持
 * 7. 中断事件处理
 * 8. 中断统计机制
 * 9. 层次化IRQ域支持
 * 10. 虚拟化支持
 * 11. 电源管理支持
 * 12. 中断亲和性管理
 * 13. 每CPU中断支持
 * 
 * 这些实现体现了Linux内核中断处理的设计哲学：
 * - 抽象层次清晰
 * - 硬件无关性
 * - 性能优化
 * - 扩展性强
 * - 维护性好
 */
LN 嵌入式离线实验

embedded_replay.py：Python 3.10+，只在内存中构造/解析教学串口帧、重放序号与超时状态。运行：python embedded_replay.py。程序不打开串口、CAN适配器或GPIO，不控制电机；STOP_REQUESTED只是停止请求，未模拟实际刹车。
snapshot_demo.c：主机C11确定性交错示例，运行gcc -std=c11 -Wall -Wextra -Werror snapshot_demo.c -o snapshot_demo后执行。它不含真实ISR或线程，不证明任何DSP上的中断、原子性或最坏执行时间。
results.json：上述Python离线检查的实际输出。教学参数不是某电机或控制板的测量结果。

请先读课程正文中的平台区别、计时边界和协议假设。串口帧不是CANopen/CiA 402或工业安全通信协议。编译器类型、缓存/DMA一致性和电流环更新时序必须在具体硬件文档上另行确认。

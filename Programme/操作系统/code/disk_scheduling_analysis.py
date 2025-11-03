#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
磁盘调度算法性能分析
实现FCFS、SSTF、SCAN、C-SCAN、LOOK算法并进行比较分析
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from typing import List, Tuple, Dict
import random

def setup_matplotlib_for_plotting():
    """
    Setup matplotlib and seaborn for plotting with proper configuration.
    Call this function before creating any plots to ensure proper rendering.
    """
    warnings.filterwarnings('default')  # Show all warnings

    # Configure matplotlib for non-interactive mode
    plt.switch_backend("Agg")

    # Set chart style
    plt.style.use("seaborn-v0_8")
    sns.set_palette("husl")

    # Configure platform-appropriate fonts for cross-platform compatibility
    # Must be set after style.use, otherwise will be overridden by style configuration
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False

class DiskScheduler:
    """磁盘调度算法基类"""
    
    def __init__(self, requests: List[int], head_position: int, disk_size: int = 200):
        self.requests = requests.copy()  # 原始请求序列
        self.head_position = head_position
        self.disk_size = disk_size
        self.total_movement = 0
        self.service_order = []
        self.completed_requests = requests.copy()
        
    def reset(self):
        """重置调度器状态"""
        self.total_movement = 0
        self.service_order = []
        self.completed_requests = self.requests.copy()

class FCFS(DiskScheduler):
    """先来先服务算法"""
    
    def schedule(self):
        """FCFS调度"""
        self.reset()
        for request in self.requests:
            movement = abs(request - self.head_position)
            self.total_movement += movement
            self.service_order.append(request)
            self.head_position = request
        return self.total_movement, self.service_order

class SSTF(DiskScheduler):
    """最短寻道时间优先算法"""
    
    def schedule(self):
        """SSTF调度"""
        self.reset()
        remaining = self.requests.copy()
        
        while remaining:
            # 找到距离当前磁头位置最近的请求
            distances = [abs(req - self.head_position) for req in remaining]
            min_idx = distances.index(min(distances))
            closest_request = remaining[min_idx]
            
            # 服务该请求
            movement = abs(closest_request - self.head_position)
            self.total_movement += movement
            self.service_order.append(closest_request)
            self.head_position = closest_request
            
            # 从剩余请求中移除
            remaining.pop(min_idx)
        
        return self.total_movement, self.service_order

class SCAN(DiskScheduler):
    """电梯算法（SCAN）"""
    
    def schedule(self, direction: str = 'right'):
        """SCAN调度"""
        self.reset()
        remaining = sorted(self.requests.copy())
        self.service_order = []
        
        # 确定初始方向
        if direction == 'right':
            # 向右移动
            for request in remaining:
                if request >= self.head_position:
                    movement = abs(request - self.head_position)
                    self.total_movement += movement
                    self.service_order.append(request)
                    self.head_position = request
            
            # 到达最右端，反向
            for request in reversed(remaining):
                if request < self.head_position:
                    movement = abs(request - self.head_position)
                    self.total_movement += movement
                    self.service_order.append(request)
                    self.head_position = request
        else:
            # 向左移动
            for request in reversed(remaining):
                if request <= self.head_position:
                    movement = abs(request - self.head_position)
                    self.total_movement += movement
                    self.service_order.append(request)
                    self.head_position = request
            
            # 到达最左端，反向
            for request in remaining:
                if request > self.head_position:
                    movement = abs(request - self.head_position)
                    self.total_movement += movement
                    self.service_order.append(request)
                    self.head_position = request
        
        return self.total_movement, self.service_order

class CSCAN(DiskScheduler):
    """循环扫描算法（C-SCAN）"""
    
    def schedule(self):
        """C-SCAN调度"""
        self.reset()
        remaining = sorted(self.requests.copy())
        self.service_order = []
        
        # 向右扫描
        for request in remaining:
            if request >= self.head_position:
                movement = abs(request - self.head_position)
                self.total_movement += movement
                self.service_order.append(request)
                self.head_position = request
        
        # 到达最右端，跳回最左端
        if self.service_order:
            last_position = self.service_order[-1]
            jump_movement = abs(self.disk_size - 1 - 0)  # 从最右端跳到最左端
            self.total_movement += jump_movement
            self.head_position = 0
        
        # 继续向右扫描剩余请求
        for request in remaining:
            if request < self.head_position:
                movement = abs(request - self.head_position)
                self.total_movement += movement
                self.service_order.append(request)
                self.head_position = request
        
        return self.total_movement, self.service_order

class LOOK(DiskScheduler):
    """LOOK算法"""
    
    def schedule(self, direction: str = 'right'):
        """LOOK调度"""
        self.reset()
        remaining = sorted(self.requests.copy())
        self.service_order = []
        
        if direction == 'right':
            # 向右移动到最远请求
            right_requests = [req for req in remaining if req >= self.head_position]
            left_requests = [req for req in remaining if req < self.head_position]
            
            # 服务右侧请求
            for request in right_requests:
                movement = abs(request - self.head_position)
                self.total_movement += movement
                self.service_order.append(request)
                self.head_position = request
            
            # 反向服务左侧请求
            for request in reversed(left_requests):
                movement = abs(request - self.head_position)
                self.total_movement += movement
                self.service_order.append(request)
                self.head_position = request
        else:
            # 向左移动到最远请求
            left_requests = [req for req in remaining if req <= self.head_position]
            right_requests = [req for req in remaining if req > self.head_position]
            
            # 服务左侧请求
            for request in reversed(left_requests):
                movement = abs(request - self.head_position)
                self.total_movement += movement
                self.service_order.append(request)
                self.head_position = request
            
            # 反向服务右侧请求
            for request in right_requests:
                movement = abs(request - self.head_position)
                self.total_movement += movement
                self.service_order.append(request)
                self.head_position = request
        
        return self.total_movement, self.service_order

def generate_test_data(num_requests: int = 20, disk_size: int = 200) -> Tuple[List[int], int]:
    """生成测试数据"""
    requests = sorted([random.randint(0, disk_size-1) for _ in range(num_requests)])
    head_position = random.randint(0, disk_size-1)
    return requests, head_position

def calculate_performance_metrics(algorithm: DiskScheduler, requests: List[int], head_position: int) -> Dict:
    """计算性能指标"""
    total_movement, service_order = algorithm.schedule()
    
    # 计算平均寻道长度
    avg_seek_length = total_movement / len(requests) if requests else 0
    
    # 计算响应时间方差
    response_times = []
    current_time = 0
    for i, request in enumerate(service_order):
        # 简化的响应时间计算（实际中需要考虑排队时间）
        response_times.append(current_time)
        current_time += abs(request - head_position) if i == 0 else abs(request - service_order[i-1])
    
    response_time_variance = np.var(response_times) if response_times else 0
    
    # 计算吞吐量（请求/单位时间）
    throughput = len(requests) / total_movement if total_movement > 0 else float('inf')
    
    return {
        'total_movement': total_movement,
        'avg_seek_length': avg_seek_length,
        'response_time_variance': response_time_variance,
        'throughput': throughput,
        'service_order': service_order
    }

def compare_algorithms(requests: List[int], head_position: int, disk_size: int = 200) -> Dict:
    """比较所有算法的性能"""
    algorithms = {
        'FCFS': FCFS(requests, head_position, disk_size),
        'SSTF': SSTF(requests, head_position, disk_size),
        'SCAN': SCAN(requests, head_position, disk_size),
        'C-SCAN': CSCAN(requests, head_position, disk_size),
        'LOOK': LOOK(requests, head_position, disk_size)
    }
    
    results = {}
    for name, algorithm in algorithms.items():
        results[name] = calculate_performance_metrics(algorithm, requests, head_position)
    
    return results

def create_performance_visualization(results: Dict, save_path: str = '/workspace/docs/disk_scheduling_performance.png'):
    """创建性能可视化图表"""
    setup_matplotlib_for_plotting()
    
    algorithms = list(results.keys())
    metrics = ['total_movement', 'avg_seek_length', 'response_time_variance', 'throughput']
    metric_names = ['总寻道距离', '平均寻道长度', '响应时间方差', '吞吐量']
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('磁盘调度算法性能比较', fontsize=16, fontweight='bold')
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    for i, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
        ax = axes[i//2, i%2]
        values = [results[alg][metric] for alg in algorithms]
        
        bars = ax.bar(algorithms, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{value:.2f}', ha='center', va='bottom', fontsize=10)
        
        ax.set_title(f'{metric_name}', fontsize=12, fontweight='bold')
        ax.set_ylabel('数值', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 旋转x轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"性能比较图表已保存到: {save_path}")

def create_seek_pattern_visualization(requests: List[int], head_position: int, save_path: str = '/workspace/docs/seek_patterns.png'):
    """创建寻道模式可视化"""
    setup_matplotlib_for_plotting()
    
    algorithms = {
        'FCFS': FCFS(requests, head_position),
        'SSTF': SSTF(requests, head_position),
        'SCAN': SCAN(requests, head_position),
        'C-SCAN': CSCAN(requests, head_position),
        'LOOK': LOOK(requests, head_position)
    }
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('磁盘调度算法寻道模式对比', fontsize=16, fontweight='bold')
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    # 绘制原始请求分布
    ax = axes[0, 0]
    ax.scatter(requests, [1]*len(requests), color='gray', alpha=0.6, s=50, label='请求位置')
    ax.axvline(x=head_position, color='red', linestyle='--', linewidth=2, label=f'初始磁头位置 ({head_position})')
    ax.set_title('原始请求分布', fontsize=12, fontweight='bold')
    ax.set_xlabel('磁道号')
    ax.set_ylabel('请求')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.5, 1.5)
    
    # 绘制各算法的寻道路径
    for idx, (name, algorithm) in enumerate(list(algorithms.items())[:5]):
        row = (idx + 1) // 3
        col = (idx + 1) % 3
        ax = axes[row, col]
        
        total_movement, service_order = algorithm.schedule()
        
        # 绘制磁头移动路径
        path_x = [head_position] + service_order
        path_y = list(range(len(path_x)))
        
        ax.plot(path_x, path_y, 'o-', color=colors[idx], linewidth=2, markersize=6, label='磁头路径')
        ax.scatter([head_position], [0], color='red', s=100, marker='*', label='起始位置', zorder=5)
        ax.scatter(service_order, list(range(1, len(service_order)+1)), 
                  color=colors[idx], s=50, alpha=0.7, zorder=3)
        
        ax.set_title(f'{name}\n总寻道距离: {total_movement}', fontsize=12, fontweight='bold')
        ax.set_xlabel('磁道号')
        ax.set_ylabel('服务顺序')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"寻道模式图表已保存到: {save_path}")

def run_comprehensive_analysis():
    """运行综合性能分析"""
    print("开始磁盘调度算法综合性能分析...")
    
    # 生成多个测试用例
    test_cases = [
        (20, 200, "小规模随机请求"),
        (50, 500, "中规模随机请求"),
        (30, 300, "集中请求（50-150范围内）"),
        (40, 400, "分散请求（0-400范围内）")
    ]
    
    all_results = {}
    
    for i, (num_requests, disk_size, description) in enumerate(test_cases):
        print(f"\n=== 测试用例 {i+1}: {description} ===")
        
        # 生成测试数据
        requests, head_position = generate_test_data(num_requests, disk_size)
        print(f"磁头初始位置: {head_position}")
        print(f"请求序列: {requests}")
        
        # 比较算法性能
        results = compare_algorithms(requests, head_position, disk_size)
        all_results[f"test_case_{i+1}"] = {
            'description': description,
            'requests': requests,
            'head_position': head_position,
            'results': results
        }
        
        # 打印性能指标
        print("\n性能指标:")
        for alg_name, metrics in results.items():
            print(f"  {alg_name}:")
            print(f"    总寻道距离: {metrics['total_movement']}")
            print(f"    平均寻道长度: {metrics['avg_seek_length']:.2f}")
            print(f"    响应时间方差: {metrics['response_time_variance']:.2f}")
            print(f"    吞吐量: {metrics['throughput']:.4f}")
    
    # 创建可视化图表
    print("\n创建性能可视化图表...")
    
    # 使用第一个测试用例创建详细比较
    first_case = all_results['test_case_1']
    create_performance_visualization(first_case['results'])
    create_seek_pattern_visualization(first_case['requests'], first_case['head_position'])
    
    # 创建综合性能对比
    create_comprehensive_comparison(all_results)
    
    return all_results

def create_comprehensive_comparison(all_results: Dict, save_path: str = '/workspace/docs/comprehensive_performance.png'):
    """创建综合性能对比图表"""
    setup_matplotlib_for_plotting()
    
    algorithms = ['FCFS', 'SSTF', 'SCAN', 'C-SCAN', 'LOOK']
    metrics = ['total_movement', 'avg_seek_length', 'response_time_variance', 'throughput']
    metric_names = ['总寻道距离', '平均寻道长度', '响应时间方差', '吞吐量']
    
    # 收集所有测试用例的数据
    test_names = list(all_results.keys())
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('磁盘调度算法综合性能分析（多测试用例）', fontsize=16, fontweight='bold')
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    for i, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
        ax = axes[i//2, i%2]
        
        # 为每个算法创建箱线图数据
        data_for_box = []
        labels = []
        
        for alg in algorithms:
            alg_data = []
            for test_name in test_names:
                alg_data.append(all_results[test_name]['results'][alg][metric])
            data_for_box.append(alg_data)
            labels.append(alg)
        
        bp = ax.boxplot(data_for_box, labels=labels, patch_artist=True)
        
        # 设置颜色
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title(f'{metric_name}', fontsize=12, fontweight='bold')
        ax.set_ylabel('数值', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 旋转x轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"综合性能对比图表已保存到: {save_path}")

if __name__ == "__main__":
    # 运行综合分析
    results = run_comprehensive_analysis()
    print("\n=== 分析完成 ===")
    print("所有图表已生成，请查看 /workspace/docs/ 目录下的文件")

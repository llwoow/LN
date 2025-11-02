# Transformer注意力机制详细解析

## 概述

Transformer是一种基于注意力机制的神经网络架构，由Google在2017年的论文"Attention Is All You Need"中首次提出。它完全摒弃了传统的循环神经网络(RNN)和卷积神经网络(CNN)，仅使用注意力机制来处理序列数据。

## 核心原理

### 1. 注意力机制的基本思想

注意力机制的核心思想是：在处理序列中的每个元素时，模型能够"关注"序列中的其他相关元素，而不是仅依赖于固定的位置上下文。

### 2. 自注意力(Self-Attention)机制

自注意力是Transformer的核心组件，它允许序列中的每个位置都关注序列中的所有位置：

**数学公式：**
```
Attention(Q, K, V) = softmax(QK^T / √d_k)V
```

其中：
- Q (Query)：查询矩阵
- K (Key)：键矩阵  
- V (Value)：值矩阵
- d_k：键向量的维度
- softmax：归一化函数

### 3. 多头注意力(Multi-Head Attention)

多头注意力通过并行计算多个注意力函数来捕获不同类型的关系：

**数学公式：**
```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h)W^O

其中 head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```

其中：
- h：注意力头数
- W_i^Q, W_i^K, W_i^V：第i个头的线性变换矩阵
- W^O：输出线性变换矩阵

## 实现细节

### 1. 位置编码(Positional Encoding)

由于Transformer没有循环结构，需要添加位置信息：

**数学公式：**
```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

其中：
- pos：位置索引
- i：维度索引
- d_model：模型维度

### 2. 前馈神经网络(Feed Forward)

每个Transformer层包含一个前馈网络：

```
FFN(x) = max(0, xW_1 + b_1)W_2 + b_2
```

### 3. 层归一化(Layer Normalization)

每个子层都使用残差连接和层归一化：

```
LayerNorm(x + Sublayer(x))
```

## 架构组件

### 1. 编码器(Encoder)

每个编码器层包含：
- 多头自注意力机制
- 前馈神经网络
- 残差连接和层归一化

### 2. 解码器(Decoder)

每个解码器层包含：
- 掩码多头自注意力机制
- 编码器-解码器注意力
- 前馈神经网络
- 残差连接和层归一化

### 3. 掩码机制

在解码器中使用因果掩码，确保位置i只能关注位置i之前的位置：

```
Mask[i, j] = 0 if j <= i else -∞
```

## 优势特点

1. **并行计算**：不依赖序列顺序，可以并行处理所有位置
2. **长距离依赖**：可以直接计算任意位置之间的注意力
3. **可解释性**：注意力权重提供了模型决策的可解释性
4. **灵活性**：可以应用于各种序列到序列的任务

## 应用场景

- 机器翻译
- 文本摘要
- 问答系统
- 语言建模
- 图像描述生成
- 代码生成

## 实现示例

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        
        # 线性变换并重塑为多头
        Q = self.W_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # 计算注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
            
        attention_weights = F.softmax(scores, dim=-1)
        context = torch.matmul(attention_weights, V)
        
        # 拼接多头输出
        context = context.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model)
        
        return self.W_o(context)
```

## 总结

Transformer注意力机制通过自注意力机制实现了对序列数据的高效建模，其核心优势在于能够并行处理序列中的所有位置，并且能够直接捕获长距离依赖关系。这种架构已经成为了现代自然语言处理和许多其他序列建模任务的基础。
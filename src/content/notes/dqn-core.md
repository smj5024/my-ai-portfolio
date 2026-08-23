---
title: DQN 的三个关键部件：网络、回放与目标值
summary: 从 Q-Learning 的表格限制出发，理解 DQN 为什么需要经验回放和目标网络，以及怎样避免常见实现错误。
published: 2026-08-22
status: learning
track: reinforcement-learning
stage: 深度强化学习
tags: [DQN, Q-Learning, PyTorch, 经验回放]
featured: true
---

## 为什么不能一直使用 Q 表

表格型 Q-Learning 为每个状态—动作对保存一个数值。当状态来自图像、IMU 时间窗或连续传感器时，状态数量会迅速膨胀，很多状态甚至永远不会重复出现。

DQN 用神经网络 $Q(s,a;\theta)$ 近似 Q 函数，输入状态，一次输出每个离散动作的估计价值。

## 训练目标

对一条交互经验 $(s,a,r,s',d)$，常用目标为：

$$
y = r + \gamma(1-d)\max_{a'}Q_{\text{target}}(s',a')
$$

损失可以写成：

$$
L(\theta)=\mathbb{E}\left[(y-Q(s,a;\theta))^2\right]
$$

其中 $d$ 表示回合是否真正终止。实现时还要区分环境的 `terminated` 与 `truncated`，否则时间上限可能被错误地当成终止状态。

## 三个关键部件

### 1. Q 网络

根据状态结构选择 MLP、CNN 或时序网络。第一版实验应优先选择小模型，先确保数据流、奖励和评估流程正确。

### 2. 经验回放

在线交互数据在时间上高度相关。经验池随机抽样可以降低相邻样本相关性，并重复利用已有数据。

### 3. 目标网络

如果预测值和目标值由同一个快速变化的网络产生，学习目标会不停移动。目标网络通过周期性硬更新或缓慢软更新提供相对稳定的监督信号。

```python
with torch.no_grad():
    next_q = target_net(next_states).max(dim=1).values
    target = rewards + gamma * (1.0 - terminated) * next_q

chosen_q = online_net(states).gather(1, actions[:, None]).squeeze(1)
loss = torch.nn.functional.smooth_l1_loss(chosen_q, target)
```

## 端侧项目中的边界

训练通常在电脑或云端完成；树莓派或 MCU 更适合运行已经训练、压缩和量化后的推理模型。真实设备上仍需要安全规则、动作限幅和失效保护，不能把策略网络当作唯一控制层。

## 下一步实验

- 在小型离散环境中建立可重复的 DQN 基线。
- 固定随机种子并记录多次运行的均值和方差。
- 对比是否使用目标网络时的训练稳定性。
- 导出 ONNX，先在电脑上核对输出一致性。

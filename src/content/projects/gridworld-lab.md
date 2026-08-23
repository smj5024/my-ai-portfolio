---
title: 可复现的 GridWorld 强化学习实验台
summary: 用一个足够小的环境验证 Bellman、动态规划、Q-Learning 与 DQN 的实现差异，并统一记录随机种子和训练曲线。
status: planned
order: 2
category: 强化学习基础实验
hardware: [PC]
algorithms: [动态规划, Q-Learning, DQN]
updated: 2026-08-22
featured: true
metrics:
  - label: 环境
    value: 待实现
  - label: 基线
    value: 待建立
---

## 目标

建立一个浏览器可展示、Python 可训练的小型网格环境。它不是为了追求复杂，而是作为后续所有算法实现的“单元测试场”。

## 计划对比

- 策略迭代与价值迭代。
- SARSA 与 Q-Learning。
- 表格法与小型 DQN。
- 不同探索率、折扣因子和奖励设计。

## 完成标准

只有满足以下条件才会把状态改为“已验证”：

1. 固定依赖版本和随机种子。
2. 至少运行多组随机种子。
3. 展示训练均值、方差和评估回报。
4. 浏览器演示与 Python 环境的规则一致。

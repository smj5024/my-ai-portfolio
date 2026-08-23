---
title: Raspberry Pi 感知—策略—动作闭环
summary: 把传感器输入、小型策略模型、安全规则和执行器连接成第一版桌面 Agent 原型。
status: planned
order: 3
category: 端侧 Agent
hardware: [Raspberry Pi 4B, 摄像头, IMU, 执行器]
algorithms: [状态估计, ONNX 推理, 行为策略]
updated: 2026-08-22
featured: false
metrics:
  - label: 目标周期
    value: 待基准测试
  - label: 模型格式
    value: 待选择
---

## 目标

在 Raspberry Pi 4B 上跑通真正的闭环：采集环境状态、执行模型推理、经过安全层处理后驱动动作，并记录每个环节的延迟。

## 设计边界

- 模型在电脑上训练，设备端主要负责推理。
- 规则安全层拥有比策略网络更高的控制优先级。
- 第一版只解决少量状态和动作，不追求通用 Agent。
- 所有指标以实机测量为准，不使用桌面电脑结果代替。

## 里程碑

1. 传感器采集与时间同步。
2. 浮点模型端侧推理。
3. 动作限幅、超时与急停。
4. 闭环日志和可视化回放。
5. 量化版本与浮点版本对照。

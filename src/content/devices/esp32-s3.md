---
title: ESP32-S3
shortName: ESP32-S3
summary: 适合低功耗传感器采集和小型 TinyML 任务，用于验证事件检测与简单本地交互。
status: planned
order: 2
role: 可穿戴与低功耗感知候选平台
specs:
  - label: 软件栈
    value: ESP-IDF（待搭建）
  - label: 模型格式
    value: INT8（候选）
  - label: 功耗
    value: 待实测
suitableFor: [IMU 事件检测, 关键词或声音事件检测, 低功耗传感器节点]
constraints: [SRAM 与 Flash 受限, 算子集合受限, 需要严格控制采样和无线通信功耗]
---

该平台会在 Pi 端闭环得到验证后再进入模型迁移阶段。先定义任务和预算，再选择模型，避免从“能不能塞进去”倒推一个没有实际价值的功能。

---
title: Raspberry Pi 4 Model B
shortName: Pi 4B
summary: 第一阶段端侧部署主平台，生态完整，适合验证 Linux 下的视觉、音频、模型推理和闭环控制。
status: planned
order: 1
role: 端侧原型与性能基线
specs:
  - label: 系统
    value: Linux / 64-bit（待配置）
  - label: 推理运行时
    value: ONNX Runtime / TFLite（待对比）
  - label: 实测延迟
    value: 待测试
suitableFor: [摄像头与 IMU 接入, Python 原型迁移, 模型量化对比, 桌面机器人控制]
constraints: [算力和散热有限, 需要端到端延迟测试, 不适合直接承担大规模模型训练]
---

Pi 4B 会作为从电脑实验跨到真实设备的第一站。重点不是跑最大的模型，而是建立可观测、可恢复的服务和控制流程。

计划记录启动时间、CPU 与内存占用、P50/P95 推理延迟、温度以及连续运行稳定性。

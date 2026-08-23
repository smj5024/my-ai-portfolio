---
title: STM32H7 系列
shortName: STM32H7
summary: 高性能 MCU 候选平台，用于研究实时控制、CMSIS-NN 和受限内存中的小型策略网络。
status: planned
order: 3
role: 实时控制与 MCU 模型迁移
specs:
  - label: 工具链
    value: STM32Cube / CMSIS-NN（候选）
  - label: 数据类型
    value: FP32 / INT8（待评估）
  - label: 峰值内存
    value: 待实测
suitableFor: [实时传感器处理, 确定性控制周期, 小型神经网络推理]
constraints: [具体资源随型号变化, 调试与部署门槛高于 Linux, 动态内存和算子选择必须受控]
---

只有在明确具体芯片、开发板和任务后，网站才会补充准确规格。现阶段把它保留为技术路线，而不虚构设备实测数据。

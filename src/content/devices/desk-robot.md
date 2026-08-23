---
title: 办公桌面机器人原型
shortName: DeskBot
summary: 把摄像头、IMU、语音输入和执行器组合起来，作为端侧 Agent 能力的集成验证载体。
status: planned
order: 4
role: 多模态闭环集成平台
specs:
  - label: 主控
    value: Raspberry Pi 4B（候选）
  - label: 传感器
    value: 摄像头 / IMU / 麦克风（待选型）
  - label: 执行器
    value: 舵机或移动底盘（待选型）
suitableFor: [环境感知, 移动检测, 语音命令, 策略与安全层验证]
constraints: [机械与电气安全, 实时性, 噪声环境, 需要明确急停和故障模式]
---

桌面机器人不是一开始就追求“通用智能”，而是用来回答一组具体问题：状态能否稳定采集、模型能否按时输出、安全层能否接管、失败过程能否复现。

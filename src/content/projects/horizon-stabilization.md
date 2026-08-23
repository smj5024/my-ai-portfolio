---
title: IMU + 视觉地平线稳定模块
summary: 一个正在开发的软件原型，用视觉线段和模拟 IMU 横滚角估计画面倾斜，为后续真实端侧感知建立数据链路。
status: building
order: 1
category: 环境感知 / 传感器融合
hardware: [摄像头, IMU, Raspberry Pi 4B]
algorithms: [卡尔曼滤波, HoughLinesP, 加权融合]
repository: https://github.com/smj5024/my-ai-portfolio/tree/main/projects/horizon-stabilization
started: 2026-04-03
updated: 2026-08-22
featured: true
metrics:
  - label: 当前阶段
    value: 软件原型
  - label: IMU 输入
    value: 模拟数据
  - label: 实机基准
    value: 待测试
---

## 要解决的问题

移动摄像头发生横滚时，画面倾斜会影响观看体验，也会让后续运动检测与视觉状态估计变得更困难。这个模块尝试融合 IMU 和视觉信息，估计横滚角并实时校正画面。

## 当前处理链路

```text
视频帧 ─→ 去畸变 ─→ 边缘/线段检测 ─┐
                                      ├─→ 角度融合 ─→ 图像旋转
模拟 IMU ─→ 卡尔曼滤波 ──────────────┘
```

代码已经实现 `HorizonStabilizer` 类，并把去畸变、视觉检测、IMU 更新、融合与画面旋转拆成独立方法。

## 当前限制

- IMU 数据由正弦函数模拟，尚未连接真实传感器。
- 默认相机内参按固定视场角和 1920×1080 分辨率估算。
- 融合权重固定为 0.5，没有随视觉置信度变化。
- 还没有角度误差、端到端延迟和树莓派帧率等实测数据。
- `cv2.imshow` 适合桌面调试，不适合作为无界面设备的最终运行方式。

## 下一步

1. 接入真实 IMU 数据并统一时间戳。
2. 增加相机标定文件与命令行参数。
3. 建立离线测试视频和角度真值。
4. 输出误差、P95 延迟、CPU 占用和帧率。
5. 在 Raspberry Pi 4B 上验证无界面处理流程。

## 可复现运行

当前 Python 原型位于仓库的 `projects/horizon-stabilization/`。安装依赖后可传入视频文件运行；真实 IMU 接入方式会在硬件测试完成后补充。

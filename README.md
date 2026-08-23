# EdgeMind Lab / 边缘智体实验室

一个面向强化学习与端侧 AI 的个人学习网站，记录从数学原理、仿真实验，到 Raspberry Pi 4B、高性能 MCU、可穿戴设备和桌面机器人的实践过程。

线上地址：[https://smj5024.github.io/my-ai-portfolio/](https://smj5024.github.io/my-ai-portfolio/)

## 为什么这样搭建

- **Astro + Markdown**：不需要数据库或服务器，文章就是仓库里的 Markdown 文件，适合逐步积累。
- **GitHub Pages**：公开仓库可免费托管静态网站，推送代码后由 GitHub Actions 自动发布。
- **Pagefind**：构建时生成站内搜索索引，不需要额外搜索服务。
- **CSDN 作为分发渠道**：适合同步精选文章并获得中文技术社区流量；本站负责完整路线、项目档案与长期归档。
- **本地保留完整数据，GitHub 负责远端备份**：仓库克隆到任意电脑后都能恢复网站内容。

## 网站结构

```text
src/
├─ content/
│  ├─ notes/       # 强化学习、端侧 AI 与工程笔记
│  ├─ projects/    # 实验档案、限制与完成标准
│  └─ devices/     # Raspberry Pi、MCU 与原型设备档案
├─ data/roadmap.ts # 六阶段学习路线
├─ pages/          # 首页、列表页、详情页、搜索、RSS
└─ styles/         # 全站视觉系统与响应式样式
```

当前内容状态会明确区分：`草稿`、`学习中`、`已规划`、`制作中`、`已验证`、`已部署`。计划不会被包装成已经完成的成果。

## 本地运行

需要 Node.js 22.12 或更高版本。

```bash
npm install
npm run dev
```

开发服务器启动后，终端会显示本地访问地址。

提交前执行完整检查：

```bash
npm run build
```

这条命令会依次执行 Astro 类型检查、静态站点构建和 Pagefind 搜索索引生成。输出目录为 `dist/`。

## 新增一篇学习笔记

在 `src/content/notes/` 新建 Markdown 文件，例如 `q-learning-first-run.md`：

```md
---
title: Q-Learning 第一次可复现实验
summary: 用最小 GridWorld 核对状态、动作、奖励与更新公式。
published: 2026-08-22
status: learning
track: reinforcement-learning
stage: 强化学习基础
tags: [Q-Learning, GridWorld]
featured: false
---

这里开始写正文。
```

保存后列表页、详情页、RSS 和搜索索引都会在构建时自动更新。项目和设备内容分别放在 `src/content/projects/`、`src/content/devices/`，已有文件可以直接作为模板。

## 部署到 GitHub Pages

仓库已包含 `.github/workflows/deploy.yml`。首次部署需要在 GitHub 仓库页面完成一次设置：

1. 打开仓库的 **Settings → Pages**。
2. 在 **Build and deployment** 中把 Source 选择为 **GitHub Actions**。
3. 将本地改动提交并推送到 `main` 分支。
4. 打开仓库的 **Actions** 页面，等待 `Deploy Astro site to GitHub Pages` 完成。

常用命令：

```bash
git add .
git commit -m "build: launch EdgeMind Lab"
git push origin main
```

站点配置目前对应：

- GitHub 用户名：`smj5024`
- 仓库名：`my-ai-portfolio`
- 站点基础路径：`/my-ai-portfolio`

如果以后修改用户名或仓库名，需要同步修改 `astro.config.mjs` 中的 `site` 和 `base`。

## 推荐的长期维护方式

1. 平时只在 Markdown 中更新学习记录，不频繁改页面组件。
2. 每个实验先写目标、输入、完成标准，再补代码和结果。
3. 实机数据记录设备型号、软件版本、输入、P50/P95 延迟、内存和失败条件。
4. 完成一篇成熟文章后，再把精简版本同步到 CSDN，并链接回本站对应档案。
5. 每次重要更新都提交到 Git，GitHub 同时承担版本历史和异地备份。

## 中断后如何恢复

如果网络或会话中断，代码仍保存在本地仓库。重新进入项目后依次运行：

```bash
git status
npm install
npm run build
```

然后从 Git 未提交文件和构建输出继续，不需要重做已有内容。实现方案、目录约定和发布步骤均保存在本 README 中。

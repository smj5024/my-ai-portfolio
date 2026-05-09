# Snake AI - Web 可视化使用指南

## 🎯 概述

本项目新增了基于 Web 的可视化界面，让你可以在**任何有浏览器的设备**上观看 AI 玩贪吃蛇，特别适合：
- ✅ VSCode Remote SSH 远程开发
- ✅ 云服务器无图形界面环境
- ✅ Docker 容器化部署
- ✅ 移动端随时查看

## 🚀 快速开始

### 方法 1：使用启动脚本（推荐）

```bash
cd rl_snake_project

# 基本用法
./start_web.sh

# 自定义参数
./start_web.sh ./models/best_model.pth 8080 50
```

### 方法 2：直接运行 Python 脚本

```bash
cd rl_snake_project

# 基本用法
python3 play_web.py --model ./models/best_model.pth

# 完整参数
python3 play_web.py \
    --model ./models/best_model.pth \
    --port 5000 \
    --speed 100 \
    --host 0.0.0.0
```

## 📺 访问 Web 界面

启动后，在浏览器中打开：

- **本地访问**: http://localhost:5000
- **远程访问**: http://<服务器IP>:5000
- **VSCode Remote**: http://localhost:5000 (自动端口转发)

## 🎨 界面功能

### 实时统计面板
- **Current Score**: 当前游戏分数
- **Best Score**: 历史最高分
- **Average Score**: 平均分
- **Episodes**: 已玩游戏局数

### 游戏画面
- 实时渲染贪吃蛇游戏
- 绿色蛇身 + 红色食物
- 自动刷新（100ms）

### 控制按钮
- **⏸️ Pause/Resume**: 暂停/继续游戏
- **🔄 Reset Stats**: 重置统计数据

## ⚙️ 参数说明

| 参数 | 默认值 | 说明 | 示例 |
|------|--------|------|------|
| `--model` | ./models/best_model.pth | 模型文件路径 | `--model ./models/final_model.pth` |
| `--speed` | 100 | 游戏速度（毫秒/步） | `--speed 50` (更快) |
| `--port` | 5000 | Web 服务端口 | `--port 8080` |
| `--host` | 0.0.0.0 | 监听地址 | `--host 127.0.0.1` |

### 速度参数建议

| Speed 值 | 效果 | 适用场景 |
|----------|------|----------|
| 10-30 | 非常快 | 快速测试 |
| 50-100 | 正常 | 日常观看 |
| 150-200 | 较慢 | 详细观察 |
| 300+ | 很慢 | 教学演示 |

## 🔧 VSCode Remote 配置

### 自动端口转发

VSCode 通常会自动检测并转发端口。如果没有：

1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 "Remote-Ports: Forward Port"
3. 输入端口号（如 5000）
4. 点击通知中的链接打开浏览器

### 手动配置端口转发

在 `.vscode/settings.json` 中添加：

```json
{
    "remote.portsAttributes": {
        "5000": {
            "label": "Snake AI Web",
            "onAutoForward": "openBrowser"
        }
    }
}
```

## 🌐 远程访问配置

### 云服务器（阿里云、腾讯云等）

1. **开放安全组端口**：
   - 登录云控制台
   - 找到安全组规则
   - 添加入站规则：TCP 5000

2. **配置防火墙**：
   ```bash
   sudo ufw allow 5000
   sudo ufw reload
   ```

3. **启动服务**：
   ```bash
   python3 play_web.py --model ./models/best_model.pth --host 0.0.0.0 --port 5000
   ```

4. **访问**：http://<公网IP>:5000

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "play_web.py", "--model", "./models/best_model.pth", "--host", "0.0.0.0"]
```

构建和运行：

```bash
docker build -t snake-ai .
docker run -p 5000:5000 -v $(pwd)/models:/app/models snake-ai
```

## 🐛 故障排除

### 问题 1：无法访问 Web 界面

**症状**：浏览器显示"无法连接"

**解决方案**：
```bash
# 1. 检查服务是否运行
ps aux | grep play_web

# 2. 检查端口占用
netstat -tlnp | grep 5000

# 3. 检查防火墙
sudo ufw status

# 4. 尝试更换端口
python3 play_web.py --port 8080
```

### 问题 2：页面加载但画面不更新

**症状**：看到界面但游戏画面静止

**解决方案**：
1. 打开浏览器开发者工具（F12）
2. 查看 Console 标签是否有错误
3. 检查 Network 标签中 `/api/game_state` 请求是否正常
4. 刷新页面重试
5. 增加 speed 参数：`--speed 200`

### 问题 3：Flask 导入失败

**症状**：`ModuleNotFoundError: No module named 'flask'`

**解决方案**：
```bash
# 安装 Flask
pip3 install --break-system-packages flask flask-cors

# 或使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors
```

### 问题 4：端口被占用

**症状**：`Address already in use`

**解决方案**：
```bash
# 查找占用端口的进程
lsof -i :5000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
python3 play_web.py --port 8080
```

## 💡 高级用法

### 同时运行多个实例

```bash
# 终端 1
python3 play_web.py --model ./models/best_model.pth --port 5000 --speed 50

# 终端 2
python3 play_web.py --model ./models/final_model.pth --port 5001 --speed 100
```

访问：
- 实例 1: http://localhost:5000
- 实例 2: http://localhost:5001

### 后台运行

```bash
# 使用 nohup
nohup python3 play_web.py --model ./models/best_model.pth > web.log 2>&1 &

# 查看日志
tail -f web.log

# 停止服务
pkill -f play_web.py
```

### 使用 systemd 管理（Linux）

创建 `/etc/systemd/system/snake-ai-web.service`：

```ini
[Unit]
Description=Snake AI Web Visualization
After=network.target

[Service]
Type=simple
User=rluser
WorkingDirectory=/home/rluser/project/rl_snake_project
ExecStart=/usr/bin/python3 play_web.py --model ./models/best_model.pth --host 0.0.0.0 --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable snake-ai-web
sudo systemctl start snake-ai-web
sudo systemctl status snake-ai-web
```

## 📊 性能优化

### 降低资源占用

```bash
# 1. 降低刷新频率（修改 play_web.py）
setInterval(fetchGameState, 200);  // 从 100ms 改为 200ms

# 2. 减小画布尺寸（修改 HTML_TEMPLATE）
<canvas id="gameCanvas" width="320" height="240"></canvas>

# 3. 使用生产级 WSGI 服务器
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 play_web:app
```

## 🎓 学习资源

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [HTML5 Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [WebSocket vs HTTP Polling](https://www.pubnub.com/blog/websockets-vs-http-polling/)

## 📝 更新日志

### v1.0 (2026-04-19)
- ✨ 新增 Web 可视化功能
- ✨ 支持实时游戏画面显示
- ✨ 添加统计面板和控制按钮
- ✨ 适配 VSCode Remote 环境
- ✨ 提供快速启动脚本

---

**享受在浏览器中观看 AI 玩贪吃蛇的乐趣！🎮🐍**

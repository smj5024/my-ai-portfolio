# 强化学习入门项目：贪吃蛇 AI

本项目是一个完整的强化学习（Reinforcement Learning, RL）入门实践项目，通过经典的贪吃蛇游戏，带你从零开始理解并实现 DQN（Deep Q-Network）算法。

## ⚡ 快速上手（3 步开始）

```bash
# 1. 安装依赖
cd rl_snake_project
pip install -r requirements.txt

# 2. 训练模型（1000 局）
python train.py --episodes 1000

# 3. 观看 AI 玩游戏
python play.py --mode watch --model ./models/best_model.pth
```

---

## 📁 项目结构

```
rl_snake_project/
├── env.py           # 游戏环境（Environment）
├── agent.py         # DQN 智能体（Agent）
├── train.py         # 训练脚本
├── play.py          # 游戏/演示脚本
├── requirements.txt # 依赖包
├── models/          # 保存的模型（训练后生成）
└── README.md        # 本文档
```

---

## 🎯 项目目标

训练一个 AI 智能体玩贪吃蛇游戏，实现：
- **吃到最多的食物**（最高分数）
- **存活时间更长**（避免撞墙和自撞）

---

## 📚 强化学习 Pipeline 详解

### 什么是强化学习？

强化学习是一种机器学习方法，智能体（Agent）通过与环境（Environment）交互，学习如何做出决策以最大化累积奖励（Reward）。

```
┌─────────────┐      动作 (Action)      ┌─────────────┐
│             │ ──────────────────────> │             │
│   Agent     │                         │ Environment │
│  (DQN 网络)  │ <────────────────────── │  (贪吃蛇)   │
│             │   状态 (State) + 奖励    │             │
└─────────────┘      (Reward)           └─────────────┘
```

### 强化学习核心要素

| 要素 | 英文 | 本项目对应 | 说明 |
|------|------|-----------|------|
| **状态** | State | 蛇头位置、食物位置、危险方向 | 环境的当前情况 |
| **动作** | Action | 直行、右转、左转 | 智能体的决策 |
| **奖励** | Reward | 吃到食物 +10，撞死 -10，每步 -0.1 | 反馈信号 |
| **策略** | Policy | ε-greedy | 决策规则 |
| **价值函数** | Q-function | DQN 网络输出 | 预测未来奖励 |

### 完整训练流程

```
1. 初始化环境 → 2. 获取初始状态 → 3. 选择动作 → 4. 执行动作
       ↑                                                    │
       │                                                    ↓
       │                                            5. 获取奖励和新状态
       │                                                    │
       │                                                    ↓
       │                                            6. 存储经验到记忆
       │                                                    │
       │                                                    ↓
       └──── 7. 从记忆采样 → 8. 训练网络 → 9. 更新目标网络 ←┘
```

---

## 🔍 代码模块详解

### 1. 环境模块 (`env.py`)

环境是强化学习中最重要的组成部分之一。它定义了：
- 游戏如何运行
- 状态如何表示
- 奖励如何计算

#### 核心类：`SnakeGameNoRender`

```python
class SnakeGameNoRender:
    """无渲染的贪吃蛇环境（用于快速训练）"""
```

#### 关键方法解析

##### `__init__()` - 初始化
```python
def __init__(self, width=640, height=480, block_size=20, speed=100):
    self.grid_width = width // block_size   # 网格宽度 = 32
    self.grid_height = height // block_size # 网格高度 = 24
```

| 参数 | 默认值 | 作用 | 可调范围 |
|------|--------|------|----------|
| `width` | 640 | 窗口宽度（像素） | 320-1280 |
| `height` | 480 | 窗口高度（像素） | 240-960 |
| `block_size` | 20 | 每个格子大小 | 10-40 |
| `speed` | 100 | 游戏速度（ms/帧） | 10-200 |

##### `reset()` - 重置环境
```python
def reset(self):
    # 蛇从中心开始，长度为 3
    self.snake = [Point(cx, cy), Point(cx-1, cy), Point(cx-2, cy)]
    self.direction = Direction.RIGHT
    self.score = 0
    self._place_food()
    return self._get_state()
```

**为什么要重置？**
- 每局游戏结束后需要重新开始
- 训练时需要大量独立的游戏样本

##### `_get_state()` - 获取状态（核心！）
```python
def _get_state(self):
    state = [
        # 危险检测（3 个方向）
        danger_straight,  # 前方是否有危险
        danger_right,     # 右侧是否有危险
        danger_left,      # 左侧是否有危险
        
        # 当前方向（one-hot 编码）
        dir_left, dir_right, dir_up, dir_down,
        
        # 食物相对位置
        food_up, food_down, food_left, food_right
    ]
    return np.array(state, dtype=np.float32)
```

**状态向量详解（11 维）：**

```
状态 = [危险直，危险右，危险左，方向左，方向右，方向上，方向下，食物上，食物下，食物左，食物右]
        │         │         │         │              │         │              │
        └─ 3 维 ──┘         └──── 4 维 ────┘         └──── 4 维 ────┘
           │                     │                      │
       危险检测              方向编码              食物位置
```

**为什么这样设计状态？**
- **危险检测**：帮助蛇避免死亡（最重要！）
- **方向编码**：让蛇知道当前朝向
- **食物位置**：引导蛇向食物移动

##### `step()` - 执行动作
```python
def step(self, action):
    """
    执行一步动作
    
    参数:
        action: 0=直行，1=右转，2=左转
    
    返回:
        (state, reward, done, info)
    """
    # 1. 更新方向
    # 2. 移动蛇头
    # 3. 检测碰撞
    # 4. 检查是否吃到食物
    # 5. 返回新状态和奖励
```

**奖励设计详解：**

| 情况 | 奖励值 | 设计原因 |
|------|--------|----------|
| 吃到食物 | +10 | 主要目标，鼓励吃食物 |
| 撞墙/自撞 | -10 | 惩罚死亡行为 |
| 每走一步 | -0.1 | 鼓励快速找到食物，避免徘徊 |
| 超时（未进食） | -10 | 防止无限循环 |

**为什么奖励这样设计？**
- 吃到食物的正奖励要足够大，让智能体明确目标
- 死亡的负奖励要足够大，让智能体学会避免
- 小步惩罚鼓励高效行动

##### 动作空间说明

```
动作 0: 继续直行
动作 1: 向右转 90 度
动作 2: 向左转 90 度
```

**为什么不是上下左右？**
- 相对方向（直/右/左）比绝对方向更容易学习
- 避免了"反向自杀"的问题（不能直接掉头）

---

### 2. 智能体模块 (`agent.py`)

智能体是做出决策的"大脑"，包含：
- **DQN 网络**：预测每个动作的价值
- **经验回放**：存储和采样历史经验
- **探索策略**：平衡探索和利用

#### DQN 网络结构

```python
class DQN(nn.Module):
    def __init__(self, input_size=11, hidden_size1=256, hidden_size2=128, output_size=3):
        self.fc1 = nn.Linear(input_size, hidden_size1)   # 11 → 256
        self.fc2 = nn.Linear(hidden_size1, hidden_size2) # 256 → 128
        self.fc3 = nn.Linear(hidden_size2, output_size)  # 128 → 3
```

**网络架构图：**
```
输入层 (11) ──→ 隐藏层 1 (256, ReLU) ──→ 隐藏层 2 (128, ReLU) ──→ 输出层 (3)
   │                                           │
   │                                           └─→ Q(直行)
状态向量                                         └─→ Q(右转)
                                                 └─→ Q(左转)
```

| 层 | 输入维度 | 输出维度 | 激活函数 | 作用 |
|----|----------|----------|----------|------|
| fc1 | 11 | 256 | ReLU | 特征提取 |
| fc2 | 256 | 128 | ReLU | 特征压缩 |
| fc3 | 128 | 3 | 无 | Q 值输出 |

#### DQNAgent 核心组件

##### 1. 经验回放缓冲区（Replay Buffer）

```python
class ReplayBuffer:
    def __init__(self, capacity=100000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
```

**为什么需要经验回放？**
- **打破时间相关性**：连续的游戏步骤高度相关，随机采样可以打破这种相关性
- **重用经验**：一条经验可以被多次学习
- **稳定训练**：避免"灾难性遗忘"

**经验元组 `(s, a, r, s', done)` 含义：**
- `s`：当前状态
- `a`：采取的动作
- `r`：获得的奖励
- `s'`：新状态
- `done`：游戏是否结束

##### 2. ε-greedy 探索策略

```python
def select_action(self, state, training=True):
    if training and random.random() < self.epsilon:
        return random.randint(0, 2)  # 探索：随机动作
    
    with torch.no_grad():
        q_values = self.policy_net(state)
        return q_values.argmax().item()  # 利用：最佳动作
```

**ε-greedy 工作原理：**

```
ε = 1.0 (初始)
│
├─ 以概率 ε 选择随机动作（探索）
│  └─ 尝试新策略，发现更好的方法
│
└─ 以概率 1-ε 选择最佳动作（利用）
   └─ 使用当前学到的最好策略

每步后：ε = ε × decay (如 0.995)
最终：ε → ε_min (如 0.01)
```

| 参数 | 默认值 | 作用 | 建议范围 |
|------|--------|------|----------|
| `epsilon` | 1.0 | 初始探索率 | 0.8-1.0 |
| `epsilon_min` | 0.01 | 最小探索率 | 0.01-0.1 |
| `epsilon_decay` | 0.995 | 探索衰减率 | 0.99-0.999 |

##### 3. Double DQN 训练

```python
def train(self):
    # 当前 Q 值
    current_q = self.policy_net(states).gather(1, actions)
    
    # Double DQN: 用 policy_net 选动作，target_net 评估
    with torch.no_grad():
        next_actions = self.policy_net(next_states).argmax(1)
        next_q = self.target_net(next_states).gather(1, next_actions)
        target_q = rewards + gamma * next_q * (1 - dones)
    
    loss = MSE(current_q, target_q)
```

**Double DQN vs 标准 DQN：**

```
标准 DQN:
target_q = r + γ × max(Q_target(s', a))
              │
              └─ 可能高估 Q 值

Double DQN:
target_q = r + γ × Q_target(s', argmax(Q_policy(s', a)))
              │              │
              │              └─ policy_net 选最佳动作
              └─ target_net 评估该动作
```

**为什么用 Double DQN？**
- 减少 Q 值过估计
- 训练更稳定
- 最终性能更好

##### 4. 目标网络（Target Network）

```python
# 初始化时复制
self.target_net.load_state_dict(self.policy_net.state_dict())

# 定期更新（每 1000 步）
if self.steps % self.target_update == 0:
    self.target_net.load_state_dict(self.policy_net.state_dict())
```

**为什么需要目标网络？**
- 提供稳定的训练目标
- 避免"追逐移动目标"问题
- 让训练更稳定

#### 关键参数详解

```python
agent = DQNAgent(
    state_size=11,        # 状态维度
    action_size=3,        # 动作数量
    learning_rate=0.001,  # 学习率
    gamma=0.95,           # 折扣因子
    epsilon=1.0,          # 初始探索率
    epsilon_min=0.01,     # 最小探索率
    epsilon_decay=0.995,  # 探索衰减
    batch_size=64,        # 批次大小
    memory_size=100000,   # 记忆容量
    target_update=1000,   # 目标网络更新间隔
)
```

| 参数 | 默认值 | 作用 | 调优建议 |
|------|--------|------|----------|
| `learning_rate` | 0.001 | 控制学习速度 | 太大不稳定，太小收敛慢 |
| `gamma` | 0.95 | 未来奖励折扣 | 0.9-0.99，越大越重视长期 |
| `batch_size` | 64 | 每次训练样本数 | 32-256，越大越稳定 |
| `memory_size` | 100000 | 经验回放容量 | 50000-200000 |
| `target_update` | 1000 | 目标网络更新步数 | 500-2000 |

---

### 3. 训练脚本 (`train.py`)

训练脚本负责协调整个训练流程。

#### 训练主循环

```python
for episode in range(num_episodes):
    state = env.reset()
    
    for step in range(max_steps):
        # 1. 选择动作
        action = agent.select_action(state)
        
        # 2. 执行动作
        next_state, reward, done, _ = env.step(action)
        
        # 3. 存储经验
        agent.remember(state, action, reward, next_state, done)
        
        # 4. 训练网络
        loss = agent.train()
        
        state = next_state
        if done:
            break
    
    # 记录统计信息
    scores.append(env.score)
```

#### 训练参数

```bash
python train.py --episodes 1000 \
                --batch-size 64 \
                --save-interval 100 \
                --save-dir ./models \
                --device cpu
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--episodes` | 1000 | 训练局数 |
| `--batch-size` | 64 | 批次大小 |
| `--save-interval` | 100 | 保存模型间隔 |
| `--device` | cpu | 运行设备 (cuda/cpu) |

#### 训练技巧

1. **训练时长建议**：
   - 快速测试：100-500 局
   - 基本可用：1000-2000 局
   - 较好性能：5000+ 局

2. **超参数调优顺序**：
   - 先调 `learning_rate`（影响最大）
   - 再调 `gamma`（长期 vs 短期）
   - 最后微调网络结构

3. **训练监控**：
   - 观察 `avg_scores` 是否上升
   - 观察 `loss` 是否稳定下降
   - 观察 `epsilon` 是否合理衰减

---

### 4. 游戏脚本 (`play.py`)

用于观看训练好的 AI 或手动玩游戏。

```bash
# 观看 AI 游戏
python play.py --mode watch --model ./models/best_model.pth

# 手动玩游戏
python play.py --mode play

# 对比 AI 和人类
python play.py --mode compare
```

---

## 🚀 快速开始

### 前置要求

- **Python 版本**: Python 3.8+ (推荐 Python 3.11+)
- **操作系统**: Linux / macOS / Windows
- **硬件要求**: 
  - CPU: 任意现代 CPU
  - GPU: 可选（使用 CUDA 可加速训练）
  - 内存: 至少 4GB RAM

### 1. 克隆项目并进入目录

```bash
cd rl_snake_project
```

### 2. 创建虚拟环境（推荐）

**Linux/macOS:**
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

**Windows:**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

> **注意**: 激活虚拟环境后，命令行前会出现 `(venv)` 标识

### 3. 安装依赖

```bash
# 升级 pip（可选但推荐）
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

**依赖包说明：**

| 包名 | 版本要求 | 用途 |
|------|----------|------|
| numpy | >=1.21.0 | 数值计算、数组操作 |
| torch | >=1.9.0 | 深度学习框架（PyTorch） |
| pygame | >=2.1.0 | 游戏渲染和图形界面 |
| matplotlib | >=3.4.0 | 训练曲线可视化 |

**验证安装：**
```bash
python -c "import numpy, torch, pygame, matplotlib; print('所有依赖安装成功！')"
```

### 4. 开始训练

#### 基础训练（推荐新手）

```bash
# 训练 1000 局，使用 CPU
python train.py --episodes 1000 --batch-size 64 --device cpu
```

#### 快速测试（验证环境）

```bash
# 只训练 100 局，快速验证代码是否正常运行
python train.py --episodes 100
```

#### 完整训练（追求更好效果）

```bash
# 训练 5000 局，每 100 局保存一次模型
python train.py --episodes 5000 --save-interval 100
```

#### 使用 GPU 加速训练

```bash
# 如果有 NVIDIA GPU 且安装了 CUDA 版本的 PyTorch
python train.py --episodes 2000 --device cuda
```

#### 训练参数详解

```bash
python train.py \
    --episodes 1000 \          # 训练局数（默认 1000）
    --batch-size 64 \          # 批次大小（默认 64，范围 32-256）
    --save-interval 100 \      # 每 N 局保存一次模型（默认 100）
    --save-dir ./models \      # 模型保存目录（默认 ./models）
    --device cpu \             # 运行设备：cpu 或 cuda（默认 cpu）
    --render-interval 0        # 每 N 局渲染一次，0 表示不渲染（默认 0）
```

**训练输出示例：**
```
Starting training for 1000 episodes...
Device: cpu
State size: 11, Action size: 3
------------------------------------------------------------
Episode    1 | Score:   0 | Avg Score (100): 0.00 | Epsilon: 0.9950 | Loss: 0.0012
Episode   10 | Score:   2 | Avg Score (100): 0.80 | Epsilon: 0.9511 | Loss: 0.0034
Episode  100 | Score:  15 | Avg Score (100): 8.50 | Epsilon: 0.6058 | Loss: 0.0156
...
------------------------------------------------------------
Training completed!
Best score: 45 (Episode 856)
Final average score (100 episodes): 32.40
Models saved to: ./models
```

### 5. 查看训练结果

训练完成后，`./models/` 目录会生成以下文件：

```
models/
├── best_model.pth           # 最佳模型（最高分）
├── final_model.pth          # 最终模型（最后一局）
├── model_episode_100.pth    # 第 100 局的模型（如果 save-interval=100）
├── model_episode_200.pth    # 第 200 局的模型
├── ...
└── training_curves.png      # 训练曲线图
```

**查看训练曲线：**
```bash
# Linux/macOS
open models/training_curves.png

# Windows
start models/training_curves.png
```

### 6. 观看 AI 玩游戏

#### 观看训练好的 AI

```bash
# 使用最佳模型
python play.py --mode watch --model ./models/best_model.pth

# 自定义速度（数字越小越快）
python play.py --mode watch --model ./models/best_model.pth --speed 50

# 使用最终模型
python play.py --mode watch --model ./models/final_model.pth
```

#### 手动玩游戏

```bash
# 以人类身份玩游戏
python play.py --mode play

# 调整游戏速度
python play.py --mode play --speed 100
```

#### 对比模式（AI vs 人类）

```bash
# 先让 AI 玩一局，然后你玩一局
python play.py --mode compare --model ./models/best_model.pth
```

**控制说明：**
- **方向键** ↑ ↓ ← → : 控制蛇的移动方向
- **ESC** : 退出游戏
- **R** : 重新开始游戏

### 7. 🌐 Web 可视化（推荐用于 VSCode 远程环境）

如果你在使用 **VSCode Remote**、**SSH 远程服务器**或**无图形界面环境**，可以使用基于浏览器的可视化界面！

#### 启动 Web 服务

```bash
# 基本用法
python play_web.py --model ./models/best_model.pth

# 自定义端口和速度
python play_web.py --model ./models/best_model.pth --port 8080 --speed 50

# 允许外部访问（默认已启用）
python play_web.py --model ./models/best_model.pth --host 0.0.0.0 --port 5000
```

#### 在浏览器中观看

启动后，打开浏览器访问：
- **本地**: http://localhost:5000
- **远程**: http://<服务器IP>:5000

**功能特性：**
- ✅ 实时显示游戏画面
- ✅ 显示当前分数、最佳分数、平均分数
- ✅ 显示训练局数统计
- ✅ 暂停/继续按钮
- ✅ 重置统计按钮
- ✅ 自动刷新（100ms）
- ✅ 美观的渐变 UI 设计

**Web 参数详解：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--model` | ./models/best_model.pth | 模型文件路径 |
| `--speed` | 100 | 游戏速度（毫秒/步），越小越快 |
| `--port` | 5000 | Web 服务器端口 |
| `--host` | 0.0.0.0 | 监听地址（0.0.0.0 表示所有接口） |

**使用场景：**
1. **VSCode Remote SSH**: 在远程服务器上运行，本地浏览器访问
2. **云服务器**: 部署后通过公网 IP 访问
3. **Docker 容器**: 映射端口后在宿主机浏览器访问
4. **无头服务器**: 无需图形界面，只要有浏览器即可

**示例输出：**
```
============================================================
🐍 Snake AI - Web Visualization
============================================================
Model: ./models/best_model.pth
Speed: 100ms per step
Server: http://0.0.0.0:5000
============================================================

📺 Open the URL above in your browser to watch!
Press Ctrl+C to stop the server

 * Serving Flask app 'play_web'
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.100:5000
```

---

## 🔍 代码模块详解

### 1. 环境模块 (`env.py`)

环境是强化学习中最重要的组成部分之一。它定义了：
- 游戏如何运行
- 状态如何表示
- 奖励如何计算

#### 核心类：`SnakeGameNoRender`

```python
class SnakeGameNoRender:
    """无渲染的贪吃蛇环境（用于快速训练）"""
```

#### 关键方法解析

##### `__init__()` - 初始化
```python
def __init__(self, width=640, height=480, block_size=20, speed=100):
    self.grid_width = width // block_size   # 网格宽度 = 32
    self.grid_height = height // block_size # 网格高度 = 24
```

| 参数 | 默认值 | 作用 | 可调范围 |
|------|--------|------|----------|
| `width` | 640 | 窗口宽度（像素） | 320-1280 |
| `height` | 480 | 窗口高度（像素） | 240-960 |
| `block_size` | 20 | 每个格子大小 | 10-40 |
| `speed` | 100 | 游戏速度（ms/帧） | 10-200 |

##### `reset()` - 重置环境
```python
def reset(self):
    # 蛇从中心开始，长度为 3
    self.snake = [Point(cx, cy), Point(cx-1, cy), Point(cx-2, cy)]
    self.direction = Direction.RIGHT
    self.score = 0
    self._place_food()
    return self._get_state()
```

**为什么要重置？**
- 每局游戏结束后需要重新开始
- 训练时需要大量独立的游戏样本

##### `_get_state()` - 获取状态（核心！）
```python
def _get_state(self):
    state = [
        # 危险检测（3 个方向）
        danger_straight,  # 前方是否有危险
        danger_right,     # 右侧是否有危险
        danger_left,      # 左侧是否有危险
        
        # 当前方向（one-hot 编码）
        dir_left, dir_right, dir_up, dir_down,
        
        # 食物相对位置
        food_up, food_down, food_left, food_right
    ]
    return np.array(state, dtype=np.float32)
```

**状态向量详解（11 维）：**

```
状态 = [危险直，危险右，危险左，方向左，方向右，方向上，方向下，食物上，食物下，食物左，食物右]
        │         │         │         │              │         │              │
        └─ 3 维 ──┘         └──── 4 维 ────┘         └──── 4 维 ────┘
           │                     │                      │
       危险检测              方向编码              食物位置
```

**为什么这样设计状态？**
- **危险检测**：帮助蛇避免死亡（最重要！）
- **方向编码**：让蛇知道当前朝向
- **食物位置**：引导蛇向食物移动

##### `step()` - 执行动作
```python
def step(self, action):
    """
    执行一步动作
    
    参数:
        action: 0=直行，1=右转，2=左转
    
    返回:
        (state, reward, done, info)
    """
    # 1. 更新方向
    # 2. 移动蛇头
    # 3. 检测碰撞
    # 4. 检查是否吃到食物
    # 5. 返回新状态和奖励
```

**奖励设计详解：**

| 情况 | 奖励值 | 设计原因 |
|------|--------|----------|
| 吃到食物 | +10 | 主要目标，鼓励吃食物 |
| 撞墙/自撞 | -10 | 惩罚死亡行为 |
| 每走一步 | -0.1 | 鼓励快速找到食物，避免徘徊 |
| 超时（未进食） | -10 | 防止无限循环 |

**为什么奖励这样设计？**
- 吃到食物的正奖励要足够大，让智能体明确目标
- 死亡的负奖励要足够大，让智能体学会避免
- 小步惩罚鼓励高效行动

##### 动作空间说明

```
动作 0: 继续直行
动作 1: 向右转 90 度
动作 2: 向左转 90 度
```

**为什么不是上下左右？**
- 相对方向（直/右/左）比绝对方向更容易学习
- 避免了"反向自杀"的问题（不能直接掉头）

---

### 2. 智能体模块 (`agent.py`)

智能体是做出决策的"大脑"，包含：
- **DQN 网络**：预测每个动作的价值
- **经验回放**：存储和采样历史经验
- **探索策略**：平衡探索和利用

#### DQN 网络结构

```python
class DQN(nn.Module):
    def __init__(self, input_size=11, hidden_size1=256, hidden_size2=128, output_size=3):
        self.fc1 = nn.Linear(input_size, hidden_size1)   # 11 → 256
        self.fc2 = nn.Linear(hidden_size1, hidden_size2) # 256 → 128
        self.fc3 = nn.Linear(hidden_size2, output_size)  # 128 → 3
```

**网络架构图：**
```
输入层 (11) ──→ 隐藏层 1 (256, ReLU) ──→ 隐藏层 2 (128, ReLU) ──→ 输出层 (3)
   │                                           │
   │                                           └─→ Q(直行)
状态向量                                         └─→ Q(右转)
                                                 └─→ Q(左转)
```

| 层 | 输入维度 | 输出维度 | 激活函数 | 作用 |
|----|----------|----------|----------|------|
| fc1 | 11 | 256 | ReLU | 特征提取 |
| fc2 | 256 | 128 | ReLU | 特征压缩 |
| fc3 | 128 | 3 | 无 | Q 值输出 |

#### DQNAgent 核心组件

##### 1. 经验回放缓冲区（Replay Buffer）

```python
class ReplayBuffer:
    def __init__(self, capacity=100000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
```

**为什么需要经验回放？**
- **打破时间相关性**：连续的游戏步骤高度相关，随机采样可以打破这种相关性
- **重用经验**：一条经验可以被多次学习
- **稳定训练**：避免"灾难性遗忘"

**经验元组 `(s, a, r, s', done)` 含义：**
- `s`：当前状态
- `a`：采取的动作
- `r`：获得的奖励
- `s'`：新状态
- `done`：游戏是否结束

##### 2. ε-greedy 探索策略

```python
def select_action(self, state, training=True):
    if training and random.random() < self.epsilon:
        return random.randint(0, 2)  # 探索：随机动作
    
    with torch.no_grad():
        q_values = self.policy_net(state)
        return q_values.argmax().item()  # 利用：最佳动作
```

**ε-greedy 工作原理：**

```
ε = 1.0 (初始)
│
├─ 以概率 ε 选择随机动作（探索）
│  └─ 尝试新策略，发现更好的方法
│
└─ 以概率 1-ε 选择最佳动作（利用）
   └─ 使用当前学到的最好策略

每步后：ε = ε × decay (如 0.995)
最终：ε → ε_min (如 0.01)
```

| 参数 | 默认值 | 作用 | 建议范围 |
|------|--------|------|----------|
| `epsilon` | 1.0 | 初始探索率 | 0.8-1.0 |
| `epsilon_min` | 0.01 | 最小探索率 | 0.01-0.1 |
| `epsilon_decay` | 0.995 | 探索衰减率 | 0.99-0.999 |

##### 3. Double DQN 训练

```python
def train(self):
    # 当前 Q 值
    current_q = self.policy_net(states).gather(1, actions)
    
    # Double DQN: 用 policy_net 选动作，target_net 评估
    with torch.no_grad():
        next_actions = self.policy_net(next_states).argmax(1)
        next_q = self.target_net(next_states).gather(1, next_actions)
        target_q = rewards + gamma * next_q * (1 - dones)
    
    loss = MSE(current_q, target_q)
```

**Double DQN vs 标准 DQN：**

```
标准 DQN:
target_q = r + γ × max(Q_target(s', a))
              │
              └─ 可能高估 Q 值

Double DQN:
target_q = r + γ × Q_target(s', argmax(Q_policy(s', a)))
              │              │
              │              └─ policy_net 选最佳动作
              └─ target_net 评估该动作
```

**为什么用 Double DQN？**
- 减少 Q 值过估计
- 训练更稳定
- 最终性能更好

##### 4. 目标网络（Target Network）

```python
# 初始化时复制
self.target_net.load_state_dict(self.policy_net.state_dict())

# 定期更新（每 1000 步）
if self.steps % self.target_update == 0:
    self.target_net.load_state_dict(self.policy_net.state_dict())
```

**为什么需要目标网络？**
- 提供稳定的训练目标
- 避免"追逐移动目标"问题
- 让训练更稳定

#### 关键参数详解

```python
agent = DQNAgent(
    state_size=11,        # 状态维度
    action_size=3,        # 动作数量
    learning_rate=0.001,  # 学习率
    gamma=0.95,           # 折扣因子
    epsilon=1.0,          # 初始探索率
    epsilon_min=0.01,     # 最小探索率
    epsilon_decay=0.995,  # 探索衰减
    batch_size=64,        # 批次大小
    memory_size=100000,   # 记忆容量
    target_update=1000,   # 目标网络更新间隔
)
```

| 参数 | 默认值 | 作用 | 调优建议 |
|------|--------|------|----------|
| `learning_rate` | 0.001 | 控制学习速度 | 太大不稳定，太小收敛慢 |
| `gamma` | 0.95 | 未来奖励折扣 | 0.9-0.99，越大越重视长期 |
| `batch_size` | 64 | 每次训练样本数 | 32-256，越大越稳定 |
| `memory_size` | 100000 | 经验回放容量 | 50000-200000 |
| `target_update` | 1000 | 目标网络更新步数 | 500-2000 |

---

### 3. 训练脚本 (`train.py`)

训练脚本负责协调整个训练流程。

#### 训练主循环

```python
for episode in range(num_episodes):
    state = env.reset()
    
    for step in range(max_steps):
        # 1. 选择动作
        action = agent.select_action(state)
        
        # 2. 执行动作
        next_state, reward, done, _ = env.step(action)
        
        # 3. 存储经验
        agent.remember(state, action, reward, next_state, done)
        
        # 4. 训练网络
        loss = agent.train()
        
        state = next_state
        if done:
            break
    
    # 记录统计信息
    scores.append(env.score)
```

#### 训练参数

```bash
python train.py --episodes 1000 \
                --batch-size 64 \
                --save-interval 100 \
                --save-dir ./models \
                --device cpu
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--episodes` | 1000 | 训练局数 |
| `--batch-size` | 64 | 批次大小 |
| `--save-interval` | 100 | 保存模型间隔 |
| `--device` | cpu | 运行设备 (cuda/cpu) |

#### 训练技巧

1. **训练时长建议**：
   - 快速测试：100-500 局
   - 基本可用：1000-2000 局
   - 较好性能：5000+ 局

2. **超参数调优顺序**：
   - 先调 `learning_rate`（影响最大）
   - 再调 `gamma`（长期 vs 短期）
   - 最后微调网络结构

3. **训练监控**：
   - 观察 `avg_scores` 是否上升
   - 观察 `loss` 是否稳定下降
   - 观察 `epsilon` 是否合理衰减

---

### 4. 游戏脚本 (`play.py`)

用于观看训练好的 AI 或手动玩游戏。

```bash
# 观看 AI 游戏
python play.py --mode watch --model ./models/best_model.pth

# 手动玩游戏
python play.py --mode play

# 对比 AI 和人类
python play.py --mode compare
```

---

## 📊 训练效果预期

| 训练局数 | 平均分数 | 表现描述 |
|----------|----------|----------|
| 100 | 5-10 | 随机移动，偶尔吃到食物 |
| 500 | 10-20 | 学会避免 immediate 危险 |
| 1000 | 20-40 | 基本会找食物，偶尔自撞 |
| 5000 | 40-80 | 熟练玩家水平 |
| 10000+ | 80+ | 高手水平，能规划路径 |

---

## 🔧 举一反三：如何修改和扩展

### 1. 修改游戏难度

```python
# 在 env.py 中修改
class SnakeGameNoRender:
    def __init__(self, width=640, height=480, block_size=20):
        # 更大的网格 = 更难
        self.grid_width = width // block_size  # 改为 40
        self.grid_height = height // block_size # 改为 30
```

### 2. 修改奖励设计

```python
# 在 env.py 的 step() 方法中
if new_head == self.food:
    reward = 10  # 改为 20 鼓励吃食物
    # 或者添加额外奖励
    reward += len(self.snake) * 0.1  # 蛇越长奖励越多
```

### 3. 修改网络结构

```python
# 在 agent.py 中
class DQN(nn.Module):
    def __init__(self, input_size=11, hidden_size1=512, hidden_size2=256, output_size=3):
        # 更大的网络 = 更强表达能力，但需要更多训练
```

### 4. 添加新功能

**想法 1：添加障碍物**
```python
# 在 env.py 中添加
self.obstacles = [Point(10, 10), Point(10, 11), ...]

def _is_collision(self, point):
    # 添加障碍物检测
    if point in self.obstacles:
        return True
```

**想法 2：多食物系统**
```python
# 同时存在多个食物，不同颜色不同分值
self.foods = [(Point(5,5), 10), (Point(20,20), 20), ...]
```

**想法 3：改变状态表示**
```python
# 使用图像作为输入（CNN）
def _get_state(self):
    # 返回整个游戏画面的像素
    return self.render_to_array()
```

---

## 📖 核心概念总结

### 强化学习 vs 其他机器学习

| 特性 | 强化学习 | 监督学习 | 无监督学习 |
|------|----------|----------|------------|
| 数据 | 交互产生 | 标注数据 | 无标注数据 |
| 反馈 | 延迟奖励 | 即时标签 | 无反馈 |
| 目标 | 最大化累积奖励 | 最小化预测误差 | 发现结构 |
| 应用 | 游戏、机器人 | 分类、回归 | 聚类、降维 |

### DQN 算法要点

1. **Q-Learning 核心**：学习 Q(s,a) = 状态 s 下动作 a 的预期累积奖励
2. **深度网络**：用神经网络近似 Q 函数
3. **经验回放**：打破时间相关性
4. **目标网络**：提供稳定训练目标
5. **ε-greedy**：平衡探索和利用

### 贝尔曼方程（理论核心）

```
Q(s,a) = r + γ × max(Q(s',a'))

其中：
- Q(s,a): 当前 Q 值
- r: 即时奖励
- γ: 折扣因子
- max(Q(s',a')): 下一状态的最大 Q 值
```

---

## 🐛 常见问题与故障排除

### Web 可视化问题

**Q: 如何在 VSCode Remote 中使用 Web 可视化？**

A: 
1. 在远程服务器上运行：
   ```bash
   python play_web.py --model ./models/best_model.pth --port 5000
   ```
2. VSCode 会自动转发端口，在本地浏览器打开：http://localhost:5000
3. 如果自动转发失败，手动配置端口转发：
   - 按 `Ctrl+Shift+P`
   - 输入 "Remote-Ports: Forward Port"
   - 输入端口号 5000

**Q: 无法访问 Web 界面？**

A:
1. 检查防火墙是否开放端口：
   ```bash
   sudo ufw allow 5000
   ```
2. 确认服务正在运行：
   ```bash
   ps aux | grep play_web
   ```
3. 检查端口占用：
   ```bash
   netstat -tlnp | grep 5000
   ```
4. 尝试更换端口：
   ```bash
   python play_web.py --port 8080
   ```

**Q: Web 界面加载但画面不更新？**

A:
1. 检查浏览器控制台是否有错误（F12）
2. 确认模型文件路径正确
3. 降低速度参数：`--speed 200`
4. 刷新页面重试

### 安装问题

**Q: pip install 失败或很慢？**

A: 使用国内镜像源加速下载：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Q: PyTorch CUDA 版本安装问题？**

A: 访问 [PyTorch 官网](https://pytorch.org/) 获取正确的安装命令：
```bash
# CPU 版本
pip install torch torchvision torchaudio

# CUDA 11.8 版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Q: pygame 导入警告 AVX2？**

A: 这是性能提示，不影响运行。如需消除：
```bash
export PYGAME_DETECT_AVX2=1
python train.py
```

### 训练问题

**Q: 训练很久分数不涨？**

A: 尝试以下方法：
1. 检查奖励设计是否合理
2. 调整学习率（尝试 0.0005 或 0.002）
3. 增加训练局数（至少 1000 局）
4. 减小 epsilon_decay（如改为 0.999）让探索更久

**Q: AI 总是撞墙或自撞？**

A: 
1. 增加死亡惩罚（修改 `env.py` 中的 reward 为 -20）
2. 检查状态表示中危险检测是否正确
3. 确保训练了足够多的局数（至少 500 局）

**Q: 训练不稳定，分数波动大？**

A:
1. 降低学习率（从 0.001 改为 0.0005）
2. 增加批次大小（从 64 改为 128）
3. 增加目标网络更新间隔（从 1000 改为 2000）
4. 增加经验回放容量（从 100000 改为 200000）

**Q: 内存不足（OOM）？**

A:
1. 减小 `memory_size`（从 100000 改为 50000）
2. 减小网络层大小（修改 `agent.py` 中的 hidden_size）
3. 减小 `batch_size`（从 64 改为 32）
4. 关闭其他占用内存的程序

**Q: Permission denied 错误？**

A: 权限问题，修复方法：
```bash
# Linux/macOS
chmod -R u+rwX /path/to/rl_snake_project
chown -R $USER:$USER /path/to/rl_snake_project

# Windows（以管理员身份运行）
icacls . /grant %USERNAME%:F /T
```

### 运行问题

**Q: 游戏窗口打不开或闪退？**

A:
1. 确保安装了 pygame：`pip install pygame`
2. 检查显示服务器（Linux 下需要 X11）
3. 尝试无渲染模式训练：`python train.py --render-interval 0`

**Q: 训练速度太慢？**

A:
1. 使用 GPU：`python train.py --device cuda`
2. 减小网格大小（修改 `env.py` 中的 block_size）
3. 减小 max_steps_per_episode（防止单局过长）
4. 使用更快的 Python 版本（3.10+）

**Q: 模型文件太大？**

A: 正常现象，DQN 模型通常几百 KB 到几 MB。如需减小：
1. 减小网络层大小
2. 使用模型压缩技术
3. 只保存 policy_net（不保存 optimizer）

### 性能调优建议

**快速提升性能的参数组合：**

```bash
# 组合 1：稳定训练
python train.py --episodes 3000 --batch-size 128 --learning-rate 0.0005

# 组合 2：快速收敛
python train.py --episodes 2000 --batch-size 64 --epsilon-decay 0.999

# 组合 3：GPU 加速
python train.py --episodes 5000 --batch-size 256 --device cuda
```

**超参数调优优先级：**
1. ⭐⭐⭐ learning_rate（影响最大）
2. ⭐⭐⭐ gamma（长期 vs 短期奖励）
3. ⭐⭐ batch_size（稳定性）
4. ⭐⭐ epsilon_decay（探索策略）
5. ⭐ network architecture（网络结构）

---

## 📊 训练效果预期

| 训练局数 | 平均分数 | 表现描述 | 预计时间（CPU） |
|----------|----------|----------|----------------|
| 100 | 5-10 | 随机移动，偶尔吃到食物 | ~1 分钟 |
| 500 | 10-20 | 学会避免 immediate 危险 | ~5 分钟 |
| 1000 | 20-40 | 基本会找食物，偶尔自撞 | ~10 分钟 |
| 5000 | 40-80 | 熟练玩家水平 | ~1 小时 |
| 10000+ | 80+ | 高手水平，能规划路径 | ~2-3 小时 |

> **注意**: 训练时间因硬件配置而异，GPU 可加速 5-10 倍

---

## 📚 进一步学习

### 推荐资源

1. **论文**：
   - [Playing Atari with Deep Reinforcement Learning](https://www.nature.com/articles/nature14236) (DQN 原始论文)
   - [Double DQN](https://arxiv.org/abs/1509.06461)

2. **课程**：
   - CS285: Deep Reinforcement Learning (UC Berkeley)
   - Reinforcement Learning Specialization (Coursera)

3. **书籍**：
   - 《Reinforcement Learning: An Introduction》(Sutton & Barto)
   - 《深度强化学习》(李宏毅)

### 进阶项目建议

1. **Dueling DQN**：分离价值和优势流
2. **Prioritized Replay**：优先采样重要经验
3. **A3C**：异步优势演员 - 评论家
4. **PPO**：近端策略优化
5. **SAC**：软演员 - 评论家

---

## 📄 许可证

本项目仅供学习使用。

---

**祝你强化学习之旅愉快！🎮🤖**

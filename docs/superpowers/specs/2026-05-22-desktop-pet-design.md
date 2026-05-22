# 罗小黑桌面宠物 — 设计规格文档

## 概述

基于 Python + PyQt6 + QML 的 macOS 桌面宠物应用。程序化绘制罗小黑形象，支持自由活动与互动反馈，打包为独立 `.app` 分发。

## 技术栈

| 层 | 技术 |
|----|------|
| 语言 | Python 3.11+ |
| GUI 框架 | PyQt6 |
| 渲染引擎 | QML Canvas API |
| 事件系统 | Qt 鼠标事件 (hover/click/drag) |
| 打包 | PyInstaller → macOS .app |

## 项目结构

```
desktop-pet/
├── main.py                 # 应用入口，QGuiApplication + 窗口创建
├── pet.py                  # 宠物状态机 (FSA)
├── renderer.py             # QML 引擎桥接，属性同步
├── interaction.py          # 鼠标事件处理
├── speech_bubble.py        # 对话气泡组件
├── resources/
│   └── ui/
│       └── PetPanel.qml    # QML 主场景（Canvas 绘制 + 动画）
├── requirements.txt        # PyQt6, PyInstaller
└── build.spec              # PyInstaller 配置
```

## 窗口系统

- 窗口引擎：QQuickWidget (嵌入 QML 场景)
- 窗口大小：200 × 200 px
- 窗口标记：`FramelessWindowHint | WindowStaysOnTopHint | SkipTaskbar`
- macOS 透明：`setAttribute(Qt.WA_TranslucentBackground)`
- 默认位置：屏幕右下角
- 鼠标穿透：默认关闭；仅在精灵区域响应事件

## 宠物状态机

```
              ┌─────────┐
      ───────→│  idle   │←──────────────
     │        └────┬────┘               │
单击         │         双击       鼠标移动(chase)
     │        ▼          │              │
     │   ┌────────┐     │              │
     └───│  jump  │─────┘    ┌─────────┘
         └────────┘          ▼
                        ┌────────┐
                        │ chase  │
                        └───┬────┘
                            │
                            ▼
                        ┌────────┐    随机触发
                        │ walk   │←────────────
                        └───┬────┘            │
                            │                  │
                            ▼                  │
                        ┌────────┐    超时    │
                   ┌───→│ idle   │────────────┘
                   │    └────────┘
             15s 无交互    │
                   │      ▼
                   │  ┌────────┐
                   └──│ sleep  │──(点击/鼠标移动)→ idle
                      └────────┘

   鼠标按住拖拽
         │
         ▼
    ┌────────┐
    │  drag  │──(松开)→ idle / hang
    └────────┘

   拖到屏幕边缘松开
         │
         ▼
    ┌────────┐
    │  hang  │──(拖回)→ idle
    └────────┘
```

### 状态定义

| 状态 | 持续方式 | 默认持续时间 |
|------|---------|-------------|
| idle | 无限（直到触发切换） | — |
| walk | 计时退出 | 2000-5000ms 随机 |
| jump | 动画结束退出 | 600ms |
| sleep | 外部事件打断 | 无限 |
| chase | 外部事件打断 | 无限（鼠标远离则 idle） |
| drag | 外部事件打断 | 无限 |
| hang | 计时退出 | 2000ms |

## 程序化绘制方案 (QML Canvas)

### 罗小黑身体结构

全部使用 QML Canvas API 逐帧绘制，黑色 + 黄色为核心配色：

| 部件 | 绘制方式 | 颜色 |
|------|---------|------|
| 头部 | 黑色正圆 | `#1a1a1a` |
| 身体 | 黑色椭圆 | `#1a1a1a` |
| 耳朵 | 等腰三角形 x2 | `#1a1a1a` |
| 内耳 | 小三角形 x2 | `#2a2a2a` |
| 眼睛 | 大正圆 x2 | `#ffdd44` |
| 瞳孔 | 小正圆 x2 | `#111111` |
| 高光 | 小正圆 x2 | `#ffffff` |
| 腿 | 小椭圆 x4 | `#1a1a1a` |
| 尾巴 | 三次贝塞尔曲线 | `#1a1a1a` |

### 动画系统

每帧全部重绘，动画参数插值实现：

- **idle**：bodyY 正弦浮动 (±3px, 2s 周期)，tailAngle 摆动 (±15°, 1.5s 周期)，随机眨眼 (每 3-5s)
- **walk**：水平位移 + bodyY 弹动，腿交替旋转，尾巴高频摆动
- **jump**：bodyY 抛物线 (0→-40→0)，眼睛缩放 (瞳孔缩小→放大→正常)
- **sleep**：bodyY 下沉 5px，眼睛闭合 (drawArc)，浮 Zzz 文字粒子
- **chase**：水平朝向鼠标移动，身体前倾 5°，腿快速交替
- **drag**：body 悬空，腿随机摆动，眼睛瞪大 120%
- **hang**：body 半透明超出屏幕边缘合成，手足无力下垂

帧率：**30fps**

## 交互反馈

| 操作 | 检测方式 | 宠物反应 | 气泡台词（随机） |
|------|---------|---------|----------------|
| 左键单击 | `mousePressEvent` + 碰撞检测 | jump | "呜？", "干嘛~", "嗯？" |
| 左键双击 | 两次单击间隔 < 400ms | 高跳 + 开心 | "主人！❤️", "嘿！" |
| 鼠标靠近 | `mouseMoveEvent` + 距离 < 100px | chase | — |
| 按住拖拽 | `mousePressEvent` + `mouseMoveEvent` | drag | "诶诶诶！", "放开我！" |
| 拖到边缘松开 | 位置 < 边界 20px | hang | "救命！", "好高！" |
| 15s 无交互 | QTimer idle 检测 | sleep | "Zzz..." |
| 睡梦中点击 | mousePressEvent + state=sleep | jump + 惊醒 | "！？", "吓我一跳！" |

## 包部署

- 打包工具：PyInstaller
- 模式：`--onefile --windowed`
- 输出：`罗小黑桌宠.app`
- macOS 最低版本：macOS 11 (Big Sur)
- 可选后处理：codesign 签名 + notarize 公证

## 非功能需求

- 内存占用：< 80MB
- CPU：idle 时 < 3%，动画时 < 8%
- 启动时间：< 2s
- 窗口应跟随 Spaces/桌面切换
- 全屏应用上自动隐藏（后续优化项）

## 后续可选扩展（当前不纳入）

- 多屏跟随
- 全屏检测自动隐藏
- 右键菜单（设置/退出）
- 快捷键全局控制
- 托盘图标

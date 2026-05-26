# macOS 透明窗口渲染残留 Bug

## 现象

点击切换宠物状态时，第一个状态（待机）的图片轮廓始终残留在窗口背景上。

## 原因

**Qt (6.7.1) 在 macOS 上的已知 Bug** — 使用 Metal 渲染后端时，`QQuickWidget` + `WA_TranslucentBackground` 透明窗口的子缓冲区不会在每帧之间正确清除。首次渲染的像素残留在窗口缓冲区中。

相关讨论：
- https://forum.qt.io/topic/143286
- https://bugreports.qt.io （QTBUG-12639, QTBUG-28531）
- https://stackoverflow.com/questions/78005539

## 已尝试的修复方案

| 方案 | 结果 |
|------|------|
| `quickWindow().setColor(transparent)` 在 `show()` 后调用 | 无效 |
| 同上，延迟 100ms 后调用 | 无效 |
| 强制 OpenGL 后端 (`QQuickWindow.setSceneGraphBackend("opengl")`) | 插件缺失，无法使用 |
| 设置 `QSurfaceFormat` alpha 通道 (8bit) | 无效 |
| `WA_NativeWindow` 在 QQuickWidget 上 | QQuickWidget 不支持 |
| QML 销毁重建 AnimatedImage (Loader active toggle) | 无效（说明不是图片缓存问题） |
| 三个独立 AnimatedImage，按状态切换 visible | 无效 |
| `clip: true` 在根 Item | 无效 |
| 三个方案组合 | 均无效 |

## 已知可工作的方案

- **软件渲染**: `QQuickWindow.setSceneGraphBackend("software")` — 能解决问题但性能差（CPU 渲染）
- **改用 QQuickWindow**（而非 QQuickWidget）— 需要重构窗口架构

## GIF 透明度检查

三个 GIF 均为 GIF89a 格式，使用调色板索引 0 作为透明色，69-74% 像素透明，无不透明近白像素。GIF 本身渲染正确，问题在 Qt/macOS 的窗口缓冲区管理。

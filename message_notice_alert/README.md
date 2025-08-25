# Windows 10 侧边栏通知程序

这是一个使用 Python 创建的 Windows 10 侧边栏通知程序，可以显示系统级的 toast 通知。

## 功能特点

- 显示 Windows 10 原生样式的侧边栏通知
- 支持自定义通知标题、内容和显示时间
- 支持命令行参数调用
- 提供演示模式显示多条通知
- **配置文件支持** - 自动保存和加载用户设置
- **配置管理工具** - 方便的配置管理界面
- **🆕 持续运行服务** - 带系统托盘图标的后台服务
- **🆕 系统托盘集成** - 右下角托盘图标，右键菜单操作
- **🆕 浮动时间窗口** - 实时显示当前时间的小窗口
- **🆕 持续提示功能** - 无时间限制的持续显示提示窗口
- **🆕 服务统计** - 显示运行状态和通知统计
- 跨平台兼容（主要针对 Windows 10/11）

## 安装依赖

### 方法1：使用批处理文件（推荐）
双击运行 `install_requirements.bat` 文件

### 方法2：手动安装
```bash
pip install plyer pystray Pillow
```

### 方法3：使用 requirements.txt
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用
```bash
# 显示默认通知（使用配置文件中的设置）
python windows_notification.py

# 自定义标题和内容
python windows_notification.py -t "我的标题" -m "我的通知内容"

# 设置显示时间（秒）
python windows_notification.py --timeout 15

# 设置应用名称
python windows_notification.py --app-name "我的应用"
```

### 配置文件管理
```bash
# 显示当前配置
python windows_notification.py --show-config

# 设置默认超时时间并保存
python windows_notification.py --set-timeout 15

# 保存当前参数为默认配置
python windows_notification.py -t "我的标题" -m "我的消息" --timeout 20 --save-config

# 使用配置管理工具
python config_manager.py --interactive

# 或者运行批处理文件进行配置
config_setup.bat
```

### 🆕 持续运行服务
```bash
# 启动带系统托盘图标的持续运行服务
python notification_service.py

# 或者使用批处理文件启动
start_service.bat

# 后台启动（最小化窗口）
start_service_background.bat
```

**系统托盘功能：**
- 使用 `logo.png` 文件作为托盘图标（如果文件存在）
- 右键点击托盘图标可以：
  - 发送测试通知
  - 发送自定义通知
  - 持续提示（子菜单）
    - 显示持续提示
    - 自定义持续提示
    - 关闭所有持续提示
  - 查看当前配置
  - 查看服务统计
  - 打开配置管理器
  - 退出服务

**🆕 浮动时间窗口功能：**
- 实时显示当前时间（时:分:秒格式）
- 自动定位在屏幕顶部中央
- 半透明窗口，始终置顶显示
- 可以拖动窗口到任意位置
- 持续显示，不会隐藏

**🆕 持续提示功能：**
- 创建无时间限制的提示窗口
- 红色背景，醒目显示重要信息
- 自动定位在屏幕中央偏上位置
- 可以拖动窗口到任意位置
- 支持多个持续提示同时显示
- 手动关闭或通过托盘菜单统一关闭
- 支持自定义标题和内容

**自定义托盘图标：**
- 将你的图标文件命名为 `logo.png` 并放在程序目录中
- 推荐尺寸：64x64 到 128x128 像素
- 支持 PNG 格式（推荐透明背景）
- 如果没有 logo.png 文件，程序会使用默认生成的图标

### 演示模式
```bash
# 运行演示模式，显示多条示例通知
python windows_notification.py --demo
```

### 完整参数示例
```bash
python windows_notification.py -t "重要提醒" -m "您有新的邮件需要查看" --timeout 20 --app-name "邮件客户端"
```

## 命令行参数

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--title` | `-t` | 配置文件中的值 | 通知标题 |
| `--message` | `-m` | 配置文件中的值 | 通知内容 |
| `--timeout` | - | 配置文件中的值 | 通知显示时间（秒） |
| `--app-name` | - | 配置文件中的值 | 应用程序名称 |
| `--demo` | - | False | 运行演示模式 |
| `--save-config` | - | False | 保存当前参数到配置文件 |
| `--show-config` | - | False | 显示当前配置 |
| `--set-timeout` | - | - | 设置默认超时时间并保存 |

## 配置文件

程序会自动创建 `notification_config.json` 配置文件来保存用户设置：

```json
{
    "timeout": 10,
    "app_name": "Python通知应用",
    "title": "Python通知",
    "message": "这是一条测试通知"
}
```

### 配置管理工具

使用 `config_manager.py` 进行配置管理：

```bash
# 显示当前配置
python config_manager.py --show

# 设置超时时间
python config_manager.py --timeout 15

# 设置应用名称
python config_manager.py --app-name "我的应用"

# 交互式配置
python config_manager.py --interactive

# 重置为默认配置
python config_manager.py --reset
```

## 注意事项

1. 确保 Windows 10/11 的通知功能已启用
2. 首次运行可能需要允许应用发送通知的权限
3. 如果通知没有显示，请检查 Windows 通知设置
4. 程序需要 Python 3.6 或更高版本

## 故障排除

### 通知不显示
1. 检查 Windows 通知设置是否启用
2. 确认焦点辅助（专注助手）没有阻止通知
3. 重启程序或重新安装 plyer 库

### 依赖安装失败
```bash
# 升级 pip
python -m pip install --upgrade pip

# 重新安装 plyer
pip uninstall plyer
pip install plyer
```

## 示例代码

在 Python 脚本中使用：

```python
from plyer import notification

# 简单通知
notification.notify(
    title="标题",
    message="内容",
    timeout=10,
    toast=True
)
```

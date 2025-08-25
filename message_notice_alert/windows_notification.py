#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 10 侧边栏通知程序
使用 plyer 库显示系统通知
"""

import time
from plyer import notification
import argparse
import sys
import json
import os
from pathlib import Path


# 配置文件路径
CONFIG_FILE = "notification_config.json"

# 默认配置
DEFAULT_CONFIG = {
    "timeout": 10,
    "app_name": "Python通知应用",
    "title": "Python通知",
    "message": "这是一条测试通知"
}


def load_config():
    """
    从配置文件加载配置
    如果配置文件不存在，则创建默认配置文件
    """
    config_path = Path(CONFIG_FILE)

    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"已从配置文件加载设置: {CONFIG_FILE}")
            return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"读取配置文件失败: {e}")
            print("使用默认配置")
            return DEFAULT_CONFIG.copy()
    else:
        # 创建默认配置文件
        save_config(DEFAULT_CONFIG)
        print(f"已创建默认配置文件: {CONFIG_FILE}")
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """
    保存配置到文件
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"配置已保存到: {CONFIG_FILE}")
        return True
    except IOError as e:
        print(f"保存配置文件失败: {e}")
        return False


def update_config_value(key, value):
    """
    更新配置文件中的单个值
    """
    config = load_config()
    config[key] = value
    return save_config(config)


def show_notification(title="通知", message="这是一条测试通知", timeout=10, app_name="Python通知"):
    """
    显示 Windows 10 侧边栏通知
    
    参数:
        title (str): 通知标题
        message (str): 通知内容
        timeout (int): 通知显示时间（秒）
        app_name (str): 应用程序名称
    """
    try:
        notification.notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=timeout,
            toast=True  # 使用 Windows 10 的 toast 通知样式
        )
        print(f"通知已发送: {title}")
        print(f"内容: {message}")
        print(f"显示时间: {timeout}秒")
        
    except Exception as e:
        print(f"发送通知时出错: {e}")
        return False
    
    return True


def show_multiple_notifications():
    """
    显示多个示例通知
    """
    # 从配置文件加载默认超时时间
    config = load_config()
    default_timeout = config.get("timeout", 10)

    notifications = [
        {
            "title": "欢迎使用",
            "message": "这是第一条通知消息！",
            "timeout": default_timeout
        },
        {
            "title": "系统提醒",
            "message": "您有新的消息需要查看",
            "timeout": default_timeout
        },
        {
            "title": "任务完成",
            "message": "您的任务已经成功完成！",
            "timeout": default_timeout
        }
    ]

    for i, notif in enumerate(notifications, 1):
        print(f"\n发送第 {i} 条通知...")
        show_notification(
            title=notif["title"],
            message=notif["message"],
            timeout=notif["timeout"]
        )

        # 等待一段时间再发送下一条通知
        if i < len(notifications):
            time.sleep(3)


def main():
    """
    主函数 - 处理命令行参数
    """
    # 加载配置文件
    config = load_config()

    parser = argparse.ArgumentParser(description="Windows 10 侧边栏通知程序")
    parser.add_argument("-t", "--title", default=config.get("title", "Python通知"), help="通知标题")
    parser.add_argument("-m", "--message", default=config.get("message", "这是一条测试通知"), help="通知内容")
    parser.add_argument("--timeout", type=int, default=config.get("timeout", 10), help="通知显示时间（秒）")
    parser.add_argument("--app-name", default=config.get("app_name", "Python通知应用"), help="应用程序名称")
    parser.add_argument("--demo", action="store_true", help="运行演示模式（显示多条通知）")
    parser.add_argument("--save-config", action="store_true", help="保存当前参数到配置文件")
    parser.add_argument("--show-config", action="store_true", help="显示当前配置")
    parser.add_argument("--set-timeout", type=int, help="设置默认超时时间并保存到配置文件")

    args = parser.parse_args()

    print("Windows 10 侧边栏通知程序")
    print("=" * 40)

    # 处理配置相关命令
    if args.show_config:
        print("当前配置:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        return

    if args.set_timeout:
        if update_config_value("timeout", args.set_timeout):
            print(f"默认超时时间已设置为: {args.set_timeout}秒")
        return

    if args.save_config:
        new_config = {
            "title": args.title,
            "message": args.message,
            "timeout": args.timeout,
            "app_name": args.app_name
        }
        if save_config(new_config):
            print("当前参数已保存为默认配置")
        return

    # 执行通知功能
    if args.demo:
        print("运行演示模式...")
        show_multiple_notifications()
    else:
        show_notification(
            title=args.title,
            message=args.message,
            timeout=args.timeout,
            app_name=args.app_name
        )

    print("\n程序执行完成！")


if __name__ == "__main__":
    main()

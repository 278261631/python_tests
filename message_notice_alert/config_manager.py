#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理工具
用于管理通知程序的配置文件
"""

import json
import os
from pathlib import Path


CONFIG_FILE = "notification_config.json"

DEFAULT_CONFIG = {
    "timeout": 10,
    "app_name": "Python通知应用",
    "title": "Python通知",
    "message": "这是一条测试通知"
}


def load_config():
    """加载配置文件"""
    config_path = Path(CONFIG_FILE)
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"读取配置文件失败: {e}")
            return DEFAULT_CONFIG.copy()
    else:
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except IOError as e:
        print(f"保存配置文件失败: {e}")
        return False


def show_config():
    """显示当前配置"""
    config = load_config()
    print("当前配置:")
    print("-" * 30)
    for key, value in config.items():
        print(f"{key:12}: {value}")


def set_timeout(timeout):
    """设置超时时间"""
    config = load_config()
    config["timeout"] = timeout
    if save_config(config):
        print(f"超时时间已设置为: {timeout}秒")
        return True
    return False


def set_app_name(app_name):
    """设置应用名称"""
    config = load_config()
    config["app_name"] = app_name
    if save_config(config):
        print(f"应用名称已设置为: {app_name}")
        return True
    return False


def set_default_title(title):
    """设置默认标题"""
    config = load_config()
    config["title"] = title
    if save_config(config):
        print(f"默认标题已设置为: {title}")
        return True
    return False


def set_default_message(message):
    """设置默认消息"""
    config = load_config()
    config["message"] = message
    if save_config(config):
        print(f"默认消息已设置为: {message}")
        return True
    return False


def reset_config():
    """重置为默认配置"""
    if save_config(DEFAULT_CONFIG):
        print("配置已重置为默认值")
        return True
    return False


def interactive_config():
    """交互式配置"""
    print("交互式配置设置")
    print("=" * 30)
    
    config = load_config()
    
    # 超时时间
    current_timeout = config.get("timeout", 10)
    timeout_input = input(f"超时时间 (当前: {current_timeout}秒): ").strip()
    if timeout_input:
        try:
            config["timeout"] = int(timeout_input)
        except ValueError:
            print("无效的超时时间，保持原值")
    
    # 应用名称
    current_app_name = config.get("app_name", "Python通知应用")
    app_name_input = input(f"应用名称 (当前: {current_app_name}): ").strip()
    if app_name_input:
        config["app_name"] = app_name_input
    
    # 默认标题
    current_title = config.get("title", "Python通知")
    title_input = input(f"默认标题 (当前: {current_title}): ").strip()
    if title_input:
        config["title"] = title_input
    
    # 默认消息
    current_message = config.get("message", "这是一条测试通知")
    message_input = input(f"默认消息 (当前: {current_message}): ").strip()
    if message_input:
        config["message"] = message_input
    
    # 保存配置
    if save_config(config):
        print("\n配置已保存！")
        show_config()
    else:
        print("\n保存配置失败！")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="通知程序配置管理工具")
    parser.add_argument("--show", action="store_true", help="显示当前配置")
    parser.add_argument("--timeout", type=int, help="设置超时时间")
    parser.add_argument("--app-name", help="设置应用名称")
    parser.add_argument("--title", help="设置默认标题")
    parser.add_argument("--message", help="设置默认消息")
    parser.add_argument("--reset", action="store_true", help="重置为默认配置")
    parser.add_argument("--interactive", action="store_true", help="交互式配置")
    
    args = parser.parse_args()
    
    if args.show:
        show_config()
    elif args.timeout:
        set_timeout(args.timeout)
    elif args.app_name:
        set_app_name(args.app_name)
    elif args.title:
        set_default_title(args.title)
    elif args.message:
        set_default_message(args.message)
    elif args.reset:
        reset_config()
    elif args.interactive:
        interactive_config()
    else:
        print("配置管理工具")
        print("使用 --help 查看可用选项")
        print("或使用 --interactive 进行交互式配置")


if __name__ == "__main__":
    main()

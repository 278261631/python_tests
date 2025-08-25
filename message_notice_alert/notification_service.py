#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 10 持续运行的通知服务程序
带有系统托盘图标和右键菜单
"""

import time
import threading
import json
import os
from pathlib import Path
from datetime import datetime
import sys

# GUI 相关导入
try:
    import pystray
    from PIL import Image, ImageDraw
    from plyer import notification
    import tkinter as tk
    from tkinter import ttk
except ImportError as e:
    print(f"缺少必要的库: {e}")
    print("请运行 install_requirements.bat 安装依赖")
    sys.exit(1)

# 导入配置管理功能
from windows_notification import load_config, save_config, show_notification


class PersistentNotificationWindow:
    """持续提示窗口类"""

    def __init__(self):
        self.root = None
        self.title_label = None
        self.message_label = None
        self.running = True

    def create_window(self, title="持续提示", message="这是一条持续显示的提示信息"):
        """创建持续提示窗口"""
        self.root = tk.Tk()
        self.root.title("持续提示")

        # 设置窗口属性
        self.root.overrideredirect(True)  # 无边框窗口
        self.root.attributes('-topmost', True)  # 置顶显示
        self.root.attributes('-alpha', 0.9)  # 半透明

        # 设置窗口样式
        self.root.configure(bg='#e74c3c')  # 红色背景，表示重要提示

        # 创建主框架
        main_frame = tk.Frame(self.root, bg='#e74c3c', padx=15, pady=10)
        main_frame.pack()

        # 创建标题标签
        self.title_label = tk.Label(
            main_frame,
            text=title,
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#e74c3c'
        )
        self.title_label.pack()

        # 创建消息标签
        self.message_label = tk.Label(
            main_frame,
            text=message,
            font=('Arial', 10),
            fg='#ffffff',
            bg='#e74c3c',
            wraplength=300,  # 自动换行
            justify='center'
        )
        self.message_label.pack(pady=(5, 0))

        # 创建关闭按钮
        close_button = tk.Button(
            main_frame,
            text="关闭",
            font=('Arial', 8),
            fg='#e74c3c',
            bg='#ffffff',
            command=self.close_window,
            padx=10,
            pady=2
        )
        close_button.pack(pady=(10, 0))

        # 设置窗口位置（屏幕中央偏上）
        self.position_window()

        # 绑定拖动事件
        main_frame.bind('<Button-1>', self.start_move)
        main_frame.bind('<B1-Motion>', self.on_move)
        self.title_label.bind('<Button-1>', self.start_move)
        self.title_label.bind('<B1-Motion>', self.on_move)
        self.message_label.bind('<Button-1>', self.start_move)
        self.message_label.bind('<B1-Motion>', self.on_move)

    def position_window(self):
        """将窗口定位到屏幕中央偏上"""
        self.root.update_idletasks()

        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 获取窗口尺寸
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()

        # 计算位置（中央偏上）
        x = (screen_width - window_width) // 2
        y = screen_height // 4  # 屏幕高度的1/4位置

        self.root.geometry(f"+{x}+{y}")

    def start_move(self, event):
        """开始拖动窗口"""
        self.root.x = event.x
        self.root.y = event.y

    def on_move(self, event):
        """拖动窗口"""
        deltax = event.x - self.root.x
        deltay = event.y - self.root.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def close_window(self):
        """关闭窗口"""
        self.running = False
        if self.root:
            self.root.destroy()

    def update_content(self, title=None, message=None):
        """更新窗口内容"""
        if title and self.title_label:
            self.title_label.config(text=title)
        if message and self.message_label:
            self.message_label.config(text=message)

    def destroy(self):
        """销毁窗口"""
        self.running = False
        if self.root:
            self.root.destroy()


class FloatingTimeWindow:
    """浮动时间显示窗口"""

    def __init__(self):
        self.root = None
        self.time_label = None
        self.running = True

    def create_window(self):
        """创建浮动时间窗口"""
        self.root = tk.Tk()
        self.root.title("时间显示")

        # 设置窗口属性
        self.root.overrideredirect(True)  # 无边框窗口
        self.root.attributes('-topmost', True)  # 置顶显示
        self.root.attributes('-alpha', 0.8)  # 半透明

        # 设置窗口样式
        self.root.configure(bg='#2c3e50')

        # 创建时间标签
        self.time_label = tk.Label(
            self.root,
            font=('Arial', 14, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50',
            padx=10,
            pady=5
        )
        self.time_label.pack()

        # 设置窗口位置（右下角）
        self.position_window()

        # 绑定事件
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.on_move)

        # 开始更新时间
        self.update_time()

    def position_window(self):
        """将窗口定位到顶部中央"""
        self.root.update_idletasks()

        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 获取窗口尺寸
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()

        # 计算位置（顶部中央，留出一些边距）
        x = (screen_width - window_width) // 2  # 水平居中
        y = 20  # 距离顶部20像素

        self.root.geometry(f"+{x}+{y}")

    def start_move(self, event):
        """开始拖动窗口"""
        self.root.x = event.x
        self.root.y = event.y

    def on_move(self, event):
        """拖动窗口"""
        deltax = event.x - self.root.x
        deltay = event.y - self.root.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def update_time(self):
        """更新时间显示"""
        if self.running and self.root:
            current_time = datetime.now().strftime('%H:%M:%S')
            if self.time_label:
                self.time_label.config(text=current_time)

            # 每秒更新一次
            self.root.after(1000, self.update_time)

    def destroy(self):
        """销毁窗口"""
        self.running = False
        if self.root:
            self.root.destroy()


class NotificationService:
    """通知服务类"""
    
    def __init__(self):
        self.config = load_config()
        self.running = True
        self.icon = None
        self.notification_count = 0
        self.time_window = None
        self.persistent_notifications = []  # 存储持续提示窗口列表
        
    def create_icon_image(self):
        """创建系统托盘图标"""
        logo_path = Path("logo.png")

        # 尝试加载 logo.png 文件
        if logo_path.exists():
            try:
                image = Image.open(logo_path)
                # 调整图标大小为标准托盘图标尺寸
                image = image.resize((64, 64), Image.Resampling.LANCZOS)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 使用 logo.png 作为托盘图标")
                return image
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 加载 logo.png 失败: {e}")
                print("使用默认生成的图标")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 未找到 logo.png 文件，使用默认图标")

        # 如果 logo.png 不存在或加载失败，创建默认图标
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 绘制一个简单的通知图标
        # 外圆
        draw.ellipse([8, 8, 56, 56], fill=(70, 130, 180, 255), outline=(30, 90, 140, 255), width=2)
        # 内圆
        draw.ellipse([20, 20, 44, 44], fill=(255, 255, 255, 255))
        # 感叹号
        draw.rectangle([30, 24, 34, 36], fill=(70, 130, 180, 255))
        draw.rectangle([30, 38, 34, 42], fill=(70, 130, 180, 255))

        return image
    
    def send_test_notification(self, icon=None, item=None):
        """发送测试通知"""
        config = load_config()
        success = show_notification(
            title="测试通知",
            message=f"这是第 {self.notification_count + 1} 条测试通知",
            timeout=config.get("timeout", 10),
            app_name=config.get("app_name", "通知服务")
        )
        
        if success:
            self.notification_count += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 发送测试通知 #{self.notification_count}")
    
    def send_custom_notification(self, icon=None, item=None):
        """发送自定义通知"""
        config = load_config()
        success = show_notification(
            title=config.get("title", "通知"),
            message=config.get("message", "这是一条通知"),
            timeout=config.get("timeout", 10),
            app_name=config.get("app_name", "通知服务")
        )
        
        if success:
            self.notification_count += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 发送自定义通知 #{self.notification_count}")
    
    def show_config_info(self, icon=None, item=None):
        """显示配置信息"""
        config = load_config()
        config_text = "当前配置:\n"
        for key, value in config.items():
            config_text += f"{key}: {value}\n"
        
        show_notification(
            title="配置信息",
            message=config_text.strip(),
            timeout=10,
            app_name="通知服务"
        )
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 显示配置信息")
    
    def open_config_manager(self, icon=None, item=None):
        """打开配置管理器"""
        import subprocess
        try:
            subprocess.Popen(["python", "config_manager.py", "--interactive"], 
                           cwd=Path(__file__).parent)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 启动配置管理器")
        except Exception as e:
            print(f"启动配置管理器失败: {e}")
    
    def quit_application(self, icon=None, item=None):
        """退出应用程序"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 用户请求退出")
        self.running = False

        # 关闭所有持续提示窗口
        for window in self.persistent_notifications[:]:
            try:
                window.destroy()
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 关闭持续提示窗口时出错: {e}")
        self.persistent_notifications.clear()

        # 关闭时间窗口
        if self.time_window:
            self.time_window.destroy()

        # 关闭托盘图标
        if self.icon:
            self.icon.stop()
    
    def create_menu(self):
        """创建右键菜单"""
        return pystray.Menu(
            pystray.MenuItem("发送测试通知", self.send_test_notification),
            pystray.MenuItem("发送自定义通知", self.send_custom_notification),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("持续提示", pystray.Menu(
                pystray.MenuItem("显示持续提示", self.show_persistent_notification),
                pystray.MenuItem("自定义持续提示", self.show_custom_persistent_notification),
                pystray.MenuItem("关闭所有持续提示", self.close_all_persistent_notifications)
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("显示配置", self.show_config_info),
            pystray.MenuItem("服务统计", self.show_statistics),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("配置管理", self.open_config_manager),
            pystray.MenuItem("定时通知", self.schedule_notification),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", self.quit_application)
        )
    
    def setup_tray_icon(self):
        """设置系统托盘图标"""
        image = self.create_icon_image()
        menu = self.create_menu()
        
        self.icon = pystray.Icon(
            "notification_service",
            image,
            "通知服务",
            menu
        )
        
        return self.icon
    
    def schedule_notification(self, icon=None, item=None):
        """安排定时通知"""
        show_notification(
            title="定时通知功能",
            message="定时通知功能正在开发中...\n敬请期待！",
            timeout=5,
            app_name="通知服务"
        )
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 定时通知功能被调用")

    def show_persistent_notification(self, icon=None, item=None):
        """显示持续提示"""
        config = load_config()

        # 创建持续提示窗口
        persistent_window = PersistentNotificationWindow()

        # 在新线程中运行窗口
        def run_persistent_window():
            try:
                persistent_window.create_window(
                    title="重要提示",
                    message="这是一条持续显示的重要提示信息\n点击关闭按钮或拖动窗口移动位置"
                )
                persistent_window.root.mainloop()
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 持续提示窗口错误: {e}")
            finally:
                # 从列表中移除已关闭的窗口
                if persistent_window in self.persistent_notifications:
                    self.persistent_notifications.remove(persistent_window)

        # 添加到管理列表
        self.persistent_notifications.append(persistent_window)

        # 启动窗口线程
        threading.Thread(target=run_persistent_window, daemon=True).start()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 创建持续提示窗口")

        # 发送普通通知告知用户
        show_notification(
            title="持续提示已创建",
            message="持续提示窗口已显示，将一直保持显示直到手动关闭",
            timeout=5,
            app_name="通知服务"
        )

    def show_custom_persistent_notification(self, icon=None, item=None):
        """显示自定义持续提示"""
        config = load_config()

        # 创建持续提示窗口
        persistent_window = PersistentNotificationWindow()

        # 在新线程中运行窗口
        def run_custom_persistent_window():
            try:
                persistent_window.create_window(
                    title=config.get("title", "持续提示"),
                    message=config.get("message", "这是一条持续显示的提示信息")
                )
                persistent_window.root.mainloop()
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 自定义持续提示窗口错误: {e}")
            finally:
                # 从列表中移除已关闭的窗口
                if persistent_window in self.persistent_notifications:
                    self.persistent_notifications.remove(persistent_window)

        # 添加到管理列表
        self.persistent_notifications.append(persistent_window)

        # 启动窗口线程
        threading.Thread(target=run_custom_persistent_window, daemon=True).start()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 创建自定义持续提示窗口")

        # 发送普通通知告知用户
        show_notification(
            title="自定义持续提示已创建",
            message="使用配置文件中的内容创建持续提示窗口",
            timeout=5,
            app_name="通知服务"
        )

    def close_all_persistent_notifications(self, icon=None, item=None):
        """关闭所有持续提示"""
        count = len(self.persistent_notifications)

        if count == 0:
            show_notification(
                title="持续提示",
                message="当前没有活动的持续提示窗口",
                timeout=3,
                app_name="通知服务"
            )
            return

        # 关闭所有持续提示窗口
        for window in self.persistent_notifications[:]:  # 使用切片复制列表
            try:
                window.destroy()
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 关闭持续提示窗口时出错: {e}")

        # 清空列表
        self.persistent_notifications.clear()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 已关闭 {count} 个持续提示窗口")

        # 发送通知
        show_notification(
            title="持续提示已关闭",
            message=f"已关闭 {count} 个持续提示窗口",
            timeout=3,
            app_name="通知服务"
        )

    def show_statistics(self, icon=None, item=None):
        """显示统计信息"""
        uptime = datetime.now().strftime('%H:%M:%S')
        stats_text = f"服务统计:\n已发送通知: {self.notification_count}\n当前时间: {uptime}\n时间窗口: 运行中"

        show_notification(
            title="服务统计",
            message=stats_text,
            timeout=8,
            app_name="通知服务"
        )
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 显示统计信息")



    def background_worker(self):
        """后台工作线程"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 后台服务启动")

        # 记录启动时间
        start_time = datetime.now()
        last_heartbeat = start_time

        while self.running:
            current_time = datetime.now()

            # 每分钟输出一次心跳信息
            if (current_time - last_heartbeat).seconds >= 60:
                uptime = current_time - start_time
                print(f"[{current_time.strftime('%H:%M:%S')}] 服务运行中... 运行时长: {uptime}")
                last_heartbeat = current_time

            # 这里可以添加其他定时任务
            time.sleep(1)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 后台服务停止")
    
    def run(self):
        """运行服务"""
        print("Windows 10 通知服务启动")
        print("=" * 40)
        print("服务已在后台运行，查看系统托盘图标")
        print("右键点击托盘图标可以:")
        print("- 发送测试通知")
        print("- 发送自定义通知")
        print("- 持续提示（无时间限制的提示窗口）")
        print("- 查看配置")
        print("- 打开配置管理")
        print("- 退出程序")
        print("=" * 40)
        print("浮动时间窗口已启动（顶部中央）")
        print("- 可以拖动窗口位置")
        print("=" * 40)
        
        # 发送启动通知
        show_notification(
            title="通知服务启动",
            message="通知服务已启动，请查看系统托盘图标和浮动时间窗口",
            timeout=5,
            app_name="通知服务"
        )

        # 创建并显示时间窗口
        self.time_window = FloatingTimeWindow()
        time_window_thread = threading.Thread(target=self.run_time_window, daemon=True)
        time_window_thread.start()

        # 启动后台工作线程
        worker_thread = threading.Thread(target=self.background_worker, daemon=True)
        worker_thread.start()

        # 设置并运行系统托盘图标
        icon = self.setup_tray_icon()

        try:
            # 运行托盘图标（这会阻塞主线程）
            icon.run()
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 收到中断信号")
        finally:
            self.running = False
            if self.time_window:
                self.time_window.destroy()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 通知服务已停止")

    def run_time_window(self):
        """运行时间窗口的线程函数"""
        try:
            self.time_window.create_window()
            self.time_window.root.mainloop()
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 时间窗口错误: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Windows 10 持续运行通知服务")
    parser.add_argument("--no-tray", action="store_true", help="不显示系统托盘图标（仅后台运行）")
    
    args = parser.parse_args()
    
    if args.no_tray:
        print("后台模式运行（无系统托盘图标）")
        service = NotificationService()
        try:
            service.background_worker()
        except KeyboardInterrupt:
            print("\n服务已停止")
    else:
        # 正常模式：带系统托盘图标
        service = NotificationService()
        service.run()


if __name__ == "__main__":
    main()

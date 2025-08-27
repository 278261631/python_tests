#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志文件查找器
从指定目录中查找匹配模式的日志文件，并根据日期筛选
"""

import os
import glob
import re
from datetime import datetime, timedelta
from typing import List, Optional
import argparse


class LogFileFinder:
    """日志文件查找器类"""
    
    def __init__(self, log_directory: str = r"D:\kats\logs\log_core_pool"):
        """
        初始化日志文件查找器
        
        Args:
            log_directory: 日志文件目录路径
        """
        self.log_directory = log_directory
        self.file_pattern = "autoredux_server_*.log"
    
    def find_log_files(self) -> List[str]:
        """
        查找所有匹配模式的日志文件
        
        Returns:
            匹配的日志文件路径列表
        """
        if not os.path.exists(self.log_directory):
            print(f"错误: 目录 {self.log_directory} 不存在")
            return []
        
        # 构建完整的搜索模式
        search_pattern = os.path.join(self.log_directory, self.file_pattern)
        
        # 查找匹配的文件
        log_files = glob.glob(search_pattern)
        
        # 只返回文件名，不包含路径
        return [os.path.basename(file) for file in log_files]
    
    def extract_date_from_filename(self, filename: str) -> Optional[datetime]:
        """
        从文件名中提取日期
        
        Args:
            filename: 文件名
            
        Returns:
            提取的日期对象，如果无法提取则返回None
        """
        # 尝试匹配常见的日期格式
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{4}_\d{2}_\d{2})',  # YYYY_MM_DD
            r'(\d{8})',              # YYYYMMDD
            r'(\d{4}\d{2}\d{2})',    # YYYYMMDD (无分隔符)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group(1)
                try:
                    # 尝试不同的日期格式解析
                    if '-' in date_str:
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    elif '_' in date_str:
                        return datetime.strptime(date_str, '%Y_%m_%d')
                    elif len(date_str) == 8:
                        return datetime.strptime(date_str, '%Y%m%d')
                except ValueError:
                    continue
        
        return None
    
    def find_files_by_date(self, target_date: str) -> List[str]:
        """
        根据指定日期查找日志文件
        
        Args:
            target_date: 目标日期，格式: YYYY-MM-DD
            
        Returns:
            匹配指定日期的文件名列表
        """
        try:
            target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        except ValueError:
            print(f"错误: 日期格式不正确，请使用 YYYY-MM-DD 格式")
            return []
        
        all_files = self.find_log_files()
        matching_files = []
        
        for filename in all_files:
            file_date = self.extract_date_from_filename(filename)
            if file_date and file_date.date() == target_dt.date():
                matching_files.append(filename)
        
        return matching_files
    
    def find_files_by_date_range(self, start_date: str, end_date: str) -> List[str]:
        """
        根据日期范围查找日志文件

        Args:
            start_date: 开始日期，格式: YYYY-MM-DD
            end_date: 结束日期，格式: YYYY-MM-DD

        Returns:
            匹配日期范围的文件名列表
        """
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            print(f"错误: 日期格式不正确，请使用 YYYY-MM-DD 格式")
            return []

        all_files = self.find_log_files()
        matching_files = []

        for filename in all_files:
            file_date = self.extract_date_from_filename(filename)
            if file_date and start_dt.date() <= file_date.date() <= end_dt.date():
                matching_files.append(filename)

        return matching_files

    def find_files_last_30_days(self) -> List[str]:
        """
        查找最近30天内的日志文件

        Returns:
            最近30天内的文件名列表，按日期排序（最新的在前）
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        all_files = self.find_log_files()
        matching_files = []

        for filename in all_files:
            file_date = self.extract_date_from_filename(filename)
            if file_date and start_date.date() <= file_date.date() <= end_date.date():
                matching_files.append((filename, file_date))

        # 按日期排序，最新的在前
        matching_files.sort(key=lambda x: x[1], reverse=True)

        return [filename for filename, _ in matching_files]

    def get_latest_file(self) -> Optional[str]:
        """
        获取最近30天内日期最新的文件

        Returns:
            最新的文件名，如果没有找到则返回None
        """
        files = self.find_files_last_30_days()
        return files[0] if files else None
    
    def display_files(self, files: List[str], title: str = "找到的日志文件"):
        """
        显示文件列表

        Args:
            files: 文件名列表
            title: 显示标题
        """
        print(f"\n{title}:")
        print("-" * 50)

        if not files:
            print("未找到匹配的文件")
            return

        for i, filename in enumerate(files, 1):
            file_date = self.extract_date_from_filename(filename)
            date_str = file_date.strftime('%Y-%m-%d') if file_date else "未知日期"
            print(f"{i:2d}. {filename} ({date_str})")

        print(f"\n总共找到 {len(files)} 个文件")

    def display_latest_file(self):
        """
        显示最近30天内最新的文件
        """
        print("正在查找最近30天内的日志文件...")
        files = self.find_files_last_30_days()

        if not files:
            print("未找到最近30天内的日志文件")
            return

        latest_file = files[0]  # 已经按日期排序，第一个是最新的
        file_date = self.extract_date_from_filename(latest_file)
        date_str = file_date.strftime('%Y-%m-%d') if file_date else "未知日期"

        print(f"\n最近30天内的日志文件:")
        print("-" * 50)
        self.display_files(files, "所有文件")

        print(f"\n推荐文件（日期最新）:")
        print("=" * 50)
        print(f"文件名: {latest_file}")
        print(f"日期: {date_str}")
        print(f"完整路径: {os.path.join(self.log_directory, latest_file)}")

        return latest_file


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='日志文件查找器')
    parser.add_argument('--dir', '-d', default=r"D:\kats\logs\log_core_pool",
                       help='日志文件目录路径')
    parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('--start-date', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--list-all', '-l', action='store_true',
                       help='列出所有匹配的日志文件')
    
    args = parser.parse_args()
    
    # 创建日志文件查找器实例
    finder = LogFileFinder(args.dir)
    
    if args.date:
        # 查找指定日期的文件
        files = finder.find_files_by_date(args.date)
        finder.display_files(files, f"日期 {args.date} 的日志文件")
    
    elif args.start_date and args.end_date:
        # 查找日期范围内的文件
        files = finder.find_files_by_date_range(args.start_date, args.end_date)
        finder.display_files(files, f"日期范围 {args.start_date} 到 {args.end_date} 的日志文件")
    
    elif args.list_all:
        # 列出所有文件
        files = finder.find_log_files()
        finder.display_files(files, "所有匹配的日志文件")
    
    else:
        # 默认模式：显示最近30天内的文件，并推荐最新的
        print("日志文件查找器")
        print("=" * 50)
        print(f"搜索目录: {finder.log_directory}")
        print(f"文件模式: {finder.file_pattern}")
        print()

        # 显示最近30天内的文件和推荐的最新文件
        latest_file = finder.display_latest_file()

        if not latest_file:
            return

        # 询问用户是否需要其他操作
        while True:
            print("\n选择操作:")
            print("1. 查找指定日期的文件")
            print("2. 查找日期范围内的文件")
            print("3. 列出所有匹配的文件")
            print("4. 重新显示最近30天的文件")
            print("5. 退出")

            choice = input("\n请输入选择 (1-5): ").strip()

            if choice == '1':
                date = input("请输入日期 (YYYY-MM-DD): ").strip()
                files = finder.find_files_by_date(date)
                finder.display_files(files, f"日期 {date} 的日志文件")

            elif choice == '2':
                start_date = input("请输入开始日期 (YYYY-MM-DD): ").strip()
                end_date = input("请输入结束日期 (YYYY-MM-DD): ").strip()
                files = finder.find_files_by_date_range(start_date, end_date)
                finder.display_files(files, f"日期范围 {start_date} 到 {end_date} 的日志文件")

            elif choice == '3':
                files = finder.find_log_files()
                finder.display_files(files, "所有匹配的日志文件")

            elif choice == '4':
                finder.display_latest_file()

            elif choice == '5':
                print("退出程序")
                break

            else:
                print("无效选择，请重新输入")


if __name__ == "__main__":
    main()

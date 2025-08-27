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
from typing import List, Optional, Set, Dict, Tuple
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
        self.k_map_file = "k_map.txt"
        self.k_map_data = self._load_k_map()
    
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
            target_date: 目标日期，格式: YYYYMMDD

        Returns:
            匹配指定日期的文件名列表
        """
        try:
            target_dt = datetime.strptime(target_date, '%Y%m%d')
        except ValueError:
            print(f"错误: 日期格式不正确，请使用 YYYYMMDD 格式")
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
            start_date: 开始日期，格式: YYYYMMDD
            end_date: 结束日期，格式: YYYYMMDD

        Returns:
            匹配日期范围的文件名列表
        """
        try:
            start_dt = datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d')
        except ValueError:
            print(f"错误: 日期格式不正确，请使用 YYYYMMDD 格式")
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

    def extract_fit_files_from_log(self, log_filename: str) -> Set[str]:
        """
        从日志文件中提取匹配 GY*_K*.fit 模式的文件名

        Args:
            log_filename: 日志文件名

        Returns:
            匹配的fit文件名集合（去重）
        """
        log_path = os.path.join(self.log_directory, log_filename)

        if not os.path.exists(log_path):
            print(f"错误: 日志文件 {log_path} 不存在")
            return set()

        fit_files = set()
        fit_pattern = re.compile(r'GY\d_K\d{3}-.*?\.fit', re.IGNORECASE)

        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    matches = fit_pattern.findall(line)
                    for match in matches:
                        fit_files.add(match)
        except Exception as e:
            print(f"读取日志文件 {log_filename} 时出错: {e}")

        return fit_files

    def _load_k_map(self) -> Dict[str, Tuple[str, str]]:
        """
        加载k_map.txt文件，构建天区索引到坐标的映射

        Returns:
            字典，键为K索引（如K001-1），值为坐标元组（RA, DEC）
        """
        k_map_path = os.path.join(os.path.dirname(__file__), self.k_map_file)
        k_map_data = {}

        if not os.path.exists(k_map_path):
            print(f"警告: k_map.txt 文件不存在于 {k_map_path}")
            return k_map_data

        try:
            with open(k_map_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    # 跳过空行和注释行
                    if not line or line.startswith('//') or line.startswith('LabelMgr'):
                        continue

                    # 解析格式: K001-1, 1.09091h, +69.0
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 3:
                        k_index = parts[0]
                        ra = parts[1]
                        dec = parts[2]
                        k_map_data[k_index] = (ra, dec)

        except Exception as e:
            print(f"读取 k_map.txt 文件时出错: {e}")

        print(f"成功加载 {len(k_map_data)} 个天区索引映射")
        return k_map_data

    def extract_k_index_from_filename(self, filename: str) -> Optional[str]:
        """
        从FIT文件名中提取天区索引 K\d{3}-\d{1}

        Args:
            filename: FIT文件名

        Returns:
            提取的K索引，如果未找到则返回None
        """
        k_pattern = re.compile(r'K\d{3}-\d{1}', re.IGNORECASE)
        match = k_pattern.search(filename)
        return match.group(0).upper() if match else None

    def get_coordinates_for_k_index(self, k_index: str) -> Optional[Tuple[str, str]]:
        """
        根据K索引获取对应的坐标

        Args:
            k_index: 天区索引，如K001-1

        Returns:
            坐标元组(RA, DEC)，如果未找到则返回None
        """
        return self.k_map_data.get(k_index.upper())

    def extract_fit_files_from_multiple_logs(self, log_filenames: List[str]) -> Set[str]:
        """
        从多个日志文件中提取匹配 GY*_K*.fit 模式的文件名

        Args:
            log_filenames: 日志文件名列表

        Returns:
            所有匹配的fit文件名集合（去重）
        """
        all_fit_files = set()

        for log_filename in log_filenames:
            print(f"正在处理日志文件: {log_filename}")
            fit_files = self.extract_fit_files_from_log(log_filename)
            all_fit_files.update(fit_files)
            print(f"  找到 {len(fit_files)} 个fit文件")

        return all_fit_files

    def display_fit_files(self, fit_files: Set[str], title: str = "找到的FIT文件"):
        """
        显示fit文件列表，包含天区索引和坐标信息

        Args:
            fit_files: fit文件名集合
            title: 显示标题
        """
        print(f"\n{title}:")
        print("-" * 80)

        if not fit_files:
            print("未找到匹配的FIT文件")
            return

        # 转换为排序的列表
        sorted_files = sorted(list(fit_files))

        print(f"{'序号':<4} {'文件名':<30} {'天区索引':<8} {'坐标(RA, DEC)':<20}")
        print("-" * 80)

        for i, filename in enumerate(sorted_files, 1):
            k_index = self.extract_k_index_from_filename(filename)
            if k_index:
                coordinates = self.get_coordinates_for_k_index(k_index)
                coord_str = f"{coordinates[0]}, {coordinates[1]}" if coordinates else "未找到坐标"
            else:
                k_index = "未找到"
                coord_str = "N/A"

            print(f"{i:<4} {filename:<30} {k_index:<8} {coord_str:<20}")

        print(f"\n总共找到 {len(fit_files)} 个唯一的FIT文件")

    def search_fit_files_in_latest(self):
        """
        在最新的日志文件中搜索fit文件
        """
        latest_file = self.get_latest_file()
        if not latest_file:
            print("未找到最近30天内的日志文件")
            return

        print(f"正在从最新日志文件中搜索FIT文件: {latest_file}")
        fit_files = self.extract_fit_files_from_log(latest_file)
        self.display_fit_files(fit_files, f"从 {latest_file} 中找到的FIT文件")

        # 显示坐标分布摘要
        if fit_files:
            self.display_coordinate_summary(fit_files)

        return fit_files

    def search_fit_files_in_recent(self, days: int = 30):
        """
        在最近指定天数内的所有日志文件中搜索fit文件

        Args:
            days: 搜索最近多少天的日志文件
        """
        recent_files = self.find_files_last_30_days()
        if not recent_files:
            print(f"未找到最近{days}天内的日志文件")
            return

        print(f"正在从最近{days}天内的 {len(recent_files)} 个日志文件中搜索FIT文件...")
        fit_files = self.extract_fit_files_from_multiple_logs(recent_files)
        self.display_fit_files(fit_files, f"从最近{days}天内的日志文件中找到的FIT文件")

        # 显示坐标分布摘要
        if fit_files:
            self.display_coordinate_summary(fit_files)

        return fit_files

    def analyze_fit_coordinates(self, fit_files: Set[str]) -> Dict[str, List[str]]:
        """
        分析FIT文件的坐标分布

        Args:
            fit_files: FIT文件名集合

        Returns:
            按坐标分组的文件字典
        """
        coord_groups = {}

        for filename in fit_files:
            k_index = self.extract_k_index_from_filename(filename)
            if k_index:
                coordinates = self.get_coordinates_for_k_index(k_index)
                if coordinates:
                    coord_key = f"{coordinates[0]}, {coordinates[1]}"
                    if coord_key not in coord_groups:
                        coord_groups[coord_key] = []
                    coord_groups[coord_key].append(filename)

        return coord_groups

    def display_coordinate_summary(self, fit_files: Set[str]):
        """
        显示FIT文件的坐标分布摘要

        Args:
            fit_files: FIT文件名集合
        """
        coord_groups = self.analyze_fit_coordinates(fit_files)

        print(f"\n坐标分布摘要:")
        print("-" * 60)
        print(f"{'坐标(RA, DEC)':<20} {'文件数量':<8} {'天区索引':<30}")
        print("-" * 60)

        for coord, files in sorted(coord_groups.items()):
            k_indices = []
            for filename in files:
                k_index = self.extract_k_index_from_filename(filename)
                if k_index and k_index not in k_indices:
                    k_indices.append(k_index)

            k_indices_str = ", ".join(sorted(k_indices))
            print(f"{coord:<20} {len(files):<8} {k_indices_str:<30}")

        print(f"\n总共涉及 {len(coord_groups)} 个不同的坐标位置")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='日志文件查找器')
    parser.add_argument('--dir', '-d', default=r"D:\kats\logs\log_core_pool",
                       help='日志文件目录路径')
    parser.add_argument('--date', help='指定日期 (YYYYMMDD)')
    parser.add_argument('--start-date', help='开始日期 (YYYYMMDD)')
    parser.add_argument('--end-date', help='结束日期 (YYYYMMDD)')
    parser.add_argument('--list-all', '-l', action='store_true',
                       help='列出所有匹配的日志文件')
    parser.add_argument('--search-fit', '-f', action='store_true',
                       help='在最新日志文件中搜索FIT文件')
    parser.add_argument('--search-fit-recent', '-fr', action='store_true',
                       help='在最近30天的日志文件中搜索FIT文件')
    
    args = parser.parse_args()
    
    # 创建日志文件查找器实例
    finder = LogFileFinder(args.dir)
    
    if args.date:
        # 查找指定日期的文件
        files = finder.find_files_by_date(args.date)
        finder.display_files(files, f"日期 {args.date} 的日志文件")
        # 在找到的文件中搜索FIT文件
        if files:
            print("\n" + "=" * 60)
            fit_files = finder.extract_fit_files_from_multiple_logs(files)
            finder.display_fit_files(fit_files, f"从日期 {args.date} 的日志文件中找到的FIT文件")
            if fit_files:
                finder.display_coordinate_summary(fit_files)

    elif args.start_date and args.end_date:
        # 查找日期范围内的文件
        files = finder.find_files_by_date_range(args.start_date, args.end_date)
        finder.display_files(files, f"日期范围 {args.start_date} 到 {args.end_date} 的日志文件")
        # 在找到的文件中搜索FIT文件
        if files:
            print("\n" + "=" * 60)
            fit_files = finder.extract_fit_files_from_multiple_logs(files)
            finder.display_fit_files(fit_files, f"从日期范围 {args.start_date} 到 {args.end_date} 的日志文件中找到的FIT文件")
            if fit_files:
                finder.display_coordinate_summary(fit_files)

    elif args.list_all:
        # 列出所有文件
        files = finder.find_log_files()
        finder.display_files(files, "所有匹配的日志文件")
        # 在所有文件中搜索FIT文件
        if files:
            print("\n" + "=" * 60)
            fit_files = finder.extract_fit_files_from_multiple_logs(files)
            finder.display_fit_files(fit_files, "从所有日志文件中找到的FIT文件")
            if fit_files:
                finder.display_coordinate_summary(fit_files)

    elif args.search_fit:
        # 在最新日志文件中搜索FIT文件
        finder.search_fit_files_in_latest()

    elif args.search_fit_recent:
        # 在最近30天的日志文件中搜索FIT文件
        finder.search_fit_files_in_recent()
    
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

        # 默认搜索最新日志文件中的FIT文件
        print("\n" + "=" * 60)
        finder.search_fit_files_in_latest()

        # 询问用户是否需要其他操作
        while True:
            print("\n选择操作:")
            print("1. 查找指定日期的文件")
            print("2. 查找日期范围内的文件")
            print("3. 列出所有匹配的文件")
            print("4. 重新显示最近30天的文件")
            print("5. 在最新日志文件中搜索FIT文件")
            print("6. 在最近30天日志文件中搜索FIT文件")
            print("7. 退出")

            choice = input("\n请输入选择 (1-7): ").strip()

            if choice == '1':
                date = input("请输入日期 (YYYYMMDD): ").strip()
                files = finder.find_files_by_date(date)
                finder.display_files(files, f"日期 {date} 的日志文件")

            elif choice == '2':
                start_date = input("请输入开始日期 (YYYYMMDD): ").strip()
                end_date = input("请输入结束日期 (YYYYMMDD): ").strip()
                files = finder.find_files_by_date_range(start_date, end_date)
                finder.display_files(files, f"日期范围 {start_date} 到 {end_date} 的日志文件")

            elif choice == '3':
                files = finder.find_log_files()
                finder.display_files(files, "所有匹配的日志文件")

            elif choice == '4':
                finder.display_latest_file()

            elif choice == '5':
                finder.search_fit_files_in_latest()

            elif choice == '6':
                finder.search_fit_files_in_recent()

            elif choice == '7':
                print("退出程序")
                break

            else:
                print("无效选择，请重新输入")


if __name__ == "__main__":
    main()

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

    def extract_timestamp_from_line(self, line: str) -> Optional[str]:
        """
        从日志行开头提取时间戳，格式: 2025-08-23 03:00:15,978

        Args:
            line: 日志行内容

        Returns:
            提取的时间戳字符串，如果未找到则返回None
        """
        timestamp_pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}')
        match = timestamp_pattern.search(line)
        return match.group(0) if match else None

    def parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """
        解析时间戳字符串为datetime对象

        Args:
            timestamp_str: 时间戳字符串，格式: 2025-08-23 03:00:15,978

        Returns:
            datetime对象，如果解析失败则返回None
        """
        try:
            # 将逗号替换为点号以符合Python的microsecond格式
            timestamp_str = timestamp_str.replace(',', '.')
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            return None

    def calculate_time_difference(self, start_time: datetime, end_time: datetime) -> str:
        """
        计算两个时间之间的差值

        Args:
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            时间差的字符串表示
        """
        time_diff = end_time - start_time
        total_seconds = time_diff.total_seconds()

        if total_seconds < 60:
            return f"{total_seconds:.3f}秒"
        elif total_seconds < 3600:
            minutes = int(total_seconds // 60)
            seconds = total_seconds % 60
            return f"{minutes}分{seconds:.3f}秒"
        else:
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = total_seconds % 60
            return f"{hours}小时{minutes}分{seconds:.3f}秒"

    def extract_fit_files_from_log(self, log_filename: str) -> Set[str]:
        """
        从日志文件中提取匹配 GY*_K*.fit 模式的文件名，并记录开始/结束时间

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

        # 初始化文件时间存储（如果不存在）
        if not hasattr(self, 'fit_file_times'):
            self.fit_file_times = {}

        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # 检查是否包含开始或结束关键词
                    if "开始" in line or "结束" in line:
                        timestamp = self.extract_timestamp_from_line(line)
                        if timestamp:
                            # 查找该行中的FIT文件名
                            matches = fit_pattern.findall(line)
                            for match in matches:
                                fit_files.add(match)

                                # 记录时间信息
                                if match not in self.fit_file_times:
                                    self.fit_file_times[match] = {}

                                if "开始" in line:
                                    self.fit_file_times[match]['start'] = timestamp
                                    # print(f"  调试: 记录开始时间 {match} -> {timestamp}")
                                elif "结束" in line:
                                    self.fit_file_times[match]['end'] = timestamp
                                    # print(f"  调试: 记录结束时间 {match} -> {timestamp}")
                    else:
                        # 普通行，只提取文件名
                        matches = fit_pattern.findall(line)
                        for match in matches:
                            fit_files.add(match)

        except Exception as e:
            print(f"读取日志文件 {log_filename} 时出错: {e}")

        return fit_files

    def _load_k_map(self) -> Dict[str, Dict[str, Tuple[str, str]]]:
        """
        加载所有系统的k_map文件，构建系统到天区索引到坐标的映射

        Returns:
            嵌套字典，外层键为系统名（如GY1），内层键为K索引（如K001-1），值为坐标元组（RA, DEC）
        """
        systems = ['GY1', 'GY2', 'GY3', 'GY4', 'GY5', 'GY6']
        all_k_map_data = {}

        for system in systems:
            k_map_file = f"k_map_{system.lower()}.txt"
            k_map_path = os.path.join(os.path.dirname(__file__), k_map_file)
            system_data = {}

            if not os.path.exists(k_map_path):
                print(f"警告: {k_map_file} 文件不存在于 {k_map_path}")
                # 如果系统文件不存在，尝试使用原始 k_map.txt
                fallback_path = os.path.join(os.path.dirname(__file__), self.k_map_file)
                if os.path.exists(fallback_path):
                    print(f"使用备用文件: {self.k_map_file}")
                    k_map_path = fallback_path
                else:
                    continue

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
                            system_data[k_index] = (ra, dec)

            except Exception as e:
                print(f"读取 {k_map_file} 文件时出错: {e}")
                continue

            all_k_map_data[system] = system_data
            print(f"成功加载 {system} 系统 {len(system_data)} 个天区索引映射")

        total_mappings = sum(len(data) for data in all_k_map_data.values())
        print(f"总共加载 {len(all_k_map_data)} 个系统，{total_mappings} 个天区索引映射")
        return all_k_map_data

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

    def get_coordinates_for_k_index(self, k_index: str, system: str = None) -> Optional[Tuple[str, str]]:
        """
        根据K索引和系统名获取对应的坐标

        Args:
            k_index: 天区索引，如K001-1
            system: 系统名，如GY1, GY2等

        Returns:
            坐标元组(RA, DEC)，如果未找到则返回None
        """
        if system and system.upper() in self.k_map_data:
            return self.k_map_data[system.upper()].get(k_index.upper())

        # 如果没有指定系统或系统不存在，尝试在所有系统中查找
        for sys_name, sys_data in self.k_map_data.items():
            coords = sys_data.get(k_index.upper())
            if coords:
                return coords

        return None

    def extract_utc_datetime_from_filename(self, filename: str) -> Optional[str]:
        """
        从FIT文件名中提取UTC日期时间 UTC20250823_202712

        Args:
            filename: FIT文件名

        Returns:
            提取的UTC日期时间字符串，如果未找到则返回None
        """
        utc_pattern = re.compile(r'UTC(\d{8}_\d{6})', re.IGNORECASE)
        match = utc_pattern.search(filename)
        return match.group(1) if match else None

    def format_utc_datetime(self, utc_str: str) -> Optional[str]:
        """
        格式化UTC日期时间字符串为可读格式

        Args:
            utc_str: UTC日期时间字符串，格式: 20250823_202712

        Returns:
            格式化后的日期时间字符串，如: 2025-08-23 20:27:12
        """
        try:
            # 解析格式: 20250823_202712
            date_part, time_part = utc_str.split('_')
            year = date_part[:4]
            month = date_part[4:6]
            day = date_part[6:8]
            hour = time_part[:2]
            minute = time_part[2:4]
            second = time_part[4:6]

            return f"{year}-{month}-{day} {hour}:{minute}:{second}"
        except (ValueError, IndexError):
            return None

    def extract_system_name_from_filename(self, filename: str) -> Optional[str]:
        """
        从FIT文件名中提取系统名称 GY\d{1}

        Args:
            filename: FIT文件名

        Returns:
            提取的系统名称，如GY1、GY2等，如果未找到则返回None
        """
        system_pattern = re.compile(r'GY\d{1}', re.IGNORECASE)
        match = system_pattern.search(filename)
        return match.group(0).upper() if match else None

    def extract_fit_files_from_multiple_logs(self, log_filenames: List[str]) -> Set[str]:
        """
        从多个日志文件中提取匹配 GY*_K*.fit 模式的文件名

        Args:
            log_filenames: 日志文件名列表

        Returns:
            所有匹配的fit文件名集合（去重）
        """
        all_fit_files = set()

        # 在处理多个文件前清空时间信息
        self.fit_file_times = {}

        for log_filename in log_filenames:
            print(f"正在处理日志文件: {log_filename}")
            fit_files = self.extract_fit_files_from_log(log_filename)
            all_fit_files.update(fit_files)
            print(f"  找到 {len(fit_files)} 个fit文件")

        return all_fit_files

    def display_fit_files(self, fit_files: Set[str], title: str = "找到的FIT文件"):
        """
        显示fit文件列表，包含系统名称、天区索引、坐标、UTC时间和处理时间信息

        Args:
            fit_files: fit文件名集合
            title: 显示标题
        """
        print(f"\n{title}:")
        print("-" * 180)

        if not fit_files:
            print("未找到匹配的FIT文件")
            return

        # 转换为排序的列表
        sorted_files = sorted(list(fit_files))

        print(f"{'序号':<4} {'文件名':<35} {'系统':<6} {'天区索引':<8} {'坐标(RA, DEC)':<20} {'UTC时间':<19} {'开始时间':<23} {'结束时间':<23} {'处理时长':<12}")
        print("-" * 180)

        # 收集数据用于生成SSC文件
        ssc_data = []

        for i, filename in enumerate(sorted_files, 1):
            # 提取系统名称 - 默认显示
            system_name = self.extract_system_name_from_filename(filename)
            system_str = system_name if system_name else "N/A"

            # 提取天区索引 - 默认显示
            k_index = self.extract_k_index_from_filename(filename)
            k_index_str = k_index if k_index else "N/A"

            # 提取坐标信息 - 默认显示
            if k_index:
                coordinates = self.get_coordinates_for_k_index(k_index, system_str)
                coord_str = f"{coordinates[0]}, {coordinates[1]}" if coordinates else "坐标未找到"
            else:
                coord_str = "N/A"

            # 提取UTC时间 - 默认显示
            utc_raw = self.extract_utc_datetime_from_filename(filename)
            if utc_raw:
                utc_formatted = self.format_utc_datetime(utc_raw)
                utc_str = utc_formatted if utc_formatted else f"格式错误:{utc_raw}"
            else:
                utc_str = "时间未找到"

            # 提取处理时间信息
            start_time_str = "未记录"
            end_time_str = "未记录"
            duration_str = "N/A"

            if hasattr(self, 'fit_file_times') and filename in self.fit_file_times:
                time_info = self.fit_file_times[filename]
                start_time_str = time_info.get('start', '未记录')
                end_time_str = time_info.get('end', '未记录')

                # 计算时间差
                if 'start' in time_info and 'end' in time_info:
                    start_dt = self.parse_timestamp(time_info['start'])
                    end_dt = self.parse_timestamp(time_info['end'])
                    if start_dt and end_dt:
                        duration_str = self.calculate_time_difference(start_dt, end_dt)

            print(f"{i:<4} {filename:<35} {system_str:<6} {k_index_str:<8} {coord_str:<20} {utc_str:<19} {start_time_str:<23} {end_time_str:<23} {duration_str:<12}")

            # 收集数据用于SSC生成
            if k_index and coordinates and start_time_str != "未记录":
                ssc_data.append({
                    'filename': filename,
                    'system': system_str,
                    'k_index': k_index,
                    'ra': coordinates[0],
                    'dec': coordinates[1],
                    'utc_time': utc_str,
                    'start_time': start_time_str,
                    'end_time': end_time_str,
                    'duration': duration_str
                })

        print(f"\n总共找到 {len(fit_files)} 个唯一的FIT文件")

        # 生成SSC文件
        if ssc_data:
            self.generate_stellarium_script(ssc_data)
            self.generate_stellarium_utc_script(ssc_data)
        else:
            print("没有足够的数据生成Stellarium脚本")

    def search_fit_files_in_latest(self):
        """
        在最新的日志文件中搜索fit文件
        """
        latest_file = self.get_latest_file()
        if not latest_file:
            print("未找到最近30天内的日志文件")
            return

        # 清空时间信息
        self.fit_file_times = {}

        print(f"正在从最新日志文件中搜索FIT文件: {latest_file}")
        fit_files = self.extract_fit_files_from_log(latest_file)

        # 调试信息：显示收集到的时间信息
        print(f"调试: 收集到 {len(self.fit_file_times)} 个文件的时间信息")
        for filename, times in self.fit_file_times.items():
            print(f"  {filename}: {times}")

        self.display_fit_files(fit_files, f"从 {latest_file} 中找到的FIT文件")

        # 显示坐标分布摘要、时间分析、系统分析和处理时间分析
        if fit_files:
            self.display_coordinate_summary(fit_files)
            self.display_time_analysis(fit_files)
            self.display_system_analysis(fit_files)
            self.display_processing_time_analysis(fit_files)

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

        # 显示坐标分布摘要、时间分析、系统分析和处理时间分析
        if fit_files:
            self.display_coordinate_summary(fit_files)
            self.display_time_analysis(fit_files)
            self.display_system_analysis(fit_files)
            self.display_processing_time_analysis(fit_files)

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
            system_name = self.extract_system_name_from_filename(filename)
            if k_index:
                coordinates = self.get_coordinates_for_k_index(k_index, system_name)
                if coordinates:
                    coord_key = f"{coordinates[0]}, {coordinates[1]}"
                    if coord_key not in coord_groups:
                        coord_groups[coord_key] = []
                    coord_groups[coord_key].append(filename)

        return coord_groups

    def display_coordinate_summary(self, fit_files: Set[str]):
        """
        显示FIT文件的坐标分布摘要，包含系统名称和时间信息

        Args:
            fit_files: FIT文件名集合
        """
        coord_groups = self.analyze_fit_coordinates(fit_files)

        print(f"\n坐标分布摘要:")
        print("-" * 120)
        print(f"{'坐标(RA, DEC)':<20} {'文件数量':<8} {'系统':<10} {'天区索引':<15} {'时间范围':<35}")
        print("-" * 120)

        for coord, files in sorted(coord_groups.items()):
            # 收集系统名称
            systems = []
            # 收集天区索引
            k_indices = []
            # 收集时间信息
            times = []

            for filename in files:
                # 收集系统名称
                system_name = self.extract_system_name_from_filename(filename)
                if system_name and system_name not in systems:
                    systems.append(system_name)

                # 收集天区索引
                k_index = self.extract_k_index_from_filename(filename)
                if k_index and k_index not in k_indices:
                    k_indices.append(k_index)

                # 收集时间信息
                utc_raw = self.extract_utc_datetime_from_filename(filename)
                if utc_raw:
                    utc_formatted = self.format_utc_datetime(utc_raw)
                    if utc_formatted:
                        times.append(utc_formatted)

            systems_str = ", ".join(sorted(systems)) if systems else "N/A"
            k_indices_str = ", ".join(sorted(k_indices)) if k_indices else "N/A"

            # 时间范围信息
            if times:
                times.sort()
                if len(times) == 1:
                    time_range = times[0]
                else:
                    time_range = f"{times[0]} ~ {times[-1]}"
            else:
                time_range = "时间信息缺失"

            print(f"{coord:<20} {len(files):<8} {systems_str:<10} {k_indices_str:<15} {time_range:<35}")

        print(f"\n总共涉及 {len(coord_groups)} 个不同的坐标位置")

    def display_time_analysis(self, fit_files: Set[str]):
        """
        显示FIT文件的时间分析

        Args:
            fit_files: FIT文件名集合
        """
        time_data = []

        for filename in fit_files:
            utc_raw = self.extract_utc_datetime_from_filename(filename)
            if utc_raw:
                utc_formatted = self.format_utc_datetime(utc_raw)
                if utc_formatted:
                    time_data.append((filename, utc_raw, utc_formatted))

        if not time_data:
            print("\n未找到包含UTC时间信息的文件")
            return

        # 按时间排序
        time_data.sort(key=lambda x: x[1])

        print(f"\n时间分析 (按时间排序):")
        print("-" * 140)
        print(f"{'序号':<4} {'UTC时间':<19} {'文件名':<35} {'系统':<6} {'天区索引':<8} {'坐标(RA, DEC)':<20}")
        print("-" * 140)

        for i, (filename, utc_raw, utc_formatted) in enumerate(time_data, 1):
            # 获取系统名称
            system_name = self.extract_system_name_from_filename(filename)
            system_str = system_name if system_name else "N/A"

            # 获取天区索引和坐标信息
            k_index = self.extract_k_index_from_filename(filename)
            k_index_str = k_index if k_index else "N/A"
            system_name = self.extract_system_name_from_filename(filename)

            if k_index:
                coordinates = self.get_coordinates_for_k_index(k_index, system_name)
                coord_str = f"{coordinates[0]}, {coordinates[1]}" if coordinates else "坐标未找到"
            else:
                coord_str = "N/A"

            print(f"{i:<4} {utc_formatted:<19} {filename:<35} {system_str:<6} {k_index_str:<8} {coord_str:<20}")

        if len(time_data) > 1:
            earliest = time_data[0][2]
            latest = time_data[-1][2]
            print(f"\n时间范围: {earliest} 到 {latest}")
            print(f"总时间跨度: {len(time_data)} 个文件")

        # 按日期分组统计
        date_groups = {}
        for filename, utc_raw, utc_formatted in time_data:
            date_part = utc_formatted.split(' ')[0]  # 提取日期部分
            if date_part not in date_groups:
                date_groups[date_part] = []
            date_groups[date_part].append(filename)

        if len(date_groups) > 1:
            print(f"\n按日期分组:")
            print("-" * 40)
            for date, files in sorted(date_groups.items()):
                print(f"{date}: {len(files)} 个文件")

        print(f"\n总共 {len(time_data)} 个文件包含UTC时间信息")

    def display_system_analysis(self, fit_files: Set[str]):
        """
        显示系统分析统计

        Args:
            fit_files: FIT文件名集合
        """
        system_groups = {}

        for filename in fit_files:
            system_name = self.extract_system_name_from_filename(filename)
            system_key = system_name if system_name else "未知系统"

            if system_key not in system_groups:
                system_groups[system_key] = []
            system_groups[system_key].append(filename)

        print(f"\n系统分析统计:")
        print("-" * 80)
        print(f"{'系统名称':<10} {'文件数量':<8} {'天区数量':<8} {'坐标数量':<8} {'时间跨度':<30}")
        print("-" * 80)

        for system, files in sorted(system_groups.items()):
            # 统计天区数量
            k_indices = set()
            # 统计坐标数量
            coordinates = set()
            # 统计时间信息
            times = []

            for filename in files:
                k_index = self.extract_k_index_from_filename(filename)
                system_name = self.extract_system_name_from_filename(filename)
                if k_index:
                    k_indices.add(k_index)
                    coord = self.get_coordinates_for_k_index(k_index, system_name)
                    if coord:
                        coordinates.add(f"{coord[0]}, {coord[1]}")

                utc_raw = self.extract_utc_datetime_from_filename(filename)
                if utc_raw:
                    utc_formatted = self.format_utc_datetime(utc_raw)
                    if utc_formatted:
                        times.append(utc_formatted)

            # 时间跨度
            if times:
                times.sort()
                if len(times) == 1:
                    time_span = times[0]
                else:
                    time_span = f"{times[0]} ~ {times[-1]}"
            else:
                time_span = "无时间信息"

            print(f"{system:<10} {len(files):<8} {len(k_indices):<8} {len(coordinates):<8} {time_span:<30}")

        print(f"\n总共涉及 {len(system_groups)} 个系统")

    def display_processing_time_analysis(self, fit_files: Set[str]):
        """
        显示处理时间分析

        Args:
            fit_files: FIT文件名集合
        """
        if not hasattr(self, 'fit_file_times') or not self.fit_file_times:
            print(f"\n处理时间分析:")
            print("-" * 60)
            print("未找到包含开始/结束时间信息的文件")
            return

        processing_data = []

        for filename in fit_files:
            if filename in self.fit_file_times:
                time_info = self.fit_file_times[filename]
                start_time = time_info.get('start')
                end_time = time_info.get('end')

                if start_time and end_time:
                    start_dt = self.parse_timestamp(start_time)
                    end_dt = self.parse_timestamp(end_time)
                    if start_dt and end_dt:
                        duration = self.calculate_time_difference(start_dt, end_dt)
                        duration_seconds = (end_dt - start_dt).total_seconds()
                        processing_data.append((filename, start_time, end_time, duration, duration_seconds))

        if not processing_data:
            print(f"\n处理时间分析:")
            print("-" * 60)
            print("未找到完整的开始/结束时间对")
            return

        # 按处理时长排序
        processing_data.sort(key=lambda x: x[4])  # 按秒数排序

        print(f"\n处理时间分析 (按处理时长排序):")
        print("-" * 120)
        print(f"{'序号':<4} {'文件名':<35} {'开始时间':<23} {'结束时间':<23} {'处理时长':<15}")
        print("-" * 120)

        total_duration = 0
        for i, (filename, start_time, end_time, duration, duration_seconds) in enumerate(processing_data, 1):
            print(f"{i:<4} {filename:<35} {start_time:<23} {end_time:<23} {duration:<15}")
            total_duration += duration_seconds

        # 统计信息
        if processing_data:
            avg_duration = total_duration / len(processing_data)
            min_duration = min(processing_data, key=lambda x: x[4])
            max_duration = max(processing_data, key=lambda x: x[4])

            print(f"\n处理时间统计:")
            print("-" * 60)
            print(f"总文件数: {len(processing_data)}")
            print(f"总处理时间: {self.calculate_time_difference(datetime.min, datetime.min + timedelta(seconds=total_duration))}")
            print(f"平均处理时间: {self.calculate_time_difference(datetime.min, datetime.min + timedelta(seconds=avg_duration))}")
            print(f"最短处理时间: {min_duration[3]} ({min_duration[0]})")
            print(f"最长处理时间: {max_duration[3]} ({max_duration[0]})")

    def generate_stellarium_script(self, ssc_data: List[Dict], output_filename: str = "stellarium_log_generated.ssc"):
        """
        根据FIT文件数据生成Stellarium脚本

        Args:
            ssc_data: FIT文件数据列表
            output_filename: 输出文件名
        """
        if not ssc_data:
            print("没有数据可用于生成Stellarium脚本")
            return

        # 计算时间线
        timeline_data = self._calculate_timeline(ssc_data)

        # 生成脚本内容
        script_content = self._generate_script_content(timeline_data)

        # 保存文件
        output_path = os.path.join(os.path.dirname(__file__), output_filename)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            print(f"\n✅ Stellarium脚本已生成: {output_path}")
            print(f"📊 包含 {len(ssc_data)} 个FIT文件的处理状态")
            print(f"⏱️  时间尺度: 1秒 = 1分钟实际时间")
            print(f"🎯 使用方法: 在Stellarium中按F12打开脚本控制台，加载并运行此文件")
        except Exception as e:
            print(f"❌ 保存脚本文件时出错: {e}")

    def _calculate_timeline(self, ssc_data: List[Dict]) -> List[Dict]:
        """计算相对时间线"""
        if not ssc_data:
            return []

        # 找到最早的开始时间作为基准
        earliest_time = None
        for entry in ssc_data:
            if entry['start_time'] != "未记录":
                start_dt = self.parse_timestamp(entry['start_time'])
                if start_dt and (earliest_time is None or start_dt < earliest_time):
                    earliest_time = start_dt

        if not earliest_time:
            # 如果没有时间信息，使用模拟时间线
            for i, entry in enumerate(ssc_data):
                entry['relative_start'] = i * 60  # 每个文件间隔1分钟
                entry['relative_duration'] = 180  # 默认3分钟处理时间
            return ssc_data

        # 计算相对时间（以秒为单位，因为1秒=1分钟）
        for entry in ssc_data:
            if entry['start_time'] != "未记录":
                start_dt = self.parse_timestamp(entry['start_time'])
                if start_dt:
                    entry['relative_start'] = int((start_dt - earliest_time).total_seconds() / 60)
                else:
                    entry['relative_start'] = 0
            else:
                entry['relative_start'] = 0

            # 计算处理时长（转换为秒）
            if entry['end_time'] != "未记录" and entry['start_time'] != "未记录":
                start_dt = self.parse_timestamp(entry['start_time'])
                end_dt = self.parse_timestamp(entry['end_time'])
                if start_dt and end_dt:
                    duration_minutes = (end_dt - start_dt).total_seconds() / 60
                    entry['relative_duration'] = max(int(duration_minutes), 30)  # 最少30秒显示
                else:
                    entry['relative_duration'] = 180  # 默认3分钟
            else:
                entry['relative_duration'] = 180  # 默认3分钟

        return ssc_data

    def _generate_script_content(self, timeline_data: List[Dict]) -> str:
        """生成脚本内容"""
        # 处理重复的 region+system 组合，调整 DEC 坐标
        timeline_data = self._adjust_duplicate_coordinates(timeline_data)

        # 计算总时长
        max_end_time = 0
        for entry in timeline_data:
            end_time = entry['relative_start'] + entry['relative_duration']
            if end_time > max_end_time:
                max_end_time = end_time

        total_duration = max_end_time + 60  # 额外1分钟缓冲

        script_content = f'''// Stellarium 脚本：显示日志中 FIT 文件处理状态
// 自动生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 时间尺度：0.3秒 = 1分钟实际时间
// 数据来源：日志文件分析结果

LabelMgr.deleteAllLabels();

// 状态颜色定义
var colors = {{
    idle: "#666666",      // 灰色 - 空闲
    waiting: "#ffff00",   // 黄色 - 等待
    processing: "#ff8800", // 橙色 - 处理中
    completed: "#00ff00",  // 绿色 - 完成
    error: "#ff0000"      // 红色 - 错误
}};

// FIT文件处理时间线（从日志提取）
var fitTimeline = [
'''

        # 添加时间线数据
        for i, entry in enumerate(timeline_data):
            script_content += f'''    {{
        filename: "{entry['filename']}",
        region: "{entry['k_index']}",
        system: "{entry['system']}",
        ra: "{entry['ra']}",
        dec: "{entry['dec']}",
        utcTime: "{entry['utc_time']}",
        startTime: {entry['relative_start']},
        duration: {entry['relative_duration']}
    }}{"," if i < len(timeline_data) - 1 else ""}
'''

        script_content += f'''];

// 获取当前状态
function getStatus(entry, currentTime) {{
    if (currentTime < entry.startTime) {{
        return "idle";
    }} else if (currentTime < entry.startTime + 5) {{
        return "waiting";
    }} else if (currentTime < entry.startTime + entry.duration - 5) {{
        return "processing";
    }} else if (currentTime < entry.startTime + entry.duration) {{
        return "completed";
    }} else {{
        return "idle";
    }}
}}

// 获取进度百分比
function getProgress(entry, currentTime) {{
    if (currentTime <= entry.startTime + 5) return 0;
    if (currentTime >= entry.startTime + entry.duration - 5) return 100;

    var processTime = currentTime - entry.startTime - 5;
    var totalProcessTime = entry.duration - 10;
    return Math.floor((processTime / totalProcessTime) * 100);
}}

// 获取状态文本
function getStatusText(entry, status, progress) {{
    var baseText = entry.region + " [" + entry.system + "]";
    switch(status) {{
        case "waiting": return baseText + " 准备";
        case "processing": return baseText + " " + progress + "%";
        case "completed": return baseText + " 完成";
        case "error": return baseText + " 错误";
        default: return baseText;
    }}
}}

core.output("开始显示FIT文件处理状态");
core.output("数据来源：日志文件分析");
core.output("文件数量：{len(timeline_data)}个");
core.output("总时长：{total_duration}秒（{total_duration}分钟实际时间）");
core.output("时间尺度：0.3秒 = 1分钟");

// 存储上一次的状态，用于优化更新
var previousStates = {{}};
var previousStats = "";

// 主显示循环
for (var currentTime = 0; currentTime < {total_duration}; currentTime++) {{
    // 显示时间信息（每次更新）
    var hours = Math.floor(currentTime / 60);
    var minutes = currentTime % 60;
    var timeDisplay = "观测时间: " + hours + ":" + String(minutes).padStart(2, '0');
    LabelMgr.deleteLabel("时间");
    LabelMgr.labelEquatorial("时间", "12.00000h", "+85.0", true, 16, "#ffffff");

    // 统计状态
    var stats = {{idle: 0, waiting: 0, processing: 0, completed: 0}};
    var activeCount = 0;
    var currentStates = {{}};

    // 处理每个FIT文件
    for (var i = 0; i < fitTimeline.length; i++) {{
        var entry = fitTimeline[i];
        var status = getStatus(entry, currentTime);
        var progress = getProgress(entry, currentTime);
        var labelName = entry.system + "_" + entry.region + "_" + i;

        stats[status]++;
        currentStates[labelName] = {{status: status, progress: progress}};

        // 检查状态是否发生变化
        var needsUpdate = false;
        if (!previousStates[labelName]) {{
            needsUpdate = true;
        }} else {{
            var prevState = previousStates[labelName];
            if (prevState.status !== status || prevState.progress !== progress) {{
                needsUpdate = true;
            }}
        }}

        // 只在状态变化时更新标签
        if (needsUpdate) {{
            // 删除旧标签
            LabelMgr.deleteLabel(labelName);

            // 如果不是空闲状态，创建新标签
            if (status !== "idle") {{
                var color = colors[status];
                var text = getStatusText(entry, status, progress);

                LabelMgr.labelEquatorial(
                    labelName,
                    entry.ra,
                    entry.dec,
                    true,
                    12,
                    color
                );
            }}
        }}

        if (status !== "idle") {{
            activeCount++;
        }}
    }}

    // 更新统计信息（仅在变化时）
    var currentStatsText = "状态 - 等待:" + stats.waiting +
                          " 处理:" + stats.processing +
                          " 完成:" + stats.completed +
                          " 活跃:" + activeCount;

    if (currentStatsText !== previousStats) {{
        LabelMgr.deleteLabel("统计");
        LabelMgr.labelEquatorial("统计", "0.00000h", "+80.0", true, 12, "#cccccc");
        previousStats = currentStatsText;
    }}

    // 保存当前状态用于下次比较
    previousStates = currentStates;

    // 等待0.3秒
    core.wait(0.3);
}}

core.output("FIT文件处理状态显示完成");
core.output("所有文件处理完毕");
'''

        return script_content

    def generate_stellarium_utc_script(self, ssc_data: List[Dict], output_filename: str = "stellarium_utc_display.ssc"):
        """
        生成基于UTC时间的Stellarium脚本，所有标签都是绿色

        Args:
            ssc_data: FIT文件数据列表
            output_filename: 输出文件名
        """
        if not ssc_data:
            print("没有数据可用于生成UTC时间Stellarium脚本")
            return

        # 生成脚本内容
        script_content = self._generate_utc_script_content(ssc_data)

        # 保存文件
        output_path = os.path.join(os.path.dirname(__file__), output_filename)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            print(f"\n✅ UTC时间Stellarium脚本已生成: {output_path}")
            print(f"📊 包含 {len(ssc_data)} 个FIT文件的UTC时间显示")
            print(f"🎨 所有标签均为绿色显示")
            print(f"⏰ 使用实际UTC时间信息")
            print(f"🎯 使用方法: 在Stellarium中按F12打开脚本控制台，加载并运行此文件")
        except Exception as e:
            print(f"❌ 保存UTC时间脚本文件时出错: {e}")

    def _generate_utc_script_content(self, ssc_data: List[Dict]) -> str:
        """生成UTC时间脚本内容"""

        script_content = f'''// Stellarium 脚本：显示FIT文件UTC时间信息
// 自动生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 显示模式：所有标签绿色显示，按UTC时间顺序出现
// 时间尺度：1秒 = 10分钟实际时间
// 数据来源：日志文件分析结果

LabelMgr.deleteAllLabels();

// 绿色标签颜色
var greenColor = "#00ff00";

// FIT文件UTC时间数据（按时间排序）
var fitData = [
'''

        # 计算相对时间并排序数据
        timeline_data = self._calculate_utc_timeline(ssc_data)

        # 处理重复的 region+system 组合，调整 DEC 坐标
        timeline_data = self._adjust_duplicate_coordinates(timeline_data)

        # 添加排序后的数据
        for i, entry in enumerate(timeline_data):
            script_content += f'''    {{
        filename: "{entry['filename']}",
        region: "{entry['k_index']}",
        system: "{entry['system']}",
        ra: "{entry['ra']}",
        dec: "{entry['dec']}",
        utcTime: "{entry['utc_time']}",
        startTime: "{entry.get('start_time', 'N/A')}",
        endTime: "{entry.get('end_time', 'N/A')}",
        relativeTime: {entry['relative_time']}
    }}{"," if i < len(timeline_data) - 1 else ""}
'''

        # 计算总时长
        max_time = max(entry['relative_time'] for entry in timeline_data) if timeline_data else 0
        total_duration = max_time + 60  # 额外1分钟缓冲

        script_content += f'''];

core.output("开始显示FIT文件UTC时间信息");
core.output("显示模式：绿色标签按时间顺序出现");
core.output("文件数量：{len(timeline_data)}个");
core.output("时间尺度：1秒 = 10分钟实际时间");
core.output("总时长：{total_duration}秒");

// 存储已显示的标签
var displayedLabels = {{}};

// 主时间循环
for (var currentTime = 0; currentTime < {total_duration}; currentTime++) {{
    // 显示当前时间信息
    var hours = Math.floor(currentTime / 6);  // 6秒 = 1小时 (因为1秒=10分钟)
    var minutes = Math.floor((currentTime % 6) * 10);  // 转换为分钟
    var timeDisplay = "观测时间: " + hours + ":" + String(minutes).padStart(2, '0');
    LabelMgr.deleteLabel("时间");
    LabelMgr.labelEquatorial("时间", "12.00000h", "+85.0", true, 16, "#ffffff");

    var activeCount = 0;
    var newLabelsThisSecond = 0;

    // 检查是否有新的标签需要显示
    for (var i = 0; i < fitData.length; i++) {{
        var entry = fitData[i];
        var labelName = entry.system + "_" + entry.region + "_" + i;

        // 如果到了显示时间且还未显示
        if (currentTime >= entry.relativeTime && !displayedLabels[labelName]) {{
            var labelText = entry.system + "_" + entry.region + " [" + entry.utcTime + "]";

            // 创建绿色标签
            LabelMgr.labelEquatorial(
                labelName,
                entry.ra,
                entry.dec,
                true,
                12,
                greenColor
            );

            displayedLabels[labelName] = true;
            newLabelsThisSecond++;
        }}

        // 统计已显示的标签
        if (displayedLabels[labelName]) {{
            activeCount++;
        }}
    }}

    // 更新统计信息
    var statsText = "UTC时间显示 - 已显示:" + activeCount + "/" + fitData.length + " 全部绿色";
    LabelMgr.deleteLabel("统计");
    LabelMgr.labelEquatorial("统计", "0.00000h", "+80.0", true, 12, "#cccccc");

    // 如果有新标签出现，显示提示
    if (newLabelsThisSecond > 0) {{
        var newLabelText = "新增 " + newLabelsThisSecond + " 个标签";
        LabelMgr.deleteLabel("新增提示");
        LabelMgr.labelEquatorial("新增提示", "0.00000h", "+75.0", true, 10, "#ffff00");
    }} else {{
        LabelMgr.deleteLabel("新增提示");
    }}

    // 等待1秒（代表10分钟实际时间）
    core.wait(1);
}}

core.output("UTC时间显示完成");
core.output("所有" + fitData.length + "个文件均已按时间顺序显示");
'''

        return script_content

    def _calculate_utc_timeline(self, ssc_data: List[Dict]) -> List[Dict]:
        """
        计算基于UTC时间的相对时间线
        时间尺度：1秒 = 10分钟实际时间

        Args:
            ssc_data: FIT文件数据列表

        Returns:
            包含相对时间的排序数据列表
        """
        if not ssc_data:
            return []

        # 解析UTC时间并找到最早时间
        timeline_data = []
        earliest_time = None

        for entry in ssc_data:
            utc_str = entry.get('utc_time', '')
            if utc_str and utc_str != 'N/A':
                try:
                    # 解析UTC时间字符串 "2025-08-23 20:27:12"
                    utc_dt = datetime.strptime(utc_str, '%Y-%m-%d %H:%M:%S')

                    if earliest_time is None or utc_dt < earliest_time:
                        earliest_time = utc_dt

                    entry_copy = entry.copy()
                    entry_copy['utc_datetime'] = utc_dt
                    timeline_data.append(entry_copy)

                except ValueError as e:
                    print(f"警告：无法解析UTC时间 '{utc_str}': {e}")
                    # 如果无法解析时间，设置为相对时间0
                    entry_copy = entry.copy()
                    entry_copy['relative_time'] = 0
                    timeline_data.append(entry_copy)

        if not earliest_time:
            # 如果没有有效的UTC时间，按顺序分配时间
            for i, entry in enumerate(timeline_data):
                entry['relative_time'] = i * 60  # 每个文件间隔1分钟（6秒显示时间）
            return timeline_data

        # 计算相对时间（以秒为单位，1秒=10分钟）
        for entry in timeline_data:
            if 'utc_datetime' in entry:
                time_diff = entry['utc_datetime'] - earliest_time
                # 将时间差转换为秒（1秒=10分钟，所以除以600）
                entry['relative_time'] = int(time_diff.total_seconds() / 600)
            else:
                entry['relative_time'] = 0

        # 按相对时间排序
        timeline_data.sort(key=lambda x: x['relative_time'])

        return timeline_data

    def _adjust_duplicate_coordinates(self, timeline_data: List[Dict]) -> List[Dict]:
        """
        调整重复的 region+system 组合的 DEC 坐标
        每多一个重复的组合，DEC 坐标偏移 -0.01 度

        Args:
            timeline_data: 时间线数据列表

        Returns:
            调整后的时间线数据列表
        """
        if not timeline_data:
            return timeline_data

        # 创建数据副本以避免修改原始数据
        adjusted_data = []
        region_system_count = {}

        for entry in timeline_data:
            # 创建条目副本
            new_entry = entry.copy()

            region = entry.get('k_index', '')
            system = entry.get('system', '')
            key = f"{system}_{region}"

            # 统计出现次数
            if key not in region_system_count:
                region_system_count[key] = 0
                # 第一次出现，不调整坐标
                new_entry['dec_adjusted'] = False
                new_entry['dec_offset'] = 0.0
            else:
                # 重复出现，需要调整坐标
                region_system_count[key] += 1

                current_dec = entry.get('dec', '+0.0')

                # 解析 DEC 坐标
                try:
                    # 移除 '+' 符号并转换为浮点数
                    dec_value = float(current_dec.replace('+', ''))

                    # 计算偏移量：每个重复 -0.01 度
                    offset = region_system_count[key] * -0.01
                    new_dec_value = dec_value + offset

                    # 格式化新的 DEC 坐标
                    if new_dec_value >= 0:
                        new_entry['dec'] = f"+{new_dec_value:.2f}"
                    else:
                        new_entry['dec'] = f"{new_dec_value:.2f}"

                    # 记录调整信息
                    new_entry['dec_adjusted'] = True
                    new_entry['dec_offset'] = offset

                except ValueError as e:
                    print(f"警告：无法解析DEC坐标 '{current_dec}': {e}")
                    new_entry['dec_adjusted'] = False
                    new_entry['dec_offset'] = 0.0

            adjusted_data.append(new_entry)

        # 统计调整结果
        adjusted_count = sum(1 for entry in adjusted_data if entry.get('dec_adjusted', False))
        if adjusted_count > 0:
            print(f"📍 调整了 {adjusted_count} 个重复坐标的DEC偏移")

            # 显示调整详情
            for entry in adjusted_data:
                if entry.get('dec_adjusted', False):
                    print(f"   {entry['system']}_{entry['k_index']}: DEC偏移 {entry['dec_offset']:.2f}° → {entry['dec']}")

        return adjusted_data


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
                finder.display_time_analysis(fit_files)
                finder.display_system_analysis(fit_files)
                finder.display_processing_time_analysis(fit_files)

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
                finder.display_time_analysis(fit_files)
                finder.display_system_analysis(fit_files)
                finder.display_processing_time_analysis(fit_files)

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
                finder.display_time_analysis(fit_files)
                finder.display_system_analysis(fit_files)
                finder.display_processing_time_analysis(fit_files)

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

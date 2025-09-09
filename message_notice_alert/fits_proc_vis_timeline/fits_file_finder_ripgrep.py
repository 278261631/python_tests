#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FITS文件查找器 - Ripgrep版本
功能：使用python-ripgrep从指定的一组目录中查找匹配规则的文件
支持：Windows和Linux系统
配置：从配置文件加载目录和匹配规则（与原版共用fits_finder_config.json）
"""

import os
import sys
import json
import re
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

try:
    import python_ripgrep as ripgrep
except ImportError:
    print("错误: 需要安装 python-ripgrep")
    print("请运行: pip install python-ripgrep")
    sys.exit(1)


class FitsFileFinderRipgrep:
    """基于Ripgrep的FITS文件查找器类"""
    
    def __init__(self, config_file: str = "fits_finder_config.json", date_suffix: str = None, ignore_date: bool = False):
        """
        初始化文件查找器

        Args:
            config_file: 配置文件路径
            date_suffix: 日期后缀，格式为yyyymmdd，默认为当前日期
            ignore_date: 是否忽略日期后缀，直接搜索基础目录
        """
        self.config_file = config_file
        self.config = {}
        self.ignore_date = ignore_date
        self.date_suffix = date_suffix or datetime.now().strftime("%Y%m%d")
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('FitsFileFinderRipgrep')
        logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler('fits_finder_ripgrep.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        Returns:
            bool: 加载成功返回True，失败返回False
        """
        try:
            if not os.path.exists(self.config_file):
                self.logger.error(f"配置文件不存在: {self.config_file}")
                return False
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            # 验证配置文件格式
            if not self._validate_config():
                return False
                
            self.logger.info(f"成功加载配置文件: {self.config_file}")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件JSON格式错误: {e}")
            return False
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """
        验证配置文件格式
        
        Returns:
            bool: 验证通过返回True，否则返回False
        """
        required_keys = ['search_directories', 'file_patterns']
        
        for key in required_keys:
            if key not in self.config:
                self.logger.error(f"配置文件缺少必需的键: {key}")
                return False
        
        if not isinstance(self.config['search_directories'], list):
            self.logger.error("search_directories必须是列表类型")
            return False
            
        if not isinstance(self.config['file_patterns'], list):
            self.logger.error("file_patterns必须是列表类型")
            return False
            
        return True
    
    def _normalize_path(self, path: str) -> str:
        """
        标准化路径，兼容Windows和Linux

        Args:
            path: 原始路径

        Returns:
            str: 标准化后的路径
        """
        return str(Path(path).resolve())

    def _get_search_directories_with_date(self) -> List[str]:
        """
        获取搜索目录列表，根据ignore_date参数决定是否添加日期后缀

        Returns:
            List[str]: 搜索目录列表
        """
        base_directories = self.config.get('search_directories', [])

        if self.ignore_date:
            # 如果忽略日期，直接返回基础目录
            self.logger.debug("忽略日期后缀，使用基础目录")
            return base_directories

        directories_with_date = []
        for base_dir in base_directories:
            # 在每个搜索目录后添加日期后缀
            dir_with_date = os.path.join(base_dir, self.date_suffix)
            directories_with_date.append(dir_with_date)
            self.logger.debug(f"添加日期后缀: {base_dir} -> {dir_with_date}")

        return directories_with_date
    
    def _build_ripgrep_patterns(self) -> List[str]:
        """
        根据配置构建ripgrep搜索模式
        
        Returns:
            List[str]: ripgrep模式列表
        """
        patterns = []
        file_patterns = self.config.get('file_patterns', [])
        
        for pattern_config in file_patterns:
            pattern_type = pattern_config.get('type', 'glob')
            pattern_value = pattern_config.get('pattern', '')
            
            if pattern_type == 'glob':
                # 将glob模式转换为ripgrep的文件名模式
                patterns.append(pattern_value)
            elif pattern_type == 'regex':
                # 直接使用正则表达式
                patterns.append(pattern_value)
            elif pattern_type == 'exact':
                # 精确匹配转换为正则表达式
                escaped_pattern = re.escape(pattern_value)
                patterns.append(f"^{escaped_pattern}$")
            elif pattern_type == 'contains':
                # 包含匹配转换为正则表达式
                escaped_pattern = re.escape(pattern_value)
                patterns.append(f".*{escaped_pattern}.*")
        
        return patterns
    
    def _should_filter_path(self, path: str) -> bool:
        """
        检查路径是否应该被过滤掉
        
        Args:
            path: 文件路径
            
        Returns:
            bool: 如果路径应该被过滤返回True，否则返回False
        """
        path_filters = self.config.get('options', {}).get('path_filters', [])
        
        if not path_filters:
            return False
        
        # 标准化路径用于匹配
        normalized_path = path.replace('\\', '/')
        
        for filter_config in path_filters:
            filter_type = filter_config.get('type', 'regex')
            filter_pattern = filter_config.get('pattern', '')
            case_sensitive = filter_config.get('case_sensitive', False)
            
            if not case_sensitive:
                normalized_path_check = normalized_path.lower()
                filter_pattern_check = filter_pattern.lower()
            else:
                normalized_path_check = normalized_path
                filter_pattern_check = filter_pattern
            
            try:
                if filter_type == 'regex':
                    flags = 0 if case_sensitive else re.IGNORECASE
                    if re.search(filter_pattern_check, normalized_path_check, flags):
                        self.logger.debug(f"路径被过滤: {path} (匹配规则: {filter_pattern})")
                        return True
                elif filter_type == 'contains':
                    if filter_pattern_check in normalized_path_check:
                        self.logger.debug(f"路径被过滤: {path} (包含: {filter_pattern})")
                        return True
                elif filter_type == 'glob':
                    import fnmatch
                    if fnmatch.fnmatch(normalized_path_check, filter_pattern_check):
                        self.logger.debug(f"路径被过滤: {path} (glob匹配: {filter_pattern})")
                        return True
                        
            except Exception as e:
                self.logger.error(f"路径过滤规则错误: {e}")
                continue
        
        return False
    
    def _should_include_path(self, path: str) -> bool:
        """
        检查路径是否应该被包含（正向过滤）
        
        Args:
            path: 文件路径
            
        Returns:
            bool: 如果路径应该被包含返回True，否则返回False
        """
        path_includes = self.config.get('options', {}).get('path_includes', [])
        
        # 如果没有配置包含规则，则包含所有路径
        if not path_includes:
            return True
        
        # 标准化路径用于匹配
        normalized_path = path.replace('\\', '/')
        
        for include_config in path_includes:
            include_type = include_config.get('type', 'regex')
            include_pattern = include_config.get('pattern', '')
            case_sensitive = include_config.get('case_sensitive', False)
            
            if not case_sensitive:
                normalized_path_check = normalized_path.lower()
                include_pattern_check = include_pattern.lower()
            else:
                normalized_path_check = normalized_path
                include_pattern_check = include_pattern
            
            try:
                if include_type == 'regex':
                    flags = 0 if case_sensitive else re.IGNORECASE
                    if re.search(include_pattern_check, normalized_path_check, flags):
                        self.logger.debug(f"路径被包含: {path} (匹配规则: {include_pattern})")
                        return True
                elif include_type == 'contains':
                    if include_pattern_check in normalized_path_check:
                        self.logger.debug(f"路径被包含: {path} (包含: {include_pattern})")
                        return True
                elif include_type == 'glob':
                    import fnmatch
                    if fnmatch.fnmatch(normalized_path_check, include_pattern_check):
                        self.logger.debug(f"路径被包含: {path} (glob匹配: {include_pattern})")
                        return True
                        
            except Exception as e:
                self.logger.error(f"路径包含规则错误: {e}")
                continue
        
        # 如果有包含规则但都不匹配，则不包含此路径
        return False

    def extract_fits_info(self, file_path: str) -> Dict[str, Optional[str]]:
        """
        从FITS文件路径中提取天区索引、系统名称和时间信息

        Args:
            file_path: FITS文件路径

        Returns:
            Dict[str, Optional[str]]: 包含提取信息的字典
                - sky_region: 天区索引 (如 K088-3)
                - system_name: 系统名称 (如 GY2)
                - timestamp: 时间戳 (如 UTC20250421_170640)
                - original_path: 原始路径
        """
        result = {
            'sky_region': None,
            'system_name': None,
            'timestamp': None,
            'original_path': file_path
        }

        try:
            # 获取文件名（不包含扩展名）
            file_name = Path(file_path).stem

            # 正则表达式模式匹配
            # 匹配格式: GY2_K088-3_No Filter_60S_Bin2_UTC20250421_170640_-20C_
            # 或者: 系统名称_天区索引_其他信息_UTC时间戳_其他信息
            pattern = r'([A-Z0-9]+)_([K][0-9]+-[0-9]+)_.*_(UTC\d{8}_\d{6})_'

            match = re.search(pattern, file_name)
            if match:
                result['system_name'] = match.group(1)  # GY2
                result['sky_region'] = match.group(2)   # K088-3
                result['timestamp'] = match.group(3)    # UTC20250421_170640

                self.logger.debug(f"成功提取信息: {file_path} -> {result}")
            else:
                # 尝试更宽松的匹配模式
                # 匹配天区索引 K数字-数字
                sky_region_pattern = r'([K][0-9]+-[0-9]+)'
                sky_match = re.search(sky_region_pattern, file_name)
                if sky_match:
                    result['sky_region'] = sky_match.group(1)

                # 匹配UTC时间戳
                timestamp_pattern = r'(UTC\d{8}_\d{6})'
                time_match = re.search(timestamp_pattern, file_name)
                if time_match:
                    result['timestamp'] = time_match.group(1)

                # 尝试提取系统名称（文件名开头的字母数字组合）
                system_pattern = r'^([A-Z0-9]+)_'
                system_match = re.search(system_pattern, file_name)
                if system_match:
                    result['system_name'] = system_match.group(1)

                if any(result[key] for key in ['sky_region', 'system_name', 'timestamp']):
                    self.logger.debug(f"部分提取信息: {file_path} -> {result}")
                else:
                    self.logger.debug(f"无法提取信息: {file_path}")

        except Exception as e:
            self.logger.error(f"提取文件信息时出错 {file_path}: {e}")

        return result

    def extract_batch_fits_info(self, file_paths: List[str]) -> List[Dict[str, Optional[str]]]:
        """
        批量提取FITS文件信息

        Args:
            file_paths: FITS文件路径列表

        Returns:
            List[Dict[str, Optional[str]]]: 提取信息的列表
        """
        results = []
        for file_path in file_paths:
            info = self.extract_fits_info(file_path)
            results.append(info)

        return results

    def find_files(self) -> List[str]:
        """
        使用ripgrep查找匹配的文件

        Returns:
            List[str]: 匹配的文件路径列表
        """
        if not self.config:
            self.logger.error("配置未加载，请先调用load_config()")
            return []

        found_files = []
        search_directories = self._get_search_directories_with_date()
        patterns = self._build_ripgrep_patterns()

        if not patterns:
            self.logger.warning("没有找到有效的搜索模式")
            return []

        self.logger.info(f"开始搜索，目录数量: {len(search_directories)}, 模式数量: {len(patterns)}")
        if self.ignore_date:
            self.logger.info("忽略日期后缀，搜索所有基础目录")
        else:
            self.logger.info(f"使用日期后缀: {self.date_suffix}")

        for directory in search_directories:
            normalized_dir = self._normalize_path(directory)

            if not os.path.isdir(normalized_dir):
                self.logger.warning(f"目录不存在: {normalized_dir}")
                continue

            self.logger.info(f"搜索目录: {normalized_dir}")

            try:
                # 使用ripgrep搜索文件
                file_patterns = self.config.get('file_patterns', [])
                recursive = self.config.get('options', {}).get('recursive_search', True)

                for pattern_config in file_patterns:
                    pattern = pattern_config.get('pattern', '')
                    pattern_type = pattern_config.get('type', 'glob')

                    self.logger.debug(f"使用模式搜索: {pattern} (类型: {pattern_type})")

                    try:
                        # 使用python-ripgrep的files函数搜索文件
                        # 对于所有模式类型，都使用files函数搜索文件名
                        files_result = ripgrep.files(
                            patterns=[pattern],  # 注意这里是patterns列表
                            paths=[normalized_dir],  # 搜索路径列表
                            globs=[pattern] if pattern_type == 'glob' else None  # glob模式
                        )

                        for file_info in files_result:
                            # files函数返回的可能是字符串或字典
                            if isinstance(file_info, str):
                                file_path = file_info
                            elif isinstance(file_info, dict):
                                file_path = file_info.get('path', '')
                            else:
                                continue

                            if not file_path:
                                continue

                            # 应用路径过滤
                            if self._should_filter_path(file_path):
                                continue

                            # 应用路径包含过滤
                            if not self._should_include_path(file_path):
                                continue

                            if file_path not in found_files:
                                found_files.append(file_path)
                                self.logger.debug(f"找到匹配文件: {file_path}")

                    except Exception as e:
                        self.logger.error(f"执行ripgrep时出错: {e}")
                        continue
                        
            except Exception as e:
                self.logger.error(f"搜索目录时出错 {normalized_dir}: {e}")
                continue
        
        # 应用最大结果数限制
        max_results = self.config.get('options', {}).get('max_results', 10000)
        if len(found_files) > max_results:
            self.logger.warning(f"结果数量 ({len(found_files)}) 超过限制 ({max_results})，截取前 {max_results} 个结果")
            found_files = found_files[:max_results]
        
        self.logger.info(f"搜索完成，共找到 {len(found_files)} 个匹配文件")
        return found_files
    
    def save_results(self, files: List[str], output_file: str = None, include_extracted_info: bool = True) -> bool:
        """
        保存搜索结果到文件

        Args:
            files: 文件路径列表
            output_file: 输出文件路径，默认为None（自动生成）
            include_extracted_info: 是否包含提取的文件信息，默认为True

        Returns:
            bool: 保存成功返回True，否则返回False
        """
        if output_file is None:
            # 从配置文件获取输出路径，如果没有配置则使用默认路径
            config_output = self.config.get('options', {}).get('output_files', {}).get('search_results')
            if config_output:
                output_file = config_output
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"fits_search_results_ripgrep_{timestamp}.txt"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"FITS文件搜索结果 (Ripgrep版本)\n")
                f.write(f"搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"找到文件数量: {len(files)}\n")
                f.write("=" * 80 + "\n\n")

                if include_extracted_info and files:
                    # 提取文件信息并以表格形式保存
                    f.write("文件信息提取结果:\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"{'序号':<4} {'天区索引':<12} {'系统名称':<12} {'时间戳':<20} {'文件路径'}\n")
                    f.write("-" * 80 + "\n")

                    extracted_info = self.extract_batch_fits_info(files)
                    successful_extractions = 0

                    for i, info in enumerate(extracted_info, 1):
                        sky_region = info['sky_region'] or 'N/A'
                        system_name = info['system_name'] or 'N/A'
                        timestamp = info['timestamp'] or 'N/A'
                        file_path = info['original_path']

                        # 统计成功提取的数量
                        if any(info[key] for key in ['sky_region', 'system_name', 'timestamp']):
                            successful_extractions += 1

                        f.write(f"{i:<4} {sky_region:<12} {system_name:<12} {timestamp:<20} {file_path}\n")

                    f.write("-" * 80 + "\n")
                    f.write(f"信息提取统计: 总文件数={len(files)}, 成功提取={successful_extractions}, 成功率={successful_extractions/len(files)*100:.1f}%\n")
                    f.write("=" * 80 + "\n\n")

                # 保存完整的文件路径列表
                f.write("完整文件路径列表:\n")
                f.write("-" * 50 + "\n")
                for i, file_path in enumerate(files, 1):
                    f.write(f"{i:4d}. {file_path}\n")

            self.logger.info(f"搜索结果已保存到: {output_file}")

            # 默认生成Timeline格式的JavaScript文件（主要格式）
            # 从配置文件获取Timeline JS输出路径
            config_timeline_js_output = self.config.get('options', {}).get('output_files', {}).get('timeline_js')
            if config_timeline_js_output:
                timeline_js_output = config_timeline_js_output
                # 确保目录存在
                timeline_dir = os.path.dirname(timeline_js_output)
                if timeline_dir and not os.path.exists(timeline_dir):
                    os.makedirs(timeline_dir, exist_ok=True)
            else:
                # 如果配置文件中没有指定，使用默认命名规则
                timeline_js_output = output_file.replace('.txt', '.js')
                if timeline_js_output == output_file:  # 如果没有.txt扩展名
                    timeline_js_output = output_file + '.js'

            self.save_timeline_js(files, timeline_js_output)

            return True

        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            return False

    def convert_to_timeline_format(self, files: List[str]) -> List[Dict[str, Any]]:
        """
        将FITS文件信息转换为vis.js Timeline格式的JSON数据

        Args:
            files: 文件路径列表

        Returns:
            List[Dict[str, Any]]: Timeline格式的数据列表
        """
        timeline_data = []
        extracted_info = self.extract_batch_fits_info(files)

        for i, info in enumerate(extracted_info, 1):
            # 构建显示内容
            content_parts = []

            # 添加系统名称
            if info['system_name']:
                content_parts.append(f"{info['system_name']}")

            # 添加天区索引
            if info['sky_region']:
                content_parts.append(f"{info['sky_region']}")

            # 如果没有提取到有效信息，使用文件名
            if not content_parts:
                file_name = Path(info['original_path']).name
                content_parts.append(f"文件: {file_name}")

            content = "|".join(content_parts)

            # 处理时间戳
            start_time = None
            if info['timestamp']:
                try:
                    # 解析UTC时间戳格式: UTC20250421_170640
                    timestamp_str = info['timestamp'].replace('UTC', '')
                    date_part = timestamp_str[:8]  # 20250421
                    time_part = timestamp_str[9:]  # 170640

                    # 构建ISO格式的日期时间字符串
                    year = date_part[:4]
                    month = date_part[4:6]
                    day = date_part[6:8]
                    hour = time_part[:2]
                    minute = time_part[2:4]
                    second = time_part[4:6]

                    start_time = f"{year}-{month}-{day}T{hour}:{minute}:{second}"

                except Exception as e:
                    self.logger.debug(f"时间戳解析失败 {info['timestamp']}: {e}")
                    start_time = None

            # 如果没有时间戳，使用序号作为时间轴位置
            if not start_time:
                # 使用当前日期加上序号作为偏移
                base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                offset_date = base_date + timedelta(days=i-1)
                start_time = offset_date.strftime("%Y-%m-%d")

            # 构建Timeline数据项
            timeline_item = {
                "id": i,
                "content": content,
                "start": start_time
            }

            # 添加额外信息作为自定义属性
            if info['sky_region']:
                timeline_item["sky_region"] = info['sky_region']
            if info['system_name']:
                timeline_item["system_name"] = info['system_name']
            if info['timestamp']:
                timeline_item["timestamp"] = info['timestamp']

            # 添加文件路径信息
            timeline_item["file_path"] = info['original_path']
            timeline_item["file_name"] = Path(info['original_path']).name

            # 根据系统名称设置不同的类型或样式
            if info['system_name']:
                timeline_item["className"] = f"system-{info['system_name'].lower()}"

            timeline_data.append(timeline_item)

        return timeline_data

    def save_timeline_json(self, files: List[str], output_file: str = None) -> bool:
        """
        将搜索结果保存为vis.js Timeline格式的JSON文件

        Args:
            files: 文件路径列表
            output_file: 输出文件路径，默认为None（自动生成）

        Returns:
            bool: 保存成功返回True，否则返回False
        """
        if output_file is None:
            # 从配置文件获取Timeline JSON输出路径
            config_timeline_output = self.config.get('options', {}).get('output_files', {}).get('timeline_json')
            if config_timeline_output:
                output_file = config_timeline_output
                # 确保目录存在
                timeline_dir = os.path.dirname(output_file)
                if timeline_dir and not os.path.exists(timeline_dir):
                    os.makedirs(timeline_dir, exist_ok=True)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"fits_timeline_data_{timestamp}.json"

        try:
            timeline_data = self.convert_to_timeline_format(files)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(timeline_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"Timeline格式数据已保存到: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"保存Timeline格式数据失败: {e}")
            return False

    def save_timeline_js(self, files: List[str], output_file: str = None) -> bool:
        """
        将搜索结果保存为vis.js Timeline格式的JavaScript文件

        Args:
            files: 文件路径列表
            output_file: 输出文件路径，默认为None（自动生成）

        Returns:
            bool: 保存成功返回True，否则返回False
        """
        if output_file is None:
            # 从配置文件获取Timeline JS输出路径
            config_timeline_output = self.config.get('options', {}).get('output_files', {}).get('timeline_js')
            if config_timeline_output:
                output_file = config_timeline_output
                # 确保目录存在
                timeline_dir = os.path.dirname(output_file)
                if timeline_dir and not os.path.exists(timeline_dir):
                    os.makedirs(timeline_dir, exist_ok=True)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"fits_data_{timestamp}.js"

        try:
            timeline_data = self.convert_to_timeline_format(files)

            # 生成JavaScript文件内容
            js_content = f'''// FITS 数据 - 由 fits_file_finder_ripgrep.py 自动生成
// 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 记录数量: {len(timeline_data)}
// 搜索目录: {', '.join(self.config.get('search_directories', []))}

var fitsData = {json.dumps(timeline_data, ensure_ascii=False, indent=2)};

// 数据统计信息
console.log('FITS 数据已加载，共 ' + fitsData.length + ' 条记录');

// 数据按系统分组统计
var systemStats = {{}};
fitsData.forEach(function(item) {{
    var system = item.system_name || 'Unknown';
    systemStats[system] = (systemStats[system] || 0) + 1;
}});
console.log('系统分布:', systemStats);
'''

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(js_content)

            self.logger.info(f"Timeline JavaScript格式数据已保存到: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"保存Timeline JavaScript格式数据失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='FITS文件查找器 (Ripgrep版本)')
    parser.add_argument('-c', '--config', default='fits_finder_config.json',
                       help='配置文件路径 (默认: fits_finder_config.json)')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    parser.add_argument('--extract-info', action='store_true',
                       help='提取并显示FITS文件的天区索引、系统名称和时间信息')
    parser.add_argument('-d', '--date', help='日期后缀，格式为yyyymmdd (默认: 当前日期)')
    parser.add_argument('-all', '--all', action='store_true',
                       help='忽略指定的日期，搜索所有基础目录')

    args = parser.parse_args()

    # 创建查找器实例
    finder = FitsFileFinderRipgrep(args.config, args.date, args.all)
    
    # 设置日志级别
    if args.verbose:
        finder.logger.setLevel(logging.DEBUG)
    
    # 加载配置
    if not finder.load_config():
        print(f"错误: 无法加载配置文件 {args.config}")
        sys.exit(1)
    
    # 查找文件
    found_files = finder.find_files()
    
    # 显示结果
    print(f"\n搜索完成！找到 {len(found_files)} 个匹配文件:")

    if args.extract_info and found_files:
        # 提取并显示文件信息
        print("\n提取的文件信息:")
        print("-" * 80)
        print(f"{'序号':<4} {'天区索引':<10} {'系统名称':<10} {'时间戳':<20} {'文件路径'}")
        print("-" * 80)

        extracted_info = finder.extract_batch_fits_info(found_files)
        for i, info in enumerate(extracted_info, 1):
            sky_region = info['sky_region'] or 'N/A'
            system_name = info['system_name'] or 'N/A'
            timestamp = info['timestamp'] or 'N/A'
            file_path = Path(info['original_path']).name  # 只显示文件名

            print(f"{i:<4} {sky_region:<10} {system_name:<10} {timestamp:<20} {file_path}")
    else:
        # 普通显示模式
        for i, file_path in enumerate(found_files, 1):
            print(f"{i:4d}. {file_path}")

    # 保存结果（默认包含提取信息和Timeline格式）
    if found_files:
        finder.save_results(found_files, args.output)


if __name__ == "__main__":
    main()

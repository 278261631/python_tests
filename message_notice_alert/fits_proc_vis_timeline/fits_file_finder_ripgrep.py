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
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import python_ripgrep as ripgrep
except ImportError:
    print("错误: 需要安装 python-ripgrep")
    print("请运行: pip install python-ripgrep")
    sys.exit(1)


class FitsFileFinderRipgrep:
    """基于Ripgrep的FITS文件查找器类"""
    
    def __init__(self, config_file: str = "fits_finder_config.json"):
        """
        初始化文件查找器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = {}
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
        search_directories = self.config['search_directories']
        patterns = self._build_ripgrep_patterns()
        
        if not patterns:
            self.logger.warning("没有找到有效的搜索模式")
            return []
        
        self.logger.info(f"开始搜索，目录数量: {len(search_directories)}, 模式数量: {len(patterns)}")
        
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
    
    def save_results(self, files: List[str], output_file: str = None) -> bool:
        """
        保存搜索结果到文件
        
        Args:
            files: 文件路径列表
            output_file: 输出文件路径，默认为None（自动生成）
            
        Returns:
            bool: 保存成功返回True，否则返回False
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"fits_search_results_ripgrep_{timestamp}.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"FITS文件搜索结果 (Ripgrep版本)\n")
                f.write(f"搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"找到文件数量: {len(files)}\n")
                f.write("-" * 50 + "\n\n")
                
                for i, file_path in enumerate(files, 1):
                    f.write(f"{i:4d}. {file_path}\n")
            
            self.logger.info(f"搜索结果已保存到: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='FITS文件查找器 (Ripgrep版本)')
    parser.add_argument('-c', '--config', default='fits_finder_config.json',
                       help='配置文件路径 (默认: fits_finder_config.json)')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    # 创建查找器实例
    finder = FitsFileFinderRipgrep(args.config)
    
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
    for i, file_path in enumerate(found_files, 1):
        print(f"{i:4d}. {file_path}")
    
    # 保存结果
    if found_files:
        finder.save_results(found_files, args.output)


if __name__ == "__main__":
    main()

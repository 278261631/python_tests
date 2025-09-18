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
import shutil
import tarfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

try:
    import python_ripgrep as ripgrep
except ImportError:
    print("错误: 需要安装 python-ripgrep")
    print("请运行: pip install python-ripgrep")
    sys.exit(1)

try:
    from astropy.io import fits
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image
    PLOT_AVAILABLE = True
except ImportError:
    print("警告: 图像处理库未安装，无法生成缩略图和中心区域图")
    print("请运行: pip install astropy matplotlib numpy pillow")
    PLOT_AVAILABLE = False

# 设置matplotlib不显示图形窗口
if PLOT_AVAILABLE:
    plt.switch_backend('Agg')


class FitsFileFinderRipgrep:
    """基于Ripgrep的FITS文件查找器类"""
    
    def __init__(self, config_file: str = "fits_finder_config.json", date_suffix: str = None, ignore_date: bool = False, output_dir: str = None, enable_log_file: bool = False):
        """
        初始化文件查找器

        Args:
            config_file: 配置文件路径，如果是相对路径，则相对于脚本文件所在目录
            date_suffix: 日期后缀，格式为yyyymmdd，默认为当前日期
            ignore_date: 是否忽略日期后缀，直接搜索基础目录
            output_dir: 输出目录路径，如果为None则默认使用"dest"目录
            enable_log_file: 是否启用日志文件输出，默认为False
        """
        # 处理配置文件路径：如果是相对路径，则相对于脚本文件所在目录
        if not os.path.isabs(config_file):
            # 获取当前脚本文件所在目录
            script_dir = Path(__file__).parent
            self.config_file = str(script_dir / config_file)
        else:
            self.config_file = config_file
        self.config = {}
        self.ignore_date = ignore_date
        self.date_suffix = date_suffix or datetime.now().strftime("%Y%m%d")
        # 如果没有指定输出目录，默认使用"dest"目录
        self.output_dir = output_dir or "dest"
        self.enable_log_file = enable_log_file
        self.logger = self._setup_logger()

        # 生成运行时间戳，用于文件命名
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 图像目录 - 存储缩略图和中心区域图，包含运行时间戳以匹配HTML文件名
        self.image_dir = os.path.join(self.output_dir, f"images_{self.run_timestamp}")
        # 注意：只有在需要生成图像时才创建目录

    def _ensure_image_dir_exists(self) -> bool:
        """
        确保图像目录存在，只有在需要生成图像时才调用此方法

        Returns:
            bool: 目录创建成功返回True，失败返回False
        """
        try:
            os.makedirs(self.image_dir, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"创建图像目录失败: {e}")
            return False

    def _generate_timestamped_filename(self, base_name: str, extension: str) -> str:
        """
        生成带时间戳和参数的文件名

        Args:
            base_name: 基础文件名（如 "fitsUsage", "fits_data"）
            extension: 文件扩展名（如 ".html", ".js"）

        Returns:
            str: 带时间戳的文件名
        """
        # 确定参数部分
        if self.ignore_date:
            param_part = "all"
        else:
            param_part = self.date_suffix

        # 生成文件名：base_name_param_timestamp.extension
        return f"{base_name}_{param_part}_{self.run_timestamp}{extension}"

    def _update_html_file_references(self, html_file_path: Path, js_filename: str, css_filename: str, vis_js_filename: str, sky_region_js_filename: str = "kats_sky_region.js") -> bool:
        """
        更新HTML文件中的CSS和JS文件引用

        Args:
            html_file_path: HTML文件路径
            js_filename: JS数据文件名
            css_filename: CSS文件名
            vis_js_filename: vis.js文件名
            sky_region_js_filename: kats_sky_region.js文件名

        Returns:
            bool: 更新成功返回True，失败返回False
        """
        try:
            # 读取HTML文件内容
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # 替换文件引用
            html_content = html_content.replace('src="fits_data.js"', f'src="{js_filename}"')
            html_content = html_content.replace('href="vis.css"', f'href="{css_filename}"')
            html_content = html_content.replace('src="vis.js"', f'src="{vis_js_filename}"')
            html_content = html_content.replace('src="kats_sky_region.js"', f'src="{sky_region_js_filename}"')

            # 写回文件
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info(f"已更新HTML文件引用: {html_file_path}")
            return True

        except Exception as e:
            self.logger.error(f"更新HTML文件引用失败: {e}")
            return False

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('FitsFileFinderRipgrep')
        logger.setLevel(logging.INFO)

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        # 添加控制台处理器
        logger.addHandler(console_handler)

        # 只有在启用日志文件时才创建文件处理器
        if self.enable_log_file:
            # 确保输出目录存在
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 创建文件处理器，日志文件放到输出目录中
            log_file_path = output_path / 'fits_finder_ripgrep.log'
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            # 添加文件处理器
            logger.addHandler(file_handler)

        return logger

    def copy_html_template_files(self, dest_dir: str = None) -> dict:
        """
        拷贝HTML模板文件到指定目录

        Args:
            dest_dir: 目标目录，如果为None则使用self.output_dir

        Returns:
            dict: 包含生成的文件名信息，格式为 {"success": bool, "files": {"html": str, "css": str, "js": str}}
        """
        if dest_dir is None:
            dest_dir = self.output_dir

        if not dest_dir:
            self.logger.warning("未指定输出目录，跳过HTML模板文件拷贝")
            return {"success": False, "files": {}}

        try:
            # 获取当前脚本所在目录
            script_dir = Path(__file__).parent
            template_dir = script_dir / "html_template"

            if not template_dir.exists():
                self.logger.error(f"HTML模板目录不存在: {template_dir}")
                return {"success": False, "files": {}}

            # 确保目标目录存在
            dest_path = Path(dest_dir)
            dest_path.mkdir(parents=True, exist_ok=True)

            # 拷贝模板文件，HTML文件使用带时间戳的文件名，CSS和JS文件保持原名
            template_files = [
                ("fitsUsage.html", "fitsUsage", ".html"),
                ("vis.css", "vis", ".css"),
                ("vis.js", "vis", ".js"),
                ("kats_sky_region.js", "kats_sky_region", ".js")
            ]
            copied_files = []
            skipped_files = []
            generated_files = {}  # 记录生成的文件名

            for template_file, base_name, extension in template_files:
                src_file = template_dir / template_file

                # 只有HTML文件使用时间戳，CSS和JS文件保持原名
                if template_file == "fitsUsage.html":
                    timestamped_filename = self._generate_timestamped_filename(base_name, extension)
                else:
                    # CSS和JS文件保持原名
                    timestamped_filename = template_file

                dest_file = dest_path / timestamped_filename

                if not src_file.exists():
                    self.logger.warning(f"模板文件不存在: {src_file}")
                    continue

                # HTML文件总是拷贝（因为文件名包含时间戳），CSS和JS文件检查是否存在
                if template_file == "fitsUsage.html":
                    # HTML文件总是拷贝
                    should_copy = True
                else:
                    # CSS和JS文件检查是否存在
                    if dest_file.exists():
                        self.logger.info(f"文件已存在，跳过: {dest_file}")
                        skipped_files.append(timestamped_filename)
                        # 记录已存在的文件名
                        if template_file == "vis.css":
                            generated_files["css"] = timestamped_filename
                        elif template_file == "vis.js":
                            generated_files["vis_js"] = timestamped_filename
                        elif template_file == "kats_sky_region.js":
                            generated_files["sky_region_js"] = timestamped_filename
                        continue
                    should_copy = True

                if should_copy:
                    try:
                        shutil.copy2(src_file, dest_file)
                        copied_files.append(timestamped_filename)
                        self.logger.info(f"已拷贝: {src_file} -> {dest_file}")

                        # 记录生成的文件名
                        if template_file == "fitsUsage.html":
                            generated_files["html"] = timestamped_filename
                        elif template_file == "vis.css":
                            generated_files["css"] = timestamped_filename
                        elif template_file == "vis.js":
                            generated_files["vis_js"] = timestamped_filename
                        elif template_file == "kats_sky_region.js":
                            generated_files["sky_region_js"] = timestamped_filename

                    except Exception as e:
                        self.logger.error(f"拷贝文件失败 {src_file} -> {dest_file}: {e}")

            self.logger.info(f"HTML模板文件拷贝完成: 拷贝 {len(copied_files)} 个文件，跳过 {len(skipped_files)} 个文件")
            if copied_files:
                self.logger.info(f"已拷贝的文件: {', '.join(copied_files)}")
            if skipped_files:
                self.logger.info(f"已跳过的文件: {', '.join(skipped_files)}")

            return {"success": True, "files": generated_files}

        except Exception as e:
            self.logger.error(f"拷贝HTML模板文件失败: {e}")
            return {"success": False, "files": {}}

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

    def _normalize_image_data(self, data: np.ndarray) -> np.ndarray:
        """
        对FITS图像数据进行归一化处理
        
        Args:
            data: 原始FITS图像数据
        
        Returns:
            np.ndarray: 归一化后的图像数据 (0-255范围的uint8)
        """
        # 移除NaN和无穷大值
        data = np.nan_to_num(data)
        
        # 计算数据的最小值和最大值（排除异常值）
        min_val = np.percentile(data, 1)
        max_val = np.percentile(data, 99)
        
        # 确保最大值大于最小值
        if max_val <= min_val:
            max_val = min_val + 1
        
        # 归一化到0-255范围
        normalized = (data - min_val) / (max_val - min_val)
        normalized = np.clip(normalized * 255, 0, 255).astype(np.uint8)
        
        return normalized

    def _create_thumbnail(self, fits_path: str, thumbnail_path: str, size: tuple = (512, 512)) -> Optional[str]:
        """
        为FITS文件创建缩略图
        
        Args:
            fits_path: FITS文件路径
            thumbnail_path: 缩略图保存路径
            size: 缩略图尺寸
        
        Returns:
            Optional[str]: 缩略图保存路径，如果创建失败返回None
        """
        if not PLOT_AVAILABLE:
            self.logger.warning("图像处理库未安装，跳过缩略图生成")
            return None
        
        try:
            # 打开FITS文件并读取数据
            with fits.open(fits_path) as hdul:
                # 假设第一个HDU包含图像数据
                if len(hdul) > 0:
                    image_data = hdul[0].data
                    
                    # 检查数据类型
                    if image_data is None:
                        self.logger.warning(f"FITS文件中没有图像数据: {fits_path}")
                        return None
                    
                    # 如果是3D数据（例如带有颜色通道），取第一个通道
                    if len(image_data.shape) > 2:
                        image_data = image_data[0]
                    
                    # 归一化图像数据
                    normalized_data = self._normalize_image_data(image_data)
                    
                    # 创建PIL图像
                    img = Image.fromarray(normalized_data)
                    
                    # 调整大小为缩略图尺寸
                    # 兼容不同版本的Pillow
                    try:
                        # Pillow >= 10.0.0
                        thumbnail_img = img.resize(size, Image.Resampling.LANCZOS)
                    except AttributeError:
                        # Pillow < 10.0.0
                        thumbnail_img = img.resize(size, Image.LANCZOS)
                    
                    # 确保图像目录存在
                    if not self._ensure_image_dir_exists():
                        return None
                    
                    # 保存缩略图
                    thumbnail_img.save(thumbnail_path)
                    
                    self.logger.debug(f"已生成缩略图: {thumbnail_path}")
                    return thumbnail_path
                else:
                    self.logger.warning(f"FITS文件为空: {fits_path}")
                    return None
        except Exception as e:
            self.logger.error(f"生成缩略图失败 {fits_path}: {e}")
            return None

    def _create_center_crop(self, fits_path: str, crop_path: str, size: tuple = (200, 200)) -> Optional[str]:
        """
        提取FITS文件的中心区域并保存为图像
        
        Args:
            fits_path: FITS文件路径
            crop_path: 中心区域图保存路径
            size: 中心区域图尺寸
        
        Returns:
            Optional[str]: 中心区域图保存路径，如果创建失败返回None
        """
        if not PLOT_AVAILABLE:
            self.logger.warning("图像处理库未安装，跳过中心区域图生成")
            return None
        
        try:
            # 打开FITS文件并读取数据
            with fits.open(fits_path) as hdul:
                # 假设第一个HDU包含图像数据
                if len(hdul) > 0:
                    image_data = hdul[0].data
                    
                    # 检查数据类型
                    if image_data is None:
                        self.logger.warning(f"FITS文件中没有图像数据: {fits_path}")
                        return None
                    
                    # 如果是3D数据（例如带有颜色通道），取第一个通道
                    if len(image_data.shape) > 2:
                        image_data = image_data[0]
                    
                    # 计算中心坐标
                    height, width = image_data.shape
                    center_y, center_x = height // 2, width // 2
                    
                    # 计算裁剪区域
                    crop_height, crop_width = size
                    half_height, half_width = crop_height // 2, crop_width // 2
                    
                    # 确保裁剪区域在图像范围内
                    start_y = max(0, center_y - half_height)
                    end_y = min(height, center_y + half_height)
                    start_x = max(0, center_x - half_width)
                    end_x = min(width, center_x + half_width)
                    
                    # 提取中心区域
                    center_data = image_data[start_y:end_y, start_x:end_x]
                    
                    # 归一化图像数据
                    normalized_data = self._normalize_image_data(center_data)
                    
                    # 创建PIL图像
                    img = Image.fromarray(normalized_data)
                    
                    # 如果裁剪区域小于目标尺寸，调整大小
                    if img.size != size:
                        # 兼容不同版本的Pillow
                        try:
                            # Pillow >= 10.0.0
                            img = img.resize(size, Image.Resampling.LANCZOS)
                        except AttributeError:
                            # Pillow < 10.0.0
                            img = img.resize(size, Image.LANCZOS)
                    
                    # 确保图像目录存在
                    if not self._ensure_image_dir_exists():
                        return None
                    
                    # 保存中心区域图
                    img.save(crop_path)
                    
                    self.logger.debug(f"已生成中心区域图: {crop_path}")
                    return crop_path
                else:
                    self.logger.warning(f"FITS文件为空: {fits_path}")
                    return None
        except Exception as e:
            self.logger.error(f"生成中心区域图失败 {fits_path}: {e}")
            return None

    def process_fits_image(self, fits_path: str, create_thumbnail: bool = True, create_center_crop: bool = True) -> Dict[str, Optional[str]]:
        """
        处理单个FITS文件，生成缩略图和中心区域图

        Args:
            fits_path: FITS文件路径
            create_thumbnail: 是否创建缩略图
            create_center_crop: 是否创建中心区域图

        Returns:
            Dict[str, Optional[str]]: 包含图像路径的字典，包含绝对路径和相对路径
        """
        result = {
            'thumbnail': None,
            'center_crop': None,
            'thumbnail_relative': None,
            'center_crop_relative': None
        }

        # 为图像生成唯一的文件名
        file_name = Path(fits_path).stem
        base_name = f"{file_name}"

        # 生成缩略图
        if create_thumbnail:
            thumbnail_path = os.path.join(self.image_dir, f"{base_name}_thumbnail.jpg")
            absolute_path = self._create_thumbnail(fits_path, thumbnail_path)
            if absolute_path:
                result['thumbnail'] = absolute_path
                # 生成相对于输出目录的相对路径
                try:
                    output_dir_path = Path(self.output_dir).resolve()
                    thumbnail_abs_path = Path(absolute_path).resolve()
                    # 将Windows路径分隔符转换为URL路径分隔符
                    result['thumbnail_relative'] = str(thumbnail_abs_path.relative_to(output_dir_path)).replace('\\', '/')
                except ValueError:
                    # 如果无法生成相对路径，使用文件名
                    result['thumbnail_relative'] = f"images_{self.run_timestamp}/{base_name}_thumbnail.jpg"

        # 生成中心区域图
        if create_center_crop:
            center_crop_path = os.path.join(self.image_dir, f"{base_name}_center.jpg")
            absolute_path = self._create_center_crop(fits_path, center_crop_path)
            if absolute_path:
                result['center_crop'] = absolute_path
                # 生成相对于输出目录的相对路径
                try:
                    output_dir_path = Path(self.output_dir).resolve()
                    center_abs_path = Path(absolute_path).resolve()
                    # 将Windows路径分隔符转换为URL路径分隔符
                    result['center_crop_relative'] = str(center_abs_path.relative_to(output_dir_path)).replace('\\', '/')
                except ValueError:
                    # 如果无法生成相对路径，使用文件名
                    result['center_crop_relative'] = f"images_{self.run_timestamp}/{base_name}_center.jpg"

        return result

    def batch_process_fits_images(self, fits_files: List[str], create_thumbnail: bool = True, create_center_crop: bool = True, max_workers: int = 20) -> Dict[str, Dict[str, Optional[str]]]:
        """
        批量处理FITS文件，为每个文件生成缩略图和中心区域图（多线程版本）

        Args:
            fits_files: FITS文件路径列表
            create_thumbnail: 是否创建缩略图
            create_center_crop: 是否创建中心区域图
            max_workers: 最大线程数，默认为20

        Returns:
            Dict[str, Dict[str, Optional[str]]]: 以FITS文件路径为键，包含图像路径的字典
        """
        results = {}

        total_files = len(fits_files)
        self.logger.info(f"开始批量处理 {total_files} 个FITS文件的图像（使用 {max_workers} 个线程）")

        # 确保图像目录存在
        if not self._ensure_image_dir_exists():
            self.logger.error("无法创建图像目录，跳过图像生成")
            return {}

        # 使用线程锁保护进度计数器
        progress_lock = threading.Lock()
        completed_count = [0]  # 使用列表以便在闭包中修改

        def process_single_image(fits_file: str) -> Tuple[str, Dict[str, Optional[str]]]:
            """处理单个FITS文件图像的内部函数"""
            try:
                image_paths = self.process_fits_image(fits_file, create_thumbnail, create_center_crop)

                # 更新进度
                with progress_lock:
                    completed_count[0] += 1
                    current_count = completed_count[0]
                    if current_count % 10 == 0 or current_count == total_files:
                        self.logger.info(f"处理进度: {current_count}/{total_files}")

                return fits_file, image_paths
            except Exception as e:
                self.logger.error(f"处理图像文件 {fits_file} 时出错: {e}")
                # 返回空结果
                empty_result = {
                    'thumbnail': None,
                    'center_crop': None,
                    'thumbnail_relative': None,
                    'center_crop_relative': None
                }

                # 更新进度
                with progress_lock:
                    completed_count[0] += 1
                    current_count = completed_count[0]
                    if current_count % 10 == 0 or current_count == total_files:
                        self.logger.info(f"处理进度: {current_count}/{total_files}")

                return fits_file, empty_result

        # 使用ThreadPoolExecutor进行多线程处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {executor.submit(process_single_image, fits_file): fits_file
                             for fits_file in fits_files}

            # 收集结果
            for future in as_completed(future_to_file):
                try:
                    fits_file, image_paths = future.result()
                    results[fits_file] = image_paths
                except Exception as e:
                    fits_file = future_to_file[future]
                    self.logger.error(f"获取文件 {fits_file} 处理结果时出错: {e}")
                    # 添加空结果
                    results[fits_file] = {
                        'thumbnail': None,
                        'center_crop': None,
                        'thumbnail_relative': None,
                        'center_crop_relative': None
                    }

        # 统计结果
        success_thumbnails = sum(1 for paths in results.values() if paths['thumbnail'] is not None)
        success_center_crops = sum(1 for paths in results.values() if paths['center_crop'] is not None)

        self.logger.info(f"批量处理完成: 成功生成 {success_thumbnails}/{total_files} 个缩略图, {success_center_crops}/{total_files} 个中心区域图")

        return results
    
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
    
    def _get_file_type_from_path(self, path: str) -> str:
        """
        根据路径确定文件类型

        Args:
            path: 文件路径

        Returns:
            str: 文件类型标识
        """
        path_includes = self.config.get('options', {}).get('path_includes', [])

        # 标准化路径用于匹配
        normalized_path = path.replace('\\', '/')

        for include_config in path_includes:
            include_type = include_config.get('type', 'regex')
            include_pattern = include_config.get('pattern', '')
            case_sensitive = include_config.get('case_sensitive', False)
            file_type = include_config.get('file_type', 'unknown')

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
                        return file_type
                elif include_type == 'contains':
                    if include_pattern_check in normalized_path_check:
                        return file_type
                elif include_type == 'glob':
                    import fnmatch
                    if fnmatch.fnmatch(normalized_path_check, include_pattern_check):
                        return file_type

            except Exception as e:
                self.logger.error(f"文件类型判断规则错误: {e}")
                continue

        return 'unknown'

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

    def cluster_data_by_region_and_time(self, extracted_info: List[Dict[str, Optional[str]]], time_threshold_minutes: int = 30) -> List[Dict[str, Any]]:
        """
        对数据进行类聚分组，依据时间和sky_region的前四位

        Args:
            extracted_info: 提取的文件信息列表
            time_threshold_minutes: 时间阈值（分钟），相邻不超过此时间的归为一组

        Returns:
            List[Dict[str, Any]]: 分组结果列表，每个分组包含：
                - group_id: 分组ID
                - sky_region_name: 天区名称（前四位）
                - start_time: 分组开始时间
                - end_time: 分组结束时间
                - items: 分组内的数据项列表（按时间排序）
                - count: 分组内项目数量
        """
        from collections import defaultdict

        # 首先按sky_region的前四位分组
        region_groups = defaultdict(list)

        for info in extracted_info:
            sky_region = info.get('sky_region', '')
            if sky_region:
                sky_region_name = sky_region[:4]  # 取前四位
            else:
                sky_region_name = 'Unknown'

            # 解析时间戳
            parsed_time = None
            if info.get('timestamp'):
                try:
                    timestamp_str = info['timestamp'].replace('UTC', '')
                    date_part = timestamp_str[:8]  # 20250421
                    time_part = timestamp_str[9:]  # 170640

                    year = int(date_part[:4])
                    month = int(date_part[4:6])
                    day = int(date_part[6:8])
                    hour = int(time_part[:2])
                    minute = int(time_part[2:4])
                    second = int(time_part[4:6])

                    parsed_time = datetime(year, month, day, hour, minute, second)
                except Exception as e:
                    self.logger.debug(f"时间解析失败 {info['timestamp']}: {e}")
                    parsed_time = None

            # 添加解析后的时间到信息中
            info_with_time = info.copy()
            info_with_time['parsed_time'] = parsed_time

            region_groups[sky_region_name].append(info_with_time)

        # 对每个天区组内的数据按时间进行二级分组
        final_groups = []
        group_id = 1

        for sky_region_name, items in region_groups.items():
            # 按时间排序（没有时间的放在最后）
            items_with_time = [item for item in items if item['parsed_time'] is not None]
            items_without_time = [item for item in items if item['parsed_time'] is None]

            items_with_time.sort(key=lambda x: x['parsed_time'])

            # 对有时间的项目进行时间聚类
            if items_with_time:
                current_group = [items_with_time[0]]

                for item in items_with_time[1:]:
                    # 计算与当前组最后一个项目的时间差
                    time_diff = abs((item['parsed_time'] - current_group[-1]['parsed_time']).total_seconds() / 60)

                    if time_diff <= time_threshold_minutes:
                        # 时间差在阈值内，加入当前组
                        current_group.append(item)
                    else:
                        # 时间差超过阈值，创建新组
                        # 先保存当前组
                        group_start_time = current_group[0]['parsed_time']
                        group_end_time = current_group[-1]['parsed_time']

                        final_groups.append({
                            'group_id': group_id,
                            'sky_region_name': sky_region_name,
                            'start_time': group_start_time,
                            'end_time': group_end_time,
                            'items': current_group,
                            'count': len(current_group)
                        })
                        group_id += 1

                        # 开始新组
                        current_group = [item]

                # 保存最后一个组
                if current_group:
                    group_start_time = current_group[0]['parsed_time']
                    group_end_time = current_group[-1]['parsed_time']

                    final_groups.append({
                        'group_id': group_id,
                        'sky_region_name': sky_region_name,
                        'start_time': group_start_time,
                        'end_time': group_end_time,
                        'items': current_group,
                        'count': len(current_group)
                    })
                    group_id += 1

            # 处理没有时间的项目，单独成组
            if items_without_time:
                final_groups.append({
                    'group_id': group_id,
                    'sky_region_name': sky_region_name,
                    'start_time': None,
                    'end_time': None,
                    'items': items_without_time,
                    'count': len(items_without_time)
                })
                group_id += 1

        # 按天区名称和开始时间排序
        final_groups.sort(key=lambda x: (x['sky_region_name'], x['start_time'] if x['start_time'] else datetime.min))

        self.logger.info(f"数据聚类完成: 共 {len(final_groups)} 个分组")
        for group in final_groups:
            if group['start_time'] and group['end_time']:
                duration = (group['end_time'] - group['start_time']).total_seconds() / 60
                self.logger.debug(f"分组 {group['group_id']}: {group['sky_region_name']}, "
                                f"{group['count']} 项, 时长 {duration:.1f} 分钟")
            else:
                self.logger.debug(f"分组 {group['group_id']}: {group['sky_region_name']}, "
                                f"{group['count']} 项, 无时间信息")

        return final_groups

    def get_file_lists_for_processing(self) -> Dict[str, List[str]]:
        """
        获取用于后续处理的文件分类列表

        Returns:
            Dict[str, List[str]]: 包含以下键的字典
                - 'axy_files': .fits.axy 文件列表
                - 'diff1_files': .diff1.fits 文件列表
                - 'fixedsrc_files': .fixedsrc.cat 文件列表
                - 'mo_files': .mo.cat 文件列表
                - 'fit_files': .fit 文件列表
        """
        files_by_type = self.get_files_by_type()

        # 重新组织为更明确的命名
        file_lists = {
            'axy_files': files_by_type.get('axy', []),
            'diff1_files': files_by_type.get('diff1', []),
            'fixedsrc_files': files_by_type.get('fixedsrc', []),
            'mo_files': files_by_type.get('mo', []),
            'fit_files': files_by_type.get('fit', []),
            'pp_fits_files': files_by_type.get('pp_fits', [])
        }

        return file_lists

    def extract_batch_fits_info(self, file_paths: List[str], max_workers: int = 20) -> List[Dict[str, Optional[str]]]:
        """
        批量提取FITS文件信息（多线程版本）

        Args:
            file_paths: FITS文件路径列表
            max_workers: 最大线程数，默认为20

        Returns:
            List[Dict[str, Optional[str]]]: 提取信息的列表
        """
        total_files = len(file_paths)

        if total_files == 0:
            return []

        # 如果文件数量较少，直接使用单线程处理
        if total_files < max_workers:
            results = []
            for file_path in file_paths:
                info = self.extract_fits_info(file_path)
                results.append(info)
            return results

        self.logger.info(f"开始批量提取 {total_files} 个FITS文件信息（使用 {max_workers} 个线程）")

        # 使用ThreadPoolExecutor进行多线程处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {executor.submit(self.extract_fits_info, file_path): file_path
                             for file_path in file_paths}

            # 收集结果，保持原始顺序
            file_to_result = {}
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    file_to_result[file_path] = result
                except Exception as e:
                    self.logger.error(f"提取文件信息 {file_path} 时出错: {e}")
                    # 创建错误结果
                    error_result = {
                        'sky_region': None,
                        'system_name': None,
                        'timestamp': None,
                        'original_path': file_path
                    }
                    file_to_result[file_path] = error_result

        # 按原始顺序重新排列结果
        results = [file_to_result[file_path] for file_path in file_paths]

        self.logger.info(f"批量提取完成，共处理 {len(results)} 个文件")
        return results

    def read_pp_fits_header(self, fits_path: str) -> Dict[str, Optional[str]]:
        """
        读取单个PP FITS文件的header信息

        Args:
            fits_path: FITS文件路径

        Returns:
            包含header信息的字典
        """
        result = {
            'file_path': fits_path,
            'file_name': Path(fits_path).name,
            'LM5SIG': None,
            'ELLIPTI': None,
            'FWHM': None,
            'error': None
        }

        try:
            with fits.open(fits_path) as hdul:
                header = hdul[0].header

                # 读取指定的header字段
                for key in ['LM5SIG', 'ELLIPTI', 'FWHM']:
                    if key in header:
                        result[key] = str(header[key])
                    else:
                        result[key] = 'N/A'

                self.logger.debug(f"成功读取 {Path(fits_path).name} 的header信息")

        except Exception as e:
            error_msg = f"读取失败: {str(e)}"
            result['error'] = error_msg
            self.logger.error(f"{Path(fits_path).name} - {error_msg}")

        return result

    def batch_read_pp_fits_headers(self, pp_fits_files: List[str], max_workers: int = 20) -> List[Dict[str, Optional[str]]]:
        """
        批量读取PP FITS文件的header信息（多线程版本）

        Args:
            pp_fits_files: PP FITS文件路径列表
            max_workers: 最大线程数，默认为20

        Returns:
            包含所有文件header信息的列表
        """
        results = []
        total_files = len(pp_fits_files)

        self.logger.info(f"开始批量读取 {total_files} 个PP FITS文件的header信息（使用 {max_workers} 个线程）")

        # 使用线程锁保护进度计数器
        progress_lock = threading.Lock()
        completed_count = [0]  # 使用列表以便在闭包中修改

        def process_single_file(fits_file: str) -> Dict[str, Optional[str]]:
            """处理单个文件的内部函数"""
            header_info = self.read_pp_fits_header(fits_file)

            # 更新进度
            with progress_lock:
                completed_count[0] += 1
                current_count = completed_count[0]
                if current_count % 10 == 0 or current_count == total_files:
                    self.logger.info(f"处理进度: {current_count}/{total_files}")

            return header_info

        # 使用ThreadPoolExecutor进行多线程处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {executor.submit(process_single_file, fits_file): fits_file
                             for fits_file in pp_fits_files}

            # 收集结果，保持原始顺序
            file_to_result = {}
            for future in as_completed(future_to_file):
                fits_file = future_to_file[future]
                try:
                    result = future.result()
                    file_to_result[fits_file] = result
                except Exception as e:
                    self.logger.error(f"处理文件 {fits_file} 时出错: {e}")
                    # 创建错误结果
                    error_result = {
                        'file_path': fits_file,
                        'file_name': Path(fits_file).name,
                        'LM5SIG': None,
                        'ELLIPTI': None,
                        'FWHM': None,
                        'error': f"多线程处理错误: {str(e)}"
                    }
                    file_to_result[fits_file] = error_result

        # 按原始顺序重新排列结果
        results = [file_to_result[fits_file] for fits_file in pp_fits_files]

        self.logger.info(f"批量读取完成，共处理 {len(results)} 个文件")
        return results

    def create_output_archive(self, archive_name: str = None) -> Optional[str]:
        """
        创建包含所有输出文件的tar.gz压缩包

        Args:
            archive_name: 压缩包名称，如果为None则自动生成

        Returns:
            Optional[str]: 压缩包路径，如果创建失败返回None
        """
        try:
            # 生成压缩包名称
            if archive_name is None:
                if self.ignore_date:
                    param_part = "all"
                else:
                    param_part = self.date_suffix
                archive_name = f"fits_output_{param_part}_{self.run_timestamp}.tar.gz"

            # 压缩包保存路径
            archive_path = os.path.join(self.output_dir, archive_name)

            self.logger.info(f"开始创建输出压缩包: {archive_path}")

            # 创建tar.gz压缩包
            with tarfile.open(archive_path, 'w:gz') as tar:
                # 添加输出目录中的所有文件
                output_path = Path(self.output_dir)

                for file_path in output_path.rglob('*'):
                    if file_path.is_file() and file_path.name != archive_name:
                        # 计算在压缩包中的相对路径
                        arcname = file_path.relative_to(output_path)
                        tar.add(file_path, arcname=arcname)
                        self.logger.debug(f"添加文件到压缩包: {arcname}")

            # 获取压缩包大小
            archive_size = os.path.getsize(archive_path)
            size_mb = archive_size / (1024 * 1024)

            self.logger.info(f"压缩包创建成功: {archive_path}")
            self.logger.info(f"压缩包大小: {size_mb:.2f} MB")

            return archive_path

        except Exception as e:
            self.logger.error(f"创建压缩包失败: {e}")
            return None

    def find_files_by_type(self) -> Dict[str, List[str]]:
        """
        使用ripgrep查找匹配的文件，按文件类型分类返回

        Returns:
            Dict[str, List[str]]: 按文件类型分类的文件路径字典
        """
        if not self.config:
            self.logger.error("配置未加载，请先调用load_config()")
            return {}

        files_by_type = {}
        search_directories = self._get_search_directories_with_date()
        patterns = self._build_ripgrep_patterns()

        if not patterns:
            self.logger.warning("没有找到有效的搜索模式")
            return {}

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
                        files_result = ripgrep.files(
                            patterns=[pattern],
                            paths=[normalized_dir],
                            globs=[pattern] if pattern_type == 'glob' else None
                        )

                        for file_info in files_result:
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

                            # 确定文件类型
                            file_type = self._get_file_type_from_path(file_path)

                            # 按类型分类存储
                            if file_type not in files_by_type:
                                files_by_type[file_type] = []

                            if file_path not in files_by_type[file_type]:
                                files_by_type[file_type].append(file_path)
                                self.logger.debug(f"找到匹配文件 ({file_type}): {file_path}")

                    except Exception as e:
                        self.logger.error(f"执行ripgrep时出错: {e}")
                        continue

            except Exception as e:
                self.logger.error(f"搜索目录时出错 {normalized_dir}: {e}")
                continue

        # 应用最大结果数限制
        max_results = self.config.get('options', {}).get('max_results', 10000)
        total_files = sum(len(files) for files in files_by_type.values())

        if total_files > max_results:
            self.logger.warning(f"结果数量 ({total_files}) 超过限制 ({max_results})，按类型截取结果")
            # 按比例截取每种类型的文件
            for file_type in files_by_type:
                current_count = len(files_by_type[file_type])
                if current_count > 0:
                    ratio = current_count / total_files
                    type_limit = int(max_results * ratio)
                    if type_limit > 0:
                        files_by_type[file_type] = files_by_type[file_type][:type_limit]

        # 统计结果
        for file_type, files in files_by_type.items():
            self.logger.info(f"搜索完成，{file_type} 类型找到 {len(files)} 个文件")

        total_found = sum(len(files) for files in files_by_type.values())
        self.logger.info(f"搜索完成，总共找到 {total_found} 个匹配文件")

        return files_by_type

    def find_files(self) -> List[str]:
        """
        使用ripgrep查找匹配的文件（兼容性方法）

        Returns:
            List[str]: 匹配的文件路径列表
        """
        files_by_type = self.find_files_by_type()
        # 合并所有类型的文件
        all_files = []
        for files in files_by_type.values():
            all_files.extend(files)
        return all_files

    def get_files_by_type(self) -> Dict[str, List[str]]:
        """
        获取按类型分类的文件列表（主要接口）

        Returns:
            Dict[str, List[str]]: 按文件类型分类的文件路径字典
                - 'axy': .fits.axy 文件列表
                - 'diff1': .diff1.fits 文件列表
                - 'fixedsrc': .fixedsrc.cat 文件列表
                - 'mo': .mo.cat 文件列表
        """
        return self.find_files_by_type()
    
    def save_results(self, files: List[str], output_file: str = None, include_extracted_info: bool = True, use_clustering: bool = True, time_threshold_minutes: int = 30) -> bool:
        """
        保存搜索结果到文件

        Args:
            files: 文件路径列表
            output_file: 输出文件路径，默认为None（自动生成）
            include_extracted_info: 是否包含提取的文件信息，默认为True
            use_clustering: 是否使用聚类分组
            time_threshold_minutes: 时间阈值（分钟）

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

        # 如果指定了输出目录，将文件放到输出目录中
        if self.output_dir:
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / Path(output_file).name

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
            # 数据文件输出到输出目录（默认为dest目录），使用带时间戳的文件名
            timestamped_js_filename = self._generate_timestamped_filename("fits_data", ".js")
            timeline_js_output = Path(self.output_dir) / timestamped_js_filename

            self.save_timeline_js(files, timeline_js_output, use_clustering, time_threshold_minutes)

            return True

        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            return False

    def save_results_by_type(self, files_by_type: Dict[str, List[str]], output_file: str = None, include_extracted_info: bool = True, use_clustering: bool = True, time_threshold_minutes: int = 30, save_text_file: bool = False, generate_images: bool = False) -> dict:
        """
        保存按类型分类的搜索结果到文件

        Args:
            files_by_type: 按文件类型分类的文件路径字典
            output_file: 输出文件路径，默认为None（自动生成）
            include_extracted_info: 是否包含提取的文件信息，默认为True
            use_clustering: 是否使用聚类分组
            time_threshold_minutes: 时间阈值（分钟）
            save_text_file: 是否保存文本文件，默认为False
            generate_images: 是否为FITS文件生成缩略图和中心区域图，默认为False

        Returns:
            dict: 包含保存结果信息，格式为 {"success": bool, "js_filename": str}
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"fits_search_results_by_type_{timestamp}.txt"

        # 如果指定了输出目录，将文件放到输出目录中
        if self.output_dir:
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / Path(output_file).name

        try:
            total_files = sum(len(files) for files in files_by_type.values())

            # 只有在需要保存文本文件时才创建和写入文本文件
            if save_text_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"FITS文件搜索结果 (按类型分类)\n")
                    f.write(f"搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"文件类型数量: {len(files_by_type)}\n")
                    f.write(f"总文件数量: {total_files}\n")
                    f.write("=" * 80 + "\n\n")

                    # 按文件类型分别处理
                    for file_type, files in files_by_type.items():
                        if not files:
                            continue

                        f.write(f"文件类型: {file_type.upper()}\n")
                        f.write(f"文件数量: {len(files)}\n")
                        f.write("-" * 60 + "\n")

                        if include_extracted_info:
                            # 对于pp_fits文件，提取header信息
                            if file_type == 'pp_fits':
                                f.write("PP FITS文件Header信息:\n")
                                f.write(f"{'序号':<4} {'文件名':<50} {'LM5SIG':<10} {'ELLIPTI':<10} {'FWHM':<10} {'错误'}\n")
                                f.write("-" * 100 + "\n")

                                header_data = self.batch_read_pp_fits_headers(files)
                                successful_extractions = 0

                                for i, info in enumerate(header_data, 1):
                                    file_name = Path(info['file_path']).name
                                    lm5sig = info['LM5SIG'] or 'N/A'
                                    ellipti = info['ELLIPTI'] or 'N/A'
                                    fwhm = info['FWHM'] or 'N/A'
                                    error = info['error'] or ''

                                    if not error:
                                        successful_extractions += 1

                                    f.write(f"{i:<4} {file_name:<50} {lm5sig:<10} {ellipti:<10} {fwhm:<10} {error}\n")

                                f.write("-" * 100 + "\n")
                                f.write(f"Header信息统计: 总文件数={len(files)}, 成功读取={successful_extractions}, 成功率={successful_extractions/len(files)*100:.1f}%\n")

                                # 统计有效数据
                                if successful_extractions > 0:
                                    valid_lm5sig = sum(1 for row in header_data if row['LM5SIG'] and row['LM5SIG'] != 'N/A')
                                    valid_ellipti = sum(1 for row in header_data if row['ELLIPTI'] and row['ELLIPTI'] != 'N/A')
                                    valid_fwhm = sum(1 for row in header_data if row['FWHM'] and row['FWHM'] != 'N/A')

                                    f.write(f"有效数据统计: LM5SIG={valid_lm5sig}, ELLIPTI={valid_ellipti}, FWHM={valid_fwhm}\n")
                            else:
                                # 对于其他文件类型，提取文件信息
                                f.write("文件信息提取结果:\n")
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

                        # 保存完整的文件路径列表
                        f.write("\n完整文件路径列表:\n")
                        f.write("-" * 50 + "\n")
                        for i, file_path in enumerate(files, 1):
                            f.write(f"{i:4d}. {file_path}\n")

                        f.write("\n" + "=" * 80 + "\n\n")

                self.logger.info(f"分类搜索结果已保存到: {output_file}")
            else:
                self.logger.info("跳过文本文件保存")

            # 只对.fit文件生成Timeline格式的JavaScript文件，其他文件作为关联文件
            fit_files = files_by_type.get('fit', [])
            timestamped_js_filename = ""

            if fit_files:
                # 如果启用了图像生成，先生成图像
                image_results = {}
                if generate_images:
                    self.logger.info(f"为 {len(fit_files)} 个FITS文件生成缩略图和中心区域图...")
                    image_results = self.batch_process_fits_images(fit_files, create_thumbnail=True, create_center_crop=True)
                    self.logger.info("图像生成完成")

                # 匹配其他类型文件到.fit文件
                other_files = {k: v for k, v in files_by_type.items() if k != 'fit'}
                fit_matches = self.match_related_files_to_fit(fit_files, other_files, generate_images)

                # 将图像信息添加到fit_matches中
                if image_results:
                    for fit_file, match_info in fit_matches.items():
                        if fit_file in image_results:
                            match_info['image_paths'] = image_results[fit_file]

                # 数据文件输出到输出目录（默认为dest目录），使用带时间戳的文件名
                timestamped_js_filename = self._generate_timestamped_filename("fits_data", ".js")
                timeline_js_output = Path(self.output_dir) / timestamped_js_filename

                self.save_timeline_js_with_related_files(fit_files, fit_matches, timeline_js_output, use_clustering, time_threshold_minutes)
            else:
                self.logger.info("没有找到.fit文件，跳过Timeline JavaScript文件生成")

            return {"success": True, "js_filename": timestamped_js_filename}

        except Exception as e:
            self.logger.error(f"保存分类结果失败: {e}")
            return {"success": False, "js_filename": ""}

    def save_timeline_js_with_related_files(self, fit_files: List[str], fit_matches: Dict[str, Dict[str, Any]], output_file: str, use_clustering: bool = True, time_threshold_minutes: int = 30) -> bool:
        """
        保存包含关联文件信息的Timeline JavaScript文件

        Args:
            fit_files: .fit文件列表
            fit_matches: 匹配结果字典
            output_file: 输出文件路径
            use_clustering: 是否使用聚类
            time_threshold_minutes: 时间阈值

        Returns:
            bool: 保存成功返回True
        """
        try:
            if use_clustering:
                # 对.fit文件进行聚类
                fit_info_list = self.extract_batch_fits_info(fit_files)
                clustered_groups = self.cluster_data_by_region_and_time(fit_info_list, time_threshold_minutes)

                # 为聚类数据添加关联文件信息
                enhanced_groups = []
                for group in clustered_groups:
                    enhanced_group = group.copy()

                    # 转换数据结构：将聚类方法的格式转换为Timeline方法期望的格式
                    items = group.get('items', [])
                    count = group.get('count', 0)

                    # 转换为Timeline期望的格式
                    enhanced_group['file_details'] = items
                    enhanced_group['item_count'] = count

                    # 提取系统名称列表
                    system_names = set()
                    for item in items:
                        system_name = item.get('system_name')
                        if system_name:
                            system_names.add(system_name)
                    enhanced_group['system_names'] = list(system_names)

                    enhanced_group['related_files'] = {
                        'axy': [],
                        'diff1': [],
                        'fixedsrc': [],
                        'mo': [],
                        'pp_fits': []
                    }

                    # 收集该组中所有.fit文件的关联文件和图像信息
                    for file_detail in items:
                        fit_file_path = file_detail.get('original_path', '')
                        if fit_file_path in fit_matches:
                            match_info = fit_matches[fit_file_path]
                            for file_type, related_files in match_info['related_files'].items():
                                enhanced_group['related_files'][file_type].extend(related_files)

                            # 将图像路径信息添加到文件详情中
                            image_paths = match_info.get('image_paths', {})
                            if image_paths:
                                if image_paths.get('thumbnail_relative'):
                                    # 将Windows路径分隔符转换为URL路径分隔符
                                    file_detail['thumbnail_path'] = image_paths['thumbnail_relative'].replace('\\', '/')
                                if image_paths.get('center_crop_relative'):
                                    # 将Windows路径分隔符转换为URL路径分隔符
                                    file_detail['center_path'] = image_paths['center_crop_relative'].replace('\\', '/')

                    enhanced_groups.append(enhanced_group)

                timeline_data = self.convert_clustered_data_to_timeline_format_with_related(enhanced_groups)
            else:
                # 单文件模式，直接转换.fit文件并添加关联文件信息
                timeline_data = self.convert_to_timeline_format_with_related(fit_files, fit_matches)

            # 保存JavaScript文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("// FITS文件Timeline数据 (包含关联文件)\n")
                f.write(f"// 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"// 主文件数量: {len(fit_files)}\n")
                f.write(f"// 聚类模式: {'启用' if use_clustering else '禁用'}\n")
                f.write("\nvar fitsData = ")

                import json

                # 自定义JSON编码器处理datetime对象
                class DateTimeEncoder(json.JSONEncoder):
                    def default(self, obj):
                        if isinstance(obj, datetime):
                            return obj.strftime('%Y-%m-%dT%H:%M:%S')
                        return super().default(obj)

                json_str = json.dumps(timeline_data, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
                f.write(json_str)
                f.write(";\n")

            self.logger.info(f"Timeline JavaScript文件已保存到: {output_file}")
            return True

        except Exception as e:
            import traceback
            self.logger.error(f"保存Timeline JavaScript文件失败: {e}")
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
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

    def convert_to_timeline_format_with_related(self, fit_files: List[str], fit_matches: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将.fit文件信息转换为包含关联文件的Timeline格式
        """
        timeline_data = []

        for fit_file in fit_files:
            match_info = fit_matches.get(fit_file, {})
            fit_info = match_info.get('fit_info', {})

            sky_region = fit_info.get('sky_region', 'Unknown')
            system_name = fit_info.get('system_name', 'Unknown')
            timestamp = fit_info.get('timestamp')

            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    start_time = dt.strftime("%Y-%m-%dT%H:%M:%S")
                except:
                    start_time = timestamp
            else:
                start_time = "1970-01-01T00:00:00"

            # 统计关联文件
            related_counts = {}
            related_files_detail = {}
            for file_type, related_files in match_info.get('related_files', {}).items():
                related_counts[file_type] = len(related_files)
                related_files_detail[file_type] = related_files

            # 构建内容描述
            content_parts = [f"{sky_region} | {system_name}"]
            if any(count > 0 for count in related_counts.values()):
                related_desc = []
                if related_counts.get('axy', 0) > 0:
                    related_desc.append(f"AXY:{related_counts['axy']}")
                if related_counts.get('diff1', 0) > 0:
                    related_desc.append(f"DIFF1:{related_counts['diff1']}")
                if related_counts.get('fixedsrc', 0) > 0:
                    related_desc.append(f"FIXEDSRC:{related_counts['fixedsrc']}")
                if related_counts.get('mo', 0) > 0:
                    related_desc.append(f"MO:{related_counts['mo']}")

                if related_desc:
                    content_parts.append(f"({', '.join(related_desc)})")

            timeline_item = {
                'id': f"fit_{len(timeline_data)}",
                'content': " | ".join(content_parts),
                'start': start_time,
                'type': 'point',
                'group': sky_region[:4] if len(sky_region) >= 4 else sky_region,
                'subgroup': system_name,
                'sky_region': sky_region,
                'system_name': system_name,
                'timestamp': timestamp,
                'file_name': Path(fit_file).name,
                'file_path': fit_file,
                'related_files': related_files_detail,
                'related_counts': related_counts
            }

            # 添加图像路径信息（如果存在）
            image_paths = match_info.get('image_paths', {})
            if image_paths:
                if image_paths.get('thumbnail_relative'):
                    # 将Windows路径分隔符转换为URL路径分隔符
                    timeline_item['thumbnail_path'] = image_paths['thumbnail_relative'].replace('\\', '/')
                if image_paths.get('center_crop_relative'):
                    # 将Windows路径分隔符转换为URL路径分隔符
                    timeline_item['center_path'] = image_paths['center_crop_relative'].replace('\\', '/')

            timeline_data.append(timeline_item)

        return timeline_data

    def convert_clustered_data_to_timeline_format_with_related(self, enhanced_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将包含关联文件的聚类数据转换为Timeline格式，每个.fit文件都有自己的关联文件
        """
        timeline_data = []

        for group in enhanced_groups:
            group_id = group.get('group_id', '')
            sky_region_name = group.get('sky_region_name', 'Unknown')
            system_names = group.get('system_names', [])
            start_time = group.get('start_time')
            end_time = group.get('end_time')
            item_count = group.get('item_count', 0)
            file_details = group.get('file_details', [])
            related_files = group.get('related_files', {})

            # 为每个.fit文件添加其专属的关联文件信息，直接整合到文件详情中
            enhanced_file_details = []
            for file_detail in file_details:
                enhanced_detail = file_detail.copy()
                fit_file_path = file_detail.get('original_path', '')

                # 为这个特定的.fit文件找到匹配的关联文件，直接添加到文件详情中
                related_file_paths = []

                # 检查每种类型的关联文件
                for file_type, files in related_files.items():
                    for related_file in files:
                        related_info = related_file.get('file_info', {})
                        # 检查关联文件是否与当前.fit文件匹配
                        if self._files_match(file_detail, related_info):
                            related_file_entry = {
                                'path': related_file.get('file_path', ''),
                                'type': file_type,
                                'match_score': related_file.get('match_score', 100)
                            }

                            # 对于pp_fits文件，添加header信息
                            if file_type == 'pp_fits' and 'header_info' in related_file:
                                related_file_entry['header_info'] = related_file['header_info']

                            related_file_paths.append(related_file_entry)

                # 将关联文件路径直接添加到文件详情中
                if related_file_paths:
                    enhanced_detail['related_file_paths'] = related_file_paths

                enhanced_file_details.append(enhanced_detail)

            # 更新file_details
            file_details = enhanced_file_details

            # 统计关联文件数量
            related_counts = {}
            for file_type, files in related_files.items():
                related_counts[file_type] = len(files)

            # 构建内容描述
            content_parts = [sky_region_name]
            if system_names:
                content_parts.append(f"系统: {', '.join(sorted(system_names))}")

            content_parts.append(f"({item_count}个FIT文件)")

            # 添加关联文件信息
            if any(count > 0 for count in related_counts.values()):
                related_desc = []
                if related_counts.get('axy', 0) > 0:
                    related_desc.append(f"AXY:{related_counts['axy']}")
                if related_counts.get('diff1', 0) > 0:
                    related_desc.append(f"DIFF1:{related_counts['diff1']}")
                if related_counts.get('fixedsrc', 0) > 0:
                    related_desc.append(f"FIXEDSRC:{related_counts['fixedsrc']}")
                if related_counts.get('mo', 0) > 0:
                    related_desc.append(f"MO:{related_counts['mo']}")
                if related_counts.get('pp_fits', 0) > 0:
                    related_desc.append(f"PP_FITS:{related_counts['pp_fits']}")

                if related_desc:
                    content_parts.append(f"关联: {', '.join(related_desc)}")

            content = " | ".join(content_parts)

            # 处理时间
            if start_time and end_time:
                start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
                end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")

                if start_time_str == end_time_str:
                    timeline_item = {
                        'id': group_id,
                        'group_id': group_id,  # 添加group_id字段用于basicUsage.html识别聚类数据
                        'content': content,
                        'start': start_time_str,
                        'type': 'point'
                    }
                else:
                    timeline_item = {
                        'id': group_id,
                        'group_id': group_id,  # 添加group_id字段用于basicUsage.html识别聚类数据
                        'content': content,
                        'start': start_time_str,
                        'end': end_time_str,
                        'type': 'range'
                    }
            else:
                timeline_item = {
                    'id': group_id,
                    'group_id': group_id,  # 添加group_id字段用于basicUsage.html识别聚类数据
                    'content': content,
                    'start': "1970-01-01T00:00:00",
                    'type': 'point'
                }

            # 添加分组信息（移除聚类级别的related_files，关联文件已整合到各个文件中）
            timeline_item.update({
                'group': sky_region_name,
                'sky_region_name': sky_region_name,
                'system_names': system_names,
                'item_count': item_count,
                'file_details': file_details
            })

            timeline_data.append(timeline_item)

        return timeline_data

    def match_related_files_to_fit(self, fit_files: List[str], other_files_by_type: Dict[str, List[str]], generate_images: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        将其他类型的文件匹配到对应的.fit文件

        Args:
            fit_files: .fit文件列表
            other_files_by_type: 其他类型文件的字典
            generate_images: 是否生成图像和读取PP FITS header信息

        Returns:
            Dict[str, Dict[str, Any]]: 以.fit文件路径为键的匹配结果
        """
        fit_file_matches = {}

        # 首先提取所有.fit文件的信息
        fit_info_list = self.extract_batch_fits_info(fit_files)

        # 为每个.fit文件创建匹配记录
        for i, fit_file in enumerate(fit_files):
            fit_info = fit_info_list[i] if i < len(fit_info_list) else {}

            fit_file_matches[fit_file] = {
                'fit_file': fit_file,
                'fit_info': fit_info,
                'sky_region': fit_info.get('sky_region'),
                'system_name': fit_info.get('system_name'),
                'timestamp': fit_info.get('timestamp'),
                'related_files': {
                    'axy': [],
                    'diff1': [],
                    'fixedsrc': [],
                    'mo': [],
                    'pp_fits': []
                }
            }

        # 匹配其他类型的文件
        for file_type, files in other_files_by_type.items():
            if file_type == 'fit_files':  # 跳过.fit文件本身
                continue

            if not files:
                continue

            # 将文件类型名称转换为简短形式
            short_type = file_type.replace('_files', '')

            # 提取其他文件的信息
            other_info_list = self.extract_batch_fits_info(files)

            for j, other_file in enumerate(files):
                other_info = other_info_list[j] if j < len(other_info_list) else {}
                other_sky_region = other_info.get('sky_region')
                other_system_name = other_info.get('system_name')
                other_timestamp = other_info.get('timestamp')

                # 寻找完全匹配的.fit文件（sky_region、system_name、timestamp 三个字段必须完全相同）
                matched_fit_file = None

                for fit_file, fit_match in fit_file_matches.items():
                    # 三个字段必须完全相同
                    if (other_sky_region and fit_match['sky_region'] and other_sky_region == fit_match['sky_region'] and
                        other_system_name and fit_match['system_name'] and other_system_name == fit_match['system_name'] and
                        other_timestamp and fit_match['timestamp'] and other_timestamp == fit_match['timestamp']):
                        matched_fit_file = fit_file
                        break

                # 如果找到完全匹配，添加到相关文件列表
                if matched_fit_file:
                    file_entry = {
                        'file_path': other_file,
                        'file_info': other_info,
                        'match_score': 100  # 完全匹配给予满分
                    }

                    # 对于pp_fits文件，只有在generate_images为True时才添加header信息
                    if short_type == 'pp_fits' and generate_images:
                        header_info = self.read_pp_fits_header(other_file)
                        file_entry['header_info'] = {
                            'LM5SIG': header_info.get('LM5SIG'),
                            'ELLIPTI': header_info.get('ELLIPTI'),
                            'FWHM': header_info.get('FWHM'),
                            'error': header_info.get('error')
                        }

                    fit_file_matches[matched_fit_file]['related_files'][short_type].append(file_entry)

        return fit_file_matches

    def _files_match(self, fit_file_info: Dict[str, Any], related_file_info: Dict[str, Any]) -> bool:
        """
        判断.fit文件和关联文件是否匹配
        要求 sky_region、system_name 和 timestamp 三个字段同时完全相同

        Args:
            fit_file_info: .fit文件信息
            related_file_info: 关联文件信息

        Returns:
            bool: 是否匹配
        """
        # 获取三个关键字段
        fit_region = fit_file_info.get('sky_region', '')
        related_region = related_file_info.get('sky_region', '')

        fit_system = fit_file_info.get('system_name', '')
        related_system = related_file_info.get('system_name', '')

        fit_timestamp = fit_file_info.get('timestamp', '')
        related_timestamp = related_file_info.get('timestamp', '')

        # 三个字段必须同时完全相同
        return (fit_region and related_region and fit_region == related_region and
                fit_system and related_system and fit_system == related_system and
                fit_timestamp and related_timestamp and fit_timestamp == related_timestamp)

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """
        解析时间戳字符串

        Args:
            timestamp_str: 时间戳字符串，如 "UTC20250826_161037"

        Returns:
            Optional[datetime]: 解析后的datetime对象，失败返回None
        """
        try:
            timestamp_str = timestamp_str.replace('UTC', '')
            date_part = timestamp_str[:8]  # 20250826
            time_part = timestamp_str[9:]  # 161037

            year = int(date_part[:4])
            month = int(date_part[4:6])
            day = int(date_part[6:8])
            hour = int(time_part[:2])
            minute = int(time_part[2:4])
            second = int(time_part[4:6])

            return datetime(year, month, day, hour, minute, second)
        except:
            return None

    def convert_clustered_data_to_timeline_format(self, files: List[str], use_clustering: bool = True, time_threshold_minutes: int = 30) -> List[Dict[str, Any]]:
        """
        将FITS文件信息转换为vis.js Timeline格式的JSON数据，支持聚类分组

        Args:
            files: 文件路径列表
            use_clustering: 是否使用聚类分组
            time_threshold_minutes: 时间阈值（分钟）

        Returns:
            List[Dict[str, Any]]: Timeline格式的数据列表
        """
        extracted_info = self.extract_batch_fits_info(files)

        if not use_clustering:
            # 不使用聚类，调用原来的方法
            return self.convert_to_timeline_format(files)

        # 使用聚类分组
        clustered_groups = self.cluster_data_by_region_and_time(extracted_info, time_threshold_minutes)
        timeline_data = []

        for group in clustered_groups:
            # 为每个分组创建一个Timeline项目
            group_id = group['group_id']
            sky_region_name = group['sky_region_name']
            items = group['items']
            count = group['count']
            start_time = group['start_time']
            end_time = group['end_time']

            # 构建分组的显示内容
            content_parts = [f"{sky_region_name}"]

            # 添加系统名称统计
            system_names = set()
            for item in items:
                if item.get('system_name'):
                    system_names.add(item['system_name'])

            if system_names:
                content_parts.append(f"系统: {', '.join(sorted(system_names))}")

            content_parts.append(f"({count}个文件)")
            content = " | ".join(content_parts)

            # 处理时间
            if start_time and end_time:
                start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
                end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")

                # 如果开始和结束时间相同，使用点类型；否则使用范围类型
                if start_time == end_time:
                    timeline_item = {
                        "id": group_id,
                        "content": content,
                        "start": start_time_str,
                        "type": "point"
                    }
                else:
                    timeline_item = {
                        "id": group_id,
                        "content": content,
                        "start": start_time_str,
                        "end": end_time_str,
                        "type": "range"
                    }
            else:
                # 没有时间信息，使用序号作为时间轴位置
                base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                offset_date = base_date + timedelta(days=group_id-1)
                start_time_str = offset_date.strftime("%Y-%m-%d")

                timeline_item = {
                    "id": group_id,
                    "content": content,
                    "start": start_time_str,
                    "type": "point"
                }

            # 添加分组信息
            timeline_item["sky_region_name"] = sky_region_name
            timeline_item["group_id"] = group_id
            timeline_item["item_count"] = count
            timeline_item["system_names"] = list(system_names)

            # 添加分组内的详细文件信息
            file_details = []
            for item in items:
                file_detail = {
                    "file_path": item['original_path'],
                    "file_name": Path(item['original_path']).name,
                    "sky_region": item.get('sky_region'),
                    "system_name": item.get('system_name'),
                    "timestamp": item.get('timestamp')
                }
                file_details.append(file_detail)

            timeline_item["file_details"] = file_details

            # 根据天区名称设置样式类
            timeline_item["className"] = f"region-{sky_region_name.lower()}"

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

    def save_timeline_js(self, files: List[str], output_file: str = None, use_clustering: bool = True, time_threshold_minutes: int = 30) -> bool:
        """
        将搜索结果保存为vis.js Timeline格式的JavaScript文件

        Args:
            files: 文件路径列表
            output_file: 输出文件路径，默认为None（自动生成）
            use_clustering: 是否使用聚类分组
            time_threshold_minutes: 时间阈值（分钟）

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
            timeline_data = self.convert_clustered_data_to_timeline_format(files, use_clustering, time_threshold_minutes)

            # 生成JavaScript文件内容
            clustering_info = "启用聚类分组" if use_clustering else "禁用聚类分组"
            js_content = f'''// FITS 数据 - 由 fits_file_finder_ripgrep.py 自动生成
// 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 记录数量: {len(timeline_data)}
// 搜索目录: {', '.join(self.config.get('search_directories', []))}
// 聚类设置: {clustering_info}
// 时间阈值: {time_threshold_minutes} 分钟

var fitsData = {json.dumps(timeline_data, ensure_ascii=False, indent=2)};

// 数据统计信息
console.log('FITS 数据已加载，共 ' + fitsData.length + ' 条记录');

// 数据按系统分组统计
var systemStats = {{}};
fitsData.forEach(function(item) {{
    if (item.system_names && item.system_names.length > 0) {{
        // 聚类模式：统计系统名称数组
        item.system_names.forEach(function(system) {{
            systemStats[system] = (systemStats[system] || 0) + (item.item_count || 1);
        }});
    }} else {{
        // 单文件模式：统计单个系统名称
        var system = item.system_name || 'Unknown';
        systemStats[system] = (systemStats[system] || 0) + 1;
    }}
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
    parser.add_argument('--output-dir', help='输出目录路径，会自动拷贝HTML模板文件')
    parser.add_argument('--save-text', action='store_true',
                       help='保存搜索结果文本文件 (默认不保存)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    parser.add_argument('--extract-info', action='store_true',
                       help='提取并显示FITS文件的天区索引、系统名称和时间信息')
    parser.add_argument('-d', '--date', help='日期后缀，格式为yyyymmdd (默认: 当前日期)')
    parser.add_argument('-all', '--all', action='store_true',
                       help='忽略指定的日期，搜索所有基础目录')
    parser.add_argument('--no-clustering', action='store_true',
                       help='禁用数据聚类分组，使用原始的单个文件模式')
    parser.add_argument('--time-threshold', type=int, default=30,
                       help='时间聚类阈值（分钟），默认30分钟')
    parser.add_argument('--enable-log-file', action='store_true',
                       help='启用日志文件输出到输出目录 (默认只输出到控制台)')
    parser.add_argument('--generate-images', action='store_true',
                       help='为FITS文件生成缩略图和中心区域图（默认不启用）')
    parser.add_argument('--thumbnail-only', action='store_true',
                       help='只生成缩略图（需与--generate-images一起使用）')
    parser.add_argument('--center-only', action='store_true',
                       help='只生成中心区域图（需与--generate-images一起使用）')

    args = parser.parse_args()

    # 创建查找器实例
    finder = FitsFileFinderRipgrep(args.config, args.date, args.all, args.output_dir, args.enable_log_file)
    
    # 设置日志级别
    if args.verbose:
        finder.logger.setLevel(logging.DEBUG)
    
    # 加载配置
    if not finder.load_config():
        print(f"错误: 无法加载配置文件 {args.config}")
        sys.exit(1)
    
    # 拷贝HTML模板文件到输出目录
    output_dir_display = args.output_dir or "dest (默认)"
    print(f"\n拷贝HTML模板文件到输出目录: {output_dir_display}")
    copy_result = finder.copy_html_template_files()
    if copy_result["success"]:
        print("HTML模板文件拷贝完成")
        html_files_info = copy_result["files"]
    else:
        print("HTML模板文件拷贝失败")
        html_files_info = {}

    # 默认按类型分类搜索
    files_by_type = finder.get_files_by_type()

    # 显示结果
    total_files = sum(len(files) for files in files_by_type.values())
    print(f"\n搜索完成！按类型找到 {total_files} 个匹配文件:")

    for file_type, files in files_by_type.items():
        print(f"  {file_type.upper()}: {len(files)} 个文件")

    if args.extract_info:
        # 按类型显示文件信息
        for file_type, files in files_by_type.items():
            if not files:
                continue

            print(f"\n{file_type.upper()} 类型文件信息:")
            print("-" * 80)
            print(f"{'序号':<4} {'天区索引':<10} {'系统名称':<10} {'时间戳':<20} {'文件路径'}")
            print("-" * 80)

            extracted_info = finder.extract_batch_fits_info(files)
            for i, info in enumerate(extracted_info, 1):
                sky_region = info['sky_region'] or 'N/A'
                system_name = info['system_name'] or 'N/A'
                timestamp = info['timestamp'] or 'N/A'
                file_path = Path(info['original_path']).name

                print(f"{i:<4} {sky_region:<10} {system_name:<10} {timestamp:<20} {file_path}")
    else:
        # 按类型显示文件路径（简化显示，只显示前5个）
        for file_type, files in files_by_type.items():
            if not files:
                continue
            print(f"\n{file_type.upper()} 类型文件（显示前5个）:")
            for i, file_path in enumerate(files[:5], 1):
                print(f"{i:4d}. {Path(file_path).name}")
            if len(files) > 5:
                print(f"     ... 还有 {len(files) - 5} 个文件")

    # 初始化保存结果变量
    save_result = {"success": False, "js_filename": None}
    
    # 保存分类结果
    if files_by_type:
        use_clustering = not args.no_clustering
        # 将图像生成参数传递给save_results_by_type方法
        save_result = finder.save_results_by_type(
            files_by_type,
            args.output,
            True,
            use_clustering,
            args.time_threshold,
            args.save_text,
            args.generate_images  # 传递图像生成参数
        )

        # 如果成功生成了JS文件且有HTML文件信息，更新HTML文件引用
        if save_result["success"] and save_result["js_filename"] and html_files_info.get("html"):
            html_file_path = Path(finder.output_dir) / html_files_info["html"]
            js_filename = save_result["js_filename"]
            css_filename = html_files_info.get("css", "vis.css")
            vis_js_filename = html_files_info.get("vis_js", "vis.js")
            sky_region_js_filename = html_files_info.get("sky_region_js", "kats_sky_region.js")

            finder._update_html_file_references(html_file_path, js_filename, css_filename, vis_js_filename, sky_region_js_filename)

        # 输出分类列表信息供后续使用
        print(f"\n文件分类列表已准备完成:")
        print(f"  axy_files: {len(files_by_type.get('axy', []))} 个 .fits.axy 文件 (关联到.fit文件)")
        print(f"  diff1_files: {len(files_by_type.get('diff1', []))} 个 .diff1.fits 文件 (关联到.fit文件)")
        print(f"  fixedsrc_files: {len(files_by_type.get('fixedsrc', []))} 个 .fixedsrc.cat 文件 (关联到.fit文件)")
        print(f"  mo_files: {len(files_by_type.get('mo', []))} 个 .mo.cat 文件 (关联到.fit文件)")
        print(f"  fit_files: {len(files_by_type.get('fit', []))} 个 .fit 文件 (主Timeline列表)")
        print(f"  pp_fits_files: {len(files_by_type.get('pp_fits', []))} 个 _pp.fits 文件 (处理后的FITS文件)")
        print(f"  可通过 finder.get_files_by_type() 获取所有分类列表")
        print(f"\n注意: 只有.fit文件会被聚合并导出到Timeline主列表，其他文件类型作为关联文件显示")

        output_dir_display = args.output_dir or "dest (默认)"
        print(f"\n输出目录: {output_dir_display}")
        print("  - 搜索结果文件和Timeline JS文件已保存到输出目录")
        print("  - HTML模板文件已拷贝到输出目录（如果不存在）")
        print("  - 可以直接在输出目录中打开fitsUsage.html查看Timeline可视化")

        # 如果启用了图像生成，创建tar.gz压缩包
        if args.generate_images:
            print(f"\n正在创建输出压缩包...")
            archive_path = finder.create_output_archive()
            if archive_path:
                print(f"✅ 压缩包创建成功: {archive_path}")
                print(f"   包含所有输出文件（HTML、JS、CSS、图像等）")
            else:
                print(f"❌ 压缩包创建失败，请检查日志")


if __name__ == "__main__":
    main()

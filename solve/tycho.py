def my_all_world2pix(wcs_info, world_coords):
  """
  简化的世界坐标到像素坐标转换函数
  """
  # 解析 WCS 信息 (示例，需要根据实际情况进行修改)
  ctype = wcs_info['CTYPE']
  crval = wcs_info['CRVAL']
  cd = wcs_info['CD']

  # 计算中间坐标系坐标
  intermediate_coords = world_coords - crval

  # 应用线性变换矩阵
  pixel_coords = cd @ intermediate_coords

  # 返回像素坐标
  return pixel_coords
from astropy.coordinates import SkyCoord


data_list = []
ra_list = []
dec_list = []
# 打开文件并逐行读取
in_line_count = 0
out_line_count = 0
with open('classify_fix.txt', 'r') as file:
    for line in file:
        # 移除行尾的换行符并按空格分割每行的数据
        parts = line.strip().split()
        in_line_count = in_line_count + 1
        # 确保分割后的数据部分正确
        if len(parts) == 8:
            out_line_count = out_line_count + 1
            # 提取数据并转换为适当的格式
            id_num, catalog, ra_hours, ra_minutes, ra_seconds, dec_degrees, dec_minutes, dec_seconds = parts

            ra_hours, ra_minutes, ra_seconds = map(float, [ra_hours, ra_minutes, ra_seconds])
            dec_degrees, dec_minutes, dec_seconds = map(float, [dec_degrees, dec_minutes, dec_seconds])

            # 计算并存储十进制的赤经和赤纬
            ra = (ra_hours + (ra_minutes / 60) + (ra_seconds / 3600)) * 15  # 转换为度
            dec = (dec_degrees + (dec_minutes / 60) + (dec_seconds / 3600))

            # 创建一个字典来存储当前行的数据
            entry = {
                'id': id_num,
                'catalog': catalog,
                'ra': ra,
                'dec': dec
            }
            long_val = ra
            if long_val>180:
                long_val = long_val - 360
            ra_list.append(ra)
            dec_list.append(dec)

            # 将字典添加到列表中
            data_list.append(entry)
        else:
            print(line)

# assert (in_line_count == out_line_count)
if in_line_count > out_line_count:
    print("!!! 缺少行 !!! %d      %d - %d" % (in_line_count - out_line_count, in_line_count, out_line_count))
else:
    print("完整通过")

# # 打印结果
# for entry in data_list:
#     print(entry)


def calc_distance(item_coord_i, item_coord_j):
    item_coord_i = SkyCoord(ra=ra_list[i], dec=dec_list[i], unit='deg')
    # item_cart_i = item_coord_i.cartesian
    item_coord_j = SkyCoord(ra=ra_list[j], dec=dec_list[j], unit='deg')
    angle_distance = item_coord_i.separation(item_coord_j)
    distance_ij = round(angle_distance.deg, 4)
    return distance_ij


for i in range(linked_len):
    # 提取每一行的四个值
    cluster_0_idx = int(linked[i, 0])
    cluster_1_idx = int(linked[i, 1])
    distance = linked[i, 2]
    num_points = linked[i, 3]
    if distance < 1 or distance > 2:
        continue
    # if distance > 2:
    #     continue
    print(f'-- {i}  {cluster_0_idx} {cluster_1_idx} {n_points}')
    # 打印每一行的四个值
    print(f"Row {i}:")
    print(f"  Cluster 0 Index: {cluster_0_idx} / {len(linked)} / {n_points}")
    print(f"  Cluster 1 Index: {cluster_1_idx} / {len(linked)} / {n_points}")
    print(f"  Distance: {distance}")
    print(f"  Number of Points: {num_points}")
    print(f'>>>> {i}   ')
    get_linked_node(i, 1)

    print()
    # if i > 10:
    #     break

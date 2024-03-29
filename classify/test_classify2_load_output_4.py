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
            if long_val > 180:
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


def calc_distance(ra_i, dec_i, ra_j, dec_j):
    item_coord_i = SkyCoord(ra=ra_i, dec=dec_i, unit='deg')
    item_coord_j = SkyCoord(ra=ra_j, dec=dec_j, unit='deg')
    angle_distance = item_coord_i.separation(item_coord_j)
    # distance_ij = round(angle_distance.deg, 4)
    return angle_distance.value


# # 打印结果
# for entry in data_list:
#     print(entry)

plan_list = []
data_list_copy = []
data_list_copy.extend(data_list)
skip_i = []
for i, entry_i in enumerate(data_list_copy):
    if i > 50:
        break
    if skip_i.__contains__(i):
        print(f'{i} skip by  near obj')
        continue
    near_obj = []
    for j, entry_j in enumerate(data_list):
        if i == j:
            print(f'{i} {j} skip by  it self obj')
            continue
        distance_ij = calc_distance(entry_i['ra'], entry_i['dec'], entry_j['ra'], entry_j['dec'])
        # print(f'{i}  {j}    {distance_ij}')
        if distance_ij < 2:
            near_obj.append(entry_j)
            skip_i.append(j)
            print(f'{i} {j}  add to  near obj')
    near_obj.append(entry_i)
    print(f'{i}   = {len(near_obj)}')
    plan_list.append(near_obj)

print(f'-------------{len(plan_list)}--------------')


def generate_color(c_index):
    color = c_index % 6
    if color == 0:
        return f"#FF5500"
    elif color == 1:
        return f"#AAAA00"
    elif color == 2:
        return f"#55FF00"
    elif color == 3:
        return f"#FFFF00"
    elif color == 4:
        return f"#FFAA00"
    elif color == 5:
        return f"#55AA00"


print(plan_list)
for p_i, plan_item in enumerate(plan_list):
    plan_color = generate_color(p_i)
    for point_item in plan_item:
        print(f'MarkerMgr.markerEquatorial("{point_item["ra"]}", "{point_item["dec"]}", true, true, "cross", "{plan_color}", 16, false, 0) ;')


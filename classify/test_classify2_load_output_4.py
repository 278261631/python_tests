import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
data_list = []
ra_list = []
dec_list = []
# 打开文件并逐行读取
in_line_count = 0
out_line_count = 0

ra_img_w = 3.3333
dec_img_h = 2.21666
ra_img_wide = ra_img_w * u.degree
dec_img_high = dec_img_h * u.degree
ra_span = ra_img_w * 0.8 * u.degree
dec_span = dec_img_h * 0.8 * u.degree

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


def calc_distance_spherical_offset(ra_i, dec_i, ra_j, dec_j):
    item_coord_i = SkyCoord(ra=ra_i, dec=dec_i, unit='deg')
    item_coord_j = SkyCoord(ra=ra_j, dec=dec_j, unit='deg')
    angle_distance = item_coord_i.spherical_offsets_to(item_coord_j)
    return angle_distance


# # 打印结果
# for entry in data_list:
#     print(entry)

plan_list = []
plan_list_centers = []
data_list_copy = []
data_list_copy.extend(data_list)
skip_i = []
for i, entry_i in enumerate(data_list_copy):
    # if i > 50:
    #     break
    if skip_i.__contains__(i):
        # print(f'{i} skip by  near obj')
        continue
    near_obj = []
    next_center_ra = entry_i['ra']
    next_center_dec = entry_i['dec']
    for j, entry_j in enumerate(data_list):
        if i == j or skip_i.__contains__(j):
            # print(f'{i} {j} skip by  it self obj')
            continue
        # distance_ij = calc_distance(entry_i['ra'], entry_i['dec'], entry_j['ra'], entry_j['dec'])
        # offset_x, offset_y = calc_distance_spherical_offset(entry_i['ra'], entry_i['dec'], entry_j['ra'], entry_j['dec'])
        offset_x, offset_y = calc_distance_spherical_offset(next_center_ra, next_center_dec, entry_j['ra'], entry_j['dec'])
        # print(f'{i}  {j}    {distance_ij}')
        if abs(offset_x) < ra_span/2 and abs(offset_y) < dec_span/2:
            near_obj.append(entry_j)
            skip_i.append(j)
            near_obj_ra_values = [item['ra'] for item in near_obj]
            near_obj_dec_values = [item['dec'] for item in near_obj]
            near_obj_ra_values.append(next_center_ra)
            near_obj_dec_values.append(next_center_dec)
            next_center_ra = np.mean(near_obj_ra_values)
            next_center_dec = np.mean(near_obj_dec_values)

            # print(f'{i}  {j}    [{entry_i["ra"]}  {entry_i["dec"]}]    [{entry_j["ra"]}  {entry_j["dec"]}]    {offset_x}  {offset_y}')
            # print(f'{i}  {j}    [{next_center_ra}  {next_center_dec}]')
            print(f'{i} {j}  add to  near obj')
            # if entry_i["dec"] == 71.30788888888888 or entry_j["dec"] == 71.30788888888888 :
            #     print(f'{i}  {j}    [{entry_i["ra"]}  {entry_i["dec"]}]    [{entry_j["ra"]}  {entry_j["dec"]}]    {offset_x}  {offset_y}')
    skip_i.append(i)
    near_obj.append(entry_i)
    plan_list_centers.append([next_center_ra, next_center_dec])
    # print(f'{i}   = {len(near_obj)}')
    plan_list.append(near_obj)

print(f'-------------{len(plan_list)}--------------')
print()


def generate_color(c_index):
    color = c_index % 12
    if color == 0:
        return f"#FF2200"
    elif color == 7:
        return f"#692000"
    elif color == 2:
        return f"#FF6600"
    elif color == 9:
        return f"#bd87de"
    elif color == 4:
        return f"#00a0f8"
    elif color == 11:
        return f"#886f04"
    elif color == 6:
        return f"#FFFF00"
    elif color == 1:
        return f"#588002"
    elif color == 8:
        return f"#AAFF00"
    elif color == 3:
        return f"#af13ef"
    elif color == 10:
        return f"#66FF00"
    elif color == 5:
        return f"#05f3c7"


print(f'MarkerMgr.deleteAllMarkers() ;')
# print(plan_list)
center_plan_item = {}
plan_center_color = '#AAAAFF'
plan_corner_color = '#888888'
for p_i, plan_item in enumerate(plan_list):
    plan_color = generate_color(p_i)
    # if p_i < 20:
    #     continue
    for point_item in plan_item:
        center_plan_item = point_item
        print(f'MarkerMgr.markerEquatorial("{point_item["ra"]}", "{point_item["dec"]}", true, true, "cross", '
              f'"{plan_color}", 8, false, 0) ;')
    center_plan_item = plan_list_centers[p_i]
    print(f'MarkerMgr.markerEquatorial("{center_plan_item[0]}", "{center_plan_item[1]}", true, true, "circle", '
          f'"{plan_color}", 10, false, 0) ;')
    ra_center = center_plan_item[0] * u.degree
    dec_center = center_plan_item[1] * u.degree
    a = SkyCoord(ra=ra_center, dec=dec_center)
    corner1 = a.spherical_offsets_by(ra_img_wide / 2, dec_img_high / 2)
    corner2 = a.spherical_offsets_by(-ra_img_wide / 2, dec_img_high / 2)
    corner3 = a.spherical_offsets_by(-ra_img_wide / 2, -dec_img_high / 2)
    corner4 = a.spherical_offsets_by(ra_img_wide / 2, -dec_img_high / 2)
    print(f'MarkerMgr.markerEquatorial("{corner1.ra.value}", "{corner1.dec.value}", true, true, "dashed-square", '
          f'"{plan_corner_color}", 6, false, 0) ;')
    print(f'MarkerMgr.markerEquatorial("{corner2.ra.value}", "{corner2.dec.value}", true, true, "dashed-square", '
          f'"{plan_corner_color}", 6, false, 0) ;')
    print(f'MarkerMgr.markerEquatorial("{corner3.ra.value}", "{corner3.dec.value}", true, true, "dashed-square", '
          f'"{plan_corner_color}", 6, false, 0) ;')
    print(f'MarkerMgr.markerEquatorial("{corner4.ra.value}", "{corner4.dec.value}", true, true, "dashed-square", '
          f'"{plan_corner_color}", 6, false, 0) ;')

print(f'; ========auto plan start {len(plan_list)} end================')
obj_count = 0
for p_i, plan_item in enumerate(plan_list):
    plan_color = generate_color(p_i)
    for point_item in plan_item:
        center_plan_item = point_item
        obj_count = obj_count + 1
    center_plan_item = plan_list_centers[p_i]
    ra_center = center_plan_item[0] * u.degree
    dec_center = center_plan_item[1] * u.degree
    a = SkyCoord(ra=ra_center, dec=dec_center)
    # print(f';begin')
    print(f'P_{p_i}    {center_plan_item[0]/15}    {center_plan_item[1]:+f}')
    # print(f';end')

print(f'; ========auto plan end exp_count:{len(plan_list)}  ojb_count:{obj_count} end================')


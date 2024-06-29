import re


def dms_to_deg(d, m, s):
    d_v = float(d)
    m_v = float(m)
    s_v = float(s)
    d_v_abs = abs(d_v)
    sign = 1 if d_v >= 0 else -1
    return sign * (d_v_abs + m_v / 60 + s_v / 3600)


def hms_to_deg(h, m, s):
    h_v = float(h)
    m_v = float(m)
    s_v = float(s)
    return (h_v * 15) + (m_v * 15 / 60) + (s_v * 15 / 3600)


def get_ra_dec_from_string(src_string_hms_dms, src_string_ra_dec):
    print(f'hms dms [{src_string_hms_dms}]{len(src_string_hms_dms)}            ra dec[{src_string_ra_dec}]{len(src_string_ra_dec)}')
    assert (len(src_string_hms_dms) > 0 and len(src_string_ra_dec) == 0) or (
                len(src_string_hms_dms) == 0 and len(src_string_ra_dec) > 0)
    src_string = src_string_hms_dms if len(src_string_hms_dms) > 0 else src_string_ra_dec

    cord_array = re.findall(r'-?\d+(?:\.\d+)?', src_string)
    if not cord_array:
        print(f"座标提取长度错误:  [{src_string}]")
        return

    if len(cord_array) == 2:
        return float(cord_array[0]), float(cord_array[1])
    if len(cord_array) == 6:
        for cord_index, cord_val in enumerate(cord_array):
            print(cord_val)
        hms_ra_deg = hms_to_deg(float(cord_array[0]), float(cord_array[1]), float(cord_array[2]))
        print(f'hms_ra_deg: {hms_ra_deg}')
        dms_dec_deg = dms_to_deg(float(cord_array[3]), float(cord_array[4]), float(cord_array[5]))
        print(f'dms_dec_deg: {dms_dec_deg}')
        return hms_ra_deg, dms_dec_deg
    else:
        print(f"座标提取长度错误:  {len(cord_array)}   [{src_string}]")
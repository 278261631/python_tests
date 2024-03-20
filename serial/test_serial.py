# pip install pyserial
import datetime

import serial


ser = serial.Serial(
    port='COM3',
    baudrate=9600,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=2
)

# 检查串口是否打开
if ser.isOpen():
    print("串口已打开")

try:
    # 获取当前日期和时间
    now = datetime.datetime.now()
    future_time = now + datetime.timedelta(seconds=2)
    # 格式化日期为 "YYYYMMDD" 格式
    formatted_date = future_time.strftime("%Y%m%d")

    # 格式化时间为 "HHMMSS" 格式
    formatted_time = future_time.strftime("%H%M%S")
    # 发送数据
    data_to_send = '{"cmd_id":202,"s_date":%s,"s_time":%s}' % (formatted_date, formatted_time)
    ser.write(data_to_send.encode())

    # 读取返回数据
    while True:
        response = ser.readline().decode()
        if response:
            print("收到数据:", response)
            break  # 如果读取到数据则退出循环
        else:
            print("未收到数据，可能需要调整timeout或其他配置")

except Exception as e:
    print("发生错误:", e)

finally:
    ser.close()

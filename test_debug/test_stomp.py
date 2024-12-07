import time
import stomp
import random
import string
import json

# 连接到ActiveMQ的配置信息
activemq_host = "localhost"
activemq_port = 61613
queue_name = "/topic/chat.general"

# 生成随机FITS文件名的函数
def generate_fits_filename():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"image_{random_str}.fits"

# 创建连接对象
conn = stomp.Connection([(activemq_host, activemq_port)])
# 连接到ActiveMQ服务器
conn.connect(wait=True)

# 生成3个随机FITS文件名
fits_files = [generate_fits_filename() for _ in range(2)]

# 为每个文件发送3个不同阶段的消息
for fits_file in fits_files:
    for stage in [1, 2, 3]:
        
        message = json.dumps({
            "fits": fits_file,
            "stage": stage,
            "result": random.choice(['success', 'failed'])
        })
        conn.send(body=message, destination=queue_name)
        print(f"已发送消息: {message}")
        time.sleep(1)  # 修改延时为3秒，控制消息发送频率
        
for fits_file in fits_files:
    for stage in [1, 2, 3]:
        
        message = json.dumps({
            "fits": fits_file,
            "stage": stage,
            "result": random.choice(['success', 'failed'])
        })
        conn.send(body=message, destination=queue_name)
        print(f"已发送消息: {message}")
        time.sleep(1)  # 修改延时为3秒，控制消息发送频率

conn.disconnect()

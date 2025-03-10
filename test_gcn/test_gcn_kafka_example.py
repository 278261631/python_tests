import time
from datetime import timedelta

from gcn_kafka import Consumer
import json

# 读取配置文件
with open('config.json') as f:
    config = json.load(f)['kafka']


consumer = Consumer(client_id=config['client_id'],
                    client_secret=config['client_secret'])
# 以上内容改成从文本获取
start_time = time.time()

# Subscribe to topics and receive alerts
consumer.subscribe(['gcn.circulars',
                    'gcn.heartbeat',
                    'gcn.notices.icecube.lvk_nu_track_search',
                    'igwn.gwalert',
                    'gcn.notices.swift.bat.guano',
                    'gcn.notices.einstein_probe.wxt.alert'])
heart_beat_count = 0
while True:
    for message in consumer.consume(timeout=1):
        elapsed_time = time.time() - start_time
        if message.error():
            print(message.error())
            continue
        if message.topic() == 'gcn.heartbeat':
            heart_beat_count += 1
            formatted_time = str(timedelta(seconds=elapsed_time)).split(".")[0]  # 格式化为HH:MM:SS

            # print(f'topic={message.topic()}, offset={message.offset()}')

            # 12 hour
            if heart_beat_count % 43200 == 0:
                print('\r 12 H pass')
            print(f'\rHeartbeat {heart_beat_count}    {formatted_time}', end='', flush=True)


            continue
        if message.topic() == 'gcn.notices.einstein_probe.wxt.alert':
            print(f'topic={message.topic()}, offset={message.offset()}')
            # Print the topic and message ID
            value = message.value()
            print(f'\r-------------')
            print(value)
            print(f'-------------')
        else:
            print(f'topic={message.topic()}, offset={message.offset()}, elapsed_time={elapsed_time}')


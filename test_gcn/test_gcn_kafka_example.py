from gcn_kafka import Consumer
import json

# 读取配置文件
with open('config.json') as f:
    config = json.load(f)['kafka']


consumer = Consumer(client_id=config['client_id'],
                    client_secret=config['client_secret'])
# 以上内容改成从文本获取


# Subscribe to topics and receive alerts
consumer.subscribe(['gcn.circulars',
                    'gcn.heartbeat',
                    'gcn.notices.icecube.lvk_nu_track_search',
                    'igwn.gwalert',
                    'gcn.notices.swift.bat.guano',
                    'gcn.notices.einstein_probe.wxt.alert'])
while True:
    for message in consumer.consume(timeout=1):
        if message.error():
            print(message.error())
            continue
        # Print the topic and message ID
        print(f'topic={message.topic()}, offset={message.offset()}')
        value = message.value()
        print(value)

import time
from datetime import timedelta
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import stomp
from gcn_kafka import Consumer
import json
import logging

# pip install stomp.py
def load_fake_kafka_ep_message():
    fake_ep_message = f"""{{
      "$schema": "https://gcn.nasa.gov/schema/v4.2.0/gcn/notices/einstein_probe/wxt/alert.schema.json",
      "instrument": "WXT",
      "trigger_time": "2024-03-01T21:46:05.13Z",
      "id": ["01708973486"],
      "ra": 120,
      "dec": 40,
      "ra_dec_error": 0.02,
      "image_energy_range": [0.5, 4],
      "net_count_rate": 1,
      "image_snr": 1,
      "additional_info": "The net count rate is derived from an accumulated image (up to 20 min) in 0.5-4 keV, assuming a constant flux. However, it can be significantly lower than the actual count rate of a burst with a duration much shorter than 20 min."
    }}"""
    # 转换成json对象返回
    json_msg = json.loads(fake_ep_message)
    return json_msg
def load_msg_format():
    grb_message = f"""{{
        "task_Dec_deg":51.1236,
        "task_Ra_deg":3.0954,
        "task_status":"",
        "filterBinningIntervalCount":[],
        "task_command":"",
        "task_sets":0,
        "task_start_time":"",
        "task_plan_text":"",
        "target_eqp":"TEST",
        "task_targets":[],
        "task_end_time":"",
        "taskName":"GRB_2020-02-01_06-41-39-901"+testTaskName+"",
        "task_type":"",
        "task_level":"1000"
        }}"""
    # 转换成json对象返回
    json_msg = json.loads(grb_message)
    return json_msg
def reset_msg_format(json_obj):
    json_obj['task_Dec_deg'] = 0
    json_obj['task_Ra_deg'] = 0
    json_obj['target_eqp'] = '---'
    json_obj['taskName'] = '---'

def send_message(topic, stomp_message):
    # 创建连接
    conn = stomp.Connection([('127.0.0.1', 61613)])
    conn.connect(wait=True)
    conn.send(body=str(stomp_message), destination=topic)
    conn.disconnect()

# 创建每天轮转的处理器
time_handler = TimedRotatingFileHandler(
    filename='gcn_kafka.log',
    when='midnight',
    backupCount=365,
    encoding='utf-8'
)
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[time_handler]
)

# 读取配置文件
with open('config.json') as f:
    config = json.load(f)['kafka']


consumer = Consumer(client_id=config['client_id'],
                    client_secret=config['client_secret'])
# 以上内容改成从文本获取
start_time = time.time()
json_format = load_msg_format()
reset_msg_format(json_format)
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
            if heart_beat_count % 10 == 0:
                print('\r test amq ')
            if heart_beat_count % 43200 == 0:
                print('\r 12 H pass')
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f'\rHeartbeat {heart_beat_count}    {formatted_time}    {current_time}', end='', flush=True)


            continue
        if message.topic() == 'gcn.notices.einstein_probe.wxt.alert':
            print(f'topic={message.topic()}, offset={message.offset()}')
            # Print the topic and message ID
            value = message.value()
            print(f'\r-------------')
            print(value)

            try:
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                milliseconds = datetime.now().microsecond // 1000  # 取毫秒部分
                time_str = f"{current_time}-{milliseconds:03d}"

                print(time_str)  # 输出示例：2024-05-20_15-30-45-123
                json_from_kafka = json.loads(value)
                json_format['task_Dec_deg'] = json_from_kafka['dec']
                json_format['task_Ra_deg'] = json_from_kafka['ra']
                json_format['target_eqp'] = 'TEST'
                json_format['taskName'] = f'GRB_{time_str}_{json_from_kafka["id"]}'

                send_message("127.0.0.1", 61613, "/topic/test_topic", json_format)

            except Exception as e:
                logging.info(e)
                print(f"Error: {e}")
            logging.info(value)
            logging.info(json_format)

            print(f'-------------')
            reset_msg_format(json_format)
        else:
            print(f'topic={message.topic()}, offset={message.offset()}, elapsed_time={elapsed_time}')
            logging.info(f'topic={message.topic()}, offset={message.offset()}, elapsed_time={elapsed_time}')

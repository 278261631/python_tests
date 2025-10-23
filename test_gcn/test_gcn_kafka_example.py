import os
import time
from datetime import timedelta
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import traceback
import xml.etree.ElementTree as ET

import stomp
from gcn_kafka import Consumer
import json
import logging

# pip install stomp.py
# pip.exe install gcn-kafka
# pip.exe install cryptography

# win7 安装   https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
# D:\xxx\python38\Scripts\pip.exe uninstall cryptography -y
# D:\xxx\python38\Scripts\pip.exe install cryptography==3.4.8
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
    # json_msg = json.loads(fake_ep_message)
    return fake_ep_message
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
        "taskName":"GRB_2020-02-01_06-41-39-901",
        "task_type":"",
        "task_level":"1000"
        }}"""
    # 转换成json对象返回
    json_msg = json.loads(grb_message)
    return json_msg
def load_msg_status_format():
    grb_message = f"""{{
    "messageTime": "2025-03-21 10:49:27", 
    "msgType": "gcn_kafka", 
    "deviceName": "gcn_kafka", 
    "deviceStatus": "OK", 
    "deviceColor": "#FFAA00",
    "sqm-val": "",
    "messageColor": "green"
    }}"""
    # 转换成json对象返回
    json_msg = json.loads(grb_message)
    return json_msg
def reset_msg_format(json_obj):
    json_obj['task_Dec_deg'] = 0
    json_obj['task_Ra_deg'] = 0
    json_obj['target_eqp'] = '---'
    json_obj['taskName'] = '---'

def send_message(server_address, server_port, topic, stomp_message):
    # 创建连接
    conn = stomp.Connection([(server_address, server_port)])
    conn.connect(wait=True)
    conn.send(body=str(stomp_message), destination=topic)
    conn.disconnect()


# 创建每天轮转的处理器
os.makedirs('log', exist_ok=True)
time_handler = TimedRotatingFileHandler(
    filename='log/gcn_kafka.log',
    when='midnight',
    backupCount=365,
    encoding='utf-8'
)
# 配置日志
logging.basicConfig(
    # level=logging.WARNING,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[time_handler]
)

# 读取配置文件
with open('config.json') as f:
    config = json.load(f)['kafka']


consumer = Consumer(client_id=config['client_id'],
                    client_secret=config['client_secret'])
# 以上内容改成从文本获取
logging.warning('Start 开始')
start_time = time.time()
json_format = load_msg_format()
reset_msg_format(json_format)
json_format_test = load_msg_format()
reset_msg_format(json_format_test)
json_status_format = load_msg_status_format()
# Subscribe to topics and receive alerts
consumer.subscribe([
                    # 'gcn.circulars',
                    'gcn.heartbeat',
                    'gcn.notices.svom.voevent.eclairs',
                    # 'gcn.notices.icecube.lvk_nu_track_search',
                    # 'igwn.gwalert',
                    # 'gcn.notices.swift.bat.guano',
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
                # print('\r test amq ')
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                milliseconds = datetime.now().microsecond // 1000  # 取毫秒部分
                time_str = f"{current_time}-{milliseconds:03d}"

                # print(time_str)  # 输出示例：2024-05-20_15-30-45-123

                # fake_value = load_fake_kafka_ep_message()
                try:

                    # fake_json_from_kafka = json.loads(fake_value)
                    # json_format_test['task_Dec_deg'] = fake_json_from_kafka['dec']
                    # json_format_test['task_Ra_deg'] = fake_json_from_kafka['ra']
                    # json_format_test['target_eqp'] = config['target_eqp']
                    # json_format_test['taskName'] = f'GRB_{time_str}_test_{fake_json_from_kafka["id"][0]}'
                    #
                    # send_message(config['server_address'], config['server_port'], config['topic_path'], json_format_test)
                    json_status_format['messageTime'] = time_str
                    send_message(config['server_address'], config['server_port'], config['status_topic_path'], json_status_format)
                except Exception as e:
                    print(f"Error-: {traceback.format_exc()}")
                    logging.exception("Error processing message")
                    print(f"Error: {e}")
                # logging.debug(json_format_test)

            if heart_beat_count % 43200 == 0:
                print('\r 12 H pass')
                logging.warning('12 H pass')
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
                json_format['target_eqp'] = config['target_eqp']
                json_format['taskName'] = f'GRB_{time_str}_EP_{json_from_kafka["id"][0]}'

                send_message(config['server_address'], config['server_port'], config['topic_path'], json_format)

            except Exception as e:
                print(f"Error-: {traceback.format_exc()}")
                logging.exception("Error processing message")
                print(f"Error: {e}")
            logging.warning(value)
            logging.warning(json_format)

            print(f'-------------')
            reset_msg_format(json_format)
        if message.topic() == 'gcn.notices.svom.voevent.eclairs':
        # if message.topic() == 'gcn.heartbeat':
        #     if heart_beat_count % 10 != 0:
        #         continue

            print(f'topic={message.topic()}, offset={message.offset()}')
            # Print the topic and message ID
            value = message.value()
            # read from eclairs-wakeup.xml
            # value = open('eclairs-wakeup.xml', 'r').read()
            print(f'\r-------------')
            print(value)

            try:
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                milliseconds = datetime.now().microsecond // 1000
                time_str = f"{current_time}-{milliseconds:03d}"

                print(time_str)

                # Parse XML
                root = ET.fromstring(value)

                # Define namespaces
                ns = {'voe': 'http://www.ivoa.net/xml/VOEvent/v2.0'}

                # Extract RA and Dec from Position2D
                # Position2D and its children are not in namespace
                position = root.find('.//Position2D')
                if position is None:
                    raise ValueError("Position2D not found in XML")

                value2 = position.find('Value2')
                if value2 is None:
                    raise ValueError("Value2 not found in Position2D")

                c1_elem = value2.find('C1')
                c2_elem = value2.find('C2')
                if c1_elem is None or c2_elem is None:
                    raise ValueError("C1 or C2 not found in Value2")

                ra = float(c1_elem.text)
                dec = float(c2_elem.text)

                # Extract Burst_Id - use iter to find elements
                burst_id = None
                for group in root.iter():
                    if 'Group' in group.tag and group.get('name') == 'Svom_Identifiers':
                        for param in group.iter():
                            if 'Param' in param.tag and param.get('name') == 'Burst_Id':
                                burst_id = param.get('value')
                                break
                        break

                if burst_id is None:
                    raise ValueError("Burst_Id not found in XML")

                json_format['task_Dec_deg'] = dec
                json_format['task_Ra_deg'] = ra
                json_format['target_eqp'] = config['target_eqp']
                json_format['taskName'] = f'GRB_{time_str}_SVOM_{burst_id}'

                send_message(config['server_address'], config['server_port'], config['topic_path'], json_format)

            except Exception as e:
                print(f"Error-: {traceback.format_exc()}")
                logging.exception("Error processing message")
                print(f"Error: {e}")
            logging.warning(value)
            logging.warning(json_format)

            print(f'-------------')
            reset_msg_format(json_format)
        else:
            print(f'topic={message.topic()}, offset={message.offset()}, elapsed_time={elapsed_time}')
            logging.warning(f'topic={message.topic()}, offset={message.offset()}, elapsed_time={elapsed_time}')

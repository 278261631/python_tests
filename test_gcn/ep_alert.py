import os
import time
import queue
import logging
import sys
import json
import threading

# paho-mqtt 1.6.1
import paho.mqtt.client as mqtt
# pip install stomp.py
import stomp

fol='./'

# Load config from config.json
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
mqtt_config = config['mqtt']
kafka_config = config['kafka']

# Heartbeat config
HEARTBEAT_INTERVAL = mqtt_config.get('heartbeat_interval', 5)  # default 60 seconds
start_time = time.time()
heart_beat_count = 0


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
    json_msg = json.loads(grb_message)
    return json_msg


def reset_msg_format(json_obj):
    json_obj['task_Dec_deg'] = 0
    json_obj['task_Ra_deg'] = 0
    json_obj['target_eqp'] = '---'
    json_obj['taskName'] = '---'


def send_message(server_address, server_port, topic, stomp_message):
    try:
        conn = stomp.Connection([(server_address, server_port)])
        conn.connect(wait=True)
        conn.send(body=str(stomp_message), destination=topic)
        conn.disconnect()
        logger.info(f"Message sent to {topic}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


# 配置logger
PROG_NAME = 'ep_alert.py'
logger = logging.getLogger()
logger.setLevel(logging.INFO)

hdl_stream = logging.StreamHandler()
hdl_stream.setLevel(logging.INFO)

fmt_stream = logging.Formatter(
    fmt=PROG_NAME+" @ %(asctime)s UTC, %(levelname)s: %(message)s",
    datefmt='%Y-%m-%dT%H:%M:%S')
fmt_stream.converter = time.gmtime

hdl_stream.setFormatter(fmt=fmt_stream)
logger.addHandler(hdl_stream)

hdl_file = logging.FileHandler(
    filename=os.path.join(fol, "{}.log".format(os.path.splitext(PROG_NAME)[0])),
    mode="a+",
    encoding="utf-8")
hdl_file.setLevel(logging.DEBUG)
hdl_file.setFormatter(fmt_stream)
logger.addHandler(hdl_file)

# Init message format
json_format = load_msg_format()
reset_msg_format(json_format)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    from datetime import datetime
    logger.info('{} - {} - {}: {}'.format(msg.topic, msg.qos, msg.retain, str(msg.payload.decode("utf-8"))))
    try:
        value = json.loads(str(msg.payload.decode("utf-8")))
        name = value['object']
        hr = float(value['hr'])
        rate = float(value['netRate'])

        # Save to log file
        if (hr > 0.04) & (rate < 2.01):
            with open(f"{fol}/EP_WXT{name}.log", "a+") as f:
                f.write(str(msg.payload.decode("utf-8")) + "\n")

        # Forward message via STOMP
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        milliseconds = datetime.now().microsecond // 1000
        time_str = f"{current_time}-{milliseconds:03d}"

        json_format['task_Dec_deg'] = float(value['dec'])
        json_format['task_Ra_deg'] = float(value['ra'])
        json_format['target_eqp'] = kafka_config['target_eqp']
        json_format['taskName'] = f'GRB_{time_str}_WXT_{name}'

        send_message(
            kafka_config['server_address'],
            kafka_config['server_port'],
            kafka_config['topic_path'],
            json_format
        )

        logger.warning(f"Forwarded EP message: {json_format['taskName']}")
        print(f"\nForwarded: {json_format['taskName']}")
        reset_msg_format(json_format)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        with open(f"{fol}/EP_bd.log", "a+") as f:
            f.write(str(msg.payload.decode("utf-8")) + "\n")

def on_connect(client, userdata, flags, rescode):
    if rescode==0:
        client.connected_flag=True #set flag
        logger.info("connected OK Returned code={}".format(rescode))
    else:
        logger.warning("Bad connection Returned code={}".format(rescode))

def on_disconnect(client, userdata, rescode):
    logging.info("disconnecting reason  "  +str(rescode))
    client.connected_flag=False
    client.disconnect_flag=True
    print("网络有波动，10秒后重启警报程序...")
    python =sys.executable
    time.sleep(10)
    os.execl(python,python,*sys.argv)


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribing qos = ", granted_qos)


# Heartbeat thread function
def heartbeat_check():
    global heart_beat_count
    from datetime import timedelta, datetime
    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        heart_beat_count += 1
        elapsed_time = time.time() - start_time
        formatted_time = str(timedelta(seconds=elapsed_time)).split(".")[0]
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")

        # Print heartbeat status on same line
        print(f'\rHeartbeat {heart_beat_count}    {formatted_time}    {current_time}', end='', flush=True)

        # Log every 10 heartbeats
        if heart_beat_count % 10 == 0:
            logger.info(f"Heartbeat {heart_beat_count}, running {formatted_time}")

        # Log every 12 hours (43200 seconds / HEARTBEAT_INTERVAL)
        twelve_hour_count = 43200 // HEARTBEAT_INTERVAL
        if heart_beat_count % twelve_hour_count == 0:
            print('\r 12 H pass')
            logger.warning('12 H pass')


host = mqtt_config['host']
port = mqtt_config['port']

topics = [(t['name'], t['qos']) for t in mqtt_config['topics']]

username = mqtt_config['username']
password = mqtt_config['password']

mqtt.Client.connected_flag = False

# 连接
client = mqtt.Client(client_id="HMT_ep", transport='tcp')
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.on_subscribe = on_subscribe

client.username_pw_set(username=username, password=password)
client.connect(host=host, port=port)

client.subscribe(topics)

# Start heartbeat thread
heartbeat_thread = threading.Thread(target=heartbeat_check, daemon=True)
heartbeat_thread.start()
logger.info("Heartbeat thread started, interval: {}s".format(HEARTBEAT_INTERVAL))

client.loop_forever()

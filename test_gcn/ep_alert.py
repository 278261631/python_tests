import os
import time
import queue
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import json
import threading

# paho-mqtt 1.6.1
# paho-mqtt 2.1.0
import paho.mqtt.client as mqtt
# pip install stomp.py
import stomp

fol='./'

# Create log folder
log_folder = os.path.join(os.path.dirname(__file__), 'log')
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Load config from config.json
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
mqtt_config = config['mqtt']
kafka_config = config['kafka']

# Heartbeat config
HEARTBEAT_INTERVAL = mqtt_config.get('heartbeat_interval', 5)  # default 60 seconds
KEEPALIVE = mqtt_config.get('keepalive', 60)  # MQTT keepalive interval
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

# File handler with daily rotation
log_file_path = os.path.join(log_folder, os.path.splitext(PROG_NAME)[0])
hdl_file = TimedRotatingFileHandler(
    filename=log_file_path + ".log",
    when='midnight',
    interval=1,
    backupCount=0,
    encoding="utf-8"
)
hdl_file.suffix = "%Y-%m-%d.log"
hdl_file.setLevel(logging.DEBUG)
hdl_file.setFormatter(fmt_stream)
logger.addHandler(hdl_file)

# Init message format
json_format = load_msg_format()
reset_msg_format(json_format)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    from datetime import datetime
    payload_str = msg.payload.decode("utf-8")
    logger.info('{} - {} - {}: {}'.format(msg.topic, msg.qos, msg.retain, payload_str))
    try:
        try:
            value = json.loads(payload_str)
            # logger.debug("Parsed with json.loads")
        except json.JSONDecodeError:
            import ast
            value = ast.literal_eval(payload_str)
            # logger.debug("Parsed with ast.literal_eval")
        name = value['object']
        hr = float(value['hr'])
        rate = float(value['netRate'])

        # Save to log file
        if (hr > 0.04) & (rate < 2.01):
            with open(f"{fol}/EP_WXT{name}.log", "a+") as f:
                f.write(payload_str + "\n")

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
        logger.error(f"Error processing message: {type(e).__name__}: {e}, payload={payload_str}")
        with open(f"{fol}/EP_bd.log", "a+") as f:
            f.write(payload_str + "\n")

def on_connect(client, userdata, flags, rescode):
    if rescode == 0:
        logger.info("connected OK Returned code={}".format(rescode))
        # 连接成功后立即订阅，保证重连后也会自动订阅
        client.subscribe(topics)
        logger.info(f"✓ subscribing topics = {topics}")
    else:
        logger.warning("Bad connection Returned code={}".format(rescode))

def on_disconnect(client, userdata, rescode):
    logger.info("disconnecting reason: " + str(rescode))
    if rescode != 0:
        logger.warning("Unexpected disconnection, will auto reconnect...")


def on_subscribe(client, userdata, mid, granted_qos):
    logger.info(f"subscribed mid={mid}, qos={granted_qos}")
    try:
        # 128 indicates subscription failure in MQTT v3.1.1
        if any(q == 128 for q in granted_qos):
            logger.error(f"subscription failed for mid={mid}, granted_qos={granted_qos}")
    except Exception:
        pass


# Heartbeat thread function - monitor connection status
def heartbeat_check():
    global heart_beat_count
    from datetime import timedelta

    # # Test message
    # test_msg_payload = '{"procver":"3.17.13","posErr":"2.161999999","cmosNum":"32","mjdrefi":"58849","dec":"8.704000000","mjdreff":"0.00080074074","reproc":"T","seqpnum":"0","versionNum":0,"origin":"NAOC","hr":"0.15","dateEnd":"2025-04-07T19:01:05.687","detnam":"CMOS32","netRate":"196.62","segNum":"53","timesys":"TT","paPnt":"0","softver":"Hea_15Aug2039_V6.22_epwxtdas_11Jul39_v3.4.0","clockapp":"F","checksum":"UANhX1MeU8MeU8Me","caldbver":"x20391113","delflag":0,"q1":"0.372559636","q2":"0.157583639","q3":"0.911895751","q4":"-0.069374710","targId":"01709134053","datasum":"0","var":"98.109999999","utcfinit":"0","timeunit":"s","ra":"181.040999999","obsId":"01709134053","alarmType":0,"dateObs":"2025-04-07T18:55:45.978","raPnt":"181.041","trigtime":"166215596.503","telescop":"EP","decPnt":"8.704000000000001","decObj":"8.704000000000001","x":"643.299999999","srcSignificance":"174.4","y":"696.399999999","raObj":"181.041","instrume":"WXT","object":"01709134053"}'
    #
    # class FakeMsg:
    #     def __init__(self, payload):
    #         self.payload = payload.encode('utf-8')
    #         self.topic = 'test/ep_alert'
    #         self.qos = 1
    #         self.retain = False
    #
    # test_triggered = False

    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        heart_beat_count += 1
        elapsed_time = time.time() - start_time
        formatted_time = str(timedelta(seconds=elapsed_time)).split(".")[0]
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")

        # Check connection status
        status = "OK" if client.is_connected() else "DISCONNECTED"

        # Print heartbeat status on same line
        print(f'\rHeartbeat {heart_beat_count}  {status}  {formatted_time}  {current_time}', end='', flush=True)

        # # Trigger test message before reaching 10 heartbeats (only once)
        # if not test_triggered and heart_beat_count == 5:
        #     logger.info("Triggering test message...")
        #     fake_msg = FakeMsg(test_msg_payload)
        #     on_message(client, None, fake_msg)
        #     test_triggered = True

        # Log every 10 heartbeats
        if heart_beat_count % 10 == 0:
            if client.is_connected():
                logger.info(f"Heartbeat {heart_beat_count}, status: {status}, running {formatted_time}")
            else:
                logger.warning(f"Heartbeat {heart_beat_count}, status: {status}, running {formatted_time}")

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

# 连接
client = mqtt.Client(client_id="HMT_ep_debug2", transport='tcp')
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.on_subscribe = on_subscribe

# Enable auto reconnect
client.reconnect_delay_set(min_delay=1, max_delay=120)

client.username_pw_set(username=username, password=password)
client.connect(host=host, port=port, keepalive=KEEPALIVE)

# subscribe will be performed in on_connect() after connection is established

# Start heartbeat thread
heartbeat_thread = threading.Thread(target=heartbeat_check, daemon=True)
heartbeat_thread.start()
logger.info("Heartbeat thread started, interval: {}s, keepalive: {}s".format(HEARTBEAT_INTERVAL, KEEPALIVE))

client.loop_forever()

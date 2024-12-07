import json
from enum import Enum

import stomp


activemq_host = "localhost"
activemq_port = 61613
queue_name = "/topic/chat.general"


class ProcessStatus(Enum):
    SUCCESS = "success"
    FAILED = "fail"
    DEFAULT = "default"
    SKIP = "skip"


def send(message):
    try:
        # 创建连接对象
        conn = stomp.Connection([(activemq_host, activemq_port)])
        # 连接到ActiveMQ服务器
        conn.connect(wait=True)
        conn.send(body=message, destination=queue_name)
        print("消息已发送到队列")
        conn.disconnect()
    except Exception as ex:
        print(f'False: {ex}')
        pass
    return False


def send_amq(fits_file, stage=1, status=ProcessStatus.DEFAULT):
    try:
        # 创建连接对象
        conn = stomp.Connection([(activemq_host, activemq_port)])
        # 连接到ActiveMQ服务器
        conn.connect(wait=True)
        result = status.value
        message = json.dumps({
            "fits": fits_file,
            "stage": stage,
            "result": result
        })
        conn.send(body=message, destination=queue_name)
        print(f"-> {message}")
        conn.disconnect()
    except Exception as ex:
        print(f'False: {ex}')
        pass
    return False


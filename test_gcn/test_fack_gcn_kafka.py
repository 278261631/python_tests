import stomp

# 队列名称
location_queue = "/queue/test-activemq-queue"

# 创建连接
conn = stomp.Connection([('127.0.0.1', 61613)])
conn.connect(wait=True)

# 发送消息到队列
def send_to_queue(msg):
    conn.send(body=str(msg), destination=location_queue)
    print(f"Sent message: {msg}")

if __name__ == '__main__':
    send_to_queue('Hello, ActiveMQ!')
    conn.disconnect()
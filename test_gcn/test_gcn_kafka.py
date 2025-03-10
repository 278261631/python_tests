from kafka import KafkaConsumer
import json

# Kafka配置参数
bootstrap_servers = 'kafka-host:9092'  # 替换为GCN Kafka实际地址
topic = 'gcn.notices.einstein_probe.wxt.alert'  # EP通知主题
group_id = 'ep-notice-consumer-group'  # 消费者组ID

# 创建Kafka消费者
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=bootstrap_servers,
    auto_offset_reset='earliest',  # 从最早的消息开始消费
    group_id=group_id,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print(f"开始监听EP通知主题: {topic}...")

try:
    for message in consumer:
        # 解析消息内容
        notice = message.value

        # 打印消息元数据
        print("\n收到新通知:")
        print(f"主题: {message.topic}")
        print(f"分区: {message.partition}")
        print(f"偏移量: {message.offset}")

        # 处理通知内容
        print("\n通知内容:")
        print(f"事件ID: {notice.get('event_id', 'N/A')}")
        print(f"触发时间: {notice.get('trigger_time', 'N/A')}")
        print(f"RA: {notice.get('ra', 'N/A')} 度")
        print(f"Dec: {notice.get('dec', 'N/A')} 度")
        print(f"可信度: {notice.get('confidence', 'N/A')}%")
        print(f"事件类型: {notice.get('event_type', 'N/A')}")
        print("原始数据:", notice)

except KeyboardInterrupt:
    print("\n用户中断，停止消费...")
finally:
    consumer.close()
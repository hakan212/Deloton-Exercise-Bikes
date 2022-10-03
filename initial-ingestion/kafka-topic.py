from confluent_kafka import Consumer
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

KAFKA_SERVER = os.getenv('KAFKA_SERVER')
KAFKA_USERNAME=os.getenv('KAFKA_USERNAME')
KAFKA_PASSWORD=os.getenv('KAFKA_PASSWORD')
KAFKA_TOPIC_NAME = os.getenv('KAFKA_TOPIC_NAME')

values = []

# Consumer with `confluent_kafka`
c = Consumer({
    'bootstrap.servers': KAFKA_SERVER,
    'group.id': f'deleton' +str(uuid.uuid1()),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': KAFKA_USERNAME,
    'sasl.password': KAFKA_PASSWORD,
    'session.timeout.ms': 6000,
    'heartbeat.interval.ms': 1000,
    'fetch.wait.max.ms': 6000,
    'auto.offset.reset': 'latest',
    'enable.auto.commit': 'false',
    'max.poll.interval.ms': '86400000',
    'topic.metadata.refresh.interval.ms': "-1",
    "client.id": 'id-002-005',
})

c.subscribe([KAFKA_TOPIC_NAME])


i = 0
while i < 50:
    kafka_message = c.poll(0.5)

    if kafka_message is not None:
        print(kafka_message)

        kafka_message_value = kafka_message.value().decode('utf-8')

        print(kafka_message_value)

    i += 1
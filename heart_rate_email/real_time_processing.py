import os
from confluent_kafka import Consumer
from dotenv import load_dotenv
load_dotenv()
import json
import re
import uuid

KAFKA_SERVER = os.getenv('KAFKA_SERVER')
KAFKA_USERNAME=os.getenv('KAFKA_USERNAME')
KAFKA_PASSWORD=os.getenv('KAFKA_PASSWORD')
KAFKA_TOPIC_NAME = os.getenv('KAFKA_TOPIC_NAME')

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

current_data = {}


def update_heart_rate (current_data: dict, log: str):
## Will update current_data given log containing information on the current ride 
    values = json.loads(log)
    new_log = values.get('log')

    if 'Telemetry' in new_log:
        new_log = new_log.split(' mendoza v9: [INFO]: Telemetry - ')
        timestamp = new_log[0]
        current_data['timestamp'] = timestamp

        heart_rpm_and_power = re.findall(r'\d+.?\d+|\d',new_log[1])
        heart_rate = int(heart_rpm_and_power[0])
        current_data['heart_rate'] = heart_rate


def update_user_information (current_data: dict, user_information: str):
## Given string from log on new user, will update current_data user information
    current_data['user_id'] = int(re.findall('"user_id":(\d+)', user_information)[0])
    current_data['user_name'] = re.findall('"name":"(\w+ \w+ \w+|\w+ \w+)', user_information)[0]
    current_data['user_dob'] = int(re.findall('"date_of_birth\\":([-\d]+)', user_information)[0])
    current_data['user_email'] = re.findall('"email_address":"(.+@\w+.\w+)"', user_information)[0]


def update_current_rider_information (current_data: dict, log: str):
## Updates information on current rider
    values = json.loads(log)
    new_log = values.get('log')
    new_log = new_log.split(' mendoza v9: [SYSTEM] data = ')

    current_data['timestamp'] = new_log[0]
    user_information = new_log[1]

    update_user_information(current_data, user_information)


while True:
    kafka_message = c.poll(0.5) #poll all messages that have occurred in last 0.5 seconds

    if kafka_message is not None: #ensure we have a message
        log = kafka_message.value().decode('utf-8')

        if 'INFO' in log: #only check for strings with INFO
            update_heart_rate(current_data, log)
        
        if 'SYSTEM' in log:
            update_current_rider_information(current_data, log)    

        if '-------' in log or 'Getting user data from server' in log:
            current_data = {}

    print(current_data)
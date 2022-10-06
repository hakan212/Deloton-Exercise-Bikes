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

current_data = {}

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


def update_duration_and_resistance(current_data: dict, duration_and_resistance: list):
## Will update current_data given [duration, resistance]
    duration = duration_and_resistance[0]
    resistance = duration_and_resistance[1]

    current_data['duration'] = float(duration)
    current_data['resistance'] = int(resistance)

def update_heart_rpm_and_power(current_data: dict, heart_rpm_and_power: list):
## Will update current_data given [heart, rpm, power]
    heart_rate = int(heart_rpm_and_power[0])
    rpm = int(heart_rpm_and_power[1])
    power = round(float(heart_rpm_and_power[2]),2)

    current_data['heart_rate'] = heart_rate
    current_data['rpm'] = rpm
    current_data['power'] = power

def update_current_ride_metrics (current_data: dict, log: str):
## Will update current_data given log containing information on the current ride 
    values = json.loads(log)
    new_log = values.get('log')

    if 'Ride' in new_log: #process strings with Ride info
        new_log = new_log.split(' mendoza v9: [INFO]: Ride - ')
        timestamp = new_log[0]
        current_data['timestamp'] = timestamp

        duration_and_resistance = re.findall(r'\d+.?\d+|\d',new_log[1])
        update_duration_and_resistance(current_data, duration_and_resistance)

    if 'Telemetry' in new_log:
        new_log = new_log.split(' mendoza v9: [INFO]: Telemetry - ')
        timestamp = new_log[0]
        current_data['timestamp'] = timestamp

        heart_rpm_and_power = re.findall(r'\d+.?\d+|\d',new_log[1])
        update_heart_rpm_and_power(current_data, heart_rpm_and_power)

def update_user_information (current_data: dict, user_information: str):
## Given string from log on new user, will update current_data user information
    current_data['user_id'] = int(re.findall('"user_id":(\d+)', user_information)[0])
    current_data['user_name'] = re.findall('"name":"(\w+ \w+ \w+|\w+ \w+)', user_information)[0]
    current_data['user_gender'] = re.findall('"gender":"(\w+)', user_information)[0]
    current_data['user_address'] = re.findall('"address":"([\w ,]+)', user_information)[0]
    current_data['user_dob'] = int(re.findall('"date_of_birth":(-\d+)', user_information)[0])
    current_data['user_email'] = re.findall('"email_address":"(.+@\w+.\w+)"', user_information)[0]
    current_data['user_height'] = int(re.findall('"height_cm":(\d+)', user_information)[0])
    current_data['user_weight'] = int(re.findall('"weight_kg":(\d+)', user_information)[0])
    current_data['user_account_created'] = int(re.findall('"account_create_date":(\d+)', user_information)[0])
    current_data['user_bike_serial'] = re.findall('"bike_serial":"(\w+)', user_information)[0]

def update_current_rider_information (current_data: dict, log: str):
## Updates information on current rider
    values = json.loads(log)
    new_log = values.get('log')
    new_log = new_log.split(' mendoza v9: [SYSTEM] data = ')

    current_data['timestamp'] = new_log[0]
    user_information = new_log[1]

    update_user_information(current_data, user_information)


def refresh_data():
    global current_data
    kafka_message = c.poll(0.5) #poll all messages that have occurred since last refresh
    

    if kafka_message is not None: #ensure we have a message
        log = kafka_message.value().decode('utf-8')

        if 'INFO' in log: #only check for strings with INFO
            update_current_ride_metrics(current_data, log)
        
        if 'SYSTEM' in log:
            update_current_rider_information(current_data, log)    

        if '-------' in log or 'Getting user data from server' in log:
            current_data = {}

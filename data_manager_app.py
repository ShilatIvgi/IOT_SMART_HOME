import sqlite3
import paho.mqtt.client as mqtt
from mqtt_init import *

# MQTT broker details
SUBSCRIBE_TOPIC = 'trashcan/fillLevel/+'  # Topic to subscribe to
THRESHOLD = 85  # Set your threshold value here

# SQLite database file
DB_FILE = 'mqtt_data.db'

# Function to create tables in the database
def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create table for sensor data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trashCanID TEXT,
        value REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create table for alerts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trashCanID TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

# Function to insert sensor data into the database
def insert_sensor_data(trashCanID, value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO sensor_data (trashCanID, value) VALUES (?, ?)', (trashCanID, value))
    conn.commit()
    conn.close()

# Function to insert an alert into the database
def insert_alert(trashCanID, message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO alerts (trashCanID, message) VALUES (?, ?)', (trashCanID, message))
    conn.commit()
    conn.close()
# Callback when a message is received on the subscribed topic
def on_message(client, userdata, message):
    try:
       # Extract trashCanID from the topic
        trashCanID = message.topic.split('/')[-1]

        # Parse the message payload as a float
        value = int(message.payload.decode())
        print(f"Received value: {value} from trashCanID: {trashCanID}")

        # Insert the sensor data into the database
        insert_sensor_data(trashCanID, value)

        # Check if value exceeds threshold and publish alert if needed
        if value > THRESHOLD:
            print(f"Value exceeds threshold ({THRESHOLD}), sending warning.")
            warning = f'''WARNING: Trash can {trashCanID} has exceeded the threshold value of {THRESHOLD}.'''
            # Insert an alert into the database
            insert_alert(trashCanID, warning)

    except ValueError:
        print(f"Invalid data received: {message.payload.decode()}")

create_tables()

# Create MQTT client instance
client = mqtt.Client()

# Set up the callback function to be called when a message is received
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_ip, int(broker_port))

# Subscribe to the desired topic
client.subscribe(SUBSCRIBE_TOPIC)

# Loop forever, checking for messages
print(f"Subscribed to {SUBSCRIBE_TOPIC}. Waiting for messages...")
client.loop_forever()

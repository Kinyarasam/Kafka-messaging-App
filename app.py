#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from confluent_kafka import Producer, Consumer, KafkaError
import threading


app = Flask(__name__)
socketio = SocketIO(app)


# Kafka configuration
kafka_bootstrap_servers = 'localhost:9092'
kafka_topic = 'messaging_app'

producer_config = {
    'bootstrap.servers': kafka_bootstrap_servers,
}

consumer_config = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'group.id': 'messaging_app_group',
    'auto.offset.reset': 'earliest',
}

# Kafka producer instance
producer = Producer(producer_config)

# Kafka consumer instance
consumer = Consumer(consumer_config)
consumer.subscribe([kafka_topic])

# Store connected clients
clients = set()


def kafka_consumer_thread():
    while True:
        msg = consumer.poll(timeout=1000)

        if msg is None:
            continue

        if not msg.error():
            message = msg.value().decode('utf-8')
            socketio.emit('new_message', {'message': message})  # , broadcast=True)

            
@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    clients.add(request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    clients.remove(request.sid)


@socketio.on('send_message')
def handle_send_message(data):
    message = data['message']

    # Produce message to Kafka
    producer.produce(kafka_topic, value=message)
    # producer.flush()



if __name__ == '__main__':
    kafka_consumer_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
    kafka_consumer_thread.start()

    socketio.run(app, debug=True)

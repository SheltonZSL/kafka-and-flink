"""Consume from a topic called 'log_topic' and print the message to the console"""

from confluent_kafka import Consumer

c = Consumer({

    'bootstrap.servers': 'localhost:9093',

    'group.id': 'mygroup',

    'auto.offset.reset': 'earliest'

    })

c.subscribe(['log_topic'])

while True:

    msg = c.poll(1.0)

    if msg is None:

        continue

    if msg.error():

        print("Consumer error: {}".format(msg.error()))

        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))


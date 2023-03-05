import time

import confluent_kafka
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic

# producer with 10 partitions
p = Producer({'bootstrap.servers': 'localhost:9093',
              'linger.ms': 100,
              'acks': 1,
              'batch.size': 100000,
              })
a = AdminClient({'bootstrap.servers': 'localhost:9093'})


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def log_generator():
    """
    This is a generator function that reads a log file and yields each line
    :return:
    """
    with open('bgl2k.log', 'r') as log_in:
        for line in log_in:
            yield line


def produce_to_kafka():

    # create a new topic with 10 partitions
    a.create_topics([NewTopic('log_topic', num_partitions=10, replication_factor=1)])
    counter = 0
    checkpoint = 0
    last_counter = 0
    while 1:
        time.sleep(0.04)
        for data in log_generator():
            # Trigger any available delivery report callbacks from previous produce() calls
            p.poll(0)
            #time.sleep(0.001)
            counter += 1
            if time.time() - checkpoint >= 1:
                print("Produced {} messages in 1 seconds".format(counter-last_counter))
                checkpoint = time.time()
                last_counter = counter
            # Asynchronously produce a message. The delivery report callback will
            # be triggered from the call to poll() above, or flush() below, when the
            # message has been successfully delivered or failed permanently.
            p.produce('log_topic', data.encode('utf-8'), partition=counter % 10) #, callback=delivery_report)
            # produce to multiple partitions
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
        p.flush()


if __name__ == '__main__':
    produce_to_kafka()

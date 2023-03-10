import time

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic
from log_protobuf_generator import log_generator

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


def produce_to_kafka():
    # create a new topic with 10 partitions
    a.create_topics([NewTopic('HDFS_log', num_partitions=10, replication_factor=1)])
    counter = 0
    checkpoint = 0
    last_counter = 0

    for log_data_raw, proto_log_data in log_generator():
        p.poll(0)

        counter += 1
        if time.time() - checkpoint >= 1:
            print("Produced {} messages in 1 seconds".format(counter - last_counter))
            checkpoint = time.time()
            last_counter = counter

        # Asynchronously produce a message. The delivery report callback will
        # be triggered from the call to poll() above, or flush() below, when the
        # message has been successfully delivered or failed permanently.
        log_value = proto_log_data.body.SerializeToString()

        log_key = proto_log_data.service.encode('utf-8')
        p.produce(topic='HDFS_log', key=log_key, value=log_data_raw.encode('utf-8'))
        # , callback=delivery_report)

    # Wait for any outstanding messages to be delivered and delivery report
    # callbacks to be triggered.
    p.flush()


if __name__ == '__main__':
    produce_to_kafka()

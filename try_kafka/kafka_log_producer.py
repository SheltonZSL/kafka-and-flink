import time

from confluent_kafka import Producer

p = Producer({'bootstrap.servers': 'localhost:9093'})


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
    for data in log_generator():
        # Trigger any available delivery report callbacks from previous produce() calls
        p.poll(0)

        # Asynchronously produce a message. The delivery report callback will
        # be triggered from the call to poll() above, or flush() below, when the
        # message has been successfully delivered or failed permanently.
        p.produce('log_topic', data.encode('utf-8'), callback=delivery_report)

    # Wait for any outstanding messages to be delivered and delivery report
    # callbacks to be triggered.
    p.flush()


if __name__ == '__main__':
    produce_to_kafka()

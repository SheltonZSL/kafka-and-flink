import argparse
import logging
import sys

from pyflink.common import WatermarkStrategy, Encoder, Types, SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat, FileSink, OutputFileConfig, \
    RollingPolicy
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer

counter = 0


def word_count(input_path, output_path):
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    env.set_parallelism(1)
    # env.add_jars("file:///flink-sql-connector-kafka-1.16.0.jar")
    # env.add_jars("file:///C:/Users/Shelton.z/OneDrive/桌面/kafka-and-flink/try_flink/datastream_api/flink-sql-connector"
    #              "-kafka-1.16.0.jar")
    # write all the data to one file
    brokers: str = 'kafka:9092'

    # protobuf serializer TODO
    source = KafkaSource.builder() \
        .set_bootstrap_servers(brokers) \
        .set_topics("log_topic") \
        .set_group_id("flink-consumer1") \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .set_property('enable.auto.commit', 'true') \
        .set_property('auto.commit.interval.ms', '200') \
        .build()

    ds = env.from_source(source, WatermarkStrategy.no_watermarks(), "Kafka Source")

    # print each in source
    #
    import time
    import os

    name = f'worker_{os.getpid()}'

    def split(line):
        global counter
        counter += 1
        if counter % 1000 == 0:
            print(f'Worker {name} working on log {counter}!!!!!!!!!!!!')
        yield from line.split()

    # compute word count
    ds = ds.flat_map(split).set_parallelism(20)

    # print(ds)
    # # define the sink
    # if output_path is not None:
    #     ds.sink_to(
    #         sink=FileSink.for_row_format(
    #             base_path=output_path,
    #             encoder=Encoder.simple_string_encoder())
    #         .with_output_file_config(
    #             OutputFileConfig.builder()
    #             .with_part_prefix("prefix")
    #             .with_part_suffix(".ext")
    #             .build())
    #         .with_rolling_policy(RollingPolicy.default_rolling_policy())
    #         .build()
    #     )
    # else:
    #     print("Printing result to stdout. Use --output to specify output path.")
    #     ds.print()
    # submit for execution
    env.execute()


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Input file to process.')
    parser.add_argument(
        '--output',
        dest='output',
        required=False,
        help='Output file to write results to.')

    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)

    word_count(known_args.input, known_args.output)

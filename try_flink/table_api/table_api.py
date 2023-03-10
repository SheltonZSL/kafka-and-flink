from pyflink.common import Row
from pyflink.table import EnvironmentSettings, TableEnvironment, TableResult, TableSchema, DataTypes, TableDescriptor, \
    Schema
from pyflink.table.udf import udtf, udf
from pyflink.table.expressions import col, lit
from pyflink.table.window import Tumble
from drain_mock import Model

# 1. create a TableEnvironment
kafka_env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())

# write all the data to one file
kafka_env.get_config().set("parallelism.default", "1")
kafka_env.get_config().set('pipeline.jars', "file:///C:/Users/Shelton.z/OneDrive/桌面/kafka-and-flink/try_flink"
                                            "/datastream_api/flink-sql-connector-kafka-1.16.0.jar;"
                                            "file:///C:/Users/Shelton.z/OneDrive/桌面/kafka-and-flink/try_flink"
                                            "/datastream_api/flink-sql-protobuf-1.16.0.jar")

# 2. create source Table


kafka_env.create_temporary_table(
    "Kafka_log",
    TableDescriptor.for_connector("kafka")
    .schema(Schema.new_builder()
            .column('service', DataTypes.STRING())
            .column("content", DataTypes.STRING())
            .build())
    .option("connector", "kafka")
    .option("topic", "HDFS_log")
    .option("properties.bootstrap.servers", "localhost:9093")
    .option("properties.group.id", "flink-consumer1")
    .option("scan.startup.mode", "earliest-offset")
    .option("key.format", "raw")
    .option("key.fields", "service")
    .option("value.format", "raw")
    .option("value.fields-include", "EXCEPT_KEY")
    .build()
)

tab = kafka_env.from_path("Kafka_log")

kafka_env.create_temporary_table(
    "sink_table",
    TableDescriptor.for_connector("kafka")
    .schema(Schema.new_builder()
            .column('service', DataTypes.STRING())
            .column("content", DataTypes.STRING())
            .build()
            )
    .option("connector", "kafka")
    .option("properties.bootstrap.servers", "localhost:9093")
    .option("topic", "HDFP_output")
    .option("value.format", "raw")
    .option("value.fields-include", "EXCEPT_KEY")
    .option("key.format", "raw")
    .option("key.fields", "service")
    .build())


@udtf(result_types=[DataTypes.STRING()])
def split(line: Row):
    for s in line[0].split():
        yield Row(s)


# compute word count
# tab.flat_map(split).alias('content')\
#     .select(col('content')) \
#     .execute_insert('sink_table') \
#     .wait()
from pyflink.table import Expression

model = udf(Model(), result_type=DataTypes.STRING())

# tab.select(tab.service, Expression.regexp_replace(tab.content, '\d{4}-\d{2}-\d{2}', '<DATETIME>')).\
#     .execute_insert('sink_table') \
#     .wait()
tab.select(tab.service, model(tab.content)) \
    .execute_insert('sink_table') \
    .wait()
# register the KafkaTableSource as table "input"

# https://cloud.tencent.com/developer/article/1769364
# https://nightlies.apache.org/flink/flink-docs-release-1.16/docs/connectors/table/formats/protobuf/#how-to-create-a-table-with-protobuf-format


# create a KafkaTableSource with protobuf format
# kafka_source = ...
# env.register_table_source("input", kafka_source)
#
# # create a KafkaTableSink with JSON format
# kafka_sink = ...
# env.register_table_sink("output", kafka_sink)
#
# # scan registered input table
# input_table = env.scan("input")
#
# # apply some transformations on input table
# output_table = input_table \
#     .filter(input_table.age > 18) \
#     .select(input_table.name.upper(), input_table.age + 1)
#
# # write output table to sink
# output_table.insert_into("output")
#
# # execute the job
# env.execute("Python Table API Example")
#
#
# # table_env.execute_sql("""
# # CREATE TABLE kafka_log (
# #    service STRING,
# #    log_data STRING
# # ) WITH (
# #   'connector' = 'kafka',
# #   'topic' = 'log_topic',
# #   'properties.bootstrap.servers' = 'localhost:9093',
# #   'properties.group.id' = 'testGroup',
# #   'scan.startup.mode' = 'earliest-offset',
# #   'key.format' = 'raw',
# #   'key.fields' = 'service',
# #
# #   'value.format' = 'raw',
# #   'value.fields-include' = 'ALL'
# # )
# # """)
# #
# # # 3. create sink Table
# # table_env.execute_sql("""
# #     CREATE TABLE print (
# #        service STRING,
# #         log_data STRING
# #     ) WITH (
# #         'connector' = 'print'
# #     )
# # """)
# #
# # source_table = table_env.from_path("kafka_log")
# # # or create a Table from a SQL query:
# # # source_table = table_env.sql_query("SELECT * FROM datagen")
# #
# # result_table = source_table.select(col("log_data"))
# # result_table.execute_insert("print").wait()

from pyflink.table import EnvironmentSettings, TableEnvironment
from pyflink.table.expressions import col

# 1. create a TableEnvironment
env_settings = EnvironmentSettings.in_streaming_mode()
table_env = TableEnvironment.create(env_settings)
table_env.get_config().set('pipeline.jars', "file:///C:/Users/Shelton.z/OneDrive/桌面/kafka-and-flink/try_flink"
                                            "/datastream_api/flink-sql-connector-kafka-1.16.0.jar;"
                                            "file:///C:/Users/Shelton.z/OneDrive/桌面/kafka-and-flink/try_flink"
                                            "/datastream_api/flink-sql-protobuf-1.16.0.jar")
# 2. create source Table
# https://cloud.tencent.com/developer/article/1769364
# https://nightlies.apache.org/flink/flink-docs-release-1.16/docs/connectors/table/formats/protobuf/#how-to-create-a-table-with-protobuf-format
table_env.execute_sql("""
CREATE TABLE kafka_log (
   service STRING,
   log_data STRING
) WITH (
  'connector' = 'kafka',
  'topic' = 'log_topic',
  'properties.bootstrap.servers' = 'localhost:9093',
  'properties.group.id' = 'testGroup',
  'scan.startup.mode' = 'earliest-offset',
  'key.format' = 'raw',
  'key.fields' = 'service',

  'value.format' = 'raw',
  'value.fields-include' = 'ALL'
)
""")

# 3. create sink Table
table_env.execute_sql("""
    CREATE TABLE print (
       service STRING,
        log_data STRING
    ) WITH (
        'connector' = 'print'
    )
""")

source_table = table_env.from_path("kafka_log")
# or create a Table from a SQL query:
# source_table = table_env.sql_query("SELECT * FROM datagen")

result_table = source_table.select(col("log_data"))
result_table.execute_insert("print").wait()

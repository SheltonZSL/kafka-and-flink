import random

from protocol.logging.Logging_pb2 import LogData, LogDataBody, TextLog, TraceContext, LogTags
from try_kafka.protocol.common.Common_pb2 import KeyStringValuePair


def log_generator():
    """Generate log data from a file, with fake skywalking tracing context."""
    with open(file='hadoop-28-min.log') as infile:
        for log in infile:
            log_text = TextLog(text=log)

            def build_log_tags() -> LogTags:
                core_tags = [
                    KeyStringValuePair(key='level', value='record.levelname'),
                    KeyStringValuePair(key='logger', value='record.name'),
                    KeyStringValuePair(key='thread', value='record.threadName')
                ]
                l_tags = LogTags()
                l_tags.data.extend(core_tags)

                return l_tags

            log_data_body = LogDataBody(type='text', text=log_text)
            log_data = LogData(
                timestamp=0,
                service=f'service_{random.randint(1, 10)}',
                serviceInstance=f'service_instance_{random.randint(1, 10)}',
                endpoint='niuniu',
                body=log_data_body,
                traceContext=TraceContext(traceId='trace_id_1', traceSegmentId='segment_id_1', spanId=1),
                tags=build_log_tags(),
                layer='niuniu',
            )
            log_msg_raw = log
            yield log_msg_raw, log_data


if __name__ == '__main__':
    for log in log_generator():
        print(log)

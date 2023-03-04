ds = env.from_source(
    source=FileSource.for_record_stream_format(StreamFormat.text_line_format(),
                                               input_path)
                     .process_static_file_set().build(),
    watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
    source_name="file_source"
)
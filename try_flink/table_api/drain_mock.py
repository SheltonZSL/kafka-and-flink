import json
from os.path import dirname

from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from pyflink.table import ScalarFunction, DataTypes


class Model(ScalarFunction):
    def __init__(self):
        self.model = None

        config = TemplateMinerConfig()
        config.load(dirname(__file__) + "/drain3.ini")
        config.profiling_enabled = True
        self.template_miner = TemplateMiner(config=config)

    def open(self, function_context):
        self.model = 0

    def eval(self, content):
        result = self.template_miner.add_log_message(content)

        self.model += 1
        print(self.model)
        result_string = json.dumps(result)
        return result_string

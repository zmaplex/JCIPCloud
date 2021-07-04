from typing import List

from django.apps import AppConfig

from base.config import ABSDBConfig


class CommonConfig(AppConfig):
    name = 'common'

    def ready(self):
        super(CommonConfig, self).ready()
        from .config import get_db_configs
        self.init_config(get_db_configs())

    @staticmethod
    def read_file(filepath):
        with open(filepath, 'r') as f:
            return f.read()

    def log_msg(self, msg):
        print(f"{self.name}::{msg}")

    def init_config(self, items: List[ABSDBConfig]):
        try:
            for item in items:
                item.init_data(self.name)
        except Exception as e:
            print(e)

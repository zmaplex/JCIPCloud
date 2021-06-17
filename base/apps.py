from common.apps import CommonConfig
from common.config import ABSDBConfig


class BaseConfig(CommonConfig):

    def ready(self):
        try:
            from common.config import get_db_configs
            items = get_db_configs()
            self.init_config(items)
        except Exception as e:
            print(e)


# VARS = vars()
#
#
# def get_db_configs():
#     data = []
#
#     for item in VARS.values():
#         if isinstance(item, ABSDBConfig):
#             data.append(item)
#     return data

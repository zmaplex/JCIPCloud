from base.config import ABSDBConfig


class DBConfig(ABSDBConfig):
    from common.models.SystemConfig import SystemConfig
    model = SystemConfig

    def init_data(self, module_name):
        obj, created = self.model.objects.get_or_create(key=self._key)
        if created:
            self.log_msg(f"创建配置项 {self._name}")
            obj.name = self._name
            obj.value = self._value
            obj.module_name = module_name
            obj.save()
        else:
            self.log_msg(f"创建配置项 {self._name}")
            pass

    def database_value(self):
        return self.model.get_value(self._key)

    def __init__(self, name, key, value):

        super().__init__(name, key, value)


"""
这里定义新的默认配置，如：
HOST_URL = DBConfig('域名', 'HOST', {'HOST_URL':'http://127.0.0.1:7000})
系统将会默认创建此条配置项
"""
API_URL = DBConfig('API域名', 'API_HOST', {'HOST_URL': 'http://127.0.0.1:7000'})
FRONT_URL = DBConfig('前端域名', 'FRONT_HOST', {'HOST_URL': 'http://127.0.0.1:7000'})

VARS = vars()


def get_db_configs():
    data = []

    for item in VARS.values():
        if isinstance(item, DBConfig):
            data.append(item)
    return data

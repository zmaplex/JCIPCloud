from pprint import pprint

from django.contrib.auth.models import User
from rest_framework import serializers


class GeneralSerializer(serializers.Serializer):

    @staticmethod
    def _log(data: dict):
        pprint(data)

    def get_user(self) -> User:
        """
        获取用户，初始化序列的时候，请添加 context={'request': request}，
        :return:
        """
        request = self.context.get('request', None)
        if request:
            return request.user
        raise RuntimeError(f"无法获取用户，请在初始化{self.__class__.__name__}的时候添加参数 context={'request': request}")

    def get_ipaddress(self) -> str:
        request = self.context.get('request', None)
        if not request:
            raise RuntimeError(f"无法获取用户IP地址，请在初始化{self.__class__.__name__}的时候添加参数 context={'request': request}")

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class BaseSerializer(GeneralSerializer):
    pass


class BaseModelSerializer(GeneralSerializer, serializers.ModelSerializer):
    pass

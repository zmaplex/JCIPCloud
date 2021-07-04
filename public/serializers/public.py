import requests
from django.conf import settings
from rest_framework import serializers

from base.serializer import BaseModelSerializer, GeneralSerializer
from base.tools import Geoip2Query
from public.models import IPInfo, RiskStatus

geo_ip = Geoip2Query()


class IPInfoSerializer(BaseModelSerializer):
    class Meta:
        model = IPInfo
        fields = '__all__'


class NormalIPInfoSerializer(GeneralSerializer):
    ipaddress = serializers.IPAddressField()

    def create(self, validated_data):
        ipaddress = validated_data.get('ipaddress')
        ip_info = geo_ip.query_city(ipaddress)

        if ip_info.is_idc:
            risk = RiskStatus.NON_HUMAN
            source_ip = self.get_ipaddress()
            score = 0
        else:
            risk = RiskStatus.REAL_PERSON
            source_ip = self.get_ipaddress() + " 正常用户"
            score = 0.3
        defaults = {'risk': risk,
                    'asn_info': ip_info.asn,
                    'source_ip': source_ip,
                    'recaptcha_score':score}

        obj, created = IPInfo.objects.update_or_create(ipaddress=ipaddress, defaults=defaults)

        return IPInfoSerializer(obj)


class GoogleRecaptchaVerifySerializer(GeneralSerializer):
    token = serializers.CharField(max_length=1024, help_text="谷歌前端验证的token")

    def create(self, validated_data):
        a = {'success': True, 'challenge_ts': '2021-06-16T06:24:53Z', 'hostname': 'localhost', 'score': 0.9,
             'action': 'homepage'}
        ipaddress = self.get_ipaddress()
        score = validated_data.get('token', 0)
        ip_info = geo_ip.query_city(ipaddress)

        if score < 0.3 or ip_info.is_idc:
            score = 0.1
            risk = RiskStatus.NON_HUMAN
        else:
            risk = RiskStatus.REAL_PERSON
        defaults = {'risk': risk,
                    'asn_info': ip_info.asn,
                    'recaptcha_score': score}

        obj, created = IPInfo.objects.update_or_create(ipaddress=ipaddress, defaults=defaults)

        return IPInfoSerializer(obj)

    def validate_token(self, token):
        url = settings.RECAPTCHA_V3_API
        secret = settings.RECAPTCHA_V3_SECRET
        data = {"secret": secret, "response": token}
        r = requests.post(url, data=data)
        res = r.json()
        if res['success']:
            return res['score']
        raise serializers.ValidationError("token 已失效")

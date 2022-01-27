import traceback

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


class UpdateBatchSerializer(GeneralSerializer):
    is_allow = serializers.BooleanField()
    ipaddresses = serializers.ListField(child=serializers.IPAddressField())

    def create(self, validated_data):
        """
        {"is_allow": true,"ipaddresses": ["1.1.1.1","1.1.1.2"]}
        """
        source_ip = self.get_ipaddress()
        ipaddresses = validated_data.get('ipaddresses', [])
        is_allow = validated_data.get('is_allow', False)
        if is_allow:
            risk = RiskStatus.REAL_PERSON
            score = 0.3
        else:
            risk = RiskStatus.MALICIOUS_IP
            score = 0

        data_list = []
        for ip in ipaddresses:
            ip_info = geo_ip.query_city(ip)
            defaults = {'risk': risk,
                        'asn_info': ip_info.asn,
                        'source_ip': source_ip,
                        "ipaddress": ip,
                        'recaptcha_score': score}
            data_list.append(IPInfo(**defaults))
        if is_allow:
            try:
                data = IPInfo.objects.bulk_create(data_list, ignore_conflicts=True)
                res = IPInfo.objects.filter(ipaddress__in=data_list, risk=RiskStatus.MALICIOUS_IP, recaptcha_score=0)
                print(res)
                res.update(risk=RiskStatus.REAL_PERSON, recaptcha_score=0.3)
                return IPInfoSerializer(data, many=True).data
            except:
                print(traceback.format_exc())
                return "批量更新白名单出错\n{}".format(traceback.format_exc())
        else:
            try:
                data = IPInfo.objects.bulk_create(data_list, ignore_conflicts=True)
                return IPInfoSerializer(data, many=True).data
            except:
                print(traceback.format_exc())
                return "批量更新黑名单出错\n{}".format(traceback.format_exc())
        return "ok"


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
                    'recaptcha_score': score}

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

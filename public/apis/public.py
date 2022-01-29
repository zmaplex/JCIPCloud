import datetime
import random
import traceback
from typing import List, Union

from django.db.models import Q
from django.db.models import QuerySet
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from base.tools import Geoip2Query
from public.models import IPInfo, RiskStatus
from public.serializers.public import IPInfoSerializer, GoogleRecaptchaVerifySerializer, NormalIPInfoSerializer, \
    UpdateBatchSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class ReportView(viewsets.ReadOnlyModelViewSet):
    queryset = IPInfo.objects.all()
    serializer_class = IPInfoSerializer
    geoip_2_query = Geoip2Query()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @staticmethod
    def get_ipaddress(request) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny],
            serializer_class=UpdateBatchSerializer)
    def update_batch_ip(self, request, *args, **kwargs):
        serializer = UpdateBatchSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            return Response(instance)


class PublicView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = IPInfo.objects.all()
    serializer_class = IPInfoSerializer
    lookup_field = 'ipaddress'
    lookup_value_regex = "[^/]+"
    geoip_2_query = Geoip2Query()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @staticmethod
    def get_ipaddress(request) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        if ip == "127.0.0.1":
            ip = "8.8.8.8"
        return ip

    @staticmethod
    def random_queryset(queryset: Union[QuerySet, List[IPInfo]]):
        total = queryset.filter(recaptcha_score__gte=0.3).count()
        random_number = 5
        if total < 5:
            random_number = total

        L1 = random.sample(range(0, total), random_number)
        data = []
        for i in L1:
            data.append(queryset.filter(recaptcha_score__gte=0.3, risk=RiskStatus.REAL_PERSON).values_list('ipaddress',
                                                                                                           flat=True)[
                            i])
        return data

    def get_queryset(self):
        return self.queryset.all()

    @action(methods=['GET'], detail=False, permission_classes=[permissions.AllowAny])
    def my_ip(self, request, *args, **kwargs):
        try:
            ip = self.get_ipaddress(request)
            return Response(ip)
        except Exception:
            return Response(traceback.format_exc(), status=500)

    @action(methods=["GET"], detail=False, permission_classes=[permissions.AllowAny])
    def ip(self, request, *args, **kwargs):
        try:
            ip = self.get_ipaddress(request)

            return Response({"ip": ip,"info":self.geoip_2_query.query_all_asn(ip)})
        except Exception:
            return Response(traceback.format_exc(), status=500)

    @action(methods=['POST'], detail=False, serializer_class=NormalIPInfoSerializer,
            permission_classes=[permissions.AllowAny])
    def report_white_ip(self, request, *args, **kwargs):
        serializer = NormalIPInfoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            return Response(instance.data)

    @action(methods=['GET'], detail=True, permission_classes=[permissions.AllowAny])
    def report_idc(self, request, ipaddress):
        try:
            data = IPInfo.objects.get(ipaddress=ipaddress)

            # 只要分数不等于 0 则删除节点防火墙规则
            if data.recaptcha_score == 0:
                code = 200
            else:
                code = 409
            return Response(IPInfoSerializer(data).data, status=code)

        except IPInfo.DoesNotExist:
            ip_info = self.geoip_2_query.query_city(ipaddress)
            risk_type = RiskStatus.MALICIOUS_IP

            obj = IPInfo.objects.create(ipaddress=ipaddress, risk=risk_type, asn_info=ip_info.asn,
                                        source_ip=self.get_ipaddress(request))
            return Response(IPInfoSerializer(obj).data)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny],
            serializer_class=GoogleRecaptchaVerifySerializer)
    def query_token(self, request, *args, **kwargs):
        serializer = GoogleRecaptchaVerifySerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            return Response(instance.data)

    @cache_response(timeout=1 * 60, cache='default')
    @action(methods=['GET'], detail=False, permission_classes=[permissions.AllowAny])
    def the_past_hour_non_human_ip(self, request, *args, **kwargs):
        """
        过去一小时的恶意IP活动记录
        """
        time = timezone.now() - datetime.timedelta(hours=2)

        data = self.queryset.filter(risk=RiskStatus.MALICIOUS_IP,
                                    recaptcha_score=0,
                                    update_at__gt=time).values_list('ipaddress', flat=True)
        data = list(data)
        if len(data) > 100:
            data = data[:100]
        return Response(data)

    @cache_response(timeout=1 * 60, cache='default')
    @action(methods=['GET'], detail=False, permission_classes=[permissions.AllowAny])
    def the_past_hour_human_ip(self, request, *args, **kwargs):
        """
        过去五分钟的真人IP活动记录
        """
        time = timezone.now() - datetime.timedelta(minutes=5)

        data = self.queryset.filter(recaptcha_score__gte=0.3, risk=RiskStatus.REAL_PERSON,
                                    update_at__gt=time).values_list('ipaddress', flat=True)
        data = list(data)
        if len(data) > 1000:
            data = data[:1000]
        return Response(data)

    @cache_response(timeout=60 * 60 * 12, cache='default')
    @action(methods=['GET'], detail=False, permission_classes=[permissions.AllowAny])
    def all_human_ip(self, request, *args, **kwargs):
        data = self.queryset.order_by().filter(risk=RiskStatus.REAL_PERSON).values_list('ipaddress', flat=True)

        return Response(data)

    @cache_response(timeout=60 * 60 * 12, cache='default')
    @action(methods=['GET'], detail=False, permission_classes=[permissions.AllowAny])
    def all_non_human_ip(self, request, *args, **kwargs):
        # data1 = self.queryset.filter(recaptcha_score=0, risk=RiskStatus.NON_HUMAN).values_list('ipaddress', flat=True)
        data = self.queryset.filter(Q(recaptcha_score=0),
                                    Q(risk=RiskStatus.NON_HUMAN) | Q(risk=RiskStatus.MALICIOUS_IP)).values_list(
            'ipaddress',
            flat=True)

        return Response(data)

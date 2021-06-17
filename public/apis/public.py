import datetime

from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from base.tools import Geoip2Query
from public.models import IPInfo, RiskStatus
from public.serializers.public import IPInfoSerializer, GoogleRecaptchaVerifySerializer


class PublicView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = IPInfo.objects.all()
    serializer_class = IPInfoSerializer
    lookup_field = 'ipaddress'
    lookup_value_regex = "[^/]+"
    geoip_2_query = Geoip2Query()

    def get_queryset(self):
        return self.queryset.all()

    @cache_response(timeout=1 * 60, cache='default')
    @action(methods=['GET'], detail=True, permission_classes=[permissions.AllowAny])
    def report_idc(self, request, ipaddress):
        try:
            data = IPInfo.objects.get(ipaddress=ipaddress)
            return Response(IPInfoSerializer(data).data)
        except IPInfo.DoesNotExist:
            ip_info = self.geoip_2_query.query_city(ipaddress)
            if ip_info.is_idc:
                risk_type = RiskStatus.NON_HUMAN
                print(ip_info.asn)
                obj = IPInfo.objects.create(ipaddress=ipaddress, risk=risk_type, asn_info=ip_info.asn)
                return Response(IPInfoSerializer(obj).data)
            else:
                return Response({'detail': 'not found'}, status=404)


    @cache_response(timeout=1 * 60, cache='default')
    @action(methods=['GET'], detail=True, permission_classes=[permissions.AllowAny])
    def query(self, request, ipaddress):
        """
        todo 要删除
        :param request:
        :param ipaddress:
        :return:
        """
        return self.report_idc(request, ipaddress)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny],
            serializer_class=GoogleRecaptchaVerifySerializer)
    def query_token(self, request, *args, **kwargs):
        serializer = GoogleRecaptchaVerifySerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            return Response(instance.data)

    @action(methods=['GET'], detail=False, permission_classes=[permissions.AllowAny])
    def the_past_hour_human_ip(self, request, *args, **kwargs):
        """
        过去一小时的真人IP活动记录
        """
        time = timezone.now() - datetime.timedelta(hours=2)

        data = self.queryset.filter(recaptcha_score__gt=0.5, risk=RiskStatus.REAL_PERSON,
                                    update_at__gt=time).values_list('ipaddress', flat=True)
        return Response(data)

    @cache_response(timeout=1 * 60, cache='default')
    @action(methods=['GET'], detail=False, permission_classes=[permissions.AllowAny])
    def all_human_ip(self, request, *args, **kwargs):
        data = self.queryset.filter(recaptcha_score__gt=0.5).values_list('ipaddress', flat=True)
        return Response(data)

    @cache_response(timeout=1 * 60, cache='default')
    @action(methods=['GET'], detail=False, permission_classes=[permissions.AllowAny])
    def all_non_human_ip(self, request, *args, **kwargs):
        data = self.queryset.filter(recaptcha_score=0, risk=RiskStatus.NON_HUMAN).values_list('ipaddress', flat=True)
        return Response(data)

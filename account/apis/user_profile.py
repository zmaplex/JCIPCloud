import hashlib

from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from account.models import UserProfile
from account.serializers.user_profile import UserProfileSerializer, UserProfileLoginSerializer, \
    UserProfileRegisterSerializer


class ProfileView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def __md5(self, string: str):
        m = hashlib.md5()
        m.update(string.encode())
        return m.hexdigest()

    def get_queryset(self):
        user: User = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        elif user.is_authenticated:
            return self.queryset.filter(user=user)
        else:
            return self.queryset.none()

    @action(methods=['GET'], detail=False, permission_classes=[permissions.AllowAny])
    def ping(self, request):
        data = {}
        for i in request.META:
            v = request.META[i]
            if isinstance(v, str) and 'HTTP_' in i:
                data[i] = v

        return Response({'detail': 'pong', 'HttpRequest.META': data})

    @action(methods=['GET'], detail=False)
    def info(self, request, *args, **kwargs):
        """
        获取用户信息
        """
        user: User = request.user
        pass

    @extend_schema(responses={200: UserProfileSerializer})
    @action(methods=['POST'], detail=False, serializer_class=UserProfileLoginSerializer,
            permission_classes=[permissions.AllowAny])
    def login(self, request, *args, **kwargs):
        """
        登录接口
        """
        serializer = UserProfileLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return Response(data)

    @extend_schema(responses={200: UserProfileSerializer})
    @action(methods=["POST"], detail=False, serializer_class=UserProfileRegisterSerializer,
            permission_classes=[permissions.AllowAny]
            )
    def register(self, request, *args, **kwargs):
        """
        注册接口
        """
        serializer = UserProfileRegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return Response(data)

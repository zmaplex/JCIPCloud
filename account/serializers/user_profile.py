from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from account.models import UserProfile
from base.serializer import BaseSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField('_email')
    token = serializers.SerializerMethodField('_token')
    username = serializers.SerializerMethodField('_username')
    is_admin = serializers.SerializerMethodField('_is_admin')
    number_of_invitations = serializers.SerializerMethodField('_number_of_invitations')

    class Meta:
        model = UserProfile
        fields = '__all__'

    def _email(self, obj: UserProfile):
        return obj.user.email

    def _token(self, obj: UserProfile):
        tokens = Token.objects.get_or_create(user=obj.user)
        if len(tokens):
            token = tokens[0]
        else:
            token = Token.objects.create(user=UserProfile.user)
        return token.key

    def _username(self, obj: UserProfile) -> str:
        return obj.user.username

    def _is_admin(self, obj: UserProfile) -> bool:
        return obj.user.is_superuser


class UserProfileLoginSerializer(serializers.Serializer):
    username = serializers.EmailField(required=True, label="邮箱")
    password = serializers.CharField(required=True, label="密码")

    def create(self, validated_data):
        username = validated_data.get('username')
        user: User = User.objects.get(username=username)
        return UserProfileSerializer(user.profile).data

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']
        try:
            user: User = User.objects.get(username=username)
            if not user.is_active:
                raise serializers.ValidationError({'username': '该账号被系列限制登录，请联系在线客服。'})
            user = authenticate(username=user.username, password=password)
            if user is None:
                raise serializers.ValidationError({'password': '密码错误'})
        except User.DoesNotExist:
            raise serializers.ValidationError({'username': '用户不存在'})
        return attrs


class UserProfileRegisterSerializer(BaseSerializer):
    username = serializers.CharField(required=True, label="用户名")
    password = serializers.CharField(min_length=1, required=True, label="密码")

    def create(self, attrs):
        username = attrs['username']
        password = attrs['password']
        ipaddress = self.get_ipaddress()
        user = User.objects.create_user(username=username, password=password)
        user_profile = UserProfile.objects.create(user=user, regitser_ipaddress=ipaddress)
        return UserProfileSerializer(user_profile).data

    def validate(self, attrs):
        username = attrs['username']
        users = User.objects.filter(username=username)
        if users.exists():
            raise serializers.ValidationError({'username': '用户名已被注册'})
        return attrs

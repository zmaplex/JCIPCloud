from django.contrib.auth.models import User
from django.db import models


from base.model import BaseModel


class UserProfile(BaseModel):
    user = models.OneToOneField(User,related_name='profile', on_delete=models.CASCADE, verbose_name="用户")
    regitser_ipaddress = models.CharField(max_length=45, verbose_name="IP地址")

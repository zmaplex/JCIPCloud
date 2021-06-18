from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from base.model import BaseModel



class RiskStatus(models.IntegerChoices):
    REAL_PERSON = 1
    NON_HUMAN = 2


class IPInfo(BaseModel):
    risk = models.IntegerField(default=RiskStatus.NON_HUMAN, choices=RiskStatus.choices)
    ipaddress = models.CharField(max_length=45, verbose_name="IP地址", unique=True)
    asn_info = models.CharField(max_length=128, verbose_name="ASN 信息")
    recaptcha_score = models.FloatField(default=0,
                                        validators=[MinValueValidator(0), MaxValueValidator(1)],
                                        verbose_name="分数",
                                        help_text="0是机器，1是真人")

    class Meta:

        ordering = ('-update_at',)

    def __str__(self):
        return self.ipaddress

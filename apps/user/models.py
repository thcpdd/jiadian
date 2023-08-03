from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel


# 拓展Django自带的用户模型类
class MyUser(AbstractUser, BaseModel):
    phone = models.CharField('手机号', max_length=11, null=True)
    introduce = models.TextField('个人介绍', default='', null=True)
    balance = models.DecimalField('余额', max_digits=11, decimal_places=2, default=0)  # 9位整数，2位小数
    total_recharge = models.DecimalField('累计充值', max_digits=11, decimal_places=2, default=0)
    total_consumption = models.DecimalField('累计消费', max_digits=11, decimal_places=2, default=0)
    image = models.ImageField('用户头像', upload_to='user', default='user/default.jpg')

    class Meta:
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        db_table = 'user_table'

    def __str__(self):
        return self.username


# 获取用户默认地址
class AddressManager:
    @staticmethod
    def get_user_default_address(user_id):
        try:
            address = Address.objects.filter(user_id=user_id).get(is_default=True)
        except Address.DoesNotExist:
            address = None

        return address


# 用户地址表
class Address(BaseModel):
    recipient = models.CharField('收件人', max_length=12)
    phone = models.CharField('手机号', max_length=11)
    province = models.CharField('省份', max_length=15)
    city = models.CharField('城市', max_length=10)
    country = models.CharField('区/县', max_length=10)
    detail_address = models.CharField('详细地址', max_length=40)
    is_default = models.BooleanField('默认地址', default=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name='所属用户')
    manager = AddressManager()

    class Meta:
        verbose_name = '地址表'
        verbose_name_plural = verbose_name
        db_table = 'address_table'

    def __str__(self):
        return self.user.username

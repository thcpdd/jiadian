from django.db import models
from db.base_model import BaseModel
from ..user.models import MyUser, Address


class OrderInfo(BaseModel):
    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成')
    )

    ORDER_STATUS_DICT = {
        1: '待支付',
        2: '待发货',
        3: '待收货',
        4: '待评价',
        5: '已完成'
    }

    PAY_METHODS_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '余额支付')
    )

    PAY_METHODS_DICT = {
        1: '货到付款',
        2: '微信支付',
        3: '支付宝',
        4: '余额支付'
    }

    PAY_METHODS_ICONS = {
        1: '/media/img/hdpay.svg',
        2: '/media/img/wxpay.svg',
        3: '/media/img/alipay.svg',
        4: '/media/img/ye.svg'
    }

    order_id = models.CharField('订单id', primary_key=True, max_length=40)
    total_price = models.DecimalField('订单总价', max_digits=11, decimal_places=2)
    freight = models.DecimalField('运费', max_digits=11, decimal_places=2)
    total_count = models.IntegerField('商品总数', null=False)
    pay_method = models.SmallIntegerField('支付方式', default=3, choices=PAY_METHODS_CHOICES)
    status = models.SmallIntegerField('订单状态', choices=ORDER_STATUS_CHOICES, default=1)
    trade_no = models.CharField('订单编号', max_length=40, null=False)
    mark = models.CharField('订单留言', max_length=255, default='')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name='所属用户')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name='订单地址')

    class Meta:
        verbose_name = '订单信息表'
        verbose_name_plural = verbose_name
        db_table = 'order_info'

    def __str__(self):
        return self.order_id


class GoodsOrder(BaseModel):
    from ..goods.models import GoodsDynamics
    price = models.DecimalField('商品总价', max_digits=11, decimal_places=2, null=False)
    count = models.IntegerField('商品总数', null=False)
    is_commented = models.BooleanField('是否评价', default=False)
    goods_dynamics = models.ForeignKey(GoodsDynamics, on_delete=models.CASCADE, verbose_name='商品动态')
    order_info = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name='订单信息')

    class Meta:
        verbose_name = '商品订单表'
        verbose_name_plural = verbose_name
        db_table = 'goods_order'

    def __str__(self):
        return self.goods_dynamics.goods_sku.name

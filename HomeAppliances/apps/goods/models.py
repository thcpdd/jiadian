from django.db import models
from db.base_model import BaseModel


class GoodsImage(BaseModel):
    image = models.ImageField(upload_to='goods')  # 127.0.0.1:8000/media/goods/xx.png
    goods_dynamics = models.ForeignKey('GoodsDynamics', on_delete=models.CASCADE, verbose_name='商品名字')

    class Meta:
        verbose_name = '商品图片表'
        verbose_name_plural = verbose_name
        db_table = 'goods_image'

    def __str__(self):
        return self.goods_dynamics.goods_sku.name


class GoodsType(BaseModel):
    GOODS_TYPES = {
        0: 'all',
        1: 'intelligence',
        2: 'electricity',
        3: 'computer',
        4: 'headset',
    }

    name = models.CharField('类型名字', max_length=20)
    image = models.ImageField('图片', upload_to='goods_type')
    logo = models.CharField('类型标志', max_length=20, default='')

    class Meta:
        verbose_name = '商品类型表'
        verbose_name_plural = verbose_name
        db_table = 'goods_type'

    def __str__(self):
        return self.name


class GoodsSPU(BaseModel):
    name = models.CharField('SUP名字', max_length=30)
    detail = models.CharField('商品详情', max_length=50)
    goods_type = models.ForeignKey(GoodsType, on_delete=models.CASCADE, verbose_name='商品类型')

    class Meta:
        verbose_name = '商品SPU表'
        verbose_name_plural = verbose_name
        db_table = 'goods_spu'

    def __str__(self):
        return self.name


class GoodsSKU(BaseModel):
    GOODS_STATUS = (
        (0, '下架'),
        (1, '上架')
    )

    name = models.CharField('商品名字', max_length=50, null=False)
    status = models.BooleanField('商品状态', default=1, choices=GOODS_STATUS)
    goods_spu = models.ForeignKey(GoodsSPU, on_delete=models.CASCADE, verbose_name='商品SPU')
    goods_type = models.ForeignKey(GoodsType, on_delete=models.CASCADE, verbose_name='商品类型', default='')

    class Meta:
        verbose_name = '商品SKU表'
        verbose_name_plural = verbose_name
        db_table = 'goods_sku'

    def __str__(self):
        return self.name


class GoodsDynamics(BaseModel):
    price = models.DecimalField('价格', max_digits=11, decimal_places=2, null=False)
    stock = models.IntegerField('库存', null=False)
    color = models.CharField('颜色', max_length=10, null=True, default='')
    size = models.CharField('尺寸/大小', max_length=40, null=True, default='')
    sales = models.IntegerField('销量', null=False)
    goods_sku = models.ForeignKey(GoodsSKU, on_delete=models.CASCADE, verbose_name='商品SKU')

    class Meta:
        verbose_name = '商品动态表'
        verbose_name_plural = verbose_name
        db_table = 'goods_dynamics_table'

    def __str__(self):
        return self.goods_sku.name


class RotationCharts(BaseModel):
    ROTATION_CHOICE = (
        (0, '不轮播'),
        (1, '轮播')
    )

    name = models.CharField('名字', max_length=10)
    is_rotate = models.BooleanField('是否轮播', default=1, choices=ROTATION_CHOICE)
    image = models.ImageField('图片', upload_to='rotation')

    class Meta:
        verbose_name = '首页轮播图'
        verbose_name_plural = verbose_name
        db_table = 'rotation_image'

    def __str__(self):
        return self.name


class GoodsComment(BaseModel):
    SCORE_CHOICE = (
        (1, '好评'),
        (2, '中评'),
        (3, '差评')
    )
    from apps.order.models import GoodsOrder
    from ..user.models import MyUser
    content = models.CharField('评论内容', max_length=255)
    score = models.SmallIntegerField('评分', choices=SCORE_CHOICE, default=1)
    goods_order = models.ForeignKey(GoodsOrder, on_delete=models.CASCADE, verbose_name='商品订单', default='')
    goods_sku = models.ForeignKey(GoodsSKU, on_delete=models.CASCADE, verbose_name='商品sku', default='')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name='所属用户', default='')

    class Meta:
        verbose_name = '商品评价表'
        verbose_name_plural = verbose_name
        db_table = 'goods_comment'

    def __str__(self):
        return self.goods_sku.name

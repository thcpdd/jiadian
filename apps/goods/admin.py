from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([GoodsImage, GoodsType, GoodsSKU, GoodsSPU, RotationCharts, GoodsDynamics, GoodsComment])

from django.contrib import admin
from django.core.cache import cache
from .models import *


class GoodsAdminModel(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete_many(['index_data', 'rotations_list'])

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        cache.delete_many(['index_data', 'rotations_list'])


admin.site.register([
    GoodsImage, GoodsType, GoodsSKU, GoodsSPU, RotationCharts, GoodsDynamics, GoodsComment
], admin_class=GoodsAdminModel)

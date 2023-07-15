from django.urls import path
from .views import *

app_name = 'goods'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),  # 首页
    path('rotation', IndexView.index_rotation, name='rotation'),  # 首页轮播图
    path('goods/detail/<int:goods_sku_id>', GoodsDetailView.as_view(), name='detail'),  # 商品详情页
    path('goods/list/<str:show_type>/<int:page>', GoodsListView.as_view(), name='list'),  # 商品列表页
    path('goods/search/all/<int:page>', SearchView.as_view(), name='search'),  # 搜索页面
]

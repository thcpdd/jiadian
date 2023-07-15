from django.urls import path
from .views import AddCartView, MyCartView

app_name = 'cart'

urlpatterns = [
    path('add', AddCartView.as_view(), name='add'),  # 加入购物车
    path('cart', MyCartView.as_view(), name='cart'),  # 购物车页面（显示购物车、增加商品、减少商品、删除商品）
]

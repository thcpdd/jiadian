from django.urls import path
from .views import *

app_name = 'user'
urlpatterns = [
    path('', UserCenterView.as_view(), name='user'),  # 用户中心页
    path("login/", LoginView.as_view(), name='login'),  # 登录
    path("register", RegisterView.as_view(), name='register'),  # 注册
    path('send', SendCode.as_view(), name='send'),  # 发送注册码
    path('logout', LogoutView.as_view(), name='logout'),  # 退出登录
    path('banlance', BalanceView.as_view(), name='balance'),  # 用户余额
    path('address', AddressView.as_view(), name='address'),  # 用户地址
    path('modify_address', ModifyAddressView.as_view(), name='modify_address'),  # 改变地址
    path('my_order/<int:page>', UserOrderView.as_view(), name='my_order'),  # 我的订单
    path('order_detail/<str:order_id>', OrderDetailView.as_view(), name='order_detail'),  # 订单详情
    path('recharge', RechargeView.as_view(), name='recharge'),  # 充值
    path('upload_image', ModifyImageView.as_view(), name='image')  # 更换头像
]

from django.urls import path
from .views import OrderView, NowBuyView, PayView, PayOkView, ConfirmReceiptView, GoodsCommentView


app_name = 'order'
urlpatterns = [
    path('order', OrderView.as_view(), name='order'),  # 订单页面（显示订单、提交订单）
    path('buy', NowBuyView.as_view(), name='buy'),  # 立即购买商品
    path('pay/<str:order_id>', PayView.as_view(), name='pay'),  # 支付页面
    path('payok/<str:order_id>', PayOkView.as_view(), name='payok'),  # 支付成功页面
    path('confirm', ConfirmReceiptView.as_view(), name='confirm'),  # 确认收货
    path('comment/<str:order_id>', GoodsCommentView.as_view(), name='comment')  # 订单评价
]

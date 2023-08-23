import os
from datetime import datetime, timedelta
from django import setup
from celery import Celery

backend = 'redis://127.0.0.1:6379/1'
broker = 'redis://127.0.0.1:6379/2'

app = Celery('celery_tasks.tasks', backend=backend, broker=broker)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeAppliances.settings')
setup()


def get_delay_time(*args, **kwargs):
    now = datetime.now()  # 获取当前时间
    utc_ctime = datetime.utcfromtimestamp(now.timestamp())  # 默认用utc时间
    time_delay = timedelta(*args, **kwargs)  # 设置延期时间
    eta = utc_ctime + time_delay  # 设置任务执行时间
    return eta


@app.task
def check_order_is_pay_task(order_id):
    """检查用户订单是否完成支付"""
    from apps.order.models import OrderInfo, GoodsOrder
    from apps.goods.models import GoodsDynamics

    try:
        order = OrderInfo.objects.get(order_id=order_id)
    except OrderInfo.DoesNotExist:
        return
    if order.status == 1:
        goods_orders = GoodsOrder.objects.filter(order_info_id=order_id)
        # 恢复商品库存与销量
        for goods_order in goods_orders:
            goods_dynamic = GoodsDynamics.objects.get(id=goods_order.goods_dynamics_id)
            goods_dynamic.stock += goods_order.count
            goods_dynamic.sales -= goods_order.count
            goods_dynamic.save()
        order.delete()


@app.task
def automatic_shipping_task(order_id):
    """自动发货"""
    from apps.order.models import OrderInfo
    try:
        order = OrderInfo.objects.get(order_id=order_id)
    except OrderInfo.DoesNotExist:
        return
    order.status = 3
    order.save()


@app.task
def send_register_email_task(username, sender, email, code):
    """异步发送邮箱"""
    from django.core.mail import send_mail

    subject = '家电之选-注册信息'
    message = f'{username}，欢迎注册家电之选会员，这是注册验证码，两分钟内有效，请及时使用：{code}'
    receiver = [email]
    send_mail(subject, message, sender, receiver)

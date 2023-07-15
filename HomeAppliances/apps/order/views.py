from django.shortcuts import render, redirect, reverse
from ..goods.views import BaseGoodsView
from ..goods.models import GoodsDynamics, GoodsImage, GoodsComment
from ..user.models import Address, MyUser
from .models import GoodsOrder, OrderInfo
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db import transaction
from django_redis import get_redis_connection
from json import loads


class OrderView(LoginRequiredMixin, BaseGoodsView):
    def get(self, request):
        dynamics_ids = request.GET.get('dynamics').split(',')

        dynamics = []
        total_count = 0
        amount_price = 0
        freight = 10
        cart_id = f'cart_{request.user.id}'
        connect = get_redis_connection()

        for dynamics_id in dynamics_ids:
            options = []
            dynamic = GoodsDynamics.objects.get(id=dynamics_id)  # 商品动态
            image = GoodsImage.objects.filter(goods_dynamics_id=dynamics_id)[0]  # 商品的一张图片
            count = int(connect.hget(cart_id, dynamics_id))  # 通过购物车查询该商品的总数
            options.append({'spec': '大小', 'name': dynamic.size})
            options.append({'spec': '颜色', 'name': dynamic.color})

            dynamics.append({
                'name': dynamic.goods_sku.name,
                'id': dynamics_id,
                'image': image.image.url,
                'price': float(dynamic.price),
                'options': options,
                'count': count,
                'total_price': count * float(dynamic.price)
            })

            total_count += count
            amount_price += float(dynamic.price) * count

        context = {
            'goods_types': self.get_navigation_info(),  # 导航栏信息
            'dynamics': dynamics,
            'total_count': total_count,  # 商品总数
            'amount_price': amount_price,  # 商品总价（不包含运费）
            'total_price': amount_price + freight,  # 商品总价（包含运费）
            'freight': freight  # 运费
        }

        return render(request, 'order/order_list.html', context)

    @staticmethod
    @transaction.atomic  # 绑定事务
    def post(request):
        form_data = eval(request.body)
        dynamics_datas = form_data.get('dynamics_datas')
        amount_price = form_data.get('amount_price')
        total_count = form_data.get('total_count')
        address_id = form_data.get('addr_id')
        mark = form_data.get('mark')

        response = {
            'success': 0,
            'status': -1,
        }

        if not all([*dynamics_datas, amount_price, total_count, address_id]):
            response['errmsg'] = '请填写完整数据'
            return JsonResponse(response)

        try:
            Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            response['errmsg'] = '该地址不存在'
            return JsonResponse(response)

        # 核心业务处理
        from time import time
        from datetime import datetime
        order_id = str(int(time())) + str(request.user.id)  # 订单编号
        trade_no = datetime.now().strftime('%Y%m%d%H%M%S') + str(request.user.id)  # 交易编号
        save_id = transaction.savepoint()  # 事务保存点
        try:
            order_info = OrderInfo.objects.create(
                order_id=order_id,
                total_price=amount_price,
                address_id=address_id,
                freight=10,
                user=request.user,
                mark=mark,
                total_count=total_count,
                trade_no=trade_no
            )
            for dynamics_data in dynamics_datas:
                dynamics_id = dynamics_data.get('id')
                count = dynamics_data.get('count')

                try:
                    dynamic = GoodsDynamics.objects.select_for_update().get(id=dynamics_id)  # 悲观锁
                except GoodsDynamics.DoesNotExist:
                    transaction.savepoint_rollback(save_id)  # 回滚到事务保存点
                    response['errmsg'] = f'id为{dynamics_id}的商品不存在'
                    return JsonResponse(response)

                if dynamic.stock < count:
                    transaction.savepoint_rollback(save_id)  # 回滚到事务保存点
                    response['errmsg'] = f'{dynamic.goods_sku.name}库存不足'
                    return JsonResponse(response)

                GoodsOrder.objects.create(
                    count=count,
                    price=count*dynamic.price,
                    goods_dynamics_id=dynamics_id,
                    order_info=order_info
                )
                dynamic.sales += count
                dynamic.stock -= count
                dynamic.save()

        except Exception as exception:
            transaction.savepoint_rollback(save_id)  # 回滚到事务保存点
            response['errmsg'] = '订单异常，请重试'
            response['exception'] = exception
            return JsonResponse(response)

        transaction.savepoint_commit(save_id)  # 提交事务
        connect = get_redis_connection()
        dynamics_ids = list(map(lambda x: x['id'], dynamics_datas))  # 获取所有商品动态id
        connect.hdel(f'cart_{request.user.id}', *dynamics_ids)  # 清除购物车数据

        response['success'] = 1
        response['status'] = 200
        response['order_id'] = order_id

        return JsonResponse(response)


class NowBuyView(LoginRequiredMixin, BaseGoodsView):
    def get(self, request):
        dynamics_id = request.GET.get('dynamics_id')
        count = int(request.GET.get('count', 1))
        dynamic = GoodsDynamics.objects.get(id=dynamics_id)
        image = GoodsImage.objects.filter(goods_dynamics_id=dynamics_id)[0]

        dynamics = [{
            'name': dynamic.goods_sku.name,
            'id': dynamics_id,
            'image': image.image.url,
            'price': float(dynamic.price),
            'count': count,
            'options': [
                {'spec': '大小', 'name': dynamic.size},
                {'spec': '颜色', 'name': dynamic.color}
            ],
            'total_price': count * float(dynamic.price)
        }]

        context = {
            'goods_types': self.get_navigation_info(),
            'dynamics': dynamics,
            'total_count': count,
            'amount_price': count * float(dynamic.price),
            'total_price': count * float(dynamic.price) + 10,
            'freight': 10,
        }

        return render(request, 'order/order_list.html', context)


class PayView(LoginRequiredMixin, BaseGoodsView):
    def get(self, request, order_id):
        try:
            order_info = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return redirect(reverse('goods:index'))

        goods_orders = GoodsOrder.objects.filter(order_info_id=order_id)
        # 动态的为商品订单对象添加属性
        goods_orders = self.add_order_attribute(goods_orders)

        methods = []  # 支付方式
        icons = OrderInfo.PAY_METHODS_ICONS
        for i, method in OrderInfo.PAY_METHODS_CHOICES:
            methods.append({
                'value': i,
                'name': method,
                'icon': icons[i],
                'is_default': 0
            })

        addr = Address.objects.get(id=order_info.address_id)
        address = addr.province + addr.city + addr.country + addr.detail_address

        user = MyUser.objects.get(id=request.user.id)

        balance = float(user.balance)

        context = {
            'goods_types': self.get_navigation_info(),
            'methods': methods,
            'total_amount': float(order_info.total_price) + float(order_info.freight),
            'goods_orders': goods_orders,
            'trade_no': order_info.trade_no,
            'order_id': order_id,
            'address': address,
            'balance': balance
        }

        return render(request, 'order/pay.html', context)

    @staticmethod
    def add_order_attribute(goods_orders):
        """为商品订单添加属性（图片、sku名字、大小、颜色）"""
        for goods_order in goods_orders:
            image = GoodsImage.objects.filter(goods_dynamics_id=goods_order.goods_dynamics_id)[0]
            goods_order.image = image.image.url
            goods_order.name = goods_order.goods_dynamics.goods_sku.name
            goods_order.options = [
                {'spec': '大小', 'name': goods_order.goods_dynamics.size},
                {'spec': '颜色', 'name': goods_order.goods_dynamics.color}
            ]
        return goods_orders

    @staticmethod
    def post(request, order_id):
        pay_method = eval(request.body).get('method')
        user = MyUser.objects.get(id=request.user.id)
        order = OrderInfo.objects.get(order_id=order_id)
        response = {
            'success': 0,
            'status': -1
        }
        if pay_method == 4:
            if user.balance < order.total_price + order.freight:
                response['errmsg'] = '余额不足，请充值'
                return JsonResponse(response)

            order.pay_method = pay_method
            order.status = 2
            user.balance -= order.total_price  # 余额减少
            user.total_consumption += order.total_price  # 消费增加

            user.save()
            order.save()
            response['success'] = 1
            response['status'] = 200
            return JsonResponse(response)
        else:
            response['errmsg'] = '暂不支持该支付方式'
            return JsonResponse(response)


class PayOkView(LoginRequiredMixin, BaseGoodsView):
    def get(self, request, order_id):
        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return redirect(reverse('goods:index'))

        address = Address.objects.get(id=order.address_id)

        goods_orders = GoodsOrder.objects.filter(order_info_id=order_id)
        goods_orders = PayView.add_order_attribute(goods_orders)  # 动态的为商品订单对象添加属性

        context = {
            'pay_status': OrderInfo.ORDER_STATUS_DICT[order.status],
            'pay_method': OrderInfo.PAY_METHODS_DICT[order.pay_method],
            'order': order,
            'goods_types': self.get_navigation_info(),
            'address': address,
            'goods_orders': goods_orders,
            'total_amount': float(order.total_price) + float(order.freight)
        }

        return render(request, 'order/payok.html', context)


class ConfirmReceiptView(LoginRequiredMixin, BaseGoodsView):
    @staticmethod
    def post(request):
        order_id = eval(request.body).get('order_id')

        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'errmsg': '订单不存在', 'success': 0, 'status': -1})

        if order.status != 3:
            return JsonResponse({'errmsg': '该订单不在确认收货状态', 'success': 0, 'status': -1})

        if order.user_id != request.user.id:
            return JsonResponse({'errmsg': '不能修改别人的订单信息', 'success': 0, 'status': -1})

        order.status = 4
        order.save()

        return JsonResponse({'msg': '确认收货成功', 'success': 1, 'status': 200})


class GoodsCommentView(LoginRequiredMixin, BaseGoodsView):
    @staticmethod
    def get(request, order_id):
        goods_orders = GoodsOrder.objects.filter(order_info_id=order_id).order_by('is_commented')
        # 动态的为商品订单对象添加属性
        goods_orders = PayView.add_order_attribute(goods_orders)

        return render(request, 'user/comment.html', {'goods_orders': goods_orders, 'order_id': order_id})

    def post(self, request, order_id):
        form_data = loads(request.body)

        content = form_data.get('content')  # 评论内容
        choices = form_data.get('choices')  # 评分
        goods_order_id = form_data.get('goods_order_id')  # 商品订单id

        response = {
            'success': 0,
            'status': -1
        }

        if not all([content, goods_order_id]):
            response['errmsg'] = '数据不完整'
            return JsonResponse(response)

        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            response['errmsg'] = '订单不存在'
            return JsonResponse(response)

        if order.status != 4:
            response['errmsg'] = '该订单不能评价'
            return JsonResponse(response)

        try:
            goods_order = GoodsOrder.objects.get(id=goods_order_id)
            if goods_order.is_commented:
                response['errmsg'] = '该商品已评价'
                return JsonResponse(response)

            GoodsComment.objects.create(
                content=content,
                score=choices,
                goods_order_id=goods_order_id,
                goods_sku_id=goods_order.goods_dynamics.goods_sku_id,
                user_id=request.user.id
            )

            goods_order.is_commented = 1
            goods_order.save()

            # 该订单的所有商品订单都完成评论，那么该订单标记为已完成
            if self.all_orders_were_commented(order_id):
                order.status = 5
                order.save()

            response['status'] = 200
            response['success'] = 1
            return JsonResponse(response)

        except GoodsOrder.DoesNotExist:
            response['errmsg'] = '商品订单不存在'
            return JsonResponse(response)

    @staticmethod
    def all_orders_were_commented(order_id):
        """判断一个订单的所有商品是否已全部评价"""
        goods_orders = GoodsOrder.objects.filter(order_info_id=order_id)
        results = map(lambda x: x.is_commented, goods_orders)
        return True if all(results) else False

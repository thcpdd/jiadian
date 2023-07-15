from django.shortcuts import render
from ..goods.models import GoodsDynamics, GoodsImage
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection
from ..goods.views import BaseGoodsView


class AddCartView(View):
    @staticmethod
    def post(request):
        response = {
            'status': -1,
            'success': 0
        }
        if not request.user.is_authenticated:
            response['errmsg'] = '用户未登录'
            return JsonResponse(response)

        form_data = eval(request.body)
        dynamics_id = form_data.get('dynamics')
        count = form_data.get('count')

        # 核心业务处理
        try:
            dynamics = GoodsDynamics.objects.get(id=dynamics_id)
        except GoodsDynamics.DoesNotExist:
            response['errmsg'] = '商品不存在'
            return JsonResponse(response)

        cart_id = f'cart_{request.user.id}'
        connect = get_redis_connection('default')
        cart_count = connect.hget(cart_id, dynamics_id)  # 存在则返回值，不存在返回None
        # 如果有数据，那么就添加数据
        if cart_count:
            count += int(cart_count)
        # 用户新增的商品数量加上原来购物车该商品的数量大于库存
        if count > dynamics.stock:
            response['errmsg'] = '商品库存不足'
            return JsonResponse(response)

        connect.hset(cart_id, dynamics_id, count)
        cart_len = connect.hlen(cart_id)  # 购物车商品总条数

        response['msg'] = '购物车添加成功'
        response['success'] = 1
        response['status'] = 200
        response['cart_len'] = cart_len

        return JsonResponse(response)


class MyCartView(LoginRequiredMixin, BaseGoodsView):
    def get(self, request):
        goods_types = self.get_navigation_info()

        connect = get_redis_connection('default')
        cart_id = f'cart_{request.user.id}'
        cart_dict = connect.hgetall(cart_id)  # {'dynamics_id': count}

        carts = []  # 用户购物车所有信息
        for dynamics_id, count in cart_dict.items():
            dynamics = GoodsDynamics.objects.get(id=dynamics_id)
            image = GoodsImage.objects.filter(goods_dynamics_id=dynamics_id)[0]
            carts.append({
                'id': dynamics.goods_sku_id,
                'sku': {
                    'id': int(dynamics_id),
                    'options': [
                        {'id': int(dynamics_id), 'name': dynamics.size, 'spec': '大小'},
                        {'id': int(dynamics_id), 'name': dynamics.color, 'spec': '颜色'}
                    ],
                    'spu': {
                        'id': int(dynamics.goods_sku.goods_spu_id),
                        'title': dynamics.goods_sku.name,
                    },
                    'pic': image.image.url,
                    'price': float(dynamics.price),
                    'stock': dynamics.stock,
                    'sales': dynamics.sales
                },
                'count': int(count),
                'owner': request.user.id
            })

        context = {
            'goods_types': goods_types,
            'carts': carts
        }

        return render(request, 'cart/cart.html', context)

    @staticmethod
    def patch(request):
        """增加或减少购物车数据"""
        form_data = eval(request.body)
        dynamics_id = form_data.get('dynamics_id')
        count = form_data.get('count')
        cart_id = f'cart_{request.user.id}'
        response = {
            'success': 0,
            'status': -1
        }
        dynamics = GoodsDynamics.objects.get(id=dynamics_id)
        if count > dynamics.stock:
            response['errmsg'] = '商品库存不足'
            return JsonResponse(response)

        connect = get_redis_connection('default')
        connect.hset(cart_id, dynamics_id, count)

        response['msg'] = '数量修改成功'
        response['status'] = 200
        response['success'] = 1

        return JsonResponse(response)

    @staticmethod
    def delete(request):
        """删除购物车某个商品"""
        dynamics_id = eval(request.body).get('dynamics_id')
        if not dynamics_id:
            return JsonResponse({'success': 0, 'status': -1, 'errmsg': '数据不完整'})

        connect = get_redis_connection('default')
        cart_id = f'cart_{request.user.id}'
        connect.hdel(cart_id, dynamics_id)

        return JsonResponse({'success': 1, 'status': 200})

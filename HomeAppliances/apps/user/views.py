from re import match
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate
from .forms import LoginForm
from .models import MyUser, Address
from ..order.views import PayView


class SendCode(View):
    @staticmethod
    def post(request):
        form_info = eval(request.body.decode('utf-8'))
        username = form_info.get('username')
        email = form_info.get('email')
        password = form_info.get('password')

        response = {
            'status': -1,
            'success': 0,
        }
        if not all([username, email, password]):
            response['errmsg'] = '数据不完整'
            return JsonResponse(response)

        if len(password) < 6:
            response['errmsg'] = '密码必须6位以上'
            return JsonResponse(response)

        if not match('.{5,20}@(qq|163|126|gmail|sina|hotmail|icould).com', email):
            response['errmsg'] = '邮箱格式不正确'
            return JsonResponse(response)

        from random import choices
        code = ''.join(choices(settings.CODE_CHARS, k=6))

        subject = '家电之选-注册信息'
        message = f'{username}，欢迎注册家电之选会员，这是注册验证码，两分钟内有效，请及时使用：{code}'
        sender = settings.EMAIL_FROM
        receiver = [email]
        send_mail(subject, message, sender, receiver)
        request.session['code'] = code
        request.session.set_expiry(120)  # 验证码2分钟后过期

        response['status'] = 200
        response['success'] = 1
        return JsonResponse(response)


class RegisterView(View):
    @staticmethod
    def get(request):
        return render(request, 'user/register.html')

    @staticmethod
    def post(request):
        form_info = eval(request.body.decode('utf-8'))
        username = form_info.get('username')
        email = form_info.get('email')
        password = form_info.get('password')
        userinput_code = form_info.get('code')

        response = {
            'status': -1,
            'success': 0
        }

        if not all([username, password, email, userinput_code]):
            response['errmsg'] = '数据不完整'
            return JsonResponse(response)

        session_code = request.session.get('code')
        if not session_code:
            response['errmsg'] = '验证码不存在或已过期'
            return JsonResponse(response)

        if userinput_code != session_code:
            response['errmsg'] = '验证码不正确'
            return JsonResponse(response)

        # 核心业务处理
        try:
            MyUser.objects.get(username=username)
            response['errmsg'] = '用户名已存在'
            return JsonResponse(response)
        except MyUser.DoesNotExist:
            user = MyUser.objects.create_user(username=username, email=email, password=password)
            user.is_active = 1
            user.save()
            request.session.flush()  # 清除会话信息
            response['status'] = 200
            response['success'] = 1

        return JsonResponse(response)


class LoginView(View):
    @staticmethod
    def get(request):
        return render(request, 'user/login.html', {'forms': LoginForm()})

    @staticmethod
    def post(request):
        forms = LoginForm(request.POST)
        context = {
            'forms': forms,
        }
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if not user:
            context['errmsg'] = '用户不存在或密码错误'
            return render(request, 'user/login.html', context)

        login(request, user)

        return redirect(reverse('user:user'))


class LogoutView(View):
    @staticmethod
    def get(request):
        logout(request)

        return redirect(reverse('goods:index'))


class UserCenterView(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        userinfo = MyUser.objects.get(id=request.user.id)
        context = {
            'active': 'userinfo',
            'userinfo': {
                'phone': userinfo.phone,
                'username:': userinfo.username,
                'introduce': userinfo.introduce,
                'balance': userinfo.balance,
                'email': userinfo.email,
            }
        }
        return render(request, 'user/user_center.html', context)

    @staticmethod
    def patch(request):
        form_info = eval(request.body.decode('utf-8'))
        response = {
            'success': 0,
            'status': -1
        }
        user = MyUser.objects.get(id=request.user.id)
        if 'email' in form_info:
            if not match('.{5,20}@(qq|163|126|gmail|sina|hotmail|icould).com', form_info.get('email')):
                response['errmsg'] = '邮箱格式不正确'
                return JsonResponse(response)
            user.email = form_info['email']
        elif 'phone' in form_info:
            if len(form_info['phone']) != 11 or not match('1[3-57-9][0-9]{9}', form_info['phone']):
                response['errmsg'] = '手机号格式不正确'
                return JsonResponse(response)
            user.phone = form_info['phone']
        else:
            if not form_info.get('introduce'):
                response['errmsg'] = '内容不能为空'
                return JsonResponse(response)
            introduce = form_info['introduce']
            if '\n' in introduce:
                introduce = introduce.replace('\n', '')

            user.introduce = introduce
            user.save()

        response['status'] = 200
        response['success'] = 1

        return JsonResponse(response)


class BalanceView(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        user = MyUser.objects.get(id=request.user.id)
        context = {
            'active': 'balance',
            'total_recharge': user.total_recharge,
            'balance': user.balance,
            'total_consumption': user.total_consumption
        }
        return render(request, 'user/balance.html', context)


class AddressView(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        context = {
            'active': 'address',
            'delete': True,
            'update': True
        }
        return render(request, 'user/address.html', context)


class ModifyAddressView(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        """获取地址"""
        address = Address.objects.filter(user_id=request.user.id).order_by('-is_default')  # 默认地址放在第一个
        data = []
        for addr in address:
            data.append({
                'id': addr.id,
                'name': addr.recipient,
                'phone': addr.phone,
                'province': addr.province,
                'city': addr.city,
                'country': addr.country,
                'address': addr.detail_address,
                'is_default': addr.is_default
            })

        return JsonResponse({'data': data})

    @staticmethod
    def delete(request):
        """删除地址"""
        addr_id = request.body.decode('utf-8')
        response = {
            'res': 0,
            'status': -1
        }
        address = Address.objects.get(id=addr_id)
        if address.user_id != request.user.id:
            response['errmsg'] = '不能删除别人的地址'
            return JsonResponse(response)

        address.delete()
        response['res'] = 1
        response['status'] = 200
        response['msg'] = '地址删除成功'

        return JsonResponse(response)

    @staticmethod
    def post(request):
        """添加地址"""
        from json import loads
        form_data = loads(request.body.decode('utf-8'))

        recipient = form_data.get('name')
        phone = form_data.get('phone')
        province = form_data.get('province')
        city = form_data.get('city')
        country = form_data.get('country')
        detail_address = form_data.get('address')
        is_default = form_data.get('is_default')

        response = {
            'res': 0,
            'status': -1,
        }

        if not all([recipient, phone, province, city, country, detail_address]):
            response['errmsg'] = '请把数据填写完整'
            return JsonResponse(response)

        if is_default:
            default_address = Address.manager.get_user_default_address(request.user.id)
            if default_address:  # 把原来默认的地址设置成不默认
                default_address.is_default = False
                default_address.save()

        Address.objects.create(
            recipient=recipient,
            phone=phone,
            province=province,
            city=city,
            country=country,
            detail_address=detail_address,
            is_default=is_default,
            user_id=request.user.id
        )

        response['status'] = 200
        response['res'] = 1
        response['msg'] = '地址添加成功'

        return JsonResponse(response)

    @staticmethod
    def put(request):
        """修改地址"""
        from json import loads
        form_data = loads(request.body.decode('utf-8'))
        response = {
            'res': 0,
            'status': -1
        }
        try:
            address = Address.objects.get(id=form_data.get('id'))
        except Address.DoesNotExist:
            response['errmsg'] = '要修改的地址不存在，请重试'
            return JsonResponse(response)

        if address.user_id != request.user.id:
            response['errmsg'] = '不能修改别人的地址'
            return JsonResponse(response)

        is_default = form_data.get('is_default')
        if is_default:
            default_address = Address.manager.get_user_default_address(request.user.id)
            if default_address:  # 把原来默认的地址设置成不默认
                default_address.is_default = False
                default_address.save()

        address.recipient = form_data.get('name')
        address.phone = form_data.get('phone')
        address.province = form_data.get('province')
        address.city = form_data.get('city')
        address.country = form_data.get('country')
        address.detail_address = form_data.get('address')
        address.is_default = is_default
        address.save()

        response['res'] = 1
        response['status'] = 200
        response['msg'] = '地址修改成功'

        return JsonResponse(response)


class UserOrderView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, page):
        from ..order.models import GoodsOrder, OrderInfo
        from db.base_model import MyPaginator
        from django.db.models import Q

        # 订单分类
        sort = int(request.GET.get('sort'))
        if not sort:
            orders = OrderInfo.objects.filter(user_id=request.user.id).order_by('-update_time')
        else:
            orders = OrderInfo.objects.filter(Q(user_id=request.user.id) & Q(status=sort)).order_by('-update_time')

        for order in orders:
            sub_orders = GoodsOrder.objects.filter(order_info_id=order.order_id)
            # 动态的为商品订单对象增加属性
            sub_orders = PayView.add_order_attribute(sub_orders)

            order.pay_status = OrderInfo.ORDER_STATUS_DICT[order.status]
            order.price = float(order.total_price) + float(order.freight)
            order.sub_orders = sub_orders

        paginator = MyPaginator(orders, 2)
        pages = paginator.page(page)

        context = {
            'active': 'order',
            'pages': pages,
            'sort': sort
        }

        return render(request, 'user/my_order.html', context)


class OrderDetailView(View):
    @staticmethod
    def get(request, order_id):
        from ..order.models import OrderInfo, GoodsOrder

        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return redirect(reverse('goods:index'))

        address = Address.objects.get(id=order.address_id)
        goods_orders = GoodsOrder.objects.filter(order_info_id=order_id)

        goods_orders = PayView.add_order_attribute(goods_orders)

        order.pay_status = OrderInfo.ORDER_STATUS_DICT[order.status]  # 订单状态
        order.price = float(order.total_price) + float(order.freight)  # 订单总价（连运费）
        order.goods_orders = goods_orders

        pay_method = OrderInfo.PAY_METHODS_DICT[order.pay_method]  # 支付方式

        context = {
            'order': order,
            'address': address,
            'pay_method': pay_method
        }

        return render(request, 'user/order_detail.html', context)


class RechargeView(View):
    @staticmethod
    def post(request):
        from django.conf import settings

        if not settings.RECHARGE_SYSTEM:
            return JsonResponse({'success': 0, 'status': -1, 'errmsg': '充值系统已关闭，请联系管理员'})

        from json import loads
        form_data = loads(request.body)

        username = form_data.get('username')
        password = form_data.get('password')
        try:
            money = float(form_data.get('money'))
        except ValueError:
            return JsonResponse({'success': 0, 'status': -1, 'errmsg': '非法金钱'})

        admin = authenticate(request, username=username, password=password)

        if not admin:
            return JsonResponse({'success': 0, 'status': -1, 'errmsg': '身份验证失败'})

        if money > 999999999.99:
            return JsonResponse({'success': 0, 'status': -1, 'errmsg': '充值数量过多，充值失败'})

        user = MyUser.objects.get(id=request.user.id)

        if float(user.balance) + money > 999999999.99:
            return JsonResponse({'success': 0, 'status': -1, 'errmsg': '账户余额超出最大限制'})

        user.balance = float(user.balance) + money
        user.total_recharge = float(user.total_recharge) + money
        user.save()

        return JsonResponse({'success': 1, 'status': 200, 'errmsg': '充值成功！'})


class ModifyImageView(View):
    @staticmethod
    def post(request):
        image = request.FILES.get('image')

        if not image:
            return JsonResponse({'success': 0, 'errmsg': '空文件'}, status=400)

        user = MyUser.objects.get(id=request.user.id)

        user.image = image
        user.save()

        return JsonResponse({'success': 1}, status=200)

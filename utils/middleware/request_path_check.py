from django.http import HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import CsrfViewMiddleware
from django.core.cache import cache
from django.conf import settings


# 发送邮箱接口限制
class CheckSendAPIMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.csrf_middleware = CsrfViewMiddleware(get_response)

    def process_request(self, request):
        """在调用发送邮件视图前处理请求"""
        path = request.path
        if path == '/user/send':
            client_ip = self._get_client_request_ip(request)

            client_info = cache.get(f'client_{client_ip}')  # 从缓存获取该ip对应的信息
            if client_info:
                return JsonResponse({'status': -1, 'success': 0, 'errmsg': '频繁请求，60秒后重试'}, status=403)
            else:
                cache.set(f'client_{client_ip}', client_ip, 60)  # 发送一次就设置60秒禁止访问时间

            request_times = cache.get(f'request_times_{client_ip}', 0)  # 获取该ip发送验证码的次数
            if request_times > 5:
                return JsonResponse({'status': -1, 'success': 0, 'errmsg': '一个ip在24小时内最多只能发送5条验证码'}, status=403)
            else:
                cache.set(f'request_times_{client_ip}', request_times + 1, 60 * 60 * 24)  # 请求次数 + 1

    @staticmethod
    def _get_client_request_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 判断是否使用代理

        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0]  # 使用代理获取真实的ip
        else:
            client_ip = request.META.get('REMOTE_ADDR')  # 未使用代理获取IP

        return client_ip


# admin页面权限
class CheckAdminPathMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        user = request.user
        path = request.path

        if path in settings.DISALLOWED_REQUEST_PATH and not user.is_superuser:
            return HttpResponse('非法请求')

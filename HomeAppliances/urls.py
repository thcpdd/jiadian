from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf import settings


urlpatterns = [
    path('', include('apps.goods.urls', namespace='goods')),
    path('user/', include('apps.user.urls', namespace='user')),
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('order/', include('apps.order.urls', namespace='order')),
    path("admin/", admin.site.urls),
]


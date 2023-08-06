from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import GoodsType, GoodsSKU, GoodsDynamics, GoodsImage, RotationCharts


class BaseGoodsView(View):
    @staticmethod
    def get_navigation_info():
        """导航栏信息"""
        goods_types = GoodsType.objects.all()
        for goods_type in goods_types:
            sku = GoodsSKU.objects.filter(goods_type_id=goods_type.id)[:4]
            goods_type.navs = [s.goods_spu.name for s in sku]

        return goods_types

    @staticmethod
    def get_sku_image(goods_sku):
        """商品sku集对应的一张图片"""
        total_goods = []
        for goods in goods_sku:
            goods_dynamics = GoodsDynamics.objects.filter(goods_sku_id=goods.id)[0]
            image = GoodsImage.objects.filter(goods_dynamics_id=goods_dynamics.id)[0]
            goods_dynamics.image = image.image.url
            total_goods.append(goods_dynamics)

        return total_goods


class IndexView(BaseGoodsView):
    def get(self, request):
        goods_types = GoodsType.objects.all()
        for goods_type in goods_types:
            sku = GoodsSKU.objects.filter(goods_type_id=goods_type.id).order_by('-update_time')[:4]
            goods_type.navs = [s.goods_spu.name for s in sku]

            goods_list = self.get_sku_image(sku)
            goods_type.goods = goods_list

        context = {
            'goods_types': goods_types
        }

        return render(request, 'goods/index.html', context)

    @staticmethod
    def index_rotation(request):
        """首页轮播图"""
        if request.method == "GET":
            rotations = RotationCharts.objects.filter(is_rotate=True)[:4]
            rotations_list = [{'img': rotation.image.url, 'desc': rotation.name} for rotation in rotations]
            return JsonResponse({'data': rotations_list})


class GoodsDetailView(BaseGoodsView):
    def get(self, request, goods_sku_id):
        goods_types = self.get_navigation_info()  # 导航栏信息

        # 查询该商品的所有图片
        goods = GoodsSKU.objects.get(id=goods_sku_id)
        goods_dynamics = GoodsDynamics.objects.filter(goods_sku_id=goods_sku_id)
        goods_images = []
        for goods_dynamic in goods_dynamics:
            images = GoodsImage.objects.filter(goods_dynamics_id=goods_dynamic.id)
            for image in images:
                goods_images.append({'img': image.image.url})

        # 查询相同类型的热销商品
        hot_goods = self.query_hot_goods(goods)
        # 查询商品的大小和颜色
        specs_data, product_data = self.query_goods_dynamics(goods_dynamics)

        context = {
            'goods_types': goods_types,
            'goods': goods,
            'goods_images': goods_images,
            'hot_goods': hot_goods,
            'specs_data': specs_data,
            'product_data': product_data
        }
        return render(request, 'goods/detail.html', context)

    @staticmethod
    def query_goods_dynamics(dynamics):
        """查询该商品的所有搭配"""
        specs_data = []
        product_data = []
        color_set = []  # 存放该商品的所有颜色
        size_set = []  # 存放该商品的所有大小/尺寸

        for dynamic in dynamics:
            if dynamic.size not in map(lambda x: x['name'], size_set):  # 为大小去重
                size_set.append({'id': dynamic.id, 'name': dynamic.size, 'spec': '大小'})
            if dynamic.color not in map(lambda x: x['name'], color_set):  # 为颜色去重
                color_set.append({'id': dynamic.id, 'name': dynamic.color, 'spec': '颜色'})

            product_data.append({
                'id': dynamic.id,
                'options': [
                    {'id': dynamic.id, 'name': dynamic.size, 'spec': '大小'},
                    {'id': dynamic.id, 'name': dynamic.color, 'spec': '颜色'}
                ],
                'spu': dynamic.goods_sku.goods_spu_id,
                'price': dynamic.price,
                'stock': dynamic.stock,
                'sales': dynamic.sales
            })

        specs_data.append({'id': dynamics[0].goods_sku_id, 'name': '大小', 'class_set': size_set})
        specs_data.append({'id': dynamics[0].goods_sku_id, 'name': '颜色', 'class_set': color_set})

        return specs_data, product_data

    @staticmethod
    def query_hot_goods(goods):
        """同类型热卖商品"""
        total_sku = GoodsSKU.objects.filter(goods_type_id=goods.goods_type.id)
        hot_goods = []
        for sku in total_sku:
            goods_dynamics = GoodsDynamics.objects.filter(goods_sku_id=sku.id)
            for goods_dynamic in goods_dynamics:
                if goods_dynamic.goods_sku_id != goods.id:  # 排除自身
                    if goods_dynamic.goods_sku_id not in map(lambda x: x.goods_sku_id, hot_goods):  # 排除相同sku商品
                        goods_dynamic.image = GoodsImage.objects.filter(goods_dynamics_id=goods_dynamic.id)[0].image.url
                        hot_goods.append(goods_dynamic)

        hot_goods = list(sorted(hot_goods, key=lambda x: x.sales, reverse=True))[:4]  # 按销量降序
        return hot_goods


class GoodsListView(BaseGoodsView):
    def get(self, request, show_type, page):
        goods_types = self.get_navigation_info()  # 导航栏信息
        for goods_type in goods_types:
            goods_type.is_active = True if goods_type.logo == show_type else False

        if show_type == 'all':
            goods_sku = GoodsSKU.objects.all()
        else:
            goods_type = GoodsType.objects.get(logo=show_type)
            goods_sku = GoodsSKU.objects.filter(goods_type_id=goods_type.id)

        total_goods = self.get_sku_image(goods_sku)

        try:
            items = list(request.GET.items())
            sort_key = items[0][1]  # 排序关键字
            total_goods = list(self.sort_goods(total_goods, sort_key))
        except IndexError:
            items = ''

        from db.base_model import MyPaginator
        paginator = MyPaginator(total_goods, 8)
        pages = paginator.page(page)
        pages.my_page_range = paginator.show_part_page_range(page, num_pages=10)

        context = {
            'show_type': show_type,
            'goods_types': goods_types,
            'pages': pages,
            'sorted': '?'
        }
        if items:
            context['sorted'] = f'?{items[0][0]}={items[0][1]}'

        return render(request, 'goods/list.html', context)

    @staticmethod
    def sort_goods(total_goods, sort_key):
        sort_choice = {
            'price': sorted(total_goods, key=lambda x: x.price),
            '-price': sorted(total_goods, key=lambda x: x.price, reverse=True),
            'sales': sorted(total_goods, key=lambda x: x.sales),
            '-sales': sorted(total_goods, key=lambda x: x.sales, reverse=True),
            'date': sorted(total_goods, key=lambda x: x.create_time),
            '-date': sorted(total_goods, key=lambda x: x.create_time, reverse=True),
        }

        return sort_choice[sort_key]


class SearchView(BaseGoodsView):
    def get(self, request, page):
        goods_types = self.get_navigation_info()  # 导航栏信息
        content = request.GET.get('search')  # 搜索内容
        goods_sku = GoodsSKU.objects.filter(name__icontains=content)  # 模糊查询

        total_goods = self.get_sku_image(goods_sku)

        from db.base_model import MyPaginator
        paginator = MyPaginator(total_goods, 4)
        pages = paginator.page(page)
        pages.my_page_range = paginator.show_part_page_range(page, num_pages=10)

        context = {
            'pages': pages,
            'show_type': 'all',
            'goods_types': goods_types
        }

        return render(request, 'goods/list.html', context)

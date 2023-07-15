from django.db import models
from django.core.paginator import Paginator, EmptyPage


# 所有模型类都继承这个模型类
class BaseModel(models.Model):
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('修改时间', auto_now=True)
    is_delete = models.BooleanField('删除标记', default=False)

    # 抽象模型类，只能被继承并且不会被实例化、不会单独为其创建数据表，只会依附在子表中
    class Meta:
        abstract = True


# 对分页的简单封装
class MyPaginator:
    def __init__(self, object_list, per_page):
        self.paginator = Paginator(object_list, per_page)

    def page(self, _page):
        try:
            pages = self.paginator.page(_page)
        except EmptyPage:
            pages = self.paginator.page(self.paginator.num_pages)

        return pages

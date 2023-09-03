from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# 对分页的简单封装
class MyPaginator:
    def __init__(self, *args, **kwargs):
        self.paginator = Paginator(*args, **kwargs)

    def page(self, number):
        try:
            pages = self.paginator.page(number)
        except EmptyPage:
            pages = self.paginator.page(self.paginator.num_pages)
        except PageNotAnInteger:
            pages = self.paginator.page(1)

        return pages

    def show_part_page_range(self, current_page, num_pages=8):
        """最多只显示num_pages页"""
        around_page = int(num_pages / 2)
        start = int(current_page) - around_page
        if num_pages % 2 != 0:
            end = int(current_page) + around_page + 1
        else:
            end = int(current_page) + around_page
        if start <= 0:
            start = 1

        if end > self.paginator.num_pages:
            end = self.paginator.num_pages + 1

        return range(start, end)

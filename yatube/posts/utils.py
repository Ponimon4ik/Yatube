from django.core.paginator import Paginator

from .settings import POST_COUNT


def paginator_page(request, post_list):
    paginator = Paginator(post_list, POST_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

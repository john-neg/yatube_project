from django.core.paginator import Paginator

from django.conf import settings


def paginator(post_list, request):
    """ Функция для разбивки постов на страницы """
    result = Paginator(post_list, settings.POSTS_LIMIT)
    page_number = request.GET.get('page')
    return result.get_page(page_number)

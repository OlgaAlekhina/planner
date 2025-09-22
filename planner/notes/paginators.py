from rest_framework.pagination import PageNumberPagination


class TaskPagination(PageNumberPagination):
    """ Пагинация для задач """
    page_size_query_param = 'limit'
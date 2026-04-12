from rest_framework.pagination import CursorPagination


class GlobalCursorPagination(CursorPagination):
    page_size = 6
    ordering = '-id'
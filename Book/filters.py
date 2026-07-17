import django_filters

from .models import Book, Category


class BookFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Поиск по названию",
    )
    author = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Автор",
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label="Категория",
    )
    price_min = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        label="Цена от",
    )
    price_max = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        label="Цена до",
    )
    year_after = django_filters.DateFilter(
        field_name="year_of_manufacture",
        lookup_expr="gte",
        label="Издано после",
    )
    year_before = django_filters.DateFilter(
        field_name="year_of_manufacture",
        lookup_expr="lte",
        label="Издано до",
    )

    class Meta:
        model = Book
        fields = []

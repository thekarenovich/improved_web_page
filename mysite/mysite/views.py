from django.db.models import Count, F
from django.shortcuts import render

from news.models import Category


def page_not_found_view(request, exception):
    context = {'categories': Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(
                   cnt__gt=0).order_by('title')}
    return render(request, '404.html', status=404, context=context)

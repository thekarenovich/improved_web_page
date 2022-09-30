from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count, F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import translation
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.core.mail import send_mail
from django.contrib import messages

from .forms import NewsFrom, UserRegisterForm, UserLoginForm, ContactForm, UpdateNewsFrom
from .models import News, Category


# def select_lang(request, code):
#     go_next = request.META.get('HTTP_REFERER', '/')
#     response = HttpResponseRedirect(go_next)
#     if code and translation.check_for_language(code):
#         if hasattr(request, 'session'):
#             request.session['django_language'] = code
#         else:
#             response.set_cookie(settings.LANGUAGE_COOKIE_NAME, code)
#         translation.activate(code)
#     return response


def email(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(form.cleaned_data['subject'], form.cleaned_data['content'], settings.EMAIL_HOST_USER,
                                 ['thekarenovich@yandex.ru'], fail_silently=True)
            if mail:
                messages.success(request, 'Письмо отправлено')
                return redirect('email')
            else:
                messages.error(request, 'Ошибка отправки')
        else:
            messages.error(request, 'Ошибка валидации')
    else:
        form = ContactForm()
    context = {'form': form, 'categories': Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')}
    return render(request, 'news/email.html', context)


def popular_news(request):
    news = News.objects.order_by('-views')[:6]
    categories = Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')
    context = {'news': news, 'categories': categories}
    return render(request, 'news/popular_news.html', context)


def user_logout(request):
    logout(request)
    return redirect('login')


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = UserLoginForm()
    context = {'form': form, 'categories': Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')}
    return render(request, 'news/login.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserRegisterForm()
    context = {'form': form, 'categories': Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')}
    return render(request, 'news/register.html', context)


class DeleteNews(DeleteView):
    model = News
    success_url = reverse_lazy('home')
    template_name = 'news/delete_news.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')
        context['news_author'] = News.objects.get(pk=self.kwargs["pk"]).author
        return context


class UpdateNews(UpdateView):
    model = News
    template_name = 'news/update_news.html'
    form_class = UpdateNewsFrom

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("view_news", kwargs={"pk": pk})

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')
        context['news_author'] = News.objects.get(pk= self.kwargs["pk"]).author
        return context


class ViewNews(DetailView):
    model = News
    context_object_name = 'news_item'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')

        self.object.views = F('views') + 1
        self.object.save()
        self.object.refresh_from_db()

        str_number_to_shorten = str(self.object.views)

        if 16 <= len(str_number_to_shorten) < 19:
            test = str_number_to_shorten[:-15]
            if test == '':
                context['views_str'] = '1Q'
            else:
                context['views_str'] = str_number_to_shorten[:-15] + "Q"

        elif 13 <= len(str_number_to_shorten) < 16:
            test = str_number_to_shorten[:-12]
            if test == '':
                context['views_str'] = '1T'
            else:
                context['views_str'] = str_number_to_shorten[:-12] + "T"

        elif 10 <= len(str_number_to_shorten) < 13:
            test = str_number_to_shorten[:-9]
            if test == '':
                context['views_str'] = '1B'
            else:
                context['views_str'] = str_number_to_shorten[:-9] + "B"

        elif 7 <= len(str_number_to_shorten) < 10:
            test = str_number_to_shorten[:-6]
            if test == '':
                context['views_str'] = '1M'
            else:
                context['views_str'] = str_number_to_shorten[:-6] + "M"

        else:
            context['views_str'] = self.object.views

        return context


class CreateNews(CreateView):
    form_class = NewsFrom
    template_name = 'news/add_news.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(CreateNews, self).form_valid(form)


class Search(ListView):
    template_name = 'news/search.html'
    paginate_by = 3

    def get_queryset(self):
        return News.objects.filter(title__icontains=self.request.GET.get('s'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')
        context['s'] = f"s={self.request.GET.get('s')}&"
        return context


class HomeNews(ListView):
    model = News
    template_name = 'news/home_news_list.html'
    context_object_name = 'news'
    paginate_by = 3
    # extra_context = {'categories': Category.objects.all()}

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')

        # news = []
        # for i in News.objects.all():
        #     if i.author == self.request.user:
        #         news.append(News.objects.get(id=i.id))
        # context['news'] = news

        # context['news'] = News.objects.filter(author=self.request.user)

        return context

    def get_queryset(self):
        return News.objects.filter(is_published=True)


class NewsByCategory(ListView):
    model = News
    template_name = 'news/category.html'
    context_object_name = 'news'
    allow_empty = False
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')
        context['title'] = Category.objects.get(pk=self.kwargs['category_id'])
        return context

    def get_queryset(self):
        return News.objects.filter(category_id=self.kwargs['category_id'], is_published=True)


class User(ListView):
    template_name = 'news/user.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(cnt=Count('news', filter=F('news__is_published'))).filter(cnt__gt=0).order_by('title')
        return context

    def get_queryset(self):
        return News.objects.filter(is_published=True)

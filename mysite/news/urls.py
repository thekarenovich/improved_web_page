from django.urls import path
from .views import *


urlpatterns = [

    path('user/', User.as_view(), name='user'),
    path('email/', email, name='email'),  # Отправление письма по почте
    path('login/', user_login, name='login'),  # Вход
    path('logout/', user_logout, name='logout'),  # Выход
    path('register/', register, name='register'),  # Регистрация
    path('news/add-news/', CreateNews.as_view(), name='add_news'),  # Добавление
    path('delete/<int:pk>/', DeleteNews.as_view(), name='delete_news'),  # Удаление записи
    path('update/<int:pk>/', UpdateNews.as_view(), name='update_news'),  # Редактирование записи
    path('news/<int:pk>/', ViewNews.as_view(), name='view_news'),  # Просмотр записи по кнопке "Прочитать"
    path('category/<int:category_id>/', NewsByCategory.as_view(), name='category'),
    # Каталог - просмотр записей опр. каталога
    path('search/', Search.as_view(), name='search'),  # Поиск записей
    path('popular_news/', popular_news, name='popular_news'),  # Популярные записи
    path('', HomeNews.as_view(), name='home'),  # Главная - просмотр всех записей
]

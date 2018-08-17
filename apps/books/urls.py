from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^books/add$', views.add_book_page),
    url(r'^books$', views.books),
    url(r'^books/(?P<id>\d+)$', views.book_show),
    url(r'^users/(?P<id>\d+)$', views.users_show),

    # Register and login urls route
    url(r'^register$', views.register, name="register"),
    url(r'^login$', views.login, name="login"),
    url(r'^logout$', views.logout, name="logout"),

    # url to add book and review
    url(r'^add_book$', views.add_book),
    url(r'^add_book_review$', views.add_book_review)
]
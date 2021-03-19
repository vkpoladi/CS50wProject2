from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:listing_pk>", views.listing_page, name="listing_page"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist_remove", views.watchlist_remove, name="watchlist_remove"),
    path("bidding", views.bidding, name="bidding"),
    path("categories", views.categories, name="categories"),
    path("category_page/<str:category>", views.category_page, name="category_page"),
    path("comment_add", views.comment_add, name="comment_add"),
    path("close_listing", views.close_listing, name="close_listing")
]



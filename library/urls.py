from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.books, name='books'),
    path('authors/', views.authors, name='authors'),
    path('authors/<int:author_id>/', views.author_detail, name='author_detail'),
    path('reviews/search/', views.reviews, name='reviews_search'),
    path('reviews/', views.reviews, name='reviews'),
    path('news/', views.news, name='news'),
    path('account/', views.account, name='account'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/ajax/', views.books_ajax, name='books_ajax'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('authors/ajax/', views.authors_ajax, name='authors_ajax'),
    path('reviews/like/<int:review_id>/', views.like_review, name='like_review'),
    path('reviews/dislike/<int:review_id>/', views.dislike_review, name='dislike_review'),
    path('books/add_favorite/', views.add_favorite, name='add_favorite'),
    path('books/remove_favorite/', views.remove_favorite, name='remove_favorite'),
    path('books/add_next_reading/', views.add_next_reading, name='add_next_reading'),
    path('books/remove_next_reading/', views.remove_next_reading, name='remove_next_reading'),
    path('reviews/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
]

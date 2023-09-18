from django.urls import path
from .views import (PostList, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, PrivatelistView, DeleteResponseView, CategoryView, subscribe_from_category, unsubscribe_from_category, SearchList,
ReplyList)


urlpatterns = [
        path('', (PostList.as_view()), name='posts'),
        path('posts/<int:pk>/', (PostDetailView.as_view()), name='post_detail'),
        path('posts/add/', PostCreateView.as_view(), name='post_create'),
        path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
        path('posts/<int:pk>/delete/',PostDeleteView.as_view(), name='post_delete'),
        path('privatelist/', PrivatelistView.as_view(), name='privatelist'),
        path('search/', SearchList.as_view(), name='search'),
        path('delete_response/<int:pk>/', DeleteResponseView.as_view(), name='delete_response'),
        path('category/<int:pk>/', CategoryView.as_view(), name='category'),
        path('subscribe/<int:pk>/', subscribe_from_category, name='subscribe'),
        path('unsubscribe/<int:pk>/', unsubscribe_from_category, name='unsubscribe'),
    ]

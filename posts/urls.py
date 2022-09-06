from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.post_create, name='post_create'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/',
         views.post_edit,
         name='post_edit'),
    path('posts/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path('500', views.server_error, name='500'),
    path('403', views.permission_denied, name='403'),
    path(
        'profile/<str:username>/profile_edit',
        views.profile_edit,
        name='profile_edit'
    ),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('group/create', views.group_create, name='group_create'),
]

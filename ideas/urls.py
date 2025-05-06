
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # if you want “All ideas” at /ideas/
    path('', views.idea_list, name='idea_list'),

    # signup is a function-based view in views.py
    path('signup/', views.signup_view, name='signup'),

    # login/logout via Django’s built-ins, pointing at your templates in templates/registration/
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('submit-idea/', views.submit_idea, name='submit_idea'),
    path('<int:pk>/', views.idea_detail, name='idea_detail'),
    path('<int:pk>/edit/', views.idea_edit, name='idea_edit'),
    path('<int:pk>/collab/', views.request_collab, name='request_collab'),
    path('<int:pk>/delete/', views.delete_idea, name='idea_delete'),
    path('browse-ideas/', views.browse_ideas, name='browse_ideas'),
    path('profile/', views.profile_view, name='profile'),
    path('create/', views.idea_create, name='idea_create'),
    path('ideas/<int:idea_id>/join/', views.send_join_request, name='send_join_request'),
    path('requests/<int:idea_id>/<int:request_id>/accept/', views.accept_request, name='accept_request'),
    path('requests/<int:idea_id>/<int:request_id>/reject/', views.reject_request, name='reject_request'),
    path('ideas/manage_requests/', views.user_manage_requests, name='user_manage_requests'),
    path('ideas/<int:idea_id>/join_requests/', views.idea_manage_requests, name='idea_manage_requests'),
]


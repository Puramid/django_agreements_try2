from django.urls import path
from . import views

app_name = 'deals'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),

    path('agreements/new/', views.agreement_create_view, name='agreement-new'),
    path('agreements/<int:pk>/edit/', views.agreement_update_view, name='agreement-edit'),
    path('agreements/<int:pk>/delete/', views.agreement_delete_view, name='agreement-delete'),

    path('agreements/<int:agreement_pk>/portfolio/new/', views.portfolio_create_view, name='portfolio-new'),
    path('portfolio/<int:pk>/edit/', views.portfolio_update_view, name='portfolio-edit'),
    path('portfolio/<int:pk>/delete/', views.portfolio_delete_view, name='portfolio-delete'),
]
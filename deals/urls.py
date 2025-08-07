from django.urls import path
from . import views

app_name = 'deals'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),

    path('agreements/new/', views.AgreementCreateView.as_view(), name='agreement-new'),
    path('agreements/<int:pk>/edit/', views.AgreementUpdateView.as_view(), name='agreement-edit'),
    path('agreements/<int:pk>/delete/', views.AgreementDeleteView.as_view(), name='agreement-delete'),

    path('agreements/<int:agreement_pk>/portfolio/new/', views.PortfolioCreateView.as_view(), name='portfolio-new'),
    path('portfolio/<int:pk>/edit/', views.PortfolioUpdateView.as_view(), name='portfolio-edit'),
    path('portfolio/<int:pk>/delete/', views.PortfolioDeleteView.as_view(), name='portfolio-delete'),
]
from django.views.generic import TemplateView
from django.urls import path
from . import views

urlpatterns = [
		path('', views.main, name='main'),
		path('database/', views.database, name='main_database'),
		path('database/assessor/<str:assessor>', views.assessor, name='assessor'),
		path('database/rrn/<str:rrn>', views.rrn, name='rrn'),
		path('login/', views.loginPage, name='login'),
		path('logoutUser/', views.logoutUser, name='logout'),
		path('register/', views.register, name='register'),
		path('todo/', TemplateView.as_view(template_name='index.html'), name='todo'),
]

from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView


app_name = 'lppm'
urlpatterns = [
	path('', views.awal, name='awal'),
	path('login/', LoginView.as_view(template_name='login.html'), name="login"),
	path('logout/', LogoutView.as_view(next_page='lppm:login'), name="logout"),
	path('home/', views.home, name='home'),
	path('home/penelitian_ls', views.penelitian_list_self, name='penelitian_list_self'),
	path('home/pengabdian_ls', views.pengabdian_list_self, name='pengabdian_list_self'),
	path('penelitian_statistik/', views.penelitian_statistik, name='penelitian_statistik'),
	path('chartPenelitian/', views.PenelitianChart.as_view()),
	path('pengabdian_statistik/', views.pengabdian_statistik, name='pengabdian_statistik'),
	path('chartPengabdian/', views.PengabdianChart.as_view()),
	path('penelitian/list/<str:nama>/', views.penelitian_list, name='penelitian_list'),
	path('pengabdian/list/<str:nama>/', views.pengabdian_list, name='pengabdian_list'),
	path('validasi/<int:pk>/', views.validasi, name='validasi'),
]
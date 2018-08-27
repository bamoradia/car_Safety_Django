from django.urls import path
from . import views

urlpatterns = [
	path('api/v1/topten', views.top_ten_list, name='top_ten_list'),
	path('api/v1/modelyears', views.get_model_years, name='get_model_years'),
]
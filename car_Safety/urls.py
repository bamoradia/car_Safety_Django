from django.urls import path
from . import views

urlpatterns = [
	path('api/v1/topsafety', views.top_safety, name='top_safety'),
	path('api/v1/modelyears', views.get_model_years, name='get_model_years'),
	path('api/v1/makes', views.get_makes, name='get_makes'),
	path('api/v1/models', views.get_models, name='get_models'),
	path('api/v1/trims', views.get_trims, name='get_trims'),
	path('api/v1/vehicleinfo', views.get_vehicle_info, name='get_vehicle_info'),
]
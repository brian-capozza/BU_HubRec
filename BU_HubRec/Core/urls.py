from django.urls import path
from Core import views

app_name = 'Core'

urlpatterns = [
    path("hubs/", views.pick_hub, name="pick_hub"),
    path("hubs/<str:hub_code>/", views.display_hub_classes, name="display_hub_classes"),
]
from django.urls import path
from Core import views
from .views import MyWizard
from .forms import Step1Form, Step2Form, Step3Form

app_name = 'Core'

urlpatterns = [
    path('', views.index, name='index'),
    path("hubs/", views.pick_hub, name="pick_hub"),
    path("hubs/<str:hub_code>/", views.display_hub_classes, name="display_hub_classes"),
    path("course/<str:college>/<str:subject>/<str:catalog_number>/", views.display_course_information, name="display_course_information"),
    path("wizard/", MyWizard.as_view([Step1Form, Step2Form, Step3Form]), name="optimizer"),
]
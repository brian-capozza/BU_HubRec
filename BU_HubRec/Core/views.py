from django.shortcuts import render, redirect

# Create your views here.

from django.shortcuts import render, get_object_or_404
from .models import Hub, Course

def pick_hub(request):
    hubs = Hub.objects.all().order_by("unit_name")
    return render(request, "pick_hub.html", {"hubs": hubs})

def display_hub_classes(request, hub_code):
    hub = get_object_or_404(Hub, unit_name=hub_code)
    courses = Course.objects.filter(hubs=hub).order_by("name")

    return render(request, "display_hub_classes.html", {
        "hub": hub,
        "courses": courses,
    })
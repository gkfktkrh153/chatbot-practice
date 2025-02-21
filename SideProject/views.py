from django.http import HttpResponse
from django.http import JsonResponse
from .models import Fruits


def index(request):
    fruitsList = Fruits.objects.all()
    return HttpResponse(fruitsList)


def get_data(request):
    data = {
        "message": "Hello from Django!",
        "count": 42
    }
    return JsonResponse(data)
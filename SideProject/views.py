from django.http import HttpResponse
from django.http import JsonResponse

from SideProject.models import Employees


def index(request):
    query = "SELECT * FROM employees"
    employees =  Employees.objects.raw(query)


    return HttpResponse(employees)


def get_data(request):
    data = {
        "message": "Hello from Django!",
        "count": 42
    }
    return JsonResponse(data)
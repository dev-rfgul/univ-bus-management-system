from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    # return render(request, 'home.html')
    return HttpResponse("Hello, this is my first Django app!")
def about(request):
    return HttpResponse("this is about page")
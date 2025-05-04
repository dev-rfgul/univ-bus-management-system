from django.shortcuts import render
from django.http import HttpResponse
from .models import Bus,Driver,Route,Schedule,StudentBooking
# Create your views here.

def home(request):
    # return render(request, 'home.html')
    return HttpResponse("Hello, this is my first Django app!")
def about(request):
    return HttpResponse("this is about page")

def add_bus(request):

    if request.method == 'POST':
        plate_number = request.POST.get('plate_number')
        capacity = request.POST.get('capacity')
        route = request.POST.get('route')

        Bus.objects.create(
            plate_number=plate_number,
            capacity=capacity,
            route=route
        )

        return HttpResponse("Bus added successfully")
    return HttpResponse("Send a POST request")

def add_driver(request):
    if request.method=='POST':
        name=request.POST.get('name'),
        license_numeber=request.POST.get('license_numeber'),
        contact_number=request.POST.get('contact_number'),
        bus=request.POST.get('bus'),

        Driver.objects.create(
            name=name,
            license_number=license_numeber,
            contact_number=contact_number,
            bus=bus
        )

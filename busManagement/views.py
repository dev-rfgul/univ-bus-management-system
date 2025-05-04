from django.shortcuts import render, get_object_or_404, redirect
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
        return HttpResponse("Driver added successfully")
    return HttpResponse("Send a POST request")

def add_route(request):
    if request.method=='POST':
        route_number=request.POST.get('route_number'),
        start_location=request.POST.get('start_location'),
        end_location=request.POST.get('end_location'),
        distance=request.POST.get('distance'),

        Route.objects.create(
            route_number=route_number,
            start_location=start_location,
            end_location=end_location,
            distance=distance
        )
        return HttpResponse("Route added successfully")
    return HttpResponse("Send a POST request")

def add_schedule(request):
    if request.method=='POST':
        bus=request.POST.get('bus'),
        route=request.POST.get('route'),
        departure_time=request.POST.get('departure_time'),
        arrival_time=request.POST.get('arrival_time'),

        Schedule.objects.create(
            bus=bus,
            route=route,
            departure_time=departure_time,
            arrival_time=arrival_time
        )
        return HttpResponse("Schedule added successfully")
    return HttpResponse("Send a POST request")

def add_student_booking(request):

    if request.method=='POST':
        student_name=request.POST.get('student_name'),
        bus=request.POST.get('bus'),
        route=request.POST.get('route'),
        booking_date=request.POST.get('booking_date'),
        seats_booked=request.POST.get('seats_booked'),

        StudentBooking.objects.create(
            student_name=student_name,
            bus=bus,
            route=route,
            booking_date=booking_date,
            seats_booked=seats_booked
        )
        return HttpResponse("Student Booking added successfully")
    return HttpResponse("Send a POST request")

def view_buses(request):
    buses = Bus.objects.all()
    context={'buses': buses}
    return render(request, 'view_buses.html', context)

def view_drivers(request):
    drivers = Driver.objects.all()
    context={'drivers': drivers}
    return render(request, 'view_drivers.html', context)

def view_routes(request):
    routes = Route.objects.all()
    context = {'routes': routes}
    return render(request, 'view_routes.html', context)

def view_schedules(request):
    schedules = Schedule.objects.all()
    return render(request, 'view_schedules.html', {'schedules': schedules})

def view_student_bookings(request):
    student_bookings = StudentBooking.objects.all()
    return render(request, 'view_student_bookings.html', {'student_bookings': student_bookings})


def available_buses(request):
    buses = []
    stops = []
    routes=Route.objects.all()

    # Handle POST request (form submission)
    if request.method == 'POST':
        route_id = request.POST.get('route')
        stop = request.POST.get('stop')  # Stop is optional
        time = request.POST.get('time')

        # Validate inputs
        if route_id:
            try:
                route = Route.objects.get(id=route_id)
                buses = Bus.objects.filter(route=route)

                # If time is selected, filter by time
                if time:
                    buses = buses.filter(schedules__departure_time=time)

                # If stop is provided, filter buses by the stop (only if stop is selected)
                if stop and stop in route.stops.split(','):
                    buses = buses.filter(route=route, schedules__departure_time=time)

                # Get stops for the selected route
                stops = [stop.strip() for stop in route.stops.split(',')]  # Split and clean stops

            except Route.DoesNotExist:
                buses = []
                stops = []

        else:
            buses = []
            stops = []

    # Handle GET request (initial page load)
    else:
        # Show available routes in the form
        routes = Route.objects.all()

        # If route is selected, get the stops for that route
        if 'route' in request.GET:
            route_id = request.GET.get('route')
            try:
                route = Route.objects.get(id=route_id)
                stops = [stop.strip() for stop in route.stops.split(',')]
            except Route.DoesNotExist:
                stops = []

    # Return the rendered response
    return render(request, 'bus_filter.html', {'routes': routes, 'stops': stops, 'buses': buses})

def register_bus(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    bus.registered_users.add(request.user)
    return redirect('available_buses')  # or show a success page

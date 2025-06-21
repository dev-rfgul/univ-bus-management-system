from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Bus,Driver,Route,Schedule,StudentBooking, ContactMessage
from .forms import UserSignInForm,UserSignupForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout as auth_logout
from django.contrib.auth.decorators import login_required

# from django.contrib import messages
# from .forms import UserSignupForm, UserSignInForm
from django.contrib.auth  import get_user_model 

User=get_user_model()
# Create your views here.

def home(request):
    # return render(request, 'home.html')
    return render(request, 'home.html', {'title': 'home'})

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

@login_required
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

# Function to filter buses based on route and stop
# and to show available buses for a specific route
@login_required
def available_buses(request):
    buses = []
    matching_routes = []  # define here to avoid UnboundLocalError

    if request.method == 'POST':
        start_location = request.POST.get('start_location', '').strip().lower()
        stop = request.POST.get('stop', '').strip().lower()

        if start_location and stop:
            for route in Route.objects.all():
                route_stops = [s.strip().lower() for s in route.stops.split(',') if s.strip()]
                # print(route_stops)

                if start_location in route_stops and stop in route_stops:
                    if route_stops.index(start_location) < route_stops.index(stop):
                        matching_routes.append(route)

            buses = Bus.objects.filter(route__in=matching_routes)
        else:
            return HttpResponse("Both stop and starting location are required.")

    return render(request, 'bus_filter.html', {
        'buses': buses,
        'routes': matching_routes
    })

# Function to register a user for a bus
@login_required
def register_bus(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    bus.registered_users.add(request.user)
    bus.available_seats -= 1
    bus.save()
    return redirect('my_registered_buses')



def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')  # Redirect to login page after successful signup
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = UserSignInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Get user by email and authenticate
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, 'Successfully logged in!')
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:   
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserSignInForm()
    return render(request, 'login.html', {'form': form})

def contact_thanks(request):
    return render(request,'thanks.html')

def contact(request):
    if request.method=='POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message: 
            ContactMessage.objects.create(name=name,email=email,message=message)
            return redirect('contact_thanks') 
            # return HttpResponse("form submitted successfully")
        else:
            error="Please fill all the details"
            return render(request,'contact.html',{'error':error,'name':name, 'message':message})
            
    return render(request, 'contact.html', {'title': 'Contact Us'})
            
@login_required
def driver_portal(request):
    user = request.user
    driver = None
    bus = None
    stops_list = []
    is_driver = getattr(user, 'is_driver', False)  # Safe check

    if is_driver:
        try:
            driver = user.driver_profile
            bus = Bus.objects.filter(driver=driver).first()
            if bus and bus.route and bus.route.stops:
                stops_list = [stop.strip() for stop in bus.route.stops.split(',')]

            if request.method == 'POST':
                new_location = request.POST.get('current_location')
                if new_location in stops_list:
                    bus.current_location = new_location
                    bus.save()

                    # 🚍 If it's the last stop, remove all registered users
                    if new_location == stops_list[-1]:
                        bus.registered_users.clear()
                        bus.available_seats = bus.capacity  # reset seat count
                        bus.save()

                    return redirect('driver_portal')  # Redirect after POST
        except Driver.DoesNotExist:
            is_driver = False  # Fallback in case profile is missing

    return render(request, 'driver_portal.html', {
        'user': user,
        'driver': driver,
        'bus': bus,
        'stops_list': stops_list,
        'is_driver': is_driver,
    })

@login_required
def my_registered_buses(request):
    user_buses = request.user.buses.select_related('driver', 'route')
    return render(request, 'my_registered_bus.html', {'buses': user_buses})

def logout(request):
    auth_logout(request)
    return redirect('home')
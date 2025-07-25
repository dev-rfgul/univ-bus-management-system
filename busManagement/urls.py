from django.urls import path,include

from .import views
from .utils import route_view

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.signin, name='login'),
    path('logout/', views.logout, name='logout'),
    path('about/',views.about,name='about'),
    path('add_bus/',views.add_bus,name='add_bus'),
    path('view_bus/',views.view_buses,name='view_buses'),
    path('add_driver/',views.add_driver,name='add_driver'),
    path('view_driver/',views.view_drivers,name='view_driver'),
    path('add_route/',views.add_route,name='add_route'),
    path('view_route/',views.view_routes,name='view_route'),
    path('add_schedule/',views.add_schedule,name='add_schedule'),
    path('view_schedule/',views.view_schedules,name='view_schedule'),
    path('add_student_booking/',views.add_student_booking,name='add_student_booking'),
    path('view_student_booking/',views.view_student_bookings,name='view_student_booking'),
    path('buses/', route_view, name='available_buses'),
    path('buses/register/<int:bus_id>/', views.register_bus, name='register_bus'),
    path('contact/', views.contact, name='contact'),
    path('contact_thanks',views.contact_thanks,name='contact_thanks'),
    path('driver_portal/',views.driver_portal,name='driver_portal'),
    path('my_registered_bus/',views.my_registered_buses,name='my_registered_buses'),
    path('indirect_route/',route_view,name='indirect_route'),
    #to handle the allauth urls,  
    path('accounts/',include("allauth.urls"))
]
from django.urls import path

from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
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
    path('buses/', views.available_buses, name='available_buses'),
    path('buses/register/<int:bus_id>/', views.register_bus, name='register_bus')
]
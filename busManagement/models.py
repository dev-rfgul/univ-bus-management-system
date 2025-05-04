from django.db import models
from django.contrib.auth.models import User


class Route(models.Model):
    route_number = models.CharField(max_length=10, unique=True)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)
    distance = models.FloatField()
    stops = models.TextField(default='')  # comma-separated
    time = models.TimeField(default='00:00:00')

    def __str__(self):
        return f"Route {self.route_number} - {self.start_location} to {self.end_location}"


class Bus(models.Model):
    bus_number = models.CharField(max_length=10, unique=True)
    driver_name = models.CharField(max_length=100)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='buses')
    capacity = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    registered_users = models.ManyToManyField(User, related_name='buses', blank=True)

    def __str__(self):
        return f"Bus {self.bus_number} - {self.driver_name}"


class Schedule(models.Model):
    bus = models.ForeignKey('Bus', on_delete=models.CASCADE, related_name='schedules')
    route = models.ForeignKey('Route', on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    def __str__(self):
        return f"Schedule for {self.bus} on {self.route}"


class StudentBooking(models.Model):
    student_name = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    seats_booked = models.PositiveIntegerField()

    def __str__(self):
        return f"Booking by {self.student_name} for {self.bus} on {self.bus.route}"


class Driver(models.Model):
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=20, unique=True)
    contact_number = models.CharField(max_length=15)
    bus = models.OneToOneField(Bus, on_delete=models.CASCADE, related_name='driver')

    def __str__(self):
        return f"Driver {self.name} - License: {self.license_number}"

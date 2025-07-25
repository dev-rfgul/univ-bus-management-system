from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_driver = models.BooleanField(default=False)
    def __str__(self):
        return self.username

class Route(models.Model):
    route_number = models.CharField(max_length=10, unique=True)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)
    distance = models.FloatField()
    stops = models.TextField(default='')  # comma-separated
    time = models.TimeField(default='00:00:00')

    def __str__(self):
        return f"Route {self.route_number} - {self.start_location} to {self.end_location}"

class Driver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='driver_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=20, unique=True)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"Driver {self.name} - License: {self.license_number}"

class Bus(models.Model):
    bus_number = models.CharField(max_length=10, unique=True)
    driver = models.OneToOneField(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='buses')
    capacity = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    registered_users = models.ManyToManyField(CustomUser, related_name='buses', blank=True)
    departure_time = models.TimeField(default='00:00:00')
    current_location = models.CharField(max_length=100, default='')

    def __str__(self):
        driver = getattr(self, 'driver', None)
        return f"Bus {self.bus_number} - {driver.name if driver else 'No Driver Assigned'}"

class Schedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    def __str__(self):
        return f"Schedule for {self.bus} on {self.route}"

class StudentBooking(models.Model):
    student_name = models.CharField(max_length=100, default='')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    seats_booked = models.PositiveIntegerField()

    def __str__(self):
        return f"Booking by {self.student_name} for {self.bus} on {self.bus.route}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} - {self.email}"

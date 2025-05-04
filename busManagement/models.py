from django.db import models

# Create your models here.

class Bus(models.Model):
    bus_number = models.CharField(max_length=10, unique=True)
    driver_name = models.CharField(max_length=100)
    route = models.CharField(max_length=100)
    capacity = models.IntegerField()
    available_seats = models.IntegerField()

    def __str__(self):
        return f"Bus {self.bus_number} - {self.driver_name}"
    
class Route(models.Model):
        route_number = models.CharField(max_length=10, unique=True)
        start_location = models.CharField(max_length=100)
        end_location = models.CharField(max_length=100)
        distance = models.FloatField()
        stops=models.TextField(default='') 

        def __str__(self):
            return f"Route {self.route_number} - {self.start_location} to {self.end_location}"
        
class Schedule(models.Model):
        bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
        route = models.ForeignKey(Route, on_delete=models.CASCADE)
        departure_time = models.TimeField()
        arrival_time = models.TimeField()

        def __str__(self):
            return f"Schedule for {self.bus} on {self.route}"

class StudentBooking(models.Model):
        student_name = models.CharField(max_length=100)
        bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
        route = models.ForeignKey(Route, on_delete=models.CASCADE)
        booking_date = models.DateField()
        seats_booked = models.IntegerField()

        def __str__(self):
            return f"Booking by {self.student_name} for {self.bus} on {self.route}"
        
class Driver(models.Model):
        name = models.CharField(max_length=100)
        license_number = models.CharField(max_length=20, unique=True)
        contact_number = models.CharField(max_length=15)
        bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
        def __str__(self):
            return f"Driver {self.name} - License: {self.license_number}"
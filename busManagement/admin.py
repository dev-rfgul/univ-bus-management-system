from django.contrib import admin
from .models import Bus, Route, Schedule, StudentBooking, Driver,ContactMessage,CustomUser


# Register your models here.

admin.site.register(Bus)
admin.site.register(Route)
admin.site.register(Schedule)
admin.site.register(StudentBooking)
admin.site.register(Driver)
admin.site.register(ContactMessage)
admin.site.register(CustomUser)

from django.contrib import admin
from .models import Car, Recall, IIHS

# Register your models here.
admin.site.register(Car)
admin.site.register(Recall)
admin.site.register(IIHS)




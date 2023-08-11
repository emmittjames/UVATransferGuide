from django.contrib import admin
from .models import AdminKey, InternalCourse, ExternalCourse, ExternalCollege, CourseTransfer, TransferRequest, Notification

admin.site.register(InternalCourse)
admin.site.register(ExternalCourse)
admin.site.register(ExternalCollege)
admin.site.register(CourseTransfer)
admin.site.register(Notification)
admin.site.register(TransferRequest)
admin.site.register(AdminKey)

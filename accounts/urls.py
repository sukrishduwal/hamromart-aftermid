from . import views
from django.urls import path
urlpatterns = [
    path("staff/", views.staff_management, name="staff_management"),
    path("add-group/", views.add_group, name="add_group"),
]
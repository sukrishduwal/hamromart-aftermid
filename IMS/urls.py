from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Add this
from django.conf.urls.static import static # Add this
from django.contrib.auth import views as auth_views # Add this for logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
] 

# This line is the "magic" that makes images show up
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
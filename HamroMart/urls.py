from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Add this
from django.conf.urls.static import static # Add this
from django.contrib.auth import views as auth_views # Add this for logout
from accounts import views  # Import the add_cashier view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('', include('products.urls')),
    path('', include('sales.urls')),
    path('', include('reports.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # path('accounts/', include('accounts.urls')),  # Add this line to include accounts app URLs
    path("staff/", views.staff_management, name="staff_management"),
] 

# This line is the "magic" that makes images show up
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
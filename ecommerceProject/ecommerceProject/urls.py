from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('store/', include('store.urls')),
    path('users/', include('accounts.urls')),
    path('', include('store.urls')),  # Home page shows store's product listing
]

from django.contrib import admin
from django.urls import path, include
from payments.views import ListItemAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('payments.urls'))
]

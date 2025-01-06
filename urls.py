from django.urls import path, include

urlpatterns = [
    path('ecom/', include("app.urls")),
]

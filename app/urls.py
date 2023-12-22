"""
URL configuration for dentiai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from api import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/images/", views.ImageViewSet.as_view({"get": "list", "post": "create"})),
    path("api/images/<str:pk>/", views.ImageViewSet.as_view({"get": "retrieve", "delete": "destroy", "put": "update"})),
    path("api/images/<str:pk>/annotations/", views.ImageAnnotationView.as_view()),
    path("api/annotations/<str:pk>/", views.AnnotationDetailView.as_view()),
]

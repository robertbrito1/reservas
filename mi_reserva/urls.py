"""
URL configuration for mi_reserva project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from reservas import views
urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.formulario_reserva, name='formulario_reserva'),
    path('guardar-reserva/', views.guardar_reserva, name='guardar_reserva'),
    path('eliminar-reserva/<int:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),
    path('terraza/', views.vista_terraza, name='terraza'),
    path('exportar-pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('editar-reserva/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    
]

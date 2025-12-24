from django.contrib import admin

# Register your models here.
from .models import Reserva

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    # Esto hace que la lista sea legible en el admin
    list_display = ( 'nombre', 'apellido', 'telefono' )
    # Añade filtros laterales
    
    # Añade un buscador por nombre
    search_fields = ('nombre', 'apellido')
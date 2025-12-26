from django.db import models

# Create your models here.
class Reserva(models.Model):
    # Opciones de turno
    TURNOS = [
        ('DIA', 'Día'),
        ('NOCHE', 'Noche'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    fecha = models.DateField()
    hora = models.TimeField()
    mesa = models.IntegerField()
    turno = models.CharField(max_length=5, choices=TURNOS)
    comentarios = models.TextField(null=True, blank=True)
    personas = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.nombre} {self.apellido} - Mesa {self.mesa} ({self.turno})"
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Reserva
from datetime import date
from django.shortcuts import get_object_or_404, redirect
def formulario_reserva(request):
    fecha_str = request.GET.get('fecha')
    fecha_actual = date.fromisoformat(fecha_str) if fecha_str else date.today()
    turno_actual = request.GET.get('turno', 'DIA')
    
    # Obtenemos las reservas completas para ese día y turno
    reservas_queryset = Reserva.objects.filter(fecha=fecha_actual, turno=turno_actual)
    
    # Creamos un diccionario para buscar rápido: {numero_mesa: objeto_reserva}
    dict_reservas = {res.mesa: res for res in reservas_queryset}
    
    mesas = []
    for i in range(101, 122):
        reserva_data = dict_reservas.get(i)
        mesas.append({
            'numero': i,
            'ocupada': reserva_data is not None,
            'detalle': reserva_data # Aquí va el nombre, tel, etc.
        })
    
    return render(request, 'inicio.html', {
        'mesas': mesas, 
        'fecha_actual': fecha_actual.isoformat(),
        'turno_actual': turno_actual
    })


def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    # Guardamos la fecha y turno para volver a la misma vista después de borrar
    fecha = reserva.fecha
    turno = reserva.turno
    reserva.delete()
    return redirect(f'/?fecha={fecha}&turno={turno}')
def guardar_reserva(request):
    if request.method == 'POST':
        # Capturamos los datos del formulario
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        telefono = request.POST.get('telefono')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        mesa = request.POST.get('mesa')
        turno = request.POST.get('turno')
        comentarios = request.POST.get('comentarios', '')

        # Creamos y guardamos el objeto en la base de datos
        try:
            nueva_reserva = Reserva(
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                fecha=fecha,
                hora=hora,
                mesa=mesa,
                turno=turno,
                comentarios=comentarios
            )
            nueva_reserva.save()
            messages.success(request, f"¡Reserva confirmada para {nombre} en el turno de {turno}!")
            return redirect('formulario_reserva')
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")
            return redirect('formulario_reserva')

    return redirect('formulario_reserva')

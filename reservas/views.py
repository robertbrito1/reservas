from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from datetime import date
from .models import Reserva
from reportlab.lib import colors
# ReportLab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def formulario_reserva(request):
    fecha_str = request.GET.get('fecha')
    fecha_actual = date.fromisoformat(fecha_str) if fecha_str else date.today()
    turno_actual = request.GET.get('turno', 'DIA')
    
    reservas_queryset = Reserva.objects.filter(fecha=fecha_actual, turno=turno_actual)
    dict_reservas = {res.mesa: res for res in reservas_queryset}
    
    mesas = []
    for i in range(101, 111):
        reserva_data = dict_reservas.get(i)
        es_conjunto = False
        
        # Lógica para detectar si es un conjunto
        if reserva_data:
            coincidencias = reservas_queryset.filter(
                nombre=reserva_data.nombre, 
                apellido=reserva_data.apellido, 
                hora=reserva_data.hora
            ).count()
            es_conjunto = coincidencias > 1

        mesas.append({
            'numero': i,
            'ocupada': reserva_data is not None,
            'detalle': reserva_data,
            'es_conjunto': es_conjunto
        })
    for i in range(120, 123):
        reserva_data = dict_reservas.get(i)
        es_conjunto = False
        
        # Lógica para detectar si es un conjunto
        if reserva_data:
            coincidencias = reservas_queryset.filter(
                nombre=reserva_data.nombre, 
                apellido=reserva_data.apellido, 
                hora=reserva_data.hora
            ).count()
            es_conjunto = coincidencias > 1

        mesas.append({
            'numero': i,
            'ocupada': reserva_data is not None,
            'detalle': reserva_data,
            'es_conjunto': es_conjunto
        })

    return render(request, 'inicio.html', {
        'mesas': mesas, 
        'fecha_actual': fecha_actual.isoformat(),
        'turno_actual': turno_actual
    })

def vista_terraza(request):
    fecha_str = request.GET.get('fecha', str(date.today()))
    turno = request.GET.get('turno', 'DIA')
    
    reservas_queryset = Reserva.objects.filter(fecha=fecha_str, turno=turno)
    
    mesas = []
    for i in range(1, 13):
        reserva_data = reservas_queryset.filter(mesa=i).first()
        es_conjunto = False
        
        if reserva_data:
            coincidencias = reservas_queryset.filter(
                nombre=reserva_data.nombre, 
                apellido=reserva_data.apellido, 
                hora=reserva_data.hora
            ).count()
            es_conjunto = coincidencias > 1

        mesas.append({
            'numero': i,
            'ocupada': reserva_data is not None,
            'detalle': reserva_data,
            'es_conjunto': es_conjunto
        })

    return render(request, 'terraza.html', {
        'mesas': mesas,
        'fecha_actual': fecha_str,
        'turno_actual': turno
    })

def guardar_reserva(request):
    if request.method == 'POST':
        mesas_raw = request.POST.get('mesa')
        lista_mesas = mesas_raw.split(',')
        
        datos = {
            'nombre': request.POST.get('nombre'),
            'apellido': request.POST.get('apellido'),
            'telefono': request.POST.get('telefono'),
            'fecha': request.POST.get('fecha'),
            'hora': request.POST.get('hora'),
            'turno': request.POST.get('turno'),
            'personas': request.POST.get('personas'),
            'comentarios': request.POST.get('comentarios'),
        }

        for num_mesa in lista_mesas:
            if num_mesa.strip():
                Reserva.objects.create(mesa=num_mesa.strip(), **datos)
        
    return redirect(f"/?fecha={request.POST.get('fecha')}&turno={request.POST.get('turno')}")

def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    fecha, turno = reserva.fecha, reserva.turno
    reserva.delete()
    return redirect(f'/?fecha={fecha}&turno={turno}')

def exportar_pdf(request):
    # 1. Capturamos los datos de la URL
    fecha_str = request.GET.get('fecha', str(date.today()))
    turno_str = request.GET.get('turno', 'DIA')
    
    # 2. Obtenemos las reservas filtradas y ordenadas por cliente
    # Cambié 'fecha_actual' por 'fecha_str' para corregir tu error
    reservas = Reserva.objects.filter(
        fecha=fecha_str, 
        turno=turno_str
    ).order_by('nombre', 'apellido', 'hora')

    # 3. Preparar respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reservas_{fecha_str}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # --- Título ---
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, height - 50, f"RESERVAS M&J - {fecha_str} ({turno_str})")
    
    # --- Encabezados de tabla ---
    y = height - 100
    p.setFont("Helvetica-Bold", 10)
    headers = ["MESA", "ZONA", "HORA", "PAX", "CLIENTE", "TEL."]
    cols = [40, 85, 140, 185, 220, 350]
    for i, h in enumerate(headers): 
        p.drawString(cols[i], y, h)
    
    p.line(40, y-5, 550, y-5)
    y -= 25
    
    # --- Listado de Reservas ---
    for r in reservas:
        # Detectar si esta reserva es parte de un grupo (mismo cliente, misma hora)
        es_grupo = reservas.filter(
            nombre=r.nombre, 
            apellido=r.apellido, 
            hora=r.hora
        ).count() > 1

        p.setFont("Helvetica", 9)
        
        # Si es grupo, pintamos el texto en un color azul oscuro o rojo para resaltar
        if es_grupo:
            p.setFillColor(colors.HexColor("#A52A2A")) # Color café/rojo oscuro
        else:
            p.setFillColor(colors.black)

        # Determinar zona y etiqueta
        zona = "TERRAZA" if r.mesa < 100 else "SALÓN"
        # Agregamos T para terraza y S para salón
        mesa_label = f"T{r.mesa}" if r.mesa < 100 else f"{r.mesa}S"
        
        # Escribir los datos en las columnas
        p.drawString(40, y, mesa_label)
        p.drawString(85, y, zona)
        p.drawString(140, y, r.hora.strftime('%H:%M') if r.hora else "--:--")
        p.drawString(185, y, str(r.personas))
        
        # Nombre del cliente (con marca si es grupo)
        nombre_display = f"{r.nombre} {r.apellido}"
        if es_grupo:
            nombre_display += " (GRUPO)"
        p.drawString(220, y, nombre_display[:30])
        
        p.drawString(350, y, str(r.telefono))
        
        # Dibujar una línea sutil debajo de cada fila
        p.setStrokeColor(colors.lightgrey)
        p.line(40, y-5, 550, y-5)
        
        y -= 20
        
        # Control de salto de página
        if y < 50:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 9)

    p.save()
    return response
   # Asegúrate de que la línea 190 (el def) y la 191 (el if) se vean así:
def editar_reserva(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id)
        reserva.nombre = request.POST.get('nombre')
        reserva.apellido = request.POST.get('apellido')
        reserva.telefono = request.POST.get('telefono')
        reserva.personas = request.POST.get('personas')
        reserva.hora = request.POST.get('hora')
        reserva.comentarios = request.POST.get('comentarios')
        reserva.save()
        
        messages.success(request, "Reserva actualizada correctamente")
        # Redirigir a la página principal manteniendo la fecha y el turno
        return redirect(f'/?fecha={reserva.fecha}&turno={reserva.turno}')
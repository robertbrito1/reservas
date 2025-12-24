from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from datetime import date
from .models import Reserva

# Importaciones para generar el PDF con ReportLab (la opción estable)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
def formulario_reserva(request):
    fecha_str = request.GET.get('fecha')
    fecha_actual = date.fromisoformat(fecha_str) if fecha_str else date.today()
    turno_actual = request.GET.get('turno', 'DIA')
    
    # Obtenemos las reservas completas para ese día y turno
    reservas_queryset = Reserva.objects.filter(fecha=fecha_actual, turno=turno_actual)
    
    # Creamos un diccionario para buscar rápido: {numero_mesa: objeto_reserva}
    dict_reservas = {res.mesa: res for res in reservas_queryset}
    
    mesas = []
    for i in range(101, 111):
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
def vista_terraza(request):
    # 1. Copiamos la lógica de obtener fecha y turno
    fecha_str = request.GET.get('fecha', str(date.today()))
    turno = request.GET.get('turno', 'DIA')
    
    # 2. Buscamos reservas
    reservas = Reserva.objects.filter(fecha=fecha_str, turno=turno)
    ocupadas = [r.mesa for r in reservas]

    mesas = []
    for i in range(1, 13):  # Mesas de la terraza
        detalle = reservas.filter(mesa=i).first()
        mesas.append({
            'numero': i,
            'ocupada': i in ocupadas,
            'detalle': detalle
        })

    # 3. Enviamos los datos
    return render(request, 'terraza.html', {
        'mesas': mesas,
        'fecha_actual': fecha_str,
        'turno_actual': turno
    })

# ESTA FUNCIÓN DEBE ESTAR AL MISMO NIVEL (BORDE IZQUIERDO) QUE LAS DEMÁS
def exportar_pdf(request):
    # 1. Capturar filtros de la URL
    fecha_str = request.GET.get('fecha', str(date.today()))
    turno = request.GET.get('turno', 'DIA')
    
    # 2. Obtener reservas
    reservas = Reserva.objects.filter(fecha=fecha_str, turno=turno).order_by('mesa')

    # 3. Preparar la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reservas_{fecha_str}_{turno}.pdf"'

    # 4. Crear el PDF con ReportLab
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # --- Encabezado ---
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height - 50, "M&J RESTAURANTE - LISTA DE RESERVAS")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, f"Fecha: {fecha_str}")
    p.drawString(50, height - 95, f"Turno: {turno}")
    p.line(50, height - 105, 550, height - 105)

    # --- Cabecera de Tabla ---
    # --- Cabecera de Tabla (Coordenadas ajustadas) ---
    y = height - 130
    p.setFont("Helvetica-Bold", 10)
    
    # Hemos separado los números para dar más aire
    p.drawString(40, y, "MESA")     # x=40
    p.drawString(85, y, "ZONA")     # x=85
    p.drawString(145, y, "HORA")    # x=145
    p.drawString(195, y, "CLIENTE") # x=195
    p.drawString(335, y, "TEL.")    # x=335 (Reducido a TEL. para ganar espacio)
    p.drawString(410, y, "COMENTARIO") # x=410 (Bastante espacio a la derecha)

    p.line(40, y-5, 560, y-5)

    # --- Datos de las Reservas ---
    p.setFont("Helvetica", 9)
    y -= 20
    for r in reservas:
        if y < 50: 
            p.showPage()
            p.setFont("Helvetica", 9)
            y = height - 50
        
        zona = "TERRAZA" if r.mesa < 100 else "SALÓN"
        
        # Usamos las mismas coordenadas X que en la cabecera
        p.drawString(40, y, str(r.mesa))
        p.drawString(85, y, zona)
        p.drawString(145, y, r.hora.strftime('%H:%M') if r.hora else "--:--")
        p.drawString(195, y, f"{r.nombre} {r.apellido}"[:22]) # Máximo 22 letras
        p.drawString(335, y, str(r.telefono))
        
        # El comentario empieza en 410. 
        # Si r.comentarios es None, ponemos vacío para que no falle
        coment = r.comentarios if r.comentarios else ""
        p.drawString(410, y, coment[:35]) # Máximo 35 letras para que no se salga del folio
        
        y -= 20
    # --- Pie de página ---
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(50, 30, f"Generado el: {date.today()}")

    p.showPage()
    p.save()
    return response
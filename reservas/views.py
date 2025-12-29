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
        fecha = request.POST.get('fecha')
        turno = request.POST.get('turno') # Ahora llegará 'NOCHE' correctamente
        
        datos = {
            'nombre': request.POST.get('nombre'),
            'apellido': request.POST.get('apellido'),
            'telefono': request.POST.get('telefono'),
            'fecha': fecha,
            'hora': request.POST.get('hora'),
            'turno': turno,
            'personas': request.POST.get('personas'),
            'comentarios': request.POST.get('comentarios'),
        }

        for num_mesa in lista_mesas:
            if num_mesa.strip():
                Reserva.objects.create(mesa=num_mesa.strip(), **datos)
        
        # Redirección inteligente
        mesa_ejemplo = int(lista_mesas[0].strip()) if lista_mesas[0].strip() else 0
        url_base = "/terraza/" if mesa_ejemplo < 100 else "/"
        return redirect(f"{url_base}?fecha={fecha}&turno={turno}")
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    fecha, turno, num_mesa = reserva.fecha, reserva.turno, reserva.mesa
    reserva.delete()
    
    url_base = "/terraza/" if num_mesa < 100 else "/"
    return redirect(f"{url_base}?fecha={fecha}&turno={turno}")
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from datetime import date

def exportar_pdf(request):
    fecha_str = request.GET.get('fecha', str(date.today()))
    turno_str = request.GET.get('turno', 'DIA')
    
    reservas_qs = Reserva.objects.filter(fecha=fecha_str, turno=turno_str).order_by('hora', 'nombre')

    reservas_agrupadas = {}
    for r in reservas_qs:
        clave = (r.nombre.lower(), r.apellido.lower(), r.hora)
        
        # Identificar salón (s) o terraza (T)
        try:
            num_mesa = int(r.mesa)
            prefijo = "T" if num_mesa >= 100 else "s"
            mesa_con_letra = f"{prefijo}{num_mesa}"
        except:
            mesa_con_letra = str(r.mesa)

        if clave not in reservas_agrupadas:
            reservas_agrupadas[clave] = {
                'mesas': [mesa_con_letra],
                'hora': r.hora,
                'nombre': f"{r.nombre} {r.apellido}",
                'telefono': r.telefono,
                'personas': r.personas,
            }
        else:
            reservas_agrupadas[clave]['mesas'].append(mesa_con_letra)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reservas_{fecha_str}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # --- Estilos para las mesas largas ---
    styles = getSampleStyleSheet()
    style_mesas = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=9,
        leading=10, # Espacio entre líneas
    )
    style_mesas_grupo = ParagraphStyle(
        'Grupo',
        parent=style_mesas,
        textColor=colors.HexColor("#A52A2A"),
    )

    # --- Título y Encabezados ---
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, height - 50, f"RESERVAS M&J - {fecha_str} ({turno_str})")
    
    y = height - 100
    p.setFont("Helvetica-Bold", 10)
    # Definimos los anchos de columna: MESAS tiene 75 puntos de ancho ahora
    headers = ["MESAS", "HORA", "PAX", "CLIENTE", "TELÉFONO"]
    cols = [40, 115, 160, 200, 380] 
    
    for i, h in enumerate(headers): 
        p.drawString(cols[i], y, h)
    
    p.line(40, y-5, 550, y-5)
    y -= 25
    
    for data in reservas_agrupadas.values():
        p.setFillColor(colors.black)

        texto_mesas = ", ".join(data['mesas'])
        es_grupo = len(data['mesas']) > 1
        label_mesas = f"G: {texto_mesas}" if es_grupo else texto_mesas

        # --- SOLUCIÓN: PARAGRAPH PARA MULTILÍNEA ---
        estilo_actual = style_mesas_grupo if es_grupo else style_mesas
        p_mesas = Paragraph(label_mesas, estilo_actual)
        
        # w_p, h_p son el ancho y alto que ocupa el texto de las mesas
        w_p, h_p = p_mesas.wrap(70, 100) # Limitamos el ancho a 70 puntos
        p_mesas.drawOn(p, cols[0], y - h_p + 8) # Dibujamos

        # Resto de datos (se mantienen igual)
        p.setFont("Helvetica", 9)
        p.drawString(cols[1], y, data['hora'].strftime('%H:%M') if data['hora'] else "--:--")
        p.drawString(cols[2], y, str(data['personas']))
        p.drawString(cols[3], y, data['nombre'].upper()[:35])
        p.drawString(cols[4], y, str(data['telefono']))
        
        # Ajustar 'y' dinámicamente según la altura de las mesas
        espacio_fila = max(h_p + 5, 20)
        p.setStrokeColor(colors.lightgrey)
        p.line(40, y - espacio_fila + 10, 550, y - espacio_fila + 10)
        
        y -= espacio_fila
        
        if y < 50:
            p.showPage()
            y = height - 50

    p.save()
    return response

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
        
        # Redirección inteligente según el número de mesa
        url_base = "/terraza/" if reserva.mesa < 100 else "/"
        return redirect(f"{url_base}?fecha={reserva.fecha}&turno={reserva.turno}")
    

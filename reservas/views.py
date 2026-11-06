from collections import Counter
from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from .models import Reserva

# Numeración de las mesas de cada zona
MESAS_SALON = list(range(101, 111)) + list(range(120, 123))
MESAS_TERRAZA = list(range(1, 13))
INFO_MESAS = "Cada mesa representa 2 comensales."


def construir_mesas(fecha, turno, numeros):
    """Devuelve el estado de cada mesa (libre/ocupada y si es parte de un grupo) para una fecha y turno."""
    reservas = list(Reserva.objects.filter(fecha=fecha, turno=turno))
    dict_reservas = {res.mesa: res for res in reservas}
    # Una reserva de grupo ocupa varias mesas con el mismo nombre, apellido y hora
    conteo_grupos = Counter((res.nombre, res.apellido, res.hora) for res in reservas)

    mesas = []
    for numero in numeros:
        reserva_data = dict_reservas.get(numero)
        es_conjunto = False
        if reserva_data:
            clave = (reserva_data.nombre, reserva_data.apellido, reserva_data.hora)
            es_conjunto = conteo_grupos[clave] > 1
        mesas.append({
            'numero': numero,
            'ocupada': reserva_data is not None,
            'detalle': reserva_data,
            'es_conjunto': es_conjunto,
        })
    return mesas


def leer_filtros(request):
    fecha_str = request.GET.get('fecha')
    fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()
    turno = request.GET.get('turno', 'DIA')
    return fecha, turno


def url_zona(num_mesa, fecha, turno, es_cliente):
    """URL a la que volver después de guardar/editar, según la zona de la mesa y el tipo de usuario."""
    if num_mesa < 100:
        base = '/cliente/terraza/' if es_cliente else '/terraza/'
    else:
        base = '/cliente/' if es_cliente else '/'
    return f"{base}?fecha={fecha}&turno={turno}"


def render_mapa(request, plantilla, numeros, solo_cliente):
    fecha, turno = leer_filtros(request)
    return render(request, plantilla, {
        'mesas': construir_mesas(fecha, turno, numeros),
        'fecha_actual': fecha.isoformat(),
        'turno_actual': turno,
        'info_mesas': INFO_MESAS,
        'solo_cliente': solo_cliente,
    })


# ---------- Vistas públicas (clientes) ----------

def formulario_cliente(request):
    """Vista pública: solo permite reservar. No muestra datos de otros clientes ni deja editar/eliminar."""
    return render_mapa(request, 'inicio.html', MESAS_SALON, solo_cliente=True)


def terraza_cliente(request):
    return render_mapa(request, 'terraza.html', MESAS_TERRAZA, solo_cliente=True)


@require_POST
def guardar_reserva(request):
    """Crea una reserva por cada mesa seleccionada. La usan tanto los empleados como los clientes."""
    lista_mesas = [m.strip() for m in request.POST.get('mesa', '').split(',') if m.strip()]
    fecha = request.POST.get('fecha')
    turno = request.POST.get('turno')

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
        Reserva.objects.create(mesa=num_mesa, **datos)

    mesa_ejemplo = int(lista_mesas[0]) if lista_mesas else 0
    es_cliente = not request.user.is_authenticated
    return redirect(url_zona(mesa_ejemplo, fecha, turno, es_cliente))


# ---------- Vistas internas (empleados, requieren login) ----------

@login_required
def formulario_reserva(request):
    return render_mapa(request, 'inicio.html', MESAS_SALON, solo_cliente=False)


@login_required
def vista_terraza(request):
    return render_mapa(request, 'terraza.html', MESAS_TERRAZA, solo_cliente=False)


@login_required
@require_POST
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.nombre = request.POST.get('nombre')
    reserva.apellido = request.POST.get('apellido')
    reserva.telefono = request.POST.get('telefono')
    reserva.personas = request.POST.get('personas')
    reserva.hora = request.POST.get('hora')
    reserva.comentarios = request.POST.get('comentarios')
    reserva.save()
    return redirect(url_zona(reserva.mesa, reserva.fecha, reserva.turno, es_cliente=False))


@login_required
@require_POST
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    fecha, turno, num_mesa = reserva.fecha, reserva.turno, reserva.mesa
    reserva.delete()
    return redirect(url_zona(num_mesa, fecha, turno, es_cliente=False))


@login_required
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
            prefijo = "s" if num_mesa >= 100 else "T"
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

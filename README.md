# Reservas 🍽️

Sistema para gestionar reservas de restaurante hecho con Django. Permite crear, editar y ver reservas, generar reportes en PDF y acceder desde el admin de Django.

## ¿Qué hace?

- Registra reservas con datos del cliente (nombre, teléfono, fecha, hora)
- Asigna mesas y turnos (día/noche)
- Guarda comentarios especiales sobre la reserva
- Exporta reservas a PDF
- Panel de administración para gestionar todo

## Instalar

**Requisitos:**
- Python 3.12+
- Git

**Pasos:**

```bash
# Clonar
git clone https://github.com/robertbrito1/reservas.git
cd reservas

# Virtual env
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# o en Windows:
.venv\Scripts\activate

# Dependencias
pip install -r requirements.txt

# Configuración
cp .env.example .env

# Base de datos
python manage.py migrate

# (Opcional) Crear usuario admin
python manage.py createsuperuser

# Ejecutar
python manage.py runserver
```

Abre **http://127.0.0.1:8000** en el navegador.

## Si algo falla

**Error: "No module named django"**
- Verifica que el venv esté activado (debes ver `(.venv)` en la terminal)
- Ejecuta: `pip install -r requirements.txt`

**Error: "no such table"**
- Ejecuta: `python manage.py migrate`

**Puerto 8000 en uso**
- Usa otro puerto: `python manage.py runserver 8001`

**En Windows PowerShell: no puedo activar venv**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

## Variables de entorno

Se configura en `.env`. Un ejemplo está en `.env.example`.

Para desarrollo no necesitas cambiar nada, solo copiar.

Para producción (Vercel/Render), actualiza:
```
DJANGO_DEBUG=False
ALLOWED_HOSTS=tudominio.com
DATABASE_URL=postgresql://...
```

## Estructura

```
reservas/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── mi_reserva/          # Config del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── reservas/            # App principal
    ├── models.py        # Modelo Reserva
    ├── views.py
    ├── urls.py
    ├── admin.py
    └── templates/
```

## Tests

```bash
python manage.py test
```

## Licencia

CC BY-NC 4.0 - Solo uso personal/educativo, no comercial.

---

**¿Problemas?** Abre un [issue](https://github.com/robertbrito1/reservas/issues) 👈

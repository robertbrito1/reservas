# reservas

Aplicación Django para tomar reservas de un restaurante.

---

Contenido
- [Descripción](#descripción)
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Requisitos](#requisitos)
- [Instalación y ejecución (local)](#instalación-y-ejecución-local)
- [Variables de entorno](#variables-de-entorno)
- [Base de datos y migraciones](#base-de-datos-y-migraciones)
- [Tests](#tests)
- [Docker (opcional)](#docker-opcional)
- [Buenas prácticas y seguridad](#buenas-prácticas-y-seguridad)
- [Contribuir](#contribuir)
- [Licencia](#licencia)
- [Contacto](#contacto)

---

## Descripción

`reservas` es una aplicación web (Django 6.x) para gestionar las reservas de un restaurante. Permite crear, editar, eliminar y exportar reservas a PDF. La app incluye un modelo `Reserva` con los campos básicos (nombre, apellido, teléfono, fecha, hora, mesa, turno, personas, comentarios).

---

## Características

- Listado y visualización de mesas por salón/terraza.
- Crear reservas (posibilidad de asignar varias mesas en una sola acción).
- Editar y eliminar reservas.
- Exportar listados de reservas a PDF (ReportLab).
- Panel de administración Django incluido.

---

## Tecnologías

- Python 3.11+ (ajustar según tu entorno)
- Django 6.x
- ReportLab (generación de PDFs)
- SQLite (por defecto en desarrollo)
- HTML / CSS para templates y frontend

Revisa `requirements.txt` para la lista completa de dependencias.

---

## Requisitos

- Git
- Python 3.11+ (o la versión que uses)
- pip
- (Opcional) Docker / docker-compose

---

## Instalación y ejecución (local)

1. Clonar el repositorio:
```bash
git clone https://github.com/robertbrito1/reservas.git
cd reservas
```

2. Crear y activar un entorno virtual:
```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno (ver siguiente sección) y ejecutar migraciones:
```bash
python manage.py migrate
```

5. Crear un superusuario (opcional, para acceder al admin):
```bash
python manage.py createsuperuser
```

6. Ejecutar el servidor de desarrollo:
```bash
python manage.py runserver
```

Abrir http://127.0.0.1:8000/ en el navegador.

---

## Variables de entorno

No incluyas secretos ni claves en el repo. Crea un archivo `.env` (no versionar) con las variables necesarias. Un ejemplo mínimo:

```text
# .env.example
DJANGO_SECRET_KEY=replace-with-your-secret
DJANGO_DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=127.0.0.1,localhost
```

Recomendación: usar `django-environ` o `python-decouple` para cargar estas variables en `settings.py`.

---

## Base de datos y migraciones

Actualmente el proyecto usa SQLite por defecto (archivo `db.sqlite3` incluido en el repo).
Comandos útiles:
```bash
python manage.py makemigrations
python manage.py migrate
```

Importante: elimina `db.sqlite3` del control de versiones si contiene datos reales:
```bash
git rm --cached db.sqlite3
echo "db.sqlite3" >> .gitignore
```

Haz backup de la base de datos antes de eliminarla del repo si contiene información relevante.

---

## Tests

En `reservas/tests.py` hay un archivo inicial; conviene añadir tests unitarios e integrados para proteger la lógica de reservas (p. ej. evitar overbooking).

Ejecutar tests:
```bash
python manage.py test
```

## Contribuir

Si quieres contribuir:
- Abre un issue describiendo la mejora o bug.
- Crea una rama con un nombre descriptivo (`feature/`, `fix/`).
- Agrega tests que cubran la nueva funcionalidad o el bug corregido.
- Haz un PR con descripción clara y referencia al issue.

Si quieres, puedo:
- Crear issues prioritarios (README, .gitignore, security, eliminar db).
- Preparar un PR que implemente .gitignore, .env.example y cambie settings para leer variables de entorno.

---

## Licencia

Este proyecto está licenciado bajo la Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).
No se permite el uso comercial del código ni de sus derivados.
Consulta el archivo LICENSE para más detalles o visita https://creativecommons.org/licenses/by-nc/4.0/


---

## Contacto

Autor/maintainer: robertbrito1 (GitHub)

---

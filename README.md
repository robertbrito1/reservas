# 🍽️ Gestor de Reservas para Restaurante

[![Demo](https://img.shields.io/badge/Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://reservas-flax-nine.vercel.app/)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

Aplicación web hecha con **Django** para gestionar las reservas de un bar-restaurante: qué mesas están libres u ocupadas en cada turno, quién ha reservado y un PDF con el listado del día para los camareros.

## 🔑 Probar la demo

| | |
|---|---|
| **Panel de empleados** | [reservas-flax-nine.vercel.app](https://reservas-flax-nine.vercel.app/) |
| Usuario | `demo` |
| Contraseña | `demo-reservas` |
| **Vista pública para clientes** (sin login) | [/cliente/](https://reservas-flax-nine.vercel.app/cliente/) |

> La demo usa **datos de prueba**. El usuario `demo` puede crear, editar y eliminar reservas, pero no tiene acceso al panel `/admin`.

## 💡 Por qué lo hice

En el bar donde trabajaba se pagaba unos **100 € al mes** por un software de reservas. Le propuse a mi jefe hacer yo una alternativa para ahorrarse ese gasto, y así nació este proyecto. Lo diseñé a partir de los problemas que veíamos en el día a día: mesas reservadas dos veces, no saber de un vistazo qué estaba libre y tener que pasar la lista a papel.

Al final el restaurante decidió no implantarlo, pero el proyecto me sirvió para construir una aplicación completa a partir de una necesidad real, desde el modelo de datos hasta el despliegue.

## ✨ Funcionalidades

- **Mapa de mesas por zona:** salón y terraza, por separado, con filtro por **fecha** y **turno** (día / noche).
- **Estado visual de cada mesa:** colores distintos para mesas libres, ocupadas y reservas de grupo. Así se ve de un vistazo qué está reservado.
- **Evitar mesas duplicadas:** las mesas ocupadas no se pueden volver a seleccionar desde el mapa; solo se elige entre las libres.
- **Reservas de grupo:** una misma reserva puede ocupar varias mesas. La app las detecta (mismo nombre, apellido y hora) y las marca como grupo `(G)`.
- **Crear, editar y eliminar reservas** desde ventanas modales, sin cambiar de página. El formulario se envía con `fetch` y muestra una confirmación.
- **Exportar a PDF** el listado del turno, ordenado por hora y agrupado por cliente, para que los camareros lo tengan a mano. Lo genero con **ReportLab**.
- **Login de empleados** con el sistema de autenticación de Django. Todas las vistas internas (salón, terraza, editar, eliminar y PDF) están protegidas con `@login_required`.
- **Vista pública para clientes** (`/cliente/` y `/cliente/terraza/`) donde se puede reservar. Muestra qué mesas están ocupadas, pero **sin los datos de otros clientes**.
- **Panel de administración de Django** para gestionar las reservas y los usuarios, con buscador por nombre.

## 🛠️ Tecnologías

| Parte | Tecnología |
|---|---|
| Backend | Python 3.12, Django 6 |
| Base de datos | SQLite en local, PostgreSQL en producción (con `dj-database-url`) |
| Frontend | Plantillas de Django, Bootstrap 5, JavaScript (`fetch`) |
| PDF | ReportLab |
| Despliegue | Vercel, WhiteNoise para los estáticos |
| Seguridad | `@login_required`, `@require_POST`, CSRF, `django-csp` (Content Security Policy) |
| Tests | `TestCase` de Django |
| Dependencias | `uv` |

## 🧠 Lo que aprendí

- Que Django trae mucho hecho: **autenticación de usuarios** (`LoginView`, `@login_required`) y un **panel de administración** que adapté en pocas líneas en `admin.py`.
- Modelar un caso real con el ORM: un modelo `Reserva` con fecha, hora, turno (`choices`), mesa y número de personas, y consultas con `filter()` por fecha y turno.
- Usar `collections.Counter` para detectar las reservas de grupo y pintarlas distinto.
- Generar un PDF desde cero con ReportLab: columnas, saltos de página y texto en varias líneas con `Paragraph` cuando un grupo tiene muchas mesas.
- Separar la configuración de desarrollo y de producción. La app usa SQLite o PostgreSQL según exista la variable `DATABASE_URL`.
- Crear **comandos de gestión propios** (`create_admin` y `create_demo_user`) que se ejecutan automáticamente en cada despliegue.
- Buenas prácticas de seguridad: la `SECRET_KEY` y el modo `DEBUG` se leen de **variables de entorno**, las acciones que modifican datos solo aceptan `POST` (con token CSRF) y la vista pública no envía datos personales al navegador.
- Escribir **tests** con el cliente de pruebas de Django para comprobar permisos, reservas de grupo y la generación del PDF.

## 📁 Estructura

```
reservas/
├── mi_reserva/            # Configuración del proyecto (settings, urls, wsgi)
├── reservas/              # App principal
│   ├── models.py          # Modelo Reserva
│   ├── views.py           # Mapa de mesas, CRUD de reservas y exportación a PDF
│   ├── admin.py           # Configuración del panel de admin
│   ├── tests.py           # Tests de permisos, reservas y PDF
│   ├── management/commands/   # create_admin y create_demo_user
│   ├── templates/         # inicio, terraza, login, exportar_pdf
│   └── static/css/
├── vercel.json            # Configuración del despliegue
└── pyproject.toml         # Dependencias (uv)
```

## 🚀 Instalación en local

```bash
git clone https://github.com/robertbrito1/reservas.git
cd reservas

# Con uv
uv sync
# o con pip
pip install -r requirements.txt

# Variables de entorno (ver .env.example). En local basta con activar el modo debug:
export DJANGO_DEBUG=True                  # en PowerShell: $env:DJANGO_DEBUG="True"

python manage.py migrate
python manage.py create_demo_user         # usuario demo / demo-reservas
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` e inicia sesión.

Para crear un administrador, define `DJANGO_SUPERUSER_PASSWORD` y ejecuta `python manage.py create_admin`.

### Tests

```bash
python manage.py test reservas
```

## 🔜 Próximas mejoras

- [x] Proteger con login todas las vistas internas y eliminar reservas solo con `POST`.
- [x] No enviar los datos de los clientes a la vista pública.
- [x] Leer `SECRET_KEY` y `DEBUG` de variables de entorno.
- [x] Añadir tests con el `TestCase` de Django.
- [ ] Validar las mesas duplicadas también en el **backend** con una restricción única (`fecha + turno + mesa`), no solo en la interfaz.
- [ ] Usar formularios de Django (`ModelForm`) para validar los datos de entrada.
- [ ] Crear un frontend en **React / Next.js** que consuma una API hecha con Django REST Framework.

## 👤 Autor

**Robert Brito** · [GitHub](https://github.com/robertbrito1) · [LinkedIn](https://www.linkedin.com/in/robertbrito/)

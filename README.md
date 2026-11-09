# Control de pólizas

Aplicación Flask para controlar pólizas, ver su estado (Vigente, Por vencer,
Vencida), consultar primas por aseguradora y descargar avisos de renovación en PDF.

## Ejecutar localmente

```bash
uv run app.py
```

Luego abrir <http://localhost:5000>. También puedes usar `iniciar_app.bat`.

## Desplegar en Render

El proyecto incluye `render.yaml` y `requirements.txt` listos para Render.

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Python: 3.12 (definido en `.python-version`)

## Estructura

- `data/` — Excel del maestro y PDFs de pólizas (solo lectura).
- `models/` — acceso a datos y reglas del negocio.
- `services/` — generación de avisos en PDF.
- `controllers/` — rutas de Flask.
- `views/` y `public/static/` — plantillas y estilos.

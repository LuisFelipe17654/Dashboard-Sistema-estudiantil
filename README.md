# Dashboard Sistema Estudiantil

Esta aplicación muestra un dashboard interactivo para el sistema de gestión estudiantil usando los módulos existentes del proyecto.

## Estructura del proyecto

- `app.py`: interfaz gráfica con Streamlit, que reutiliza las funcionalidades de los módulos de negocio.
- `main.py`: menú de consola original.
- `estudiantes.py`: carga, registro, actualización y filtrado de estudiantes.
- `notas.py`: manejo de notas, registro y sincronización con el CSV.
- `promedios.py`: cálculo de promedios y clasificación de estudiantes.
- `utils.py`: utilidades comunes, rutas y parseo de datos.
- `estudiantes.csv`: datos iniciales de estudiantes.
- `notas.txt`: datos iniciales de notas.
- `requirements.txt`: dependencias necesarias para ejecutar la app gráfica.

## Requisitos

- Python 3.8+
- `pandas`
- `matplotlib`
- `streamlit`

## Instalación

Ejecuta en el directorio del proyecto:

```bash
pip install -r requirements.txt
```

## Ejecutar la interfaz gráfica

Desde el directorio del proyecto:

```bash
streamlit run app.py
```

## Uso

- `Estudiantes`: explorar, filtrar, registrar y actualizar alumnos.
- `Notas`: ver notas cargadas, agregar nuevas notas y actualizar notas existentes.
- `Promedios`: revisar promedios por estudiante y ver top/low.
- `Análisis`: ver gráficos de tendencias por carrera, edad y asignatura.

## Notas

La app gráfica reutiliza directamente las funciones de `estudiantes.py`, `notas.py` y `promedios.py`, por lo que mantiene la conexión con el sistema original.

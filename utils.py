"""Utilidades compartidas para el sistema de gestión de estudiantes.

Este módulo define rutas de archivo, el catálogo de carreras y funciones de soporte
para parsear valores numéricos y extraer notas de filas CSV.
"""

# archivos de datos
archivo_estudiantes = "uploads/estudiantes.csv"
archivo_notas = "uploads/notas.txt"

# catálogo de carreras y sus asignaturas asociadas
CARRERAS = {
    'ingenieria de sistemas': ['programacion i', 'estructuras de datos'],
    'administracion': ['contabilidad', 'finanzas'],
    'derecho': ['constitucional', 'civil'],
    'psicologia': ['psicologia general', 'psicologia clinica'],
    'arquitectura': ['dibujo tecnico', 'proyectos']
}


# Funciones para convertir valores numéricos en una notación de coma o punto a float, y para extraer notas de filas de datos con claves como 'nota', 'nota_1', etc., buscando en cualquier fila de datos que pueda contener información relevante para el cálculo de promedios.
def _parse_float(value):
    """Convertir valores numéricos en una notación de coma o punto a float.

    Devuelve None si no se puede convertir.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return float(value)
        except Exception:
            return None
    s = str(value).strip()
    if s == '':
        return None
    s = s.replace(',', '.')
    try:
        return float(s)
    except Exception:
        return None

# Funciones para convertir valores numéricos en una notación de coma o punto a float, y para extraer notas de filas de datos con claves como 'nota', 'nota_1', etc., buscando en cualquier fila de datos que pueda contener información relevante para el cálculo de promedios.
def _extraer_notas_de_fila(fila):
    """Extraer todos los valores de nota de una fila de datos.

    Busca claves como 'nota', 'nota_1', 'nota_2' o 'nota_3'.
    """
    notas = []
    for key, value in fila.items():
        if key is None:
            continue
        lower_key = str(key).lower()
        if lower_key == 'nota' or lower_key.startswith('nota_'):
            parsed = _parse_float(value)
            if parsed is not None:
                notas.append(parsed)
    return notas

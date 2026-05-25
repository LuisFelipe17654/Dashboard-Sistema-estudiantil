"""Cálculo de promedios y clasificación de estudiantes.

Este módulo usa los registros de notas disponibles para calcular promedios
por estudiante y mostrar listados relevantes.
"""

# Se importan los módulos necesarios para cada funcionalidad del sistema
from estudiantes import cargar_estudiantes
from notas import _leer_notas_txt
from utils import _extraer_notas_de_fila


# Funciones para calcular promedios por estudiante, listar estudiantes por promedio y mostrar aprobados/reprobados según los registros de notas disponibles. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
def _promedio_por_estudiante(registros):
    """Calcular el promedio final de cada estudiante a partir de sus registros."""
    promedios = {}
    for registro in registros:
        notas = registro.get('notas', [])
        if not notas:
            continue
        promedio_asignatura = sum(notas) / len(notas)
        id_est = registro.get('id_estudiante')
        if id_est:
            promedios.setdefault(id_est, []).append(promedio_asignatura)
    promedios_finales = {}
    for id_est, valores in promedios.items():
        if valores:
            promedios_finales[id_est] = sum(valores) / len(valores)
    return promedios_finales


# obtener_proemdio_por_estudiante ayuda a calcular el promedio de cada estudiante utilizando los registros de notas disponibles. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
def obtener_promedios_por_estudiante():
    """Devolver un diccionario de promedios por ID de estudiante."""
    registros = _leer_notas_txt()
    if not registros:
        estudiantes_list = cargar_estudiantes()
        registros = []
        for e in estudiantes_list:
            id_est = e.get('id_estudiante') or e.get('matricula')
            notas = _extraer_notas_de_fila(e)
            if id_est and notas:
                registros.append({'id_estudiante': id_est, 'asignatura': e.get('asignatura', ''), 'notas': notas})
    return _promedio_por_estudiante(registros)


# calcular_promedio_por_id ayuda a calcular el promedio de un estudiante específico por su ID utilizando los registros de notas disponibles. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
def calcular_promedio_por_id(id_estudiante):
    """Calcular y devolver el promedio de un estudiante por su ID."""
    promedios = obtener_promedios_por_estudiante()
    return promedios.get(id_estudiante)


# obtener_estados_aprobados_reprobados devuelve dos diccionarios: uno con los estudiantes aprobados (promedio >= 3.0) y otro con los reprobados (promedio < 3.0), utilizando los promedios calculados a partir de los registros de notas disponibles. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
def obtener_estados_aprobados_reprobados():
    """Devolver listas de aprobados y reprobados según promedio."""
    promedios = obtener_promedios_por_estudiante()
    aprobados = {id_est: prom for id_est, prom in promedios.items() if prom >= 3.0}
    reprobados = {id_est: prom for id_est, prom in promedios.items() if prom < 3.0}
    return aprobados, reprobados

# Funciones para calcular promedios por estudiante, listar estudiantes por promedio y mostrar aprobados/reprobados según los registros de notas disponibles. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
def calcular_promedio(id_estudiante):
    """Imprimir el promedio del estudiante identificado por `id_estudiante`."""
    try:
        registros = _leer_notas_txt()
        # Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
        if registros:
            promedios = _promedio_por_estudiante(registros)
            promedio = promedios.get(id_estudiante)
            if promedio is None:
                print("No se encontraron notas para este estudiante.")
                return
            print(f"El promedio del estudiante {id_estudiante} es: {promedio:.2f}")
            return
        estudiantes = cargar_estudiantes()
        registros = []
        # For para extraer notas del CSV de estudiantes para el cálculo si no hay registros en `notas.txt`.
        for e in estudiantes:
            id_est = e.get('id_estudiante') or e.get('matricula')
            notas = _extraer_notas_de_fila(e)
            if id_est and notas:
                registros.append({'id_estudiante': id_est, 'asignatura': e.get('asignatura', ''), 'notas': notas})
        promedios = _promedio_por_estudiante(registros)
        promedio = promedios.get(id_estudiante)
        if promedio is None:
            print("No se encontraron notas para este estudiante.")
            return
        print(f"El promedio del estudiante {id_estudiante} es: {promedio:.2f}")
    except Exception as e:
        print(f"Error al calcular promedio: {e}")


# Funciones para calcular promedios por estudiante, listar estudiantes por promedio y mostrar aprobados/reprobados según los registros de notas disponibles. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
def estudiantes_mayor_promedio():
    """Mostrar los estudiantes ordenados de mayor a menor promedio."""
    try:
        registros = _leer_notas_txt()
        # Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
        if not registros:
            estudiantes = cargar_estudiantes()
            registros = []
            for e in estudiantes:
                id_est = e.get('id_estudiante') or e.get('matricula')
                notas = _extraer_notas_de_fila(e)
                if id_est and notas:
                    registros.append({'id_estudiante': id_est, 'asignatura': e.get('asignatura', ''), 'notas': notas})
        promedios = _promedio_por_estudiante(registros)
        # Si no hay promedios calculados, mostrar un mensaje indicando que no se encontraron notas para calcular promedios.
        if not promedios:
            print("No se encontraron notas para calcular promedios.")
            return
        estudiantes_ordenados = sorted(promedios.items(), key=lambda x: x[1], reverse=True)
        print("Estudiantes ordenados por promedio:")
        for id_est, promedio in estudiantes_ordenados:
            print(f"ID Estudiante: {id_est}, Promedio: {promedio:.2f}")
    except Exception as e:
        print(f"Error al calcular estudiantes con mayor promedio: {e}")


# estudiantes_menor_promedio muestra los estudiantes ordenados de menor a mayor promedio utilizando los registros de notas disponibles. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
def estudiantes_menor_promedio():
    """Mostrar los estudiantes ordenados de menor a mayor promedio."""
    try:
        registros = _leer_notas_txt()
        # Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
        if not registros:
            estudiantes = cargar_estudiantes()
            registros = []
            for e in estudiantes:
                id_est = e.get('id_estudiante') or e.get('matricula')
                notas = _extraer_notas_de_fila(e)
                if id_est and notas:
                    registros.append({'id_estudiante': id_est, 'asignatura': e.get('asignatura', ''), 'notas': notas})
        promedios = _promedio_por_estudiante(registros)
        # Si no hay promedios calculados, mostrar un mensaje indicando que no se encontraron notas para calcular promedios.
        if not promedios:
            print("No se encontraron notas para calcular promedios.")
            return
        estudiantes_ordenados = sorted(promedios.items(), key=lambda x: x[1])
        print("Estudiantes ordenados por menor promedio:")
        for id_est, promedio in estudiantes_ordenados:
            print(f"ID Estudiante: {id_est}, Promedio: {promedio:.2f}")
    except Exception as e:
        print(f"Error al calcular estudiantes con menor promedio: {e}")


# estudiantes_aprobados_reprobados muestra qué estudiantes aprobaron o reprobaron según su promedio utilizando los registros de notas disponibles. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
def estudiantes_aprobados_reprobados():
    """Mostrar qué estudiantes aprobaron o reprobaron según su promedio."""
    try:
        registros = _leer_notas_txt()
        # Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
        if not registros:
            estudiantes = cargar_estudiantes()
            registros = []
            for e in estudiantes:
                id_est = e.get('id_estudiante') or e.get('matricula')
                notas = _extraer_notas_de_fila(e)
                if id_est and notas:
                    registros.append({'id_estudiante': id_est, 'asignatura': e.get('asignatura', ''), 'notas': notas})
        promedios = _promedio_por_estudiante(registros)
        aprobados = [id_est for id_est, promedio in promedios.items() if promedio >= 3.0]
        reprobados = [id_est for id_est, promedio in promedios.items() if promedio < 3.0]
        print("--------------------------------------------------------------------------")
        print("Estudiantes aprobados:")
        # For para mostrar los estudiantes aprobados ordenados por ID y su promedio.
        for id_est in sorted(set(aprobados)):
            print(f"ID Estudiante: {id_est} - Promedio: {promedios[id_est]:.2f}")
        print("--------------------------------------------------------------------------")
        print("\nEstudiantes reprobados:")
        # For para mostrar los estudiantes reprobados ordenados por ID y su promedio.
        for id_est in sorted(set(reprobados)):
            print(f"ID Estudiante: {id_est} - Promedio: {promedios[id_est]:.2f}")
    except Exception as e:
        print(f"Error al calcular estudiantes aprobados/reprobados: {e}")
        print("--------------------------------------------------------------------------")

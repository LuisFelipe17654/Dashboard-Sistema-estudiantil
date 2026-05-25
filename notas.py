"""Módulo de gestión de notas del sistema.

Este módulo registra notas en `notas.txt`, actualiza el CSV de estudiantes y permite leer
los registros existentes para cálculo de promedios.
"""

# Se importan los módulos necesarios para cada funcionalidad del sistema
import csv
from utils import archivo_notas, archivo_estudiantes, _parse_float, _extraer_notas_de_fila
from estudiantes import obtener_carrera_por_id, obtener_asignaturas_por_carrera, estudiante_existe


# Funciones para agregar, actualizar y listar notas, así como leer el archivo de notas y sincronizar con el CSV de estudiantes.
def _obtener_fieldnames_notas():
    """Obtener los nombres de campo válidos para el archivo de notas."""
    try:
        with open(archivo_notas, mode='r', newline='') as f:
            reader = csv.reader(f)
            first = next(reader, None)
            if first is None:
                return ['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
            return [h for h in first]
    except FileNotFoundError:
        return ['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
    except Exception:
        return ['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3']


# Funciones para agregar, actualizar y listar notas, así como leer el archivo de notas y sincronizar con el CSV de estudiantes.
def _leer_notas_txt():
    """Leer el archivo `notas.txt` y devolver registros con notas parseadas."""
    registros = []
    try:
        with open(archivo_notas, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                return []
            for row in reader:
                id_est = row.get('id_estudiante') or row.get('ID_ESTUDIANTE') or row.get('id') or row.get('matricula')
                asignatura = row.get('asignatura') or row.get('ASIGNATURA') or ''
                notas = _extraer_notas_de_fila(row)
                if id_est and notas:
                    registros.append({'id_estudiante': id_est, 'asignatura': asignatura, 'notas': notas})
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error al leer notas: {e}")
    return registros


# Funciones para agregar, actualizar y listar notas, así como leer el archivo de notas y sincronizar con el CSV de estudiantes.
def _guardar_nota_en_csv(id_estudiante, asignatura, notas):
    """Actualizar el registro de notas en el CSV de estudiantes para mantener sincronía."""
    try:
        estudiantes = []
        fieldnames = ['matricula', 'nombre', 'apellido', 'edad', 'id_estudiante', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
        with open(archivo_estudiantes, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            if reader.fieldnames:
                fieldnames = list(dict.fromkeys(reader.fieldnames + fieldnames))
            for row in reader:
                estudiantes.append(row)
        updated = False
        for row in estudiantes:
            if str(row.get('id_estudiante', '')).strip() == str(id_estudiante).strip():
                row['asignatura'] = asignatura
                row['nota_1'] = notas[0] if len(notas) > 0 else ''
                row['nota_2'] = notas[1] if len(notas) > 1 else ''
                row['nota_3'] = notas[2] if len(notas) > 2 else ''
                updated = True
                break
        if not updated:
            estudiantes.append({
                'matricula': '',
                'nombre': '',
                'apellido': '',
                'edad': '',
                'id_estudiante': id_estudiante,
                'carrera': '',
                'asignatura': asignatura,
                'nota_1': notas[0] if len(notas) > 0 else '',
                'nota_2': notas[1] if len(notas) > 1 else '',
                'nota_3': notas[2] if len(notas) > 2 else ''
            })
        with open(archivo_estudiantes, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in estudiantes:
                writer.writerow(row)
    except FileNotFoundError:
        fieldnames = ['matricula', 'nombre', 'apellido', 'edad', 'id_estudiante', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
        with open(archivo_estudiantes, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'matricula': '',
                'nombre': '',
                'apellido': '',
                'edad': '',
                'id_estudiante': id_estudiante,
                'carrera': '',
                'asignatura': asignatura,
                'nota_1': notas[0] if len(notas) > 0 else '',
                'nota_2': notas[1] if len(notas) > 1 else '',
                'nota_3': notas[2] if len(notas) > 2 else ''
            })
    except Exception as e:
        print(f"Error al actualizar estudiantes.csv con nota: {e}")


# Funciones para agregar, actualizar y listar notas, así como leer el archivo de notas y sincronizar con el CSV de estudiantes.
def agregar_nota(id_estudiante, asignatura, nota):
    """Agregar uno o varios valores de nota para un estudiante en el sistema."""
    try:
        notas = []
        if isinstance(nota, (list, tuple)):
            for n in nota:
                parsed = _parse_float(n)
                if parsed is None or parsed < 1.0 or parsed > 5.0:
                    print("Error: Cada nota debe ser un número entre 1.0 y 5.0.")
                    return
                notas.append(parsed)
        else:
            parsed = _parse_float(nota)
            if parsed is None or parsed < 1.0 or parsed > 5.0:
                print("Error: La nota debe ser un número entre 1.0 y 5.0.")
                return
            notas = [parsed]
        if not estudiante_existe(id_estudiante):
            print("Error: El estudiante no existe.")
            return
        carrera = obtener_carrera_por_id(id_estudiante)
        if carrera:
            asignaturas = obtener_asignaturas_por_carrera(carrera)
            if asignaturas and asignatura.strip().lower() not in asignaturas:
                print("Error: La asignatura no corresponde a la carrera del estudiante.")
                print("Asignaturas válidas:")
                for a in asignaturas:
                    print(f" - {a}")
                return
        fieldnames = _obtener_fieldnames_notas()
        row = {
            'id_estudiante': id_estudiante,
            'asignatura': asignatura,
            'nota_1': notas[0] if len(notas) > 0 else '',
            'nota_2': notas[1] if len(notas) > 1 else '',
            'nota_3': notas[2] if len(notas) > 2 else ''
        }
        for fn in fieldnames:
            if fn not in row:
                row[fn] = ''
        write_header = False
        try:
            with open(archivo_notas, mode='r', newline='') as f:
                if f.read(1) == '':
                    write_header = True
        except FileNotFoundError:
            write_header = True
        with open(archivo_notas, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        _guardar_nota_en_csv(id_estudiante, asignatura, notas)
        print("Nota agregada exitosamente.")
    except Exception as e:
        print(f"Error al agregar nota: {e}")


# Funciones para agregar, actualizar y listar notas, así como leer el archivo de notas y sincronizar con el CSV de estudiantes.
def actualizar_nota(id_estudiante, asignatura, nueva_nota):
    """Actualizar una nota existente en el archivo de notas y sincronizar el CSV."""
    try:
        parsed = _parse_float(nueva_nota)
        if parsed is None or parsed < 1.0 or parsed > 5.0:
            print("Error: La nota debe ser un número entre 1.0 y 5.0.")
            return
        updated = False
        notas_para_csv = None
        with open(archivo_notas, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames or []
            registros = []
            for row in reader:
                if str(row.get('id_estudiante') or row.get('ID_ESTUDIANTE') or row.get('id') or row.get('matricula')) == str(id_estudiante) and str(row.get('asignatura') or row.get('ASIGNATURA') or '') == str(asignatura):
                    for key in ['nota_1', 'nota_2', 'nota_3', 'nota']:
                        if key in row:
                            row[key] = parsed
                            updated = True
                            break
                    notas_para_csv = [row.get('nota_1', ''), row.get('nota_2', ''), row.get('nota_3', '')]
                registros.append(row)
        if not updated:
            print("No se encontró la nota indicada para actualizar.")
            return
        with open(archivo_notas, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(registros)
        if notas_para_csv is not None:
            _guardar_nota_en_csv(id_estudiante, asignatura, notas_para_csv)
        print("Nota actualizada exitosamente.")
    except FileNotFoundError:
        print("Error: El archivo de notas no existe.")
    except Exception as e:
        print(f"Error al actualizar nota: {e}")


# Funciones para agregar, actualizar y listar notas, así como leer el archivo de notas y sincronizar con el CSV de estudiantes.
def listar_notas():
    """Mostrar en pantalla todos los registros leídos desde `notas.txt`."""
    registros = _leer_notas_txt()
    if not registros:
        print("No hay registros de notas.")
        return
    print("\nListado de notas:")
    for r in registros:
        print(f"ID: {r.get('id_estudiante')}, Asignatura: {r.get('asignatura')}, Notas: {r.get('notas')}")

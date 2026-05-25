"""Módulo de gestión de notas del sistema.

Este módulo registra notas en `notas.txt`, actualiza el CSV de estudiantes y permite leer
los registros existentes para cálculo de promedios.
"""

# Se importan los módulos necesarios para cada funcionalidad del sistema
import csv
from utils import archivo_notas, archivo_estudiantes, _parse_float, _extraer_notas_de_fila
from estudiantes import obtener_carrera_por_id, obtener_asignaturas_por_carrera, estudiante_existe


# _obtener_fieldnames_notas obtiene los nombres de campo válidos para el archivo de notas, leyendo la primera fila del archivo `notas.txt` si existe. Si el archivo no existe o está vacío, devuelve un conjunto predeterminado de nombres de campo. Esta función es útil para asegurar que al escribir nuevas notas se utilicen los nombres de campo correctos y se mantenga la consistencia en el formato del archivo de notas.
def _obtener_fieldnames_notas(archivo=None):
    """Obtener los nombres de campo válidos para el archivo de notas."""
    try:
        path = archivo if archivo else archivo_notas
        with open(path, mode='r', newline='') as f:
            reader = csv.reader(f)
            first = next(reader, None)
            if first is None:
                return ['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
            return [h for h in first]
    except FileNotFoundError:
        return ['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
    except Exception:
        return ['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3']


# _leer_notas lee el archivo `notas.txt` y devuelve los registros de notas en un formato estructurado. La función utiliza `_leer_notas_txt` para obtener los registros crudos, luego procesa cada registro para extraer las notas individuales (nota_1, nota_2, nota_3) y devuelve una lista de diccionarios con la información del estudiante, asignatura y las notas correspondientes. Si no hay registros de notas o si ocurre algún error durante la lectura, devuelve una lista vacía.
def _leer_notas_txt(archivo=None):
    """Leer el archivo `notas.txt` y devolver registros con notas parseadas."""
    registros = []
    try:
        path = archivo if archivo else archivo_notas
        with open(path, mode='r', newline='') as file:
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


# leer_notas es una función que lee los registros de notas desde el archivo `notas.txt` y devuelve una lista de diccionarios con la información del estudiante, asignatura y las notas correspondientes. La función utiliza `_leer_notas_txt` para obtener los registros crudos, luego procesa cada registro para extraer las notas individuales (nota_1, nota_2, nota_3) y devuelve una lista de diccionarios con la información estructurada. Si no hay registros de notas o si ocurre algún error durante la lectura, devuelve una lista vacía.
def leer_notas(archivo=None):
    """Leer y devolver los registros de notas desde notas.txt o desde la ruta proporcionada."""
    registros = _leer_notas_txt(archivo=archivo)
    salida = []
    for registro in registros:
        notas_valores = registro.get('notas', [])
        salida.append({
            'id_estudiante': registro.get('id_estudiante', ''),
            'asignatura': registro.get('asignatura', ''),
            'nota_1': notas_valores[0] if len(notas_valores) > 0 else None,
            'nota_2': notas_valores[1] if len(notas_valores) > 1 else None,
            'nota_3': notas_valores[2] if len(notas_valores) > 2 else None,
        })
    return salida


# guardar_nota_en_csv es una función que actualiza el registro de notas en el archivo CSV de estudiantes para mantener la sincronía entre los datos de notas y la información del estudiante. La función toma el ID del estudiante, la asignatura y las notas como parámetros, luego carga los estudiantes desde el archivo CSV, busca el estudiante correspondiente por su ID y actualiza los campos de asignatura y notas. Si el estudiante no existe, agrega un nuevo registro con la información proporcionada. Finalmente, escribe nuevamente la lista completa de estudiantes en el archivo CSV. Si ocurre algún error durante este proceso, se captura la excepción y se muestra un mensaje de error.
def _guardar_nota_en_csv(id_estudiante, asignatura, notas, archivo_estudiantes_destino=None):
    """Actualizar el registro de notas en el CSV de estudiantes para mantener sincronía."""
    try:
        estudiantes = []
        fieldnames = ['matricula', 'nombre', 'apellido', 'edad', 'id_estudiante', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
        path = archivo_estudiantes_destino if archivo_estudiantes_destino else archivo_estudiantes
        with open(path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            if reader.fieldnames:
                fieldnames = list(dict.fromkeys(reader.fieldnames + fieldnames))
            for row in reader:
                estudiantes.append(row)
        updated = False
        # Busca el estudiante correspondiente por su ID y actualiza los campos de asignatura y notas. Si el estudiante no existe, agrega un nuevo registro con la información proporcionada. Finalmente, escribe nuevamente la lista completa de estudiantes en el archivo CSV. Si ocurre algún error durante este proceso, se captura la excepción y se muestra un mensaje de error.
        for row in estudiantes:
            if str(row.get('id_estudiante', '')).strip() == str(id_estudiante).strip():
                row['asignatura'] = asignatura
                row['nota_1'] = notas[0] if len(notas) > 0 else ''
                row['nota_2'] = notas[1] if len(notas) > 1 else ''
                row['nota_3'] = notas[2] if len(notas) > 2 else ''
                updated = True
                break
        # Si no se encontró el estudiante para actualizar, agrega un nuevo registro con la información proporcionada. Luego escribe nuevamente la lista completa de estudiantes en el archivo CSV, asegurándose de incluir el encabezado. Si ocurre algún error durante la escritura, se captura la excepción y se muestra un mensaje de error.
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
        # Escribe la lista completa de estudiantes actualizada en el archivo CSV, asegurándose de incluir el encabezado. Si ocurre algún error durante la escritura, se captura la excepción y se muestra un mensaje de error.
        with open(path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in estudiantes:
                writer.writerow(row)
    except FileNotFoundError:
        fieldnames = ['matricula', 'nombre', 'apellido', 'edad', 'id_estudiante', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
        # Si el archivo de estudiantes no existe, crea un nuevo archivo con el registro de la nota proporcionada. Si ocurre algún error durante la creación del archivo, se captura la excepción y se muestra un mensaje de error.
        path = archivo_estudiantes_destino if archivo_estudiantes_destino else archivo_estudiantes
        with open(path, mode='w', newline='') as file:
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
def agregar_nota(id_estudiante, asignatura, nota, archivo_notas_destino=None, archivo_estudiantes_destino=None):
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
        fieldnames = _obtener_fieldnames_notas(archivo=archivo_notas_destino)
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
        path = archivo_notas_destino if archivo_notas_destino else archivo_notas
        try:
            with open(path, mode='r', newline='') as f:
                if f.read(1) == '':
                    write_header = True
        except FileNotFoundError:
            write_header = True
        with open(path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        _guardar_nota_en_csv(id_estudiante, asignatura, notas, archivo_estudiantes_destino=archivo_estudiantes_destino)
        print("Nota agregada exitosamente.")
        return True
    except Exception as e:
        print(f"Error al agregar nota: {e}")
        return False


# Funciones para agregar, actualizar y listar notas, así como leer el archivo de notas y sincronizar con el CSV de estudiantes.
def actualizar_nota(id_estudiante, asignatura, nueva_nota, archivo_notas_destino=None, archivo_estudiantes_destino=None):
    """Actualizar una nota existente en el archivo de notas y sincronizar el CSV."""
    try:
        parsed = _parse_float(nueva_nota)
        if parsed is None or parsed < 1.0 or parsed > 5.0:
            print("Error: La nota debe ser un número entre 1.0 y 5.0.")
            return
        updated = False
        notas_para_csv = None
        path = archivo_notas_destino if archivo_notas_destino else archivo_notas
        with open(path, mode='r', newline='') as file:
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
            return False
        with open(path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(registros)
        if notas_para_csv is not None:
            _guardar_nota_en_csv(id_estudiante, asignatura, notas_para_csv, archivo_estudiantes_destino=archivo_estudiantes_destino)
        print("Nota actualizada exitosamente.")
        return True
    except FileNotFoundError:
        print("Error: El archivo de notas no existe.")
        return False
    except Exception as e:
        print(f"Error al actualizar nota: {e}")
        return False


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


def eliminar_nota(id_estudiante, asignatura, archivo_notas_destino=None, archivo_estudiantes_destino=None):
    """Eliminar una nota por ID de estudiante y asignatura. Devuelve True si se eliminó."""
    try:
        path = archivo_notas_destino if archivo_notas_destino else archivo_notas
        with open(path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames or []
            registros = [row for row in reader]
        nuevo = []
        removed = False
        for row in registros:
            idv = str(row.get('id_estudiante') or row.get('ID_ESTUDIANTE') or row.get('id') or row.get('matricula'))
            asig = str(row.get('asignatura') or row.get('ASIGNATURA') or '')
            if idv == str(id_estudiante) and asig == str(asignatura):
                removed = True
                continue
            nuevo.append(row)
        if not removed:
            print('No se encontró la nota indicada para eliminar.')
            return False
        with open(path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(nuevo)

        # Buscar si quedan notas para ese estudiante/asignatura y actualizar CSV de estudiantes
        encontrados = [r for r in nuevo if (str(r.get('id_estudiante') or r.get('ID_ESTUDIANTE') or r.get('id') or r.get('matricula')) == str(id_estudiante) and str(r.get('asignatura') or r.get('ASIGNATURA') or '') == str(asignatura))]
        if encontrados:
            row = encontrados[-1]
            notas_vals = [_parse_float(row.get('nota_1')), _parse_float(row.get('nota_2')), _parse_float(row.get('nota_3'))]
            _guardar_nota_en_csv(id_estudiante, asignatura, notas_vals, archivo_estudiantes_destino=archivo_estudiantes_destino)
        else:
            # No quedan notas para esa asignatura; limpiar en CSV
            _guardar_nota_en_csv(id_estudiante, '', [], archivo_estudiantes_destino=archivo_estudiantes_destino)
        print('Nota eliminada correctamente.')
        return True
    except FileNotFoundError:
        print('Error: El archivo de notas no existe.')
        return False
    except Exception as e:
        print(f'Error al eliminar nota: {e}')
        return False

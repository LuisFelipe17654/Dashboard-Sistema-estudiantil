"""Módulo de gestión de estudiantes.

Este módulo proporciona funciones para cargar estudiantes desde CSV, registrar
nuevos estudiantes, actualizar datos, buscar por ID y filtrar resultados.
"""

# Importaciones necesarias para manejar archivos CSV, rutas de datos, catálogo de carreras y funciones de soporte para parsear valores numéricos y extraer notas de filas CSV.

import csv
from utils import archivo_estudiantes, CARRERAS, _parse_float, _extraer_notas_de_fila


# _obtener_fieldnames_estudiantes es una función interna que intenta leer el archivo `estudiantes.csv` para determinar los encabezados actuales. Si el archivo no existe o no tiene encabezados, devuelve una lista de encabezados predeterminada que incluye campos comunes como 'matricula', 'nombre', 'apellido', 'edad', 'id_estudiante', 'carrera', 'asignatura' y campos de notas como 'nota_1', 'nota_2' y 'nota_3'. Esta función es útil para asegurar que al registrar o actualizar estudiantes, se mantenga la consistencia en los campos utilizados en el archivo CSV.
def _obtener_fieldnames_estudiantes():
    """Obtener los encabezados actuales del archivo de estudiantes."""
    try:
        with open(archivo_estudiantes, mode='r', newline='') as f:
            reader = csv.reader(f)
            first = next(reader, None)
            if first is None:
                return ['matricula', 'nombre', 'apellido', 'edad', 'id_estudiante', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
            if 'matricula' in [h.lower() for h in first]:
                return [h for h in first]
            return ['matricula', 'nombre', 'apellido', 'edad', 'id_estudiante', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
    except FileNotFoundError:
        return ['matricula', 'nombre', 'apellido', 'edad', 'id_estudiante', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3']
    except Exception:
        return ['matricula', 'nombre', 'apellido', 'edad', 'id_estudiante', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3']

# cargar_estudiantes es una función que lee el archivo `estudiantes.csv` y convierte los campos numéricos apropiadamente. Intenta convertir el campo 'edad' a un número entero o flotante si es posible, y también busca campos de notas como 'nota', 'nota_1', etc., para convertirlos a números flotantes utilizando la función `_parse_float`. Si el archivo no existe, devuelve una lista vacía. Si ocurre algún error durante la lectura o conversión, se captura la excepción y se muestra un mensaje de error, devolviendo también una lista vacía.
def cargar_estudiantes(archivo=None):
    """Leer estudiantes desde un CSV (por defecto `archivo_estudiantes`) y convertir campos numéricos."""
    estudiantes = []
    # Intenta convertir el campo 'edad' a un número entero o flotante si es posible, y también busca campos de notas como 'nota', 'nota_1', etc., para convertirlos a números flotantes utilizando la función `_parse_float`. Si el archivo no existe, devuelve una lista vacía. Si ocurre algún error durante la lectura o conversión, se captura la excepción y se muestra un mensaje de error, devolviendo también una lista vacía.
    try:
        path = archivo if archivo else archivo_estudiantes
        with open(path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            # Si el archivo no tiene encabezados, se devuelve una lista vacía ya que no se pueden mapear los campos correctamente.
            if reader.fieldnames is None:
                return estudiantes
            for row in reader:
                r = {k: v for k, v in row.items()}
                if 'edad' in r and r['edad'] not in (None, ''):
                    try:
                        r['edad'] = int(r['edad'])
                    except Exception:
                        try:
                            r['edad'] = float(r['edad'])
                        except Exception:
                            pass
                for key, value in list(r.items()):
                    if key is None:
                        continue
                    lower_key = key.lower()
                    if lower_key == 'edad':
                        if value not in (None, ''):
                            try:
                                r[key] = int(value)
                            except Exception:
                                try:
                                    r[key] = float(value)
                                except Exception:
                                    pass
                    # Intenta convertir campos de notas como 'nota', 'nota_1', etc., a números flotantes utilizando la función `_parse_float`. Si el valor no se puede convertir, se deja como está.
                    elif lower_key == 'nota' or lower_key.startswith('nota_'):
                        if value not in (None, ''):
                            parsed = _parse_float(value)
                            if parsed is not None:
                                r[key] = parsed
                estudiantes.append(r)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error al cargar estudiantes: {e}")
    return estudiantes

# obtener_ultima_matricula devuelve el valor numérico de la última matrícula registrada en el archivo `estudiantes.csv`. Si no hay estudiantes registrados, devuelve un valor inicial de 2026000. La función lee todos los estudiantes, extrae el campo 'matricula', intenta convertirlo a un número entero y mantiene un seguimiento del valor máximo encontrado. Si ocurre algún error durante la lectura o conversión, se captura la excepción y se muestra un mensaje de error, devolviendo el valor inicial de 2026000.
def obtener_ultima_matricula():
    """Devolver el valor numérico de la última matrícula registrada."""
    estudiantes = cargar_estudiantes()
    if not estudiantes:
        return 2026000
    max_val = 0
    for e in estudiantes:
        m = e.get('matricula')
        try:
            n = int(str(m))
            if n > max_val:
                max_val = n
        except Exception:
            continue
    return max_val

# obtener_ultimo_id_estudiante devuelve una tupla con el prefijo y el número del último ID de estudiante registrado en el archivo `estudiantes.csv`. El prefijo se asume que es 'EST' y el número es la parte numérica que sigue al prefijo. Si no hay estudiantes registrados, devuelve el prefijo 'EST' y un número inicial de 0. La función lee todos los estudiantes, extrae el campo 'id_estudiante', verifica si comienza con el prefijo esperado, intenta convertir la parte numérica a un entero y mantiene un seguimiento del valor máximo encontrado. Si ocurre algún error durante la lectura o conversión, se captura la excepción y se muestra un mensaje de error, devolviendo el prefijo 'EST' y el número inicial de 0.
def obtener_ultimo_id_estudiante():
    """Devolver el prefijo y el número del último ID de estudiante."""
    estudiantes = cargar_estudiantes()
    max_num = 0
    prefix = 'EST'
    for e in estudiantes:
        idv = e.get('id_estudiante') or ''
        if isinstance(idv, str) and idv.upper().startswith(prefix):
            suf = idv[len(prefix):]
            try:
                n = int(suf)
                if n > max_num:
                    max_num = n
            except Exception:
                continue
    return (prefix, max_num)

# obtener_estudiante_por_id busca un estudiante por su ID y devuelve el registro completo. La función lee todos los estudiantes, compara el campo 'id_estudiante' con el ID proporcionado (ignorando mayúsculas y espacios) y devuelve el primer registro que coincida. Si no se encuentra ningún estudiante con el ID proporcionado, devuelve None. Si ocurre algún error durante la lectura o comparación, se captura la excepción y se muestra un mensaje de error, devolviendo None.
def obtener_estudiante_por_id(id_estudiante):
    """Buscar un estudiante por su ID y devolver el registro completo."""
    estudiantes = cargar_estudiantes()
    target = str(id_estudiante).strip().upper()
    for e in estudiantes:
        if str(e.get('id_estudiante', '')).strip().upper() == target:
            return e
    return None

# obtener_carrera_por_id devuelve la carrera del estudiante identificado por su ID. La función utiliza la función `obtener_estudiante_por_id` para obtener el registro completo del estudiante y luego extrae el campo 'carrera'. Si el estudiante no se encuentra o no tiene un campo de carrera válido, devuelve None. Si ocurre algún error durante la búsqueda o extracción, se captura la excepción y se muestra un mensaje de error, devolviendo None.
def obtener_carrera_por_id(id_estudiante):
    """Devolver la carrera del estudiante identificado por su ID."""
    estudiante = obtener_estudiante_por_id(id_estudiante)
    if estudiante and 'carrera' in estudiante:
        return str(estudiante['carrera']).strip().lower()
    return None

# obtener_asignaturas_por_carrera devuelve la lista de asignaturas válidas para la carrera proporcionada. La función toma el nombre de la carrera, lo normaliza (eliminando espacios y convirtiendo a minúsculas) y busca en el catálogo de carreras definido en `CARRERAS`. Si la carrera se encuentra en el catálogo, devuelve la lista de asignaturas asociadas. Si la carrera no se encuentra o si el valor proporcionado es None, devuelve una lista vacía. Si ocurre algún error durante la búsqueda, se captura la excepción y se muestra un mensaje de error, devolviendo una lista vacía.
def obtener_asignaturas_por_carrera(carrera):
    """Devolver la lista de asignaturas válidas para la carrera proporcionada."""
    if carrera is None:
        return []
    return CARRERAS.get(carrera.strip().lower(), [])


# registrar_estudiante agrega un estudiante nuevo al archivo `estudiantes.csv`. La función toma los datos del estudiante como parámetros, construye un diccionario con los campos correspondientes y escribe una nueva fila en el archivo CSV. Si el archivo no existe o está vacío, se escribe un encabezado antes de agregar la fila. Si ocurre algún error durante la escritura, se captura la excepción y se muestra un mensaje de error, devolviendo False. Si el registro se realiza exitosamente, devuelve True.
def registrar_estudiante(matricula, nombre, apellido, edad, id_estudiante, carrera, archivo=None):
    """Agregar un estudiante nuevo al archivo `estudiantes.csv` o a la ruta proporcionada."""
    try:
        path = archivo if archivo else archivo_estudiantes
        fieldnames = _obtener_fieldnames_estudiantes()
        row = {
            'matricula': matricula,
            'nombre': nombre,
            'apellido': apellido,
            'edad': edad,
            'id_estudiante': id_estudiante,
            'carrera': carrera
        }
        # Asegura que todos los campos necesarios estén presentes en el diccionario de la fila, incluso si algunos valores son None o están vacíos, para evitar problemas al escribir en el CSV.
        for fn in fieldnames:
            if fn not in row:
                row[fn] = ''
        write_header = False
        try:
            with open(path, mode='r', newline='') as f:
                if f.read(1) == '':
                    write_header = True
        except FileNotFoundError:
            write_header = True

        # Escribe la nueva fila en el archivo CSV de destino
        with open(path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        print("Estudiante registrado exitosamente.")
        return True
    except Exception as e:
        print(f"Error al registrar estudiante: {e}")
        return False


#registrar_estudiante_auto es una función que registra un estudiante generando automáticamente la matrícula e ID. La función toma los datos del estudiante como parámetros, valida la carrera proporcionada, obtiene la última matrícula y el último ID de estudiante para generar nuevos valores únicos, y luego llama a `registrar_estudiante` para agregar el nuevo estudiante al archivo CSV. Si la carrera no es válida o si ocurre algún error durante el proceso, se captura la excepción y se muestra un mensaje de error, devolviendo None para ambos valores. Si el registro se realiza exitosamente, devuelve la nueva matrícula y el nuevo ID generados.
def registrar_estudiante_auto(nombre, apellido, edad, carrera, archivo=None):
    """Registrar un estudiante generando matrícula e ID automáticamente."""
    try:
        carrera_norm = carrera.strip().lower()
        # Valida la carrera proporcionada contra el catálogo de carreras definido en `CARRERAS`. Si la carrera no es válida, muestra un mensaje de error y devuelve None para ambos valores.
        if carrera_norm not in CARRERAS:
            print("Error: Carrera no reconocida. Registre una carrera válida de la lista.")
            return None, None
        last = obtener_ultima_matricula()
        nueva_matricula = str(int(last) + 1)
        prefix, last_id_num = obtener_ultimo_id_estudiante()
        nuevo_id_num = last_id_num + 1
        nuevo_id = f"{prefix}{nuevo_id_num:03d}"
        registrar_estudiante(nueva_matricula, nombre, apellido, edad, nuevo_id, carrera_norm, archivo=archivo)
        print(f"Estudiante creado. Matrícula: {nueva_matricula}, ID: {nuevo_id}")
        return nueva_matricula, nuevo_id
    except Exception as e:
        print(f"Error al crear estudiante automáticamente: {e}")
        return None, None


# listar_estudiantes muestra en pantalla todos los estudiantes registrados en el archivo `estudiantes.csv`. La función carga los estudiantes utilizando `cargar_estudiantes`, verifica si hay estudiantes registrados y luego imprime los detalles de cada estudiante, incluyendo matrícula, ID, nombre completo, carrera, asignatura y notas. Si no hay estudiantes registrados, muestra un mensaje indicando que no hay estudiantes. Si ocurre algún error durante la carga o impresión de los estudiantes, se captura la excepción y se muestra un mensaje de error.
def listar_estudiantes():
    """Mostrar en pantalla todos los estudiantes registrados."""
    estudiantes = cargar_estudiantes()
    if not estudiantes:
        print("No hay estudiantes registrados.")
        return
    print("\nListado de estudiantes:")
    for e in estudiantes:
        notas = _extraer_notas_de_fila(e)
        nota_text = ', '.join(str(n) for n in notas) if notas else 'Sin notas'
        print(f"Matricula: {e.get('matricula')}, ID: {e.get('id_estudiante')}, Nombre: {e.get('nombre')} {e.get('apellido')}, Carrera: {e.get('carrera')}, Asignatura: {e.get('asignatura')}, Notas: {nota_text}")


# estudiante_existe verifica si existe un estudiante por su matrícula o ID. La función carga los estudiantes utilizando `cargar_estudiantes`, normaliza el valor de búsqueda y compara tanto la matrícula como el ID de cada estudiante con el valor proporcionado. Si encuentra una coincidencia, devuelve True. Si no se encuentra ningún estudiante con la matrícula o ID proporcionados, devuelve False. Si ocurre algún error durante la carga o comparación, se captura la excepción y se muestra un mensaje de error, devolviendo False.
def estudiante_existe(matricula):
    """Verificar si existe un estudiante por matrícula o ID."""
    try:
        estudiantes = cargar_estudiantes()
        target = str(matricula).strip()
        for e in estudiantes:
            if str(e.get('matricula', '')).strip() == target or str(e.get('id_estudiante', '')).strip() == target:
                return True
    except Exception as e:
        print(f"Error al verificar estudiante: {e}")
        return False
    return False


# actualizar_estudiante actualiza los datos de un estudiante existente identificado por su matrícula. La función carga los estudiantes utilizando `cargar_estudiantes`, busca el estudiante con la matrícula proporcionada y actualiza los campos que se le pasen como parámetros (nombre, apellido, edad, ID y carrera). Después de actualizar el estudiante, escribe nuevamente la lista completa de estudiantes en el archivo CSV. Si no se encuentra ningún estudiante con la matrícula proporcionada, muestra un mensaje indicando que no se encontró el estudiante para actualizar. Si ocurre algún error durante la carga, actualización o escritura de los estudiantes, se captura la excepción y se muestra un mensaje de error, devolviendo False. Si la actualización se realiza exitosamente, devuelve True.
def actualizar_estudiante(matricula, nombre=None, apellido=None, edad=None, id_estudiante=None, carrera=None, archivo=None):
    """Actualizar un estudiante existente identificado por matrícula."""
    try:
        estudiantes = cargar_estudiantes(archivo=archivo)
        if not estudiantes:
            print("No hay estudiantes registrados.")
            return
        updated = False
        # Busca el estudiante con la matrícula proporcionada y actualiza los campos que se le pasen como parámetros (nombre, apellido, edad, ID y carrera). Después de actualizar el estudiante, escribe nuevamente la lista completa de estudiantes en el archivo CSV. Si no se encuentra ningún estudiante con la matrícula proporcionada, muestra un mensaje indicando que no se encontró el estudiante para actualizar. Si ocurre algún error durante la carga, actualización o escritura de los estudiantes, se captura la excepción y se muestra un mensaje de error, devolviendo False. Si la actualización se realiza exitosamente, devuelve True.
        for e in estudiantes:
            if str(e.get('matricula', '')) == str(matricula):
                if nombre:
                    e['nombre'] = nombre
                if apellido:
                    e['apellido'] = apellido
                if edad is not None and edad != '':
                    try:
                        e['edad'] = int(edad)
                    except Exception:
                        try:
                            e['edad'] = float(edad)
                        except Exception:
                            e['edad'] = edad
                if id_estudiante:
                    e['id_estudiante'] = id_estudiante
                if carrera:
                    e['carrera'] = carrera
                updated = True
        if not updated:
            print("Estudiante no encontrado para actualizar.")
            return False
        fieldnames = _obtener_fieldnames_estudiantes()
        path = archivo if archivo else archivo_estudiantes
        # Escribe la lista completa de estudiantes actualizada en el archivo CSV de destino
        with open(path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for e in estudiantes:
                row = {fn: e.get(fn, '') for fn in fieldnames}
                writer.writerow(row)
        print("Estudiante actualizado exitosamente.")
        return True
    except Exception as e:
        print(f"Error al actualizar estudiante: {e}")
        return False


# filtrar_estudiantes_por_carrera imprime en pantalla los estudiantes que pertenecen a la carrera solicitada. La función carga los estudiantes utilizando `cargar_estudiantes`, filtra aquellos cuyo campo 'carrera' coincide con la carrera proporcionada (ignorando mayúsculas y espacios) y luego imprime los detalles de los estudiantes filtrados. Si no se encuentran estudiantes para la carrera solicitada, muestra un mensaje indicando que no se encontraron estudiantes para esa carrera. Si ocurre algún error durante la carga o filtrado de los estudiantes, se captura la excepción y se muestra un mensaje de error.
def filtrar_estudiantes_por_carrera(carrera):
    """Imprimir los estudiantes que pertenecen a la carrera solicitada."""
    try:
        estudiantes_filtrados = []
        estudiantes = cargar_estudiantes()
        for e in estudiantes:
            if 'carrera' in e and isinstance(e['carrera'], str) and e['carrera'].lower() == carrera.lower():
                estudiantes_filtrados.append(e)
        if not estudiantes_filtrados:
            print("No se encontraron estudiantes para esta carrera.")
            return
        print(f"Estudiantes en la carrera {carrera}:")
        for estudiante in estudiantes_filtrados:
            print(estudiante)
    except Exception as e:
        print(f"Error al filtrar estudiantes: {e}")


def eliminar_estudiante(identificador, archivo=None):
    """Eliminar un estudiante por matrícula o ID. Devuelve True si se eliminó."""
    try:
        estudiantes = cargar_estudiantes(archivo=archivo)
        if not estudiantes:
            print("No hay estudiantes registrados.")
            return False
        nuevo = []
        removed = False
        for e in estudiantes:
            if str(e.get('matricula', '')).strip() == str(identificador).strip() or str(e.get('id_estudiante', '')).strip() == str(identificador).strip():
                removed = True
                continue
            nuevo.append(e)
        if not removed:
            print('No se encontró el estudiante a eliminar.')
            return False
        fieldnames = _obtener_fieldnames_estudiantes()
        path = archivo if archivo else archivo_estudiantes
        with open(path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for e in nuevo:
                row = {fn: e.get(fn, '') for fn in fieldnames}
                writer.writerow(row)
        print('Estudiante eliminado correctamente.')
        return True
    except Exception as e:
        print(f'Error al eliminar estudiante: {e}')
        return False

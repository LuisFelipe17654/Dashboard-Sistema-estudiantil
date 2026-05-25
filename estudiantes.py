"""Módulo de gestión de estudiantes.

Este módulo proporciona funciones para cargar estudiantes desde CSV, registrar
nuevos estudiantes, actualizar datos, buscar por ID y filtrar resultados.
"""


import csv
from utils import archivo_estudiantes, CARRERAS, _parse_float, _extraer_notas_de_fila


# Funciones para manejar estudiantes: cargar, registrar, actualizar, buscar y filtrar por carrera.
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

# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
def cargar_estudiantes():
    """Leer estudiantes de `estudiantes.csv` y convertir los campos numéricos apropiadamente."""
    estudiantes = []
    try:
        with open(archivo_estudiantes, mode='r', newline='') as file:
            reader = csv.DictReader(file)
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

# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
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

# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
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

# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
def obtener_estudiante_por_id(id_estudiante):
    """Buscar un estudiante por su ID y devolver el registro completo."""
    estudiantes = cargar_estudiantes()
    target = str(id_estudiante).strip().upper()
    for e in estudiantes:
        if str(e.get('id_estudiante', '')).strip().upper() == target:
            return e
    return None

# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
def obtener_carrera_por_id(id_estudiante):
    """Devolver la carrera del estudiante identificado por su ID."""
    estudiante = obtener_estudiante_por_id(id_estudiante)
    if estudiante and 'carrera' in estudiante:
        return str(estudiante['carrera']).strip().lower()
    return None

# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
def obtener_asignaturas_por_carrera(carrera):
    """Devolver la lista de asignaturas válidas para la carrera proporcionada."""
    if carrera is None:
        return []
    return CARRERAS.get(carrera.strip().lower(), [])


# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
def registrar_estudiante(matricula, nombre, apellido, edad, id_estudiante, carrera):
    """Agregar un estudiante nuevo al archivo `estudiantes.csv`."""
    try:
        fieldnames = _obtener_fieldnames_estudiantes()
        row = {
            'matricula': matricula,
            'nombre': nombre,
            'apellido': apellido,
            'edad': edad,
            'id_estudiante': id_estudiante,
            'carrera': carrera
        }
        for fn in fieldnames:
            if fn not in row:
                row[fn] = ''
        write_header = False
        try:
            with open(archivo_estudiantes, mode='r', newline='') as f:
                if f.read(1) == '':
                    write_header = True
        except FileNotFoundError:
            write_header = True

        with open(archivo_estudiantes, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        print("Estudiante registrado exitosamente.")
    except Exception as e:
        print(f"Error al registrar estudiante: {e}")


# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
def registrar_estudiante_auto(nombre, apellido, edad, carrera):
    """Registrar un estudiante generando matrícula e ID automáticamente."""
    try:
        carrera_norm = carrera.strip().lower()
        if carrera_norm not in CARRERAS:
            print("Error: Carrera no reconocida. Registre una carrera válida de la lista.")
            return None, None
        last = obtener_ultima_matricula()
        nueva_matricula = str(int(last) + 1)
        prefix, last_id_num = obtener_ultimo_id_estudiante()
        nuevo_id_num = last_id_num + 1
        nuevo_id = f"{prefix}{nuevo_id_num:03d}"
        registrar_estudiante(nueva_matricula, nombre, apellido, edad, nuevo_id, carrera_norm)
        print(f"Estudiante creado. Matrícula: {nueva_matricula}, ID: {nuevo_id}")
        return nueva_matricula, nuevo_id
    except Exception as e:
        print(f"Error al crear estudiante automáticamente: {e}")
        return None, None


# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
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


# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
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


# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
def actualizar_estudiante(matricula, nombre=None, apellido=None, edad=None, id_estudiante=None, carrera=None):
    """Actualizar un estudiante existente identificado por matrícula."""
    try:
        estudiantes = cargar_estudiantes()
        if not estudiantes:
            print("No hay estudiantes registrados.")
            return
        updated = False
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
            return
        fieldnames = _obtener_fieldnames_estudiantes()
        with open(archivo_estudiantes, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for e in estudiantes:
                row = {fn: e.get(fn, '') for fn in fieldnames}
                writer.writerow(row)
        print("Estudiante actualizado exitosamente.")
    except Exception as e:
        print(f"Error al actualizar estudiante: {e}")


# Funciones para cargar estudiantes desde CSV, registrar nuevos estudiantes, actualizar datos, buscar por ID y filtrar por carrera.
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

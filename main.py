"""Punto de entrada del sistema de gestión de estudiantes.

Este módulo ofrece un menú principal y submenús para:
- ver y registrar estudiantes
- agregar y actualizar notas
- calcular promedios y listar resultados
"""

# Se importan los módulos necesarios para cada funcionalidad del sistema
from utils import CARRERAS
import estudiantes
import notas
import promedios

# El menú principal y los submenús se definen en la función `menu()`, que se ejecuta al iniciar el programa.
def menu():
    """Mostrar el menú principal y delegar acciones a los módulos correspondientes."""
    while True:
        print("\n----- Sistema de Gestión: Menú Principal -----")
        print("1. Estudiantes")
        print("2. Notas")
        print("3. Promedios")
        print("0. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            while True:
                print("\n--- Estudiantes ---")
                print("1. Datos de estudiantes actuales")
                print("2. Registrar estudiante")
                print("3. Actualizar estudiante")
                print("4. Filtrar estudiantes por carrera")
                print("0. Volver")
                opt_e = input("Seleccione: ")
                if opt_e == '1':
                    estudiantes.listar_estudiantes()
                elif opt_e == '2':
                    print("Listado de carreras disponibles (escriba exactamente una):")
                    for c in CARRERAS.keys():
                        print(f" - {c}")
                    nombre = input("Nombre: ")
                    apellido = input("Apellido: ")
                    edad = input("Edad: ")
                    carrera = input("Carrera: ")
                    carrera_norm = carrera.strip().lower()
                    if carrera_norm not in CARRERAS:
                        print("Carrera no reconocida. Use una de las opciones listadas (en minúsculas).")
                        continue
                    nuevo_mat, nuevo_id = estudiantes.registrar_estudiante_auto(nombre, apellido, edad, carrera_norm)
                    if nuevo_id:
                        asignaturas = estudiantes.obtener_asignaturas_por_carrera(carrera_norm)
                        if asignaturas:
                            print("Asignaturas disponibles para esta carrera:")
                            for a in asignaturas:
                                print(f" - {a}")
                            agregar_ahora = input("¿Desea agregar una nota ahora para este estudiante? (s/n): ").strip().lower()
                            if agregar_ahora == 's':
                                asignatura = input("Asignatura: ").strip().lower()
                                if asignatura not in asignaturas:
                                    print("Asignatura no válida para esta carrera. Use una de las opciones listadas.")
                                else:
                                    nota1 = input("Nota 1 (1.0 - 5.0): ")
                                    nota2 = input("Nota 2 (1.0 - 5.0, opcional): ")
                                    nota3 = input("Nota 3 (1.0 - 5.0, opcional): ")
                                    notas_lista = [nota for nota in [nota1, nota2, nota3] if nota.strip() != '']
                                    notas.agregar_nota(nuevo_id, asignatura, notas_lista)
                elif opt_e == '3':
                    matricula = input("Matrícula del estudiante a actualizar: ")
                    nombre = input("Nuevo nombre (dejar en blanco para no cambiar): ")
                    apellido = input("Nuevo apellido (dejar en blanco para no cambiar): ")
                    edad = input("Nueva edad (dejar en blanco para no cambiar): ")
                    id_estudiante = input("Nuevo ID Estudiante (dejar en blanco para no cambiar): ")
                    carrera = input("Nueva carrera (dejar en blanco para no cambiar): ")
                    estudiantes.actualizar_estudiante(matricula, nombre, apellido, edad, id_estudiante, carrera)
                elif opt_e == '4':
                    carrera = input("Carrera: ")
                    estudiantes.filtrar_estudiantes_por_carrera(carrera)
                elif opt_e == '0':
                    break
                else:
                    print("Opción no válida.")

        elif opcion == '2':
            while True:
                print("\n--- Notas ---")
                print("1. Agregar nota")
                print("2. Actualizar nota")
                print("3. Ver notas")
                print("0. Volver")
                opt_n = input("Seleccione: ")
                if opt_n == '1':
                    id_estudiante = input("ID Estudiante: ")
                    carrera = estudiantes.obtener_carrera_por_id(id_estudiante)
                    if carrera:
                        asignaturas = estudiantes.obtener_asignaturas_por_carrera(carrera)
                        if asignaturas:
                            print("Asignaturas disponibles para este estudiante:")
                            for a in asignaturas:
                                print(f" - {a}")
                    asignatura = input("Asignatura: ").strip().lower()
                    nota1 = input("Nota 1 (1.0 - 5.0): ")
                    nota2 = input("Nota 2 (1.0 - 5.0, opcional): ")
                    nota3 = input("Nota 3 (1.0 - 5.0, opcional): ")
                    notas_lista = [nota for nota in [nota1, nota2, nota3] if nota.strip() != '']
                    notas.agregar_nota(id_estudiante, asignatura, notas_lista)
                elif opt_n == '2':
                    id_estudiante = input("ID Estudiante: ")
                    carrera = estudiantes.obtener_carrera_por_id(id_estudiante)
                    if carrera:
                        asignaturas = estudiantes.obtener_asignaturas_por_carrera(carrera)
                        if asignaturas:
                            print("Asignaturas disponibles para este estudiante:")
                            for a in asignaturas:
                                print(f" - {a}")
                    asignatura = input("Asignatura: ").strip().lower()
                    nueva_nota = input("Nueva nota (1.0 - 5.0): ")
                    notas.actualizar_nota(id_estudiante, asignatura, nueva_nota)
                elif opt_n == '3':
                    notas.listar_notas()
                elif opt_n == '0':
                    break
                else:
                    print("Opción no válida.")

        elif opcion == '3':
            while True:
                print("\n--- Promedios ---")
                print("1. Calcular promedio (por ID)")
                print("2. Estudiantes con mayor promedio")
                print("3. Estudiantes con menor promedio")
                print("4. Estudiantes aprobados/reprobados")
                print("0. Volver")
                opt_p = input("Seleccione: ")
                if opt_p == '1':
                    id_estudiante = input("ID Estudiante: ")
                    promedios.calcular_promedio(id_estudiante)
                elif opt_p == '2':
                    promedios.estudiantes_mayor_promedio()
                elif opt_p == '3':
                    promedios.estudiantes_menor_promedio()
                elif opt_p == '4':
                    promedios.estudiantes_aprobados_reprobados()
                elif opt_p == '0':
                    break
                else:
                    print("Opción no válida.")

        elif opcion == '0':
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

# El programa se inicia ejecutando la función `menu()`, que muestra el menú principal y permite al usuario navegar entre las diferentes funcionalidades del sistema.
if __name__ == "__main__":
    menu()

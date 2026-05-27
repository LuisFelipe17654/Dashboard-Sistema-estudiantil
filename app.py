"""Dashboard Estudiantil con soporte para subir archivos, borrar registros y paletas de color."""

# Libreria os para manejo de rutas de archivos y tiempo
import os
import time

# Librerias para manejo de datos y visualización
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

#  Importaciones de los módulos del sistema para acceder a las funcionalidades de gestión de estudiantes, notas y promedios.
import estudiantes
import notas
import promedios
from utils import archivo_estudiantes, archivo_notas


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

EXPECTED_STUDENT_COLUMNS = [
    'matricula', 'nombre', 'apellido', 'edad', 'id_estudiante', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3'
]



"""
Este módulo se encarga de calcular promedios por estudiante, listar estudiantes por promedio y mostrar aprobados/reprobados según los registros de notas disponibles. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
Utiliza los registros de notas disponibles para calcular promedios por estudiante y mostrar listados relevantes. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
"""
# normalizar los datos de estudiantes para asegurar que todas las columnas esperadas estén presentes, convertir tipos de datos y calcular promedios cuando sea posible, facilitando su uso en el dashboard y otras partes del sistema.
def normalize_students(df: pd.DataFrame) -> pd.DataFrame:
    for col in EXPECTED_STUDENT_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    df['edad'] = pd.to_numeric(df['edad'], errors='coerce').astype('Int64')
    for col in ['nota_1', 'nota_2', 'nota_3']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['promedio'] = df[['nota_1', 'nota_2', 'nota_3']].mean(axis=1, skipna=True)
    df['carrera'] = df['carrera'].fillna('desconocida')
    df['asignatura'] = df['asignatura'].fillna('sin asignatura')
    df['id_estudiante'] = df['id_estudiante'].fillna('').astype(str)
    return df


@st.cache_data
def load_students(archivo=None) -> pd.DataFrame:
    estudiantes_list = estudiantes.cargar_estudiantes(archivo=archivo)
    if not estudiantes_list:
        return pd.DataFrame(columns=EXPECTED_STUDENT_COLUMNS + ['promedio'])
    df = pd.DataFrame(estudiantes_list)
    return normalize_students(df)


# st.cache_data - load_notes para almacenar en caché los datos de notas, evitando recargas innecesarias y mejorando el rendimiento del dashboard al acceder a los datos desde los módulos del sistema.
@st.cache_data
def load_notes(archivo=None) -> pd.DataFrame:
    notas_list = notas.leer_notas(archivo=archivo)
    if not notas_list:
        df = pd.DataFrame(columns=['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3'])
    else:
        df = pd.DataFrame(notas_list)
    for col in ['nota_1', 'nota_2', 'nota_3']:
        if col not in df.columns:
            df[col] = pd.NA
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['promedio'] = df[['nota_1', 'nota_2', 'nota_3']].mean(axis=1, skipna=True)
    df['asignatura'] = df['asignatura'].fillna('sin asignatura')
    df['id_estudiante'] = df['id_estudiante'].fillna('').astype(str)
    return df


# career_assignment_filters para aplicar filtros dinámicos por carrera y asignatura en el dashboard, permitiendo a los usuarios explorar los datos de estudiantes según sus intereses específicos.
def career_assignment_filters(df: pd.DataFrame):
    carreras = sorted(df['carrera'].dropna().unique())
    opciones_carrera = st.sidebar.multiselect('Filtrar por carrera', carreras, default=carreras)

    asignaturas = sorted(df.loc[df['carrera'].isin(opciones_carrera), 'asignatura'].dropna().unique())
    opciones_asignatura = st.sidebar.multiselect('Filtrar por asignatura', asignaturas, default=asignaturas)

    df_filtrado = df.loc[df['carrera'].isin(opciones_carrera) & df['asignatura'].isin(opciones_asignatura)]
    return df_filtrado


# plot_grade_distribution para crear un histograma de la distribución de notas, proporcionando una visualización clara de cómo se distribuyen las calificaciones entre los estudiantes, lo que puede ayudar a identificar tendencias o áreas de mejora.
def plot_grade_distribution(df: pd.DataFrame, title: str):
    grades = df[['nota_1', 'nota_2', 'nota_3']].melt(value_name='nota')['nota'].dropna()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(grades, bins=[1, 2, 3, 4, 5, 6], edgecolor='black', color=plt.cm.viridis(0.6))
    ax.set_title(title)
    ax.set_xlabel('Nota')
    ax.set_ylabel('Cantidad de valores')
    ax.set_xticks([1, 2, 3, 4, 5])
    st.pyplot(fig)


# plot_bar_average para crear un gráfico de barras que muestra el promedio por carrera o asignatura, facilitando la comparación visual de los promedios entre diferentes grupos y ayudando a identificar cuáles tienen mejores o peores rendimientos.
def plot_bar_average(df: pd.DataFrame, group_by: str, label: str, title: str):
    if df.empty:
        st.write('No hay datos suficientes para graficar.')
        return
    summary = df.groupby(group_by)['promedio'].mean().sort_values(ascending=False)
    if summary.empty:
        st.write('No hay datos suficientes para graficar.')
        return
    fig, ax = plt.subplots(figsize=(8, 4))
    cmap = plt.cm.get_cmap('tab20')
    colors = [cmap(i % cmap.N) for i in range(len(summary))]
    summary.plot(kind='bar', color=colors, ax=ax)
    ax.set_title(title)
    ax.set_ylabel('Promedio')
    ax.set_xlabel(label)
    ax.set_ylim(0, 5)
    st.pyplot(fig)


def render_students_page(df_students: pd.DataFrame, student_file_path: str):
    st.header('Estudiantes')
    st.markdown('Explora la lista de estudiantes y filtra por carrera o asignatura.')
    # Inicializar session_state para limpiar formularios
    if 'reg_nombre' not in st.session_state:
        st.session_state.reg_nombre = ''
    if 'reg_apellido' not in st.session_state:
        st.session_state.reg_apellido = ''
    if 'reg_edad' not in st.session_state:
        st.session_state.reg_edad = ''
    if 'upd_matricula' not in st.session_state:
        st.session_state.upd_matricula = ''
    if 'upd_nombre' not in st.session_state:
        st.session_state.upd_nombre = ''
    if 'upd_apellido' not in st.session_state:
        st.session_state.upd_apellido = ''
    if 'upd_edad' not in st.session_state:
        st.session_state.upd_edad = ''
    if 'upd_id' not in st.session_state:
        st.session_state.upd_id = ''
    if 'del_id' not in st.session_state:
        st.session_state.del_id = ''
    # Verificar si hay datos
    if df_students.empty:
        st.warning('No hay datos de estudiantes. Por favor, sube un archivo CSV de estudiantes en la sección "Cargar datos" de la barra lateral para comenzar.')
        return

    # Aplicar filtros dinámicos por carrera y asignatura en el dashboard, permitiendo a los usuarios explorar los datos de estudiantes según sus intereses específicos.
    df_filtrado = career_assignment_filters(df_students)
    st.subheader('Tabla de estudiantes')
    st.dataframe(df_filtrado[['matricula', 'id_estudiante', 'nombre', 'apellido', 'edad', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3', 'promedio']])

    # Mostrar métricas clave sobre los estudiantes, como el total de estudiantes, registros con notas y carreras disponibles, proporcionando una visión rápida del estado general de los datos.
    col1, col2, col3 = st.columns(3)
    col1.metric('Estudiantes totales', len(df_students))
    col2.metric('Registros con notas', int(df_students['promedio'].notna().sum()))
    col3.metric('Carreras disponibles', df_students['carrera'].nunique())

    # Permitir la búsqueda de estudiantes por ID, mostrando los detalles correspondientes en una tabla, facilitando el acceso rápido a la información de un estudiante específico.
    st.subheader('Buscar estudiante por ID')
    selected_id = st.selectbox('Seleccionar ID de estudiante', options=[''] + sorted(df_students['id_estudiante'].unique().tolist()))
    if selected_id:
        detalle = df_students.loc[df_students['id_estudiante'] == selected_id]
        if not detalle.empty:
            st.write(detalle.reset_index(drop=True))
        else:
            st.warning('No se encontró información para ese ID.')

    # with st.expander para registrar un nuevo estudiante, proporcionando un formulario interactivo para ingresar los datos del estudiante y agregarlo al sistema, mejorando la gestión de estudiantes desde el dashboard.
    with st.expander('Registrar nuevo estudiante'):
        with st.form('registrar_estudiante_form'):
            nombre = st.text_input('Nombre', value=st.session_state.reg_nombre)
            apellido = st.text_input('Apellido', value=st.session_state.reg_apellido)
            edad = st.text_input('Edad', value=st.session_state.reg_edad)
            carrera = st.selectbox('Carrera', list(estudiantes.CARRERAS.keys()))
            submitted = st.form_submit_button('Registrar estudiante')
            # if submitted para manejar la lógica de registro de un nuevo estudiante, validando los datos ingresados y utilizando las funciones del módulo `estudiantes` para agregar el nuevo estudiante al sistema, proporcionando retroalimentación sobre el éxito o fracaso del registro.
            if submitted:
                matricula, nuevo_id = estudiantes.registrar_estudiante_auto(nombre, apellido, edad, carrera, archivo=student_file_path)
                if nuevo_id:
                    st.success(f'Estudiante registrado con ID {nuevo_id} y matrícula {matricula}.')
                    time.sleep(2)
                    # Limpiar formulario
                    st.session_state.reg_nombre = ''
                    st.session_state.reg_apellido = ''
                    st.session_state.reg_edad = ''
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error('No se pudo registrar el estudiante. Verifique los datos e intente de nuevo.')

    # with st.expander para actualizar los datos de un estudiante existente, proporcionando un formulario interactivo para ingresar la matrícula del estudiante a actualizar y los nuevos datos, permitiendo modificar la información de un estudiante ya registrado en el sistema.
    with st.expander('Actualizar datos de estudiante'):
        st.info('Deja los campos opcionales en blanco si no deseas cambiarlos. Solo se actualizarán los campos que completes.')
        with st.form('actualizar_estudiante_form'):
            matricula = st.text_input('Matrícula del estudiante a actualizar', value=st.session_state.upd_matricula)
            nombre = st.text_input('Nuevo nombre (opcional - dejar en blanco si no deseas cambiar)', value=st.session_state.upd_nombre)
            apellido = st.text_input('Nuevo apellido (opcional - dejar en blanco si no deseas cambiar)', value=st.session_state.upd_apellido)
            edad = st.text_input('Nueva edad (opcional - dejar en blanco si no deseas cambiar)', value=st.session_state.upd_edad)
            id_estudiante = st.text_input('Nuevo ID Estudiante (opcional - dejar en blanco si no deseas cambiar)', value=st.session_state.upd_id)
            carrera = st.selectbox('Nueva carrera (opcional)', [''] + list(estudiantes.CARRERAS.keys()))
            submitted = st.form_submit_button('Actualizar estudiante')
            # if submitted para manejar la lógica de actualización de un estudiante existente, validando los datos ingresados y utilizando las funciones del módulo `estudiantes` para actualizar la información del estudiante en el sistema, proporcionando retroalimentación sobre el éxito o fracaso de la actualización.
            if submitted:
                success = estudiantes.actualizar_estudiante(matricula, nombre or None, apellido or None, edad or None, id_estudiante or None, carrera or None, archivo=student_file_path)
                if success:
                    st.success('Datos de estudiante actualizados correctamente.')
                    time.sleep(2)
                    # Limpiar formulario
                    st.session_state.upd_matricula = ''
                    st.session_state.upd_nombre = ''
                    st.session_state.upd_apellido = ''
                    st.session_state.upd_edad = ''
                    st.session_state.upd_id = ''
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error('No se pudo actualizar el estudiante. Revise la matrícula e intente de nuevo.')

    with st.expander('Eliminar estudiante (dos pasos)'):
        id_to_delete = st.text_input('Matrícula o ID del estudiante a eliminar', value=st.session_state.del_id)
        if id_to_delete:
            detalle = df_students.loc[(df_students['matricula'].astype(str) == str(id_to_delete)) | (df_students['id_estudiante'].astype(str) == str(id_to_delete))]
            if not detalle.empty:
                st.write(detalle.reset_index(drop=True))
                confirm = st.text_input('Escriba ELIMINAR para confirmar')
                if confirm == 'ELIMINAR':
                    ok = estudiantes.eliminar_estudiante(id_to_delete, archivo=student_file_path)
                    if ok:
                        st.success('Estudiante eliminado.')
                        time.sleep(2)
                        # Limpiar formulario
                        st.session_state.del_id = ''
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error('No se pudo eliminar el estudiante.')
            else:
                st.info('No se encontró el estudiante especificado.')

    with st.expander('Gráfica de distribución de notas en estudiantes'):
        plot_grade_distribution(df_filtrado, 'Distribución de notas por estudiante')


def render_notes_page(df_students: pd.DataFrame, df_notes: pd.DataFrame, student_file_path: str, notes_file_path: str):
    st.header('Notas')
    st.markdown('Visualiza y actualiza las notas usando la lógica del sistema existente.')

    # Inicializar session_state para limpiar formularios de notas
    if 'add_id_est' not in st.session_state:
        st.session_state.add_id_est = ''
    if 'add_asign' not in st.session_state:
        st.session_state.add_asign = ''
    if 'add_nota1' not in st.session_state:
        st.session_state.add_nota1 = ''
    if 'add_nota2' not in st.session_state:
        st.session_state.add_nota2 = ''
    if 'add_nota3' not in st.session_state:
        st.session_state.add_nota3 = ''
    if 'upd_id_est' not in st.session_state:
        st.session_state.upd_id_est = ''
    if 'upd_asign' not in st.session_state:
        st.session_state.upd_asign = ''
    if 'upd_nota' not in st.session_state:
        st.session_state.upd_nota = ''
    if 'del_id_est' not in st.session_state:
        st.session_state.del_id_est = ''
    if 'del_asign' not in st.session_state:
        st.session_state.del_asign = ''

    # Verificar si hay datos de estudiantes
    if df_students.empty:
        st.warning('No hay datos de estudiantes. Por favor, sube un archivo CSV de estudiantes en la sección "Cargar datos" de la barra lateral.')
        return

    st.subheader('Notas cargadas')
    st.dataframe(df_notes[['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3', 'promedio']])

    st.subheader('Agregar nueva nota')
    with st.form('agregar_nota_form'):
        id_estudiante = st.text_input('ID Estudiante', value=st.session_state.add_id_est)
        asignatura = st.text_input('Asignatura', value=st.session_state.add_asign).strip().lower()
        nota1 = st.text_input('Nota 1', value=st.session_state.add_nota1)
        nota2 = st.text_input('Nota 2 (opcional)', value=st.session_state.add_nota2)
        nota3 = st.text_input('Nota 3 (opcional)', value=st.session_state.add_nota3)
        submitted = st.form_submit_button('Agregar nota')
        if submitted:
            notas_lista = [nota for nota in [nota1, nota2, nota3] if nota.strip() != '']
            success = notas.agregar_nota(id_estudiante.strip(), asignatura, notas_lista, archivo_notas_destino=notes_file_path, archivo_estudiantes_destino=student_file_path)
            if success:
                st.success('Nota agregada correctamente.')
                time.sleep(2)
                # Limpiar formulario
                st.session_state.add_id_est = ''
                st.session_state.add_asign = ''
                st.session_state.add_nota1 = ''
                st.session_state.add_nota2 = ''
                st.session_state.add_nota3 = ''
                st.cache_data.clear()
                st.rerun()
            else:
                st.error('No se pudo agregar la nota. Verifique los datos.')

    st.subheader('Actualizar nota existente')
    with st.form('actualizar_nota_form'):
        id_estudiante = st.text_input('ID Estudiante para actualización', value=st.session_state.upd_id_est)
        asignatura = st.text_input('Asignatura a actualizar', value=st.session_state.upd_asign).strip().lower()
        nueva_nota = st.text_input('Nueva nota', value=st.session_state.upd_nota)
        submitted = st.form_submit_button('Actualizar nota')
        if submitted:
            success = notas.actualizar_nota(id_estudiante.strip(), asignatura, nueva_nota, archivo_notas_destino=notes_file_path, archivo_estudiantes_destino=student_file_path)
            if success:
                st.success('Nota actualizada correctamente.')
                time.sleep(2)
                # Limpiar formulario
                st.session_state.upd_id_est = ''
                st.session_state.upd_asign = ''
                st.session_state.upd_nota = ''
                st.cache_data.clear()
                st.rerun()
            else:
                st.error('No se pudo actualizar la nota. Verifique los datos.')

    with st.expander('Eliminar nota (dos pasos)'):
        idn = st.text_input('ID Estudiante para eliminar nota', value=st.session_state.del_id_est)
        asign = st.text_input('Asignatura a eliminar', value=st.session_state.del_asign).strip().lower()
        if idn and asign:
            matches = df_notes.loc[(df_notes['id_estudiante'] == idn) & (df_notes['asignatura'] == asign)]
            if not matches.empty:
                st.write(matches.reset_index(drop=True))
                confirm = st.text_input('Escriba ELIMINAR para confirmar la eliminación de la nota')
                if confirm == 'ELIMINAR':
                    ok = notas.eliminar_nota(idn, asign, archivo_notas_destino=notes_file_path, archivo_estudiantes_destino=student_file_path)
                    if ok:
                        st.success('Nota eliminada correctamente.')
                        time.sleep(2)
                        # Limpiar formulario
                        st.session_state.del_id_est = ''
                        st.session_state.del_asign = ''
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error('No se pudo eliminar la nota.')
            else:
                st.info('No se encontró la nota especificada.')

    st.subheader('Promedio por asignatura')
    if not df_notes.empty:
        asignatura_promedios = df_notes.groupby('asignatura')['promedio'].mean().sort_values(ascending=False)
        st.bar_chart(asignatura_promedios)
    else:
        st.write('No hay registros en notas.')

    with st.expander('Histograma de notas'):
        plot_grade_distribution(df_notes, 'Distribución de notas en notas')


def render_averages_page(df_students: pd.DataFrame, notes_file_path: str):
    st.header('Promedios')
    st.markdown('Revisa promedios usando los datos del sistema.')

    # Verificar si hay datos
    if df_students.empty:
        st.warning('No hay datos de estudiantes. Por favor, sube un archivo CSV de estudiantes en la sección "Cargar datos" de la barra lateral.')
        return

    promedios_data = promedios.obtener_promedios_por_estudiante()
    if not promedios_data:
        st.warning('No hay promedios calculables con los datos actuales.')
        return

    averages_df = pd.DataFrame([{'id_estudiante': id_est, 'promedio_estudiante': valor} for id_est, valor in promedios_data.items()])
    merged = averages_df.merge(df_students[['id_estudiante', 'nombre', 'apellido', 'carrera']].drop_duplicates('id_estudiante'), on='id_estudiante', how='left')
    merged['estado'] = merged['promedio_estudiante'].apply(lambda x: 'Aprobado' if x >= 3.0 else 'Reprobado')

    st.subheader('Promedio general por estudiante')
    st.dataframe(merged.sort_values('promedio_estudiante', ascending=False).reset_index(drop=True))

    st.subheader('Mejores promedios')
    st.write(merged.sort_values('promedio_estudiante', ascending=False).head(5))

    st.subheader('Peores promedios')
    st.write(merged.sort_values('promedio_estudiante', ascending=True).head(5))

    aprobados, reprobados = promedios.obtener_estados_aprobados_reprobados()
    col1, col2 = st.columns(2)
    col1.metric('Aprobados', len(aprobados))
    col2.metric('Reprobados', len(reprobados))

    # with st.expander para mostrar un gráfico de los mejores promedios, proporcionando una visualización clara de los estudiantes con los promedios más altos, lo que puede ayudar a identificar a los estudiantes destacados y analizar sus características.
    with st.expander('Gráfico de los mejores promedios'):
        fig, ax = plt.subplots(figsize=(8, 4))
        top = merged.sort_values('promedio_estudiante', ascending=False).head(10)
        cmap = plt.cm.get_cmap('Set2')
        colors = [cmap(i % cmap.N) for i in range(len(top))]
        ax.bar(top['id_estudiante'], top['promedio_estudiante'], color=colors)
        ax.set_ylim(0, 5)
        ax.set_title('Top 10 promedios')
        ax.set_xlabel('ID Estudiante')
        ax.set_ylabel('Promedio')
        st.pyplot(fig)

    st.subheader('Promedio por carrera')
    career_avg = merged.groupby('carrera')['promedio_estudiante'].mean().sort_values(ascending=False)
    plot_bar_average(pd.DataFrame({'carrera': career_avg.index, 'promedio': career_avg.values}), 'carrera', 'Carrera', 'Promedio promedio por carrera')


# render_analysis_page para mostrar la página de análisis en el dashboard, incluyendo gráficos dinámicos para comprender tendencias por carrera, asignatura y edades, proporcionando una interfaz interactiva para analizar los datos de los estudiantes desde diferentes perspectivas y descubrir patrones o insights relevantes.
def render_analysis_page(df_students: pd.DataFrame):
    st.header('Análisis')
    st.markdown('Gráficos dinámicos para comprender tendencias por carrera, asignatura y edades.')

    # Verificar si hay datos
    if df_students.empty:
        st.warning('No hay datos de estudiantes. Por favor, sube un archivo CSV de estudiantes en la sección "Cargar datos" de la barra lateral.')
        return

    st.subheader('Edad vs promedio')
    scatter = df_students.dropna(subset=['edad', 'promedio'])
    if not scatter.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.scatter(scatter['edad'], scatter['promedio'], c='tab:blue', alpha=0.7)
        ax.set_xlabel('Edad')
        ax.set_ylabel('Promedio')
        ax.set_title('Relación entre edad y promedio')
        st.pyplot(fig)
    else:
        st.write('No hay datos suficientes para graficar edad vs promedio.')

    st.subheader('Promedio por carrera')
    plot_bar_average(df_students, 'carrera', 'Carrera', 'Promedio promedio por carrera')

    st.subheader('Promedio por asignatura')
    plot_bar_average(df_students, 'asignatura', 'Asignatura', 'Promedio promedio por asignatura')

    st.subheader('Resumen rápido de estadísticas')
    st.write(df_students[['carrera', 'asignatura', 'promedio']].groupby(['carrera', 'asignatura']).mean().round(2))


# main para iniciar el dashboard, proporcionando una estructura clara para navegar entre las diferentes secciones (estudiantes, notas, promedios, análisis) y conectando con los módulos del sistema para mostrar datos en tablas, gráficos y permitir la actualización de registros.
def main():
    st.title('Dashboard Estudiantil')
    st.markdown('Una interfaz interactiva para gestionar estudiantes, notas y promedios usando las funcionalidades existentes.')

    # SIDEBAR: Reorganización - Título, Panel, Carga de datos, Archivos
    st.sidebar.title('Sistema de Gestión')
    
    # Seleccionar sección primero
    page = st.sidebar.selectbox('Seleccionar sección', ['Estudiantes', 'Notas', 'Promedios', 'Análisis'])
    
    # Separator
    st.sidebar.markdown('---')
    
    # Cargar datos
    st.sidebar.header('Cargar datos')
    uploaded_students = st.sidebar.file_uploader('Subir CSV de estudiantes', type=['csv'], key='up_students')
    uploaded_notes = st.sidebar.file_uploader('Subir archivo de notas (CSV o TXT)', type=['csv', 'txt'], key='up_notes')

    student_file_path = archivo_estudiantes
    notes_file_path = archivo_notas

    if uploaded_students is not None:
        dest = os.path.join(UPLOADS_DIR, uploaded_students.name)
        with open(dest, 'wb') as f:
            f.write(uploaded_students.getbuffer())
        st.sidebar.success(f'Archivo de estudiantes subido: {uploaded_students.name}')
        student_file_path = dest

    if uploaded_notes is not None:
        destn = os.path.join(UPLOADS_DIR, uploaded_notes.name)
        with open(destn, 'wb') as f:
            f.write(uploaded_notes.getbuffer())
        st.sidebar.success(f'Archivo de notas subido: {uploaded_notes.name}')
        notes_file_path = destn

    # Archivos subidos
    st.sidebar.markdown('---')
    st.sidebar.markdown('**Tus archivos** (descarga o elimina)')
    files = os.listdir(UPLOADS_DIR)
    
    if files:
        for fn in files:
            col1, col2, col3 = st.sidebar.columns([2, 1, 1])
            col1.write(f'📄 {fn}')
            
            # Botón de descarga
            file_path = os.path.join(UPLOADS_DIR, fn)
            with open(file_path, 'rb') as f:
                file_data = f.read()
            col2.download_button(
                label='⬇️',
                data=file_data,
                file_name=fn,
                key=f'download_{fn}',
                help='Descargar archivo'
            )
            
            # Botón de eliminar
            if col3.button('🗑️', key=f'del_{fn}', help='Eliminar archivo'):
                try:
                    os.remove(file_path)
                    st.cache_data.clear()
                    st.rerun()
                except Exception:
                    st.sidebar.error('No se pudo eliminar el archivo')
    else:
        st.sidebar.info('Sin archivos aún')

    # Información del sistema
    st.sidebar.markdown('---')
    st.sidebar.markdown('**Módulos del sistema:**')
    st.sidebar.markdown('- `estudiantes.py`\n- `notas.py`\n- `promedios.py`\n- `utils.py`')

    # Cargar datos
    df_students = load_students(archivo=student_file_path)
    df_notes = load_notes(archivo=notes_file_path)

    # Mostrar información de estado
    if df_students.empty and df_notes.empty:
        st.info('¡Bienvenido! Para comenzar, sube un archivo CSV de estudiantes en la sección "Cargar datos" de la barra lateral izquierda. Puedes subir archivos adicionales de notas si lo deseas.')

    if page == 'Estudiantes':
        render_students_page(df_students, student_file_path)
    elif page == 'Notas':
        render_notes_page(df_students, df_notes, student_file_path, notes_file_path)
    elif page == 'Promedios':
        render_averages_page(df_students, notes_file_path)
    elif page == 'Análisis':
        render_analysis_page(df_students)


if __name__ == '__main__':
    main()

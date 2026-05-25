# Este archivo implementa un dashboard interactivo usando Streamlit para visualizar y gestionar estudiantes, notas y promedios. Se conecta con los módulos existentes (`estudiantes.py`, `notas.py`, `promedios.py`) para mostrar datos en tablas, gráficos y permitir la actualización de registros. El dashboard incluye filtros dinámicos por carrera y asignatura, así como análisis visuales de tendencias en los datos.

"""importaciones necesarias para la construcción del dashboard, incluyendo Streamlit para la interfaz, pandas para el manejo de datos y matplotlib para las visualizaciones. También se importan los módulos del sistema para acceder a las funcionalidades de gestión de estudiantes, notas y promedios."""

# Libreria os para manejo de rutas y archivos
import os

# Librerias para manejo de datos y visualización
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

#  Importaciones de los módulos del sistema para acceder a las funcionalidades de gestión de estudiantes, notas y promedios.
import estudiantes
import notas
import promedios


"""
Este módulo se encarga de calcular promedios por estudiante, listar estudiantes por promedio y mostrar aprobados/reprobados según los registros de notas disponibles. Si no hay registros en `notas.txt`, se intentará extraer notas del CSV de estudiantes para el cálculo.
"""
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXPECTED_STUDENT_COLUMNS = [
    'matricula',
    'nombre',
    'apellido',
    'edad',
    'id_estudiante',
    'carrera',
    'asignatura',
    'nota_1',
    'nota_2',
    'nota_3',
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


# st.cache_data - load_students para almacenar en caché los datos de estudiantes y notas, evitando recargas innecesarias y mejorando el rendimiento del dashboard al acceder a los datos desde los módulos del sistema.
@st.cache_data
def load_students() -> pd.DataFrame:
    estudiantes_list = estudiantes.cargar_estudiantes()
    if not estudiantes_list:
        return pd.DataFrame(columns=EXPECTED_STUDENT_COLUMNS + ['promedio'])
    df = pd.DataFrame(estudiantes_list)
    return normalize_students(df)


# st.cache_data - load_notes para almacenar en caché los datos de notas, evitando recargas innecesarias y mejorando el rendimiento del dashboard al acceder a los datos desde los módulos del sistema.
@st.cache_data
def load_notes() -> pd.DataFrame:
    notas_list = notas.leer_notas()
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
    ax.hist(grades, bins=[1, 2, 3, 4, 5, 6], edgecolor='black', color='#4c72b0')
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
    summary.plot(kind='bar', color='#f28e2b', ax=ax)
    ax.set_title(title)
    ax.set_ylabel('Promedio')
    ax.set_xlabel(label)
    ax.set_ylim(0, 5)
    st.pyplot(fig)


# render_students_page para mostrar la página de estudiantes en el dashboard, incluyendo una tabla de estudiantes con filtros dinámicos, métricas clave y formularios para registrar y actualizar estudiantes, proporcionando una interfaz interactiva para gestionar la información de los estudiantes.
def render_students_page(df_students: pd.DataFrame):
    st.header('Estudiantes')
    st.markdown('Explora la lista de estudiantes y filtra por carrera o asignatura.')

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
            nombre = st.text_input('Nombre')
            apellido = st.text_input('Apellido')
            edad = st.text_input('Edad')
            carrera = st.selectbox('Carrera', list(estudiantes.CARRERAS.keys()))
            submitted = st.form_submit_button('Registrar estudiante')
            # if submitted para manejar la lógica de registro de un nuevo estudiante, validando los datos ingresados y utilizando las funciones del módulo `estudiantes` para agregar el nuevo estudiante al sistema, proporcionando retroalimentación sobre el éxito o fracaso del registro.
            if submitted:
                matricula, nuevo_id = estudiantes.registrar_estudiante_auto(nombre, apellido, edad, carrera)
                if nuevo_id:
                    st.success(f'Estudiante registrado con ID {nuevo_id} y matrícula {matricula}.')
                    st.experimental_rerun()
                else:
                    st.error('No se pudo registrar el estudiante. Verifique los datos e intente de nuevo.')

    # with st.expander para actualizar los datos de un estudiante existente, proporcionando un formulario interactivo para ingresar la matrícula del estudiante a actualizar y los nuevos datos, permitiendo modificar la información de un estudiante ya registrado en el sistema.
    with st.expander('Actualizar datos de estudiante'):
        with st.form('actualizar_estudiante_form'):
            matricula = st.text_input('Matrícula del estudiante a actualizar')
            nombre = st.text_input('Nuevo nombre (opcional)')
            apellido = st.text_input('Nuevo apellido (opcional)')
            edad = st.text_input('Nueva edad (opcional)')
            id_estudiante = st.text_input('Nuevo ID Estudiante (opcional)')
            carrera = st.selectbox('Nueva carrera (opcional)', [''] + list(estudiantes.CARRERAS.keys()))
            submitted = st.form_submit_button('Actualizar estudiante')
            # if submitted para manejar la lógica de actualización de un estudiante existente, validando los datos ingresados y utilizando las funciones del módulo `estudiantes` para actualizar la información del estudiante en el sistema, proporcionando retroalimentación sobre el éxito o fracaso de la actualización.
            if submitted:
                success = estudiantes.actualizar_estudiante(matricula, nombre or None, apellido or None, edad or None, id_estudiante or None, carrera or None)
                if success:
                    st.success('Datos de estudiante actualizados correctamente.')
                    st.experimental_rerun()
                else:
                    st.error('No se pudo actualizar el estudiante. Revise la matrícula e intente de nuevo.')

    # with st.expander para mostrar una gráfica de la distribución de notas por estudiante, proporcionando una visualización clara de cómo se distribuyen las calificaciones entre los estudiantes filtrados, lo que puede ayudar a identificar tendencias o áreas de mejora específicas para ese grupo de estudiantes.
    with st.expander('Gráfica de distribución de notas en estudiantes'):
        plot_grade_distribution(df_filtrado, 'Distribución de notas por estudiante')


# render_notes_page para mostrar la página de notas en el dashboard, incluyendo una tabla de notas, formularios para agregar y actualizar notas, y visualizaciones de promedios por asignatura, proporcionando una interfaz interactiva para gestionar las notas de los estudiantes.
def render_notes_page(df_students: pd.DataFrame, df_notes: pd.DataFrame):
    st.header('Notas')
    st.markdown('Visualiza y actualiza las notas usando la lógica del sistema existente.')

    st.subheader('Notas desde notas.txt')
    st.dataframe(df_notes[['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3', 'promedio']])

    st.subheader('Agregar nueva nota')
    with st.form('agregar_nota_form'):
        id_estudiante = st.text_input('ID Estudiante')
        asignatura = st.text_input('Asignatura').strip().lower()
        nota1 = st.text_input('Nota 1')
        nota2 = st.text_input('Nota 2 (opcional)')
        nota3 = st.text_input('Nota 3 (opcional)')
        submitted = st.form_submit_button('Agregar nota')
        if submitted:
            notas_lista = [nota for nota in [nota1, nota2, nota3] if nota.strip() != '']
            success = notas.agregar_nota(id_estudiante.strip(), asignatura, notas_lista)
            if success:
                st.success('Nota agregada correctamente.')
                st.experimental_rerun()
            else:
                st.error('No se pudo agregar la nota. Verifique los datos.')

    st.subheader('Actualizar nota existente')
    with st.form('actualizar_nota_form'):
        id_estudiante = st.text_input('ID Estudiante para actualización')
        asignatura = st.text_input('Asignatura a actualizar').strip().lower()
        nueva_nota = st.text_input('Nueva nota')
        submitted = st.form_submit_button('Actualizar nota')
        if submitted:
            success = notas.actualizar_nota(id_estudiante.strip(), asignatura, nueva_nota)
            if success:
                st.success('Nota actualizada correctamente.')
                st.experimental_rerun()
            else:
                st.error('No se pudo actualizar la nota. Verifique los datos.')

    st.subheader('Promedio por asignatura en notas.txt')
    if not df_notes.empty:
        asignatura_promedios = df_notes.groupby('asignatura')['promedio'].mean().sort_values(ascending=False)
        st.bar_chart(asignatura_promedios)
    else:
        st.write('No hay registros en notas.txt.')

    with st.expander('Histograma de notas en notas.txt'):
        plot_grade_distribution(df_notes, 'Distribución de notas en notas.txt')


# render_averages_page para mostrar la página de promedios en el dashboard, incluyendo una tabla de promedios por estudiante, gráficos de los mejores y peores promedios, y métricas de aprobados/reprobados, proporcionando una interfaz interactiva para analizar los promedios de los estudiantes utilizando los datos disponibles.
def render_averages_page(df_students: pd.DataFrame):
    st.header('Promedios')
    st.markdown('Revisa promedios usando los datos del sistema.')

    promedios_data = promedios.obtener_promedios_por_estudiante()
    if not promedios_data:
        st.warning('No hay promedios calculables con los datos actuales.')
        return

    averages_df = pd.DataFrame(
        [{'id_estudiante': id_est, 'promedio_estudiante': valor} for id_est, valor in promedios_data.items()]
    )
    merged = averages_df.merge(
        df_students[['id_estudiante', 'nombre', 'apellido', 'carrera']].drop_duplicates('id_estudiante'),
        on='id_estudiante',
        how='left',
    )
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
        ax.bar(top['id_estudiante'], top['promedio_estudiante'], color='#2ca02c')
        ax.set_ylim(0, 5)
        ax.set_title('Top 10 promedios')
        ax.set_xlabel('ID Estudiante')
        ax.set_ylabel('Promedio')
        st.pyplot(fig)

    st.subheader('Promedio por carrera')
    career_avg = merged.groupby('carrera')['promedio_estudiante'].mean().sort_values(ascending=False)
    st.bar_chart(career_avg)


# render_analysis_page para mostrar la página de análisis en el dashboard, incluyendo gráficos dinámicos para comprender tendencias por carrera, asignatura y edades, proporcionando una interfaz interactiva para analizar los datos de los estudiantes desde diferentes perspectivas y descubrir patrones o insights relevantes.
def render_analysis_page(df_students: pd.DataFrame):
    st.header('Análisis')
    st.markdown('Gráficos dinámicos para comprender tendencias por carrera, asignatura y edades.')

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

    page = st.sidebar.selectbox('Seleccionar sección', ['Estudiantes', 'Notas', 'Promedios', 'Análisis'])
    df_students = load_students()
    df_notes = load_notes()

    if page == 'Estudiantes':
        render_students_page(df_students)
    elif page == 'Notas':
        render_notes_page(df_students, df_notes)
    elif page == 'Promedios':
        render_averages_page(df_students)
    elif page == 'Análisis':
        render_analysis_page(df_students)

    # Información adicional en la barra lateral sobre el propósito del dashboard, instrucciones de uso y conexión con los módulos del sistema, proporcionando contexto y orientación a los usuarios para aprovechar al máximo las funcionalidades del dashboard.
    st.sidebar.markdown('---')
    st.sidebar.markdown('Conexión con los módulos del sistema:')
    st.sidebar.markdown('- `estudiantes.py`')
    st.sidebar.markdown('- `notas.py`')
    st.sidebar.markdown('- `promedios.py`')
    st.sidebar.markdown('- `utils.py`')


if __name__ == '__main__':
    main()

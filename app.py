import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ESTUDIANTES_FILE = os.path.join(BASE_DIR, "estudiantes.csv")
NOTAS_FILE = os.path.join(BASE_DIR, "notas.txt")


@st.cache_data
def load_students() -> pd.DataFrame:
    df = pd.read_csv(ESTUDIANTES_FILE)
    df['edad'] = pd.to_numeric(df['edad'], errors='coerce').astype('Int64')
    for col in ['nota_1', 'nota_2', 'nota_3']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = pd.NA
    df['promedio'] = df[['nota_1', 'nota_2', 'nota_3']].mean(axis=1, skipna=True)
    df['carrera'] = df['carrera'].fillna('desconocida')
    df['asignatura'] = df['asignatura'].fillna('sin asignatura')
    return df


@st.cache_data
def load_notes() -> pd.DataFrame:
    try:
        df = pd.read_csv(NOTAS_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3'])
    for col in ['nota_1', 'nota_2', 'nota_3']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = pd.NA
    df['promedio'] = df[['nota_1', 'nota_2', 'nota_3']].mean(axis=1, skipna=True)
    df['asignatura'] = df['asignatura'].fillna('sin asignatura')
    return df


def get_student_averages(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['id_estudiante', 'promedio'])
    promedio_por_estudiante = (
        df.groupby('id_estudiante')['promedio']
        .mean()
        .reset_index()
        .rename(columns={'promedio': 'promedio_estudiante'})
    )
    return promedio_por_estudiante


def career_assignment_filters(df: pd.DataFrame):
    carreras = sorted(df['carrera'].dropna().unique())
    opciones_carrera = st.sidebar.multiselect('Filtrar por carrera', carreras, default=carreras)

    asignaturas = sorted(df.loc[df['carrera'].isin(opciones_carrera), 'asignatura'].dropna().unique())
    opciones_asignatura = st.sidebar.multiselect('Filtrar por asignatura', asignaturas, default=asignaturas)

    df_filtrado = df.loc[df['carrera'].isin(opciones_carrera) & df['asignatura'].isin(opciones_asignatura)]
    return df_filtrado, opciones_carrera, opciones_asignatura


def plot_grade_distribution(df: pd.DataFrame, title: str):
    grades = df[['nota_1', 'nota_2', 'nota_3']].melt(value_name='nota')['nota'].dropna()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(grades, bins=[1, 2, 3, 4, 5, 6], edgecolor='black', color='#4c72b0')
    ax.set_title(title)
    ax.set_xlabel('Nota')
    ax.set_ylabel('Cantidad de valores')
    ax.set_xticks([1, 2, 3, 4, 5])
    st.pyplot(fig)


def plot_bar_average(df: pd.DataFrame, group_by: str, label: str, title: str):
    if df.empty:
        st.write('No hay datos suficientes para graficar.')
        return
    summary = df.groupby(group_by)['promedio'].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    summary.plot(kind='bar', color='#f28e2b', ax=ax)
    ax.set_title(title)
    ax.set_ylabel('Promedio')
    ax.set_xlabel(label)
    ax.set_ylim(0, 5)
    st.pyplot(fig)


def render_students_page(df_students: pd.DataFrame):
    st.header('Estudiantes')
    st.markdown('Explora la lista de estudiantes y filtra por carrera o asignatura.')

    df_filtrado, _, _ = career_assignment_filters(df_students)
    st.subheader('Tabla de estudiantes')
    st.dataframe(df_filtrado[['matricula', 'id_estudiante', 'nombre', 'apellido', 'edad', 'carrera', 'asignatura', 'nota_1', 'nota_2', 'nota_3', 'promedio']])

    col1, col2, col3 = st.columns(3)
    col1.metric('Estudiantes totales', len(df_students))
    col2.metric('Registros con notas', int(df_students['promedio'].notna().sum()))
    col3.metric('Carreras disponibles', df_students['carrera'].nunique())

    st.subheader('Detalle por estudiante')
    selected_id = st.selectbox('Seleccionar ID de estudiante', options=[''] + sorted(df_students['id_estudiante'].astype(str).unique().tolist()))
    if selected_id:
        detalle = df_students.loc[df_students['id_estudiante'] == selected_id]
        if not detalle.empty:
            st.write(detalle.reset_index(drop=True))
        else:
            st.write('No se encontró información para ese ID.')

    with st.expander('Gráfica de distribución de notas en estudiantes'): 
        plot_grade_distribution(df_filtrado, 'Distribución de notas por estudiante')


def render_notes_page(df_students: pd.DataFrame, df_notes: pd.DataFrame):
    st.header('Notas')
    st.markdown('Visualiza las notas registradas en archivo y compara con los datos de estudiantes.')

    st.subheader('Notas desde `notas.txt`')
    st.dataframe(df_notes[['id_estudiante', 'asignatura', 'nota_1', 'nota_2', 'nota_3', 'promedio']])

    st.subheader('Promedio por asignatura en notas.txt')
    if not df_notes.empty:
        asignatura_promedios = df_notes.groupby('asignatura')['promedio'].mean().sort_values(ascending=False)
        st.bar_chart(asignatura_promedios)
    else:
        st.write('No hay registros en notas.txt.')

    with st.expander('Histograma de notas en notas.txt'):
        plot_grade_distribution(df_notes, 'Distribución de notas en notas.txt')

    st.subheader('Comparación de notas del CSV y notas.txt')
    combined = pd.concat([df_students.assign(Origen='CSV'), df_notes.assign(Origen='NOTAS_TXT')], sort=False)
    if not combined.empty:
        st.write('Resumen de registros combinados:')
        st.dataframe(combined[['Origen', 'id_estudiante', 'asignatura', 'promedio']].head(20))
    else:
        st.write('No hay datos combinados para mostrar.')


def render_averages_page(df_students: pd.DataFrame, df_notes: pd.DataFrame):
    st.header('Promedios')
    st.markdown('Revisa los promedios por estudiante, los mejores y los que necesitan apoyo.')

    student_averages = get_student_averages(df_students)
    merged = student_averages.merge(df_students[['id_estudiante', 'nombre', 'apellido', 'carrera']].drop_duplicates('id_estudiante'), on='id_estudiante', how='left')
    merged['estado'] = merged['promedio_estudiante'].apply(lambda x: 'Aprobado' if x >= 3.0 else 'Reprobado')

    st.subheader('Promedio general por estudiante')
    st.dataframe(merged.sort_values('promedio_estudiante', ascending=False).reset_index(drop=True))

    st.subheader('Mejores promedios')
    st.write(merged.sort_values('promedio_estudiante', ascending=False).head(5))

    st.subheader('Peores promedios')
    st.write(merged.sort_values('promedio_estudiante', ascending=True).head(5))

    aprobados = merged[merged['estado'] == 'Aprobado']
    reprobados = merged[merged['estado'] == 'Reprobado']
    col1, col2 = st.columns(2)
    col1.metric('Aprobados', len(aprobados))
    col2.metric('Reprobados', len(reprobados))

    with st.expander('Gráfico de los mejores promedios'):
        fig, ax = plt.subplots(figsize=(8, 4))
        top = merged.sort_values('promedio_estudiante', ascending=False).head(10)
        ax.bar(top['id_estudiante'], top['promedio_estudiante'], color='#2ca02c')
        ax.set_ylim(0, 5)
        ax.set_title('Top 10 promedios')
        ax.set_xlabel('ID Estudiante')
        ax.set_ylabel('Promedio')
        st.pyplot(fig)

    st.subheader('Promedios por carrera')
    career_avg = merged.groupby('carrera')['promedio_estudiante'].mean().sort_values(ascending=False)
    st.bar_chart(career_avg)

    if not df_notes.empty:
        st.subheader('Promedio a partir de notas.txt')
        notes_averages = get_student_averages(df_notes.rename(columns={'id_estudiante': 'id_estudiante'}))
        st.dataframe(notes_averages.sort_values('promedio_estudiante', ascending=False).reset_index(drop=True))


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


def main():
    st.title('Dashboard Estudiantil')
    st.markdown(
        'Una interfaz interactiva para gestionar estudiantes, notas y promedios con filtros y gráficos.'
    )

    page = st.sidebar.selectbox('Seleccionar sección', ['Estudiantes', 'Notas', 'Promedios', 'Análisis'])
    df_students = load_students()
    df_notes = load_notes()

    if page == 'Estudiantes':
        render_students_page(df_students)
    elif page == 'Notas':
        render_notes_page(df_students, df_notes)
    elif page == 'Promedios':
        render_averages_page(df_students, df_notes)
    elif page == 'Análisis':
        render_analysis_page(df_students)

    st.sidebar.markdown('---')
    st.sidebar.markdown('Carga de datos desde:')
    st.sidebar.markdown(f'- `estudiantes.csv` ({len(df_students)} filas)')
    st.sidebar.markdown(f'- `notas.txt` ({len(df_notes)} filas)')


if __name__ == '__main__':
    main()

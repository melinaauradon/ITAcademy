import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# Título
st.title("📊 Dashboard de Análisis")

# Cargar datos
df_full = pd.read_csv("streamlit/df_full.csv")

# Mostrar dataset
with st.expander("Ver datos"):
    st.dataframe(df)

# Sidebar
st.sidebar.header("Filtros")

# Selección de columna categórica
columnas_cat = df.select_dtypes(include="object").columns.tolist()

if columnas_cat:
    columna_filtro = st.sidebar.selectbox(
        "Selecciona una categoría",
        columnas_cat
    )

    opciones = st.sidebar.multiselect(
        "Valores",
        df[columna_filtro].dropna().unique(),
        default=df[columna_filtro].dropna().unique()
    )

    df = df[df[columna_filtro].isin(opciones)]

# Métricas
col1, col2, col3 = st.columns(3)

col1.metric("Filas", len(df))
col2.metric("Columnas", len(df.columns))
col3.metric("Valores nulos", int(df.isnull().sum().sum()))

st.divider()

# Columnas numéricas
columnas_num = df.select_dtypes(include="number").columns.tolist()

if len(columnas_num) > 0:

    col1, col2 = st.columns(2)

    with col1:

        variable = st.selectbox(
            "Variable para histograma",
            columnas_num
        )

        fig = px.histogram(
            df,
            x=variable,
            title=f"Distribución de {variable}"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        variable_box = st.selectbox(
            "Variable para boxplot",
            columnas_num,
            key="box"
        )

        fig = px.box(
            df,
            y=variable_box,
            title=f"Boxplot de {variable_box}"
        )

        st.plotly_chart(fig, use_container_width=True)

# Scatter si hay dos variables numéricas
if len(columnas_num) >= 2:

    st.subheader("Relación entre variables")

    x = st.selectbox(
        "Eje X",
        columnas_num,
        key="x"
    )

    y = st.selectbox(
        "Eje Y",
        columnas_num,
        index=1,
        key="y"
    )

    fig = px.scatter(
        df,
        x=x,
        y=y,
        title=f"{x} vs {y}"
    )

    st.plotly_chart(fig, use_container_width=True)

# Correlación
if len(columnas_num) >= 2:

    st.subheader("Matriz de correlación")

    corr = df[columnas_num].corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig, use_container_width=True)

import pandas as pd
import streamlit as st
import plotly.express as px

# =================================
# CONFIGURACIÓN
# =================================

st.set_page_config(
    page_title="Dashboard Comercial",
    layout="wide"
)

# =================================
# CARGA DE DATOS
# =================================

df_full = pd.read_csv("streamlit/df_full.csv")

# =================================
# TÍTULO
# =================================

st.title(" Dashboard Comercial")

st.markdown(
    """
    Análisis de ventas por campaña y categoría de producto.
    """
)
# =================================
# FILTROS
# =================================

st.sidebar.header("Filtros")

# Cálculo de valores por defecto de las fechas
timestamp_datetime = pd.to_datetime(df_full["timestamp"], errors="coerce")
fecha_minima = timestamp_datetime.min().date()
fecha_maxima = timestamp_datetime.max().date()

# Opciones de los selectbox
campanas_opciones = ["Todos"] + sorted(df_full["campaign_id"].dropna().unique().tolist())
categorias_opciones = ["Todos"] + sorted(df_full["merchant_category"].dropna().unique().tolist())

# Inicializar los estados de los filtros si no existen
if "rango_fechas" not in st.session_state:
    st.session_state.rango_fechas = (fecha_minima, fecha_maxima)
if "campana" not in st.session_state:
    st.session_state.campana = "Todos"
if "categoria" not in st.session_state:
    st.session_state.categoria = "Todos"

# Botón para borrar los filtros
if st.sidebar.button("Borrar Filtros", use_container_width=True):
    st.session_state.rango_fechas = (fecha_minima, fecha_maxima)
    st.session_state.campana = "Todos"
    st.session_state.categoria = "Todos"
    st.rerun() # Recarga la app para aplicar el reinicio visual instantáneamente

# Renderizado de los inputs conectados al session_state
rango_fechas = st.sidebar.date_input(
    "Rango de Fechas",
    key="rango_fechas",
    min_value=fecha_minima,
    max_value=fecha_maxima,
)

campana = st.sidebar.selectbox(
    "Campaña",
    options=campanas_opciones,
    key="campana"
)

categoria = st.sidebar.selectbox(
    "Categoría",
    options=categorias_opciones,
    key="categoria"
)

# =================================
# APLICACIÓN DE LOS FILTROS
# =================================

# Creamos una copia para no modificar el dataframe original
df_filtrado = df_full.copy()

# A) Aplicar filtro de fechas (solo si el usuario seleccionó inicio y fin)
df_filtrado["timestamp"] = pd.to_datetime(df_filtrado["timestamp"], errors="coerce")
if len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
    df_filtrado = df_filtrado[
        (df_filtrado["timestamp"].dt.date >= fecha_inicio) &
        (df_filtrado["timestamp"].dt.date <= fecha_fin)
    ]
df_global_periodo = df_filtrado.copy()

# B) Aplicar filtro de Campaña
if campana != "Todos":
    df_filtrado = df_filtrado[df_filtrado["campaign_id"] == campana]

# C) Aplicar filtro de Categoría
if categoria != "Todos":
    df_filtrado = df_filtrado[df_filtrado["merchant_category"] == categoria]

# =================================
# KPIs
# =================================

facturacion = df_filtrado['amount'].sum()
total_tx = df_filtrado['id_tx'].nunique()

# 1. Ticket Medio Real (Evita el sesgo si una transacción tiene múltiples filas por producto)
ticket_medio = facturacion / total_tx if total_tx > 0 else 0

# 2. Descuento Medio Real
descuento_medio_real = df_filtrado['discount_amount'].mean() if len(df_filtrado) > 0 else 0

# Renderizado de métricas en 3 columnas
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Facturación Total", f"{facturacion:,.0f} €".replace(",", "."))
with col2:
    st.metric("Ticket Medio Real", f"{ticket_medio:,.2f} €".replace(",", "."))
with col3:
    st.metric("Descuento Medio", f"{descuento_medio_real:,.2f} €".replace(",", "."))

st.markdown("---")

# si el cruce de filtros deja el dataset sin filas, no da error
if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles para la combinación de filtros seleccionada.")
else:
    
    # =================================
    # VISUALIZACIÓN 1 : CANALES DE COMPRA
    # =================================
    st.subheader("Campañas por Canal de Venta")
    ventas_canal_campania = (
        df_filtrado[df_filtrado["campaign_id"] != "NO_CAMPAIGN"]
        .groupby(["campaign_id", "channel"])["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    fig1 = px.bar(
        ventas_canal_campania,
        x="campaign_id",
        y="amount",
        color="channel",
        labels={"campaign_id": "Campaña", "amount": "Facturación (€)", "channel": "Canal de Venta"},
        barmode="relative"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # =================================
    # VISUALIZACIÓN 2: FILTRO VS GLOBAL
     # =================================
    st.subheader("Análisis de Categorías: Filtro Actual vs Comportamiento Global")
    
    # Agrupamos la facturación del filtro activo
    cat_filtrado = df_filtrado.groupby("merchant_category")["amount"].sum().reset_index().rename(columns={"amount": "Filtro Seleccionado"})
    
    # Agrupamos la facturación del periodo completo (sin el filtro de campaña/categoría lateral)
    cat_global = df_global_periodo.groupby("merchant_category")["amount"].sum().reset_index().rename(columns={"amount": "Total Mercado (Periodo)"})
    
    # Cruzamos los datos para generar el benchmark
    comparativa_cat = pd.merge(cat_global, cat_filtrado, on="merchant_category", how="left").fillna(0)

    fig2 = px.bar(
        comparativa_cat, 
        x="merchant_category", 
        y=["Total Mercado (Periodo)", "Filtro Seleccionado"],
        barmode="group",
        labels={"value": "Facturación (€)", "merchant_category": "Categoría", "variable": "Ámbito"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # =================================
    # VISUALIZACIÓN 3: RANGOS POR PERCENTIL
    # =================================
    st.subheader("Gasto por Categoría")
    
    df_rangos = df_filtrado.groupby('merchant_category')['amount'].agg([
        ('Percentil 25', lambda x: x.quantile(0.25)),
        ('Mediana (P50)', 'median'),
        ('Percentil 75', lambda x: x.quantile(0.75))
    ]).reset_index()

    fig3 = px.bar(
        df_rangos,
        x='merchant_category',
        y=['Percentil 25', 'Mediana (P50)', 'Percentil 75'],
        barmode='group',
        labels={'value': 'Importe (€)', 'merchant_category': 'Categoría', 'variable': 'Métrica'}
    )
    fig3.update_layout(hovermode="x unified")
    st.plotly_chart(fig4, use_container_width=True)

    # =================================
    # VISUALIZACIÓN 4 : CAMPAÑAS POR CATEGORÍA
    # =================================

    st.subheader("Análisis de Campañas por Categoría")
    st.markdown("_Esta gráfica muestra cómo se distribuye la facturación entre las distintas campañas para la categoría y fechas seleccionadas._")

    # Creamos un dataframe que aplique fechas y categoría, pero IGNORE el filtro de campaña lateral
    df_campanas = df_global_periodo.copy()
    if categoria != "Todos":
        df_campanas = df_campanas[df_campanas["merchant_category"] == categoria]

    facturacion_por_campana = (
        df_campanas.groupby("campaign_id")["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    fig_4 = px.bar(
        facturacion_por_campana,
        x="campaign_id",
        y="amount",
        title=f"Facturación por Campaña - Categoría: {categoria}",
        labels={"campaign_id": "Campaña", "amount": "Facturación Total (€)"},
        text_auto=",.0f" # Muestra el valor encima de las barras formateado
    )
 
    fig_4.update_traces(textposition="outside", marker_color="#1f77b4")
    fig_4.update_layout(xaxis_tickangle=-45)
    
    
    st.plotly_chart(fig_campanas, use_container_width=True)


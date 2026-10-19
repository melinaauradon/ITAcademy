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

# 1. Filtro de Tiempo (Rango de fechas)

timestamp_datetime = pd.to_datetime(df_full["timestamp"], errors="coerce")

fecha_minima = timestamp_datetime.min().date()
fecha_maxima = timestamp_datetime.max().date()


rango_fechas = st.sidebar.date_input(
    "Rango de Fechas",
    value=(fecha_minima, fecha_maxima), # Por defecto muestra todo el rango
    min_value=fecha_minima,
    max_value=fecha_maxima,
)

# Filtro de Campaña
campanas = ["Todos"] + sorted(
    df_full["campaign_id"].dropna().unique().tolist()
)
campana = st.sidebar.selectbox(
    "Campaña",
    campanas
)

# Filtro de Categoría
categorias = ["Todos"] + sorted(
    df_full["merchant_category"].dropna().unique().tolist()
)
categoria = st.sidebar.selectbox(
    "Categoría",
    categorias
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

# B) Aplicar filtro de Campaña
if campana != "Todos":
    df_filtrado = df_filtrado[df_filtrado["campaign_id"] == campana]

# C) Aplicar filtro de Categoría
if categoria != "Todos":
    df_filtrado = df_filtrado[df_filtrado["merchant_category"] == categoria]

# =================================
# INDICADORES PRINCIPALES (KPIs CORREGIDOS)
# =================================
st.subheader("📈 Análisis de Eficiencia Comercial")

facturacion = df_filtrado['amount'].sum()
total_tx = df_filtrado['id_tx'].nunique()

# 1. Ticket Medio Real (Evita el sesgo si una transacción tiene múltiples filas por producto)
ticket_medio = facturacion / total_tx if total_tx > 0 else 0

# 2. Descuento Eficiente (Calculado solo sobre transacciones que SÍ tuvieron promoción)
df_con_descuento = df_filtrado[df_filtrado['discount_amount'] > 0]
descuento_medio_real = df_con_descuento['discount_amount'].mean() if len(df_con_descuento) > 0 else 0

# 3. Porcentaje de penetración de las promociones
ratio_promocional = (df_con_descuento['id_tx'].nunique() / total_tx * 100) if total_tx > 0 else 0

# Renderizado de métricas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Facturación Total", f"{facturacion:,.0f} €".replace(",", "."))
with col2:
    st.metric("Ticket Medio Real", f"{ticket_medio:,.2f} €".replace(",", "."))
with col3:
    st.metric("Descuento Medio (Si aplica)", f"{descuento_medio_real:,.2f} €".replace(",", "."))
with col4:
    st.metric("% Ventas con Descuento", f"{ratio_promocional:,.1f} %")

st.markdown("---")

# Control de datos vacíos: si el cruce de filtros deja el dataset sin filas, frena errores visuales
if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles para la combinación de filtros seleccionada.")
else:
    # =================================
    # VISUALIZACIÓN 1 (YA APLICADA POR TI)
    # AFINIDAD DE CANAL POR CAMPAÑA
    # =================================
    st.subheader("🎯 Distribución Omnicanal")
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
        title="Análisis Omnicanal: Distribución de Campañas por Canal de Venta",
        labels={"campaign_id": "Campaña", "amount": "Facturación (€)", "channel": "Canal de Venta"},
        barmode="relative"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # =================================
    # VISUALIZACIÓN 2 & 3: COMPARATIVA VS MERCADO GLOBAL
    # (Evita el sesgo del filtro atrapado)
    # =================================
    st.subheader("🛍️ Análisis de Categorías: Filtro Actual vs Comportamiento Global")
    
    # Agrupamos la facturación del filtro activo
    cat_filtrado = df_filtrado.groupby("merchant_category")["amount"].sum().reset_index().rename(columns={"amount": "Filtro Seleccionado"})
    # Agrupamos la facturación del periodo completo (sin el filtro de campaña/categoría lateral)
    cat_global = df_global_periodo.groupby("merchant_category")["amount"].sum().reset_index().rename(columns={"amount": "Total Mercado (Periodo)"})
    
    # Cruzamos los datos para generar el benchmark
    comparativa_cat = pd.merge(cat_global, cat_filtrado, on="merchant_category", how="left").fillna(0)

    fig3 = px.bar(
        comparativa_cat, 
        x="merchant_category", 
        y=["Total Mercado (Periodo)", "Filtro Seleccionado"],
        barmode="group",
        title="Aporte del Filtro/Campaña seleccionado al Total de cada Categoría",
        labels={"value": "Facturación (€)", "merchant_category": "Categoría", "variable": "Ámbito"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # =================================
    # VISUALIZACIÓN 4: RANGOS POR PERCENTIL
    # (Sustituye a Min/Max para eliminar ruidos y Outliers)
    # =================================
    st.subheader("📊 Distribución Real del Gasto por Categoría (Sin Outliers)")
    st.markdown("_Esta gráfica muestra los percentiles 25, 50 (Mediana) y 75 para entender el rango de compra del 50% central de los clientes, esquivando transacciones anómalas._")

    df_rangos = df_filtrado.groupby('merchant_category')['amount'].agg([
        ('Percentil 25', lambda x: x.quantile(0.25)),
        ('Mediana (P50)', 'median'),
        ('Percentil 75', lambda x: x.quantile(0.75))
    ]).reset_index()

    fig4 = px.bar(
        df_rangos,
        x='merchant_category',
        y=['Percentil 25', 'Mediana (P50)', 'Percentil 75'],
        barmode='group',
        title='Rango de Compra Típico por Categoría',
        labels={'value': 'Importe (€)', 'merchant_category': 'Categoría', 'variable': 'Métrica'}
    )
    fig4.update_layout(hovermode="x unified")
    st.plotly_chart(fig4, use_container_width=True)

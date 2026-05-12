import pandas as pd
import streamlit as st
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================

st.set_page_config(
    page_title="Monitor de Potenciómetro ESP32",
    page_icon="🎛️",
    layout="wide"
)

# ==========================================
# ESTILOS PERSONALIZADOS
# ==========================================

st.markdown("""
<style>

.main {
    padding: 2rem;
}

h1 {
    color: #00ADB5;
}

.metric-box {
    background-color: #222831;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# TÍTULO
# ==========================================

st.title("🎛️ Monitor de Potenciómetro ESP32")

# ==========================================
# INTRODUCCIÓN DEL SISTEMA
# ==========================================

st.markdown("""
## 🔎 ¿Qué hace este sistema?

Este proyecto utiliza un **potenciómetro conectado a un ESP32** para realizar lecturas analógicas en tiempo real.

El potenciómetro funciona como una **resistencia variable**, permitiendo modificar manualmente el voltaje que recibe el microcontrolador.  
El ESP32 convierte esta señal analógica en valores digitales dentro de un rango de **0 a 4095**, utilizando su convertidor ADC de 12 bits.

Posteriormente:

- El ESP32 procesa la lectura.
- Convierte el valor a porcentaje.
- Envía los datos mediante WiFi.
- Almacena la información en InfluxDB.
- Streamlit visualiza y analiza los datos obtenidos.

La interfaz permite observar gráficas, estadísticas y filtros para analizar el comportamiento del potenciómetro en tiempo real.
""")

# ==========================================
# INFORMACIÓN DEL SISTEMA
# ==========================================

with st.expander("ℹ️ Información del Sistema"):

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Hardware")
        st.write("- Microcontrolador: ESP32")
        st.write("- Sensor: Potenciómetro")
        st.write("- Entrada analógica: GPIO 34")
        st.write("- Resolución ADC: 12 bits")

    with col2:
        st.write("### Comunicación")
        st.write("- Base de datos: InfluxDB")
        st.write("- Frecuencia de muestreo: 2 segundos")
        st.write("- Red: WiFi")
        st.write("- Variable medida: Porcentaje de posición")

# ==========================================
# FUNCIÓN EXPLICATIVA DEL POTENCIÓMETRO
# ==========================================

def explicar_potenciometro(valor_porcentaje):

    if valor_porcentaje <= 20:
        return (
            "🔵 El potenciómetro se encuentra en un nivel BAJO. "
            "La resistencia variable permite un paso reducido de señal "
            "eléctrica hacia el ESP32."
        )

    elif valor_porcentaje <= 40:
        return (
            "🟢 El potenciómetro está en un nivel MEDIO-BAJO. "
            "El voltaje analógico comienza a incrementarse de manera gradual."
        )

    elif valor_porcentaje <= 60:
        return (
            "🟡 El potenciómetro está en un nivel MEDIO. "
            "El ESP32 recibe aproximadamente la mitad del rango analógico disponible."
        )

    elif valor_porcentaje <= 80:
        return (
            "🟠 El potenciómetro se encuentra en un nivel MEDIO-ALTO. "
            "La señal analógica enviada al ESP32 es elevada."
        )

    else:
        return (
            "🔴 El potenciómetro está en un nivel ALTO. "
            "La lectura analógica está cercana al máximo permitido por el ADC del ESP32."
        )

# ==========================================
# CARGA DE CSV
# ==========================================

uploaded_file = st.file_uploader(
    "📂 Cargar archivo CSV exportado desde InfluxDB",
    type=["csv"]
)

# ==========================================
# PROCESAMIENTO
# ==========================================

if uploaded_file is not None:

    try:

        df = pd.read_csv(uploaded_file)

        # ==========================================
        # DETECTAR COLUMNAS
        # ==========================================

        time_col = None

        for col in df.columns:
            if "time" in col.lower():
                time_col = col
                break

        variable_col = None

        for col in df.columns:
            if "porcentaje" in col.lower():
                variable_col = col
                break

        if variable_col is None:
            variable_col = df.columns[1]

        # ==========================================
        # PREPARAR DATOS
        # ==========================================

        df = df.rename(columns={variable_col: "porcentaje"})

        if time_col:
            df[time_col] = pd.to_datetime(df[time_col])
            df = df.set_index(time_col)

        # ==========================================
        # MÉTRICAS PRINCIPALES
        # ==========================================

        st.subheader("📌 Métricas en Tiempo Real")

        col1, col2, col3, col4 = st.columns(4)

        valor_actual = df["porcentaje"].iloc[-1]
        valor_max = df["porcentaje"].max()
        valor_min = df["porcentaje"].min()
        promedio = df["porcentaje"].mean()

        col1.metric("Valor Actual", f"{valor_actual:.2f}%")
        col2.metric("Máximo", f"{valor_max:.2f}%")
        col3.metric("Mínimo", f"{valor_min:.2f}%")
        col4.metric("Promedio", f"{promedio:.2f}%")

        # ==========================================
        # INTERPRETACIÓN AUTOMÁTICA
        # ==========================================

        st.subheader("🧠 Interpretación de la Lectura")

        explicacion = explicar_potenciometro(valor_actual)

        st.info(explicacion)

        # ==========================================
        # TABS
        # ==========================================

        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Gráficas",
            "📊 Estadísticas",
            "🎚️ Filtros",
            "🛰️ Sistema"
        ])

        # ==========================================
        # TAB 1 - GRÁFICAS
        # ==========================================

        with tab1:

            st.subheader("Visualización del Potenciómetro")

            tipo = st.selectbox(
                "Tipo de gráfica",
                ["Línea", "Área", "Barra"]
            )

            if tipo == "Línea":
                st.line_chart(df["porcentaje"])

            elif tipo == "Área":
                st.area_chart(df["porcentaje"])

            else:
                st.bar_chart(df["porcentaje"])

            st.write("### Datos Recientes")
            st.dataframe(df.tail(10))

        # ==========================================
        # TAB 2 - ESTADÍSTICAS
        # ==========================================

        with tab2:

            st.subheader("Análisis Estadístico")

            st.dataframe(df["porcentaje"].describe())

            st.write("### Distribución de Valores")

            st.bar_chart(
                df["porcentaje"].value_counts(bins=10)
            )

        # ==========================================
        # TAB 3 - FILTROS
        # ==========================================

        with tab3:

            st.subheader("Filtrado de Datos")

            min_val = float(df["porcentaje"].min())
            max_val = float(df["porcentaje"].max())

            rango = st.slider(
                "Seleccionar rango",
                min_val,
                max_val,
                (min_val, max_val)
            )

            filtrado = df[
                (df["porcentaje"] >= rango[0]) &
                (df["porcentaje"] <= rango[1])
            ]

            st.write(f"Registros encontrados: {len(filtrado)}")

            st.dataframe(filtrado)

            st.download_button(
                label="⬇️ Descargar CSV Filtrado",
                data=filtrado.to_csv().encode("utf-8"),
                file_name="potenciometro_filtrado.csv",
                mime="text/csv"
            )

        # ==========================================
        # TAB 4 - SISTEMA
        # ==========================================

        with tab4:

            st.subheader("Información del Dispositivo")

            st.write("### ESP32")
            st.write("- Dispositivo IoT conectado vía WiFi")
            st.write("- Envía datos a InfluxDB cada 2 segundos")

            st.write("### Potenciómetro")
            st.write("- Rango ADC: 0 - 4095")
            st.write("- Conversión a porcentaje")
            st.write("- Entrada analógica GPIO34")

            st.write("### Base de Datos")
            st.write("- Plataforma: InfluxDB Cloud")
            st.write("- Bucket: Clase1")

    except Exception as e:

        st.error(f"Error procesando archivo: {str(e)}")

else:

    st.info("👆 Cargue un archivo CSV exportado desde InfluxDB.")

# ==========================================
# FOOTER
# ==========================================

st.markdown("""
---
### Proyecto IoT - ESP32 + InfluxDB + Streamlit

Sistema de monitoreo analógico usando potenciómetro y visualización web.
""")

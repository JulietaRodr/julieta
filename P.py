import streamlit as st
import yfinance as yf
import altair as alt
import pandas as pd
import google.generativeai as genai
import numpy as np
import plotly.express as px
from datetime import datetime
from pandas.tseries.offsets import DateOffset
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configurar la API Key para Generative AI
TOKEN_GENAI = os.getenv("TOKEN_GENAI")
if TOKEN_GENAI:
    genai.configure(api_key=TOKEN_GENAI)
    model = genai.GenerativeModel("models/gemini-1.5-pro")
else:
    st.warning("⚠️ La API Key de Generative AI no está configurada. Algunas funcionalidades estarán limitadas.")

# Estilo general
dark_brown = "#3e1f14"
light_beige = "#fff5e6"
light_pink = "#f3c1c6"
pale_gold = "#d4a373"
girly_placeholder = "#a1887f"
bright_pink = "#e88f9c"

# CSS personalizado
theme_css = f"""
<style>
body, .main, .block-container {{
  background-color: {light_beige};
  color: {dark_brown};
}}
h1, h2, h3, h4, h5, h6, p, li, span, div, label, table, th, td {{
  color: {dark_brown} !important;
}}
[data-testid="stSidebar"] {{
  background-color: #fff1dc;
  color: {dark_brown};
}}
[data-testid="stMetricDelta"] {{
  color: {bright_pink};
}}
input, .stTextInput > div > input, .stButton > button {{
  background-color: #fffaf2;
  color: {dark_brown};
  border-color: {pale_gold};
}}
.stButton > button {{
  background-color: {bright_pink};
  color: white;
  border: 2px solid {dark_brown};
  font-weight: bold;
  transition: 0.3s;
  padding: 10px 20px;
  border-radius: 10px;
}}
.stButton > button:hover {{
  background-color: #f7d6db;
  color: {dark_brown};
}}
.stSelectbox > div > div {{
  background-color: white !important;
  color: {dark_brown} !important;
  border: 2px solid {dark_brown} !important;
  padding: 10px !important;
  border-radius: 8px !important;
}}
th {{
  background-color: #f3c1c6;
  font-weight: bold;
}}
td {{
  border-top: 1px solid {dark_brown};
  padding: 10px;
}}
</style>
"""

# Aplicar tema
st.set_page_config(page_title="🌸 Exploradora de Acciones con Estilo", layout="wide")
st.markdown(theme_css, unsafe_allow_html=True)

# Menú lateral con nueva opción de portafolio
menu = st.sidebar.radio("🌟 Menú", ["🔍 Análisis de empresa", "📰 Buscar noticias", "💼 Portafolio de Inversión"])

if menu == "🔍 Análisis de empresa":
    st.title("💗 Exploradora de Acciones para Mujeres Inversionistas")
    st.markdown("Bienvenida a tu espacio financiero ✨\nAnaliza acciones con estilo, confianza y claridad 💖")

    # Input para símbolo bursátil y período
    ticker_input = st.text_input("🔍 Escribe el símbolo bursátil (Ej. AAPL, MSFT, TSLA...):", placeholder="Ej. AAPL")
    periodo = st.selectbox("🕒 Periodo a analizar:", ["6mo", "1y", "5y", "max"], index=0)

    if st.button("✨ Analizar empresa"):
        if ticker_input.strip():
            try:
                ticker = yf.Ticker(ticker_input.strip().upper())
                info = ticker.info

                if not info or info.get("regularMarketPrice") is None:
                    st.warning("🚫 No pudimos encontrar ese símbolo. ¡Revisa que esté bien escrito!")
                else:
                    nombre = info.get("longName", "Nombre no disponible")
                    descripcion = info.get("longBusinessSummary", "Descripción no disponible")
                    sector = info.get("sector", "No disponible")
                    industria = info.get("industry", "No disponible")
                    pais = info.get("country", "No disponible")
                    logo = info.get("logo_url", "")

                    st.markdown(f"## 💼 {nombre}")
                    if logo:
                        st.image(logo, width=120)

                    prompt = f"""Traduce y adapta el siguiente texto al español profesional, cálido y fácil de entender para mujeres que están aprendiendo sobre inversiones:\n\nDescripción:\n{descripcion}\n\nSector: {sector}\nIndustria: {industria}\nPaís: {pais}"""
                    try:
                        if model:
                            respuesta = model.generate_content(prompt)
                            traducido = respuesta.text
                        else:
                            traducido = descripcion
                    except Exception:
                        traducido = descripcion

                    with st.expander("🌷 ¿Qué hace esta empresa?", expanded=True):
                        st.markdown(traducido)

                    st.subheader("📊 Datos financieros clave")
                    claves = {
                        "📈 Precio actual": f"${info.get('regularMarketPrice', 'NA')}",
                        "🔄 Cambio diario": f"{info.get('regularMarketChangePercent', 0):.2f}%",
                        "🏢 Capitalización de mercado": info.get("marketCap", "NA"),
                        "📦 Volumen (hoy)": info.get("volume", "NA"),
                        "📊 Volumen promedio (30 días)": info.get("averageVolume", "NA"),
                        "📚 Ratio P/E": info.get("trailingPE", "NA"),
                        "💵 Ganancias por acción (EPS)": info.get("trailingEps", "NA"),
                        "📉 Beta (volatilidad histórica)": info.get("beta", "NA"),
                        "🗓️ Próximo reporte de resultados": info.get("earningsDate", "NA")
                    }
                    st.table(pd.DataFrame.from_dict(claves, orient="index", columns=["Valor estimado"]))

                    hist = ticker.history(period=periodo).reset_index()
                    hist["MA20"] = hist["Close"].rolling(window=20).mean()

                    st.subheader("📈 Evolución del precio y volumen")
                    precio = alt.Chart(hist).mark_line(color="#e88f9c").encode(x="Date:T", y="Close:Q")
                    promedio = alt.Chart(hist).mark_line(strokeDash=[4, 4], color="#d4a373").encode(x="Date:T", y="MA20:Q")
                    volumen = alt.Chart(hist).mark_bar(opacity=0.3).encode(x="Date:T", y=alt.Y("Volume:Q", title="Volumen"))
                    st.altair_chart((precio + promedio) & volumen, use_container_width=True)

                    st.subheader("📆 Rendimiento anual compuesto (CAGR)")
                    hoy = hist["Date"].max()
                    rendimiento = {"Periodo": [], "CAGR": []}

                    def calcular_cagr(p0, pf, años):
                        if p0 > 0 and años > 0:
                            return (pf / p0) ** (1 / años) - 1
                        return None

                    for años in [1, 3, 5]:
                        fecha_inicio = hoy - DateOffset(years=años)
                        datos = hist[hist["Date"] >= fecha_inicio]
                        if not datos.empty:
                            p0, pf = datos.iloc[0]["Close"], datos.iloc[-1]["Close"]
                            cagr = calcular_cagr(p0, pf, años)
                            rendimiento["Periodo"].append(f"{años} año(s)")
                            rendimiento["CAGR"].append(f"{cagr*100:.2f}%" if cagr else "No disponible")
                        else:
                            rendimiento["Periodo"].append(f"{años} año(s)")
                            rendimiento["CAGR"].append("No disponible")

                    st.dataframe(pd.DataFrame(rendimiento))

                    st.subheader("💫 Volatilidad del precio")
                    rend_diarios = hist["Close"].pct_change()
                    std_anual = np.std(rend_diarios) * np.sqrt(252)
                    st.metric("Desviación estándar anualizada", f"{std_anual * 100:.2f}%")

                    st.subheader("📉 Gráfica de cierre con línea de tendencia")
                    fig = px.line(hist, x="Date", y="Close", title="Precio de cierre con línea de tendencia", line_shape="linear")
                    fig.update_traces(line=dict(color=bright_pink))
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
        else:
            st.warning("🔔 Ingresa un símbolo para analizar.")
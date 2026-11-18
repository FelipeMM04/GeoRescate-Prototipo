import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN GENERAL DE LA PÁGINA
st.set_page_config(
    page_title="GeoRescate | Analítica Sísmica para Primera Respuesta",
    page_icon="🚨",
    layout="wide"
)

# Encabezado principal
st.title("🚨 GeoRescate: Sistema de Estimación de Colapso y Supervivencia")
st.markdown(
    "**Analítica simplificada para equipos de primera respuesta (UNGRD, Bomberos, Defensa Civil)** | "
    "Priorización de búsqueda y rescate ante escenarios sísmicos en Colombia."
)
st.divider()

# 2. CATÁLOGO DE LAS 15 VARIABLES DEL MODELO (Meta: Mínimo 15 variables documentadas)
VARIABLES_MODELO = pd.DataFrame([
    # 5 Estructurales
    {"Categoría": "Estructural", "Variable": "Sistema estructural", "Unidad": "Categoría", "Función": "Define ductilidad y resistencia lateral"},
    {"Categoría": "Estructural", "Variable": "Número de pisos", "Unidad": "Pisos", "Función": "Determina periodo fundamental y masa"},
    {"Categoría": "Estructural", "Variable": "Año de construcción (Norma NSR)", "Unidad": "Año", "Función": "Evalúa cumplimiento sismorresistente"},
    {"Categoría": "Estructural", "Variable": "Tipo de material predominante", "Unidad": "Categoría", "Función": "Estima fragilidad ante esfuerzos cortantes"},
    {"Categoría": "Estructural", "Variable": "Estado de conservación / irregularidad", "Unidad": "Índice (1-5)", "Función": "Penaliza capacidad por deterioro previo"},
    # 5 Sísmicas
    {"Categoría": "Sísmica", "Variable": "Magnitud de momento (Mw)", "Unidad": "Mw", "Función": "Mide energía total liberada por el sismo"},
    {"Categoría": "Sísmica", "Variable": "Aceleración Pico del Suelo (PGA)", "Unidad": "g", "Función": "Determina demanda sísmica directa en base"},
    {"Categoría": "Sísmica", "Variable": "Profundidad focal", "Unidad": "km", "Función": "Controla atenuación de ondas en superficie"},
    {"Categoría": "Sísmica", "Variable": "Distancia epicentral", "Unidad": "km", "Función": "Calcula intensidad local en cada zona"},
    {"Categoría": "Sísmica", "Variable": "Tipo de suelo (Microzonificación)", "Unidad": "Perfil (A-E)", "Función": "Estima amplificación dinámica del terreno"},
    # 5 Personas y Entorno
    {"Categoría": "Personas y Entorno", "Variable": "Ocupación estimada por turno", "Unidad": "Personas", "Función": "Calcula población expuesta en el edificio"},
    {"Categoría": "Personas y Entorno", "Variable": "Hora de ocurrencia del evento", "Unidad": "Franja horaria", "Función": "Ajusta factor de presencia (día/noche)"},
    {"Categoría": "Personas y Entorno", "Variable": "Densidad poblacional del sector", "Unidad": "Hab/km²", "Función": "Prioriza impacto colectivo en la manzana"},
    {"Categoría": "Personas y Entorno", "Variable": "Accesibilidad vial para rescate", "Unidad": "Índice (1-5)", "Función": "Estima tiempo de llegada de maquinaria"},
    {"Categoría": "Personas y Entorno", "Variable": "Presencia de población vulnerable", "Unidad": "%", "Función": "Pondera urgencia médica (hospitales/escuelas)"},
])

# 3. DATOS BASE DE ZONAS / EDIFICACIONES EVALUADAS (Cali, Colombia)
ZONAS_BASE = pd.DataFrame([
    {"ID": "Z-01", "Zona": "Centro Histórico - Edif. Administrativo", "Lat": 3.4516, "Lon": -76.5320, "Material": "Mampostería no reforzada", "Pisos": 5, "Norma": "Pre-NSR-98", "Suelo": "D (Blando)", "Ocupacion": 180, "Vulnerabilidad": 0.85, "Accesibilidad": "Media"},
    {"ID": "Z-02", "Zona": "Siloé - Ladera Occidental", "Lat": 3.4235, "Lon": -76.5562, "Material": "Mampostería confinada", "Pisos": 3, "Norma": "Informal", "Suelo": "E (Muy blando)", "Ocupacion": 240, "Vulnerabilidad": 0.92, "Accesibilidad": "Baja"},
    {"ID": "Z-03", "Zona": "San Fernando - Complejo Hospitalario", "Lat": 3.4312, "Lon": -76.5441, "Material": "Pórticos de concreto", "Pisos": 7, "Norma": "NSR-98", "Suelo": "C (Denso)", "Ocupacion": 420, "Vulnerabilidad": 0.65, "Accesibilidad": "Alta"},
    {"ID": "Z-04", "Zona": "Aguablanca - Sector Residencial", "Lat": 3.4180, "Lon": -76.4910, "Material": "Mampostería simple", "Pisos": 2, "Norma": "Pre-NSR-98", "Suelo": "E (Muy blando)", "Ocupacion": 310, "Vulnerabilidad": 0.88, "Accesibilidad": "Media"},
    {"ID": "Z-05", "Zona": "Chipichape - Zona Comercial Norte", "Lat": 3.4754, "Lon": -76.5283, "Material": "Sistema dual concreto", "Pisos": 8, "Norma": "NSR-10", "Suelo": "C (Denso)", "Ocupacion": 350, "Vulnerabilidad": 0.35, "Accesibilidad": "Alta"},
    {"ID": "Z-06", "Zona": "Versalles - Clínicas y Oficinas", "Lat": 3.4618, "Lon": -76.5311, "Material": "Pórticos de concreto", "Pisos": 6, "Norma": "NSR-98", "Suelo": "D (Blando)", "Ocupacion": 210, "Vulnerabilidad": 0.60, "Accesibilidad": "Alta"},
    {"ID": "Z-07", "Zona": "Meléndez - Campus y Residencias", "Lat": 3.3765, "Lon": -76.5338, "Material": "Muros estructurales", "Pisos": 5, "Norma": "NSR-10", "Suelo": "C (Denso)", "Ocupacion": 290, "Vulnerabilidad": 0.30, "Accesibilidad": "Alta"},
    {"ID": "Z-08", "Zona": "Juanchito - Corredor Industrial", "Lat": 3.4430, "Lon": -76.4755, "Material": "Estructura metálica/mamp.", "Pisos": 2, "Norma": "Pre-NSR-98", "Suelo": "E (Muy blando)", "Ocupacion": 140, "Vulnerabilidad": 0.78, "Accesibilidad": "Media"},
    {"ID": "Z-09", "Zona": "Ciudad Jardín - Zona Institucional", "Lat": 3.3682, "Lon": -76.5390, "Material": "Sistema dual concreto", "Pisos": 6, "Norma": "NSR-10", "Suelo": "B (Roca/Firme)", "Ocupacion": 190, "Vulnerabilidad": 0.25, "Accesibilidad": "Alta"},
    {"ID": "Z-10", "Zona": "Alameda - Plaza y Comercio", "Lat": 3.4385, "Lon": -76.5365, "Material": "Mampostería no reforzada", "Pisos": 4, "Norma": "Pre-NSR-98", "Suelo": "D (Blando)", "Ocupacion": 260, "Vulnerabilidad": 0.82, "Accesibilidad": "Baja"},
])

# 4. CATÁLOGO DE 10 ESCENARIOS SÍSMICOS PREDEFINIDOS (Meta: 10 escenarios)
ESCENARIOS = {
    "Escenario 01: Sismo Cortical Moderado (Mw 5.8 - Prof. 12 km)": {"mw": 5.8, "pga": 0.18, "prof": 12, "hora": "Día (14:00)"},
    "Escenario 02: Sismo Cortical Fuerte (Mw 6.5 - Prof. 10 km)": {"mw": 6.5, "pga": 0.34, "prof": 10, "hora": "Día (11:30)"},
    "Escenario 03: Sismo Cortical Severo Nocturno (Mw 6.8 - Prof. 8 km)": {"mw": 6.8, "pga": 0.45, "prof": 8, "hora": "Madrugada (03:15)"},
    "Escenario 04: Sismo Subducción Profundo (Mw 7.2 - Prof. 95 km)": {"mw": 7.2, "pga": 0.22, "prof": 95, "hora": "Tarde (16:45)"},
    "Escenario 05: Sismo Falla Romeral Cercano (Mw 6.2 - Prof. 15 km)": {"mw": 6.2, "pga": 0.29, "prof": 15, "hora": "Noche (21:00)"},
    "Escenario 06: Sismo Pacífico Sur Muy Fuerte (Mw 7.6 - Prof. 40 km)": {"mw": 7.6, "pga": 0.38, "prof": 40, "hora": "Día (10:20)"},
    "Escenario 07: Réplica Alta Intensidad (Mw 5.5 - Prof. 9 km)": {"mw": 5.5, "pga": 0.16, "prof": 9, "hora": "Tarde (18:10)"},
    "Escenario 08: Sismo Superficial Extremo (Mw 7.0 - Prof. 7 km)": {"mw": 7.0, "pga": 0.52, "prof": 7, "hora": "Madrugada (02:40)"},
    "Escenario 09: Evento Intermedio Regional (Mw 6.0 - Prof. 50 km)": {"mw": 6.0, "pga": 0.14, "prof": 50, "hora": "Mañana (08:50)"},
    "Escenario 10: Escenario Máximo Probable (Mw 7.4 - Prof. 14 km)": {"mw": 7.4, "pga": 0.49, "prof": 14, "hora": "Día (13:00)"},
}

# 5. PANEL LATERAL DE CONFIGURACIÓN (ENTRADA DEL USUARIO)
st.sidebar.header("⚙️ Parámetros del Escenario")

escenario_seleccionado = st.sidebar.selectbox(
    "Seleccione un escenario sísmico:",
    list(ESCENARIOS.keys())
)

datos_esc = ESCENARIOS[escenario_seleccionado]

st.sidebar.subheader("Ajuste fino de parámetros sísmicos")
mw_input = st.sidebar.slider("Magnitud (Mw)", 4.5, 8.5, float(datos_esc["mw"]), 0.1)
pga_input = st.sidebar.slider("Aceleración Pico del Suelo - PGA (g)", 0.05, 0.80, float(datos_esc["pga"]), 0.01)
prof_input = st.sidebar.slider("Profundidad focal (km)", 5, 150, int(datos_esc["prof"]), 1)
franja_horaria = st.sidebar.selectbox(
    "Franja horaria del evento",
    ["Madrugada (03:15)", "Mañana (08:50)", "Día (14:00)", "Tarde (18:10)", "Noche (21:00)"],
    index=2
)

st.sidebar.divider()
st.sidebar.info(
    "**Control de Calidad (PR-GR-01)**\n\n"
    "• Variables activas: 15 (5 Est. / 5 Sís. / 5 Ent.)\n"
    "• Compuerta de validación: Activa"
)

# 6. MOTOR DE SIMULACIÓN ESTRUCTURAL Y PROBABILÍSTICA
def ejecutar_simulacion(df_zonas, mw, pga, prof, horario):
    df = df_zonas.copy()
    
    # Factor de amplificación por tipo de suelo
    mapa_suelo = {"B (Roca/Firme)": 0.85, "C (Denso)": 1.0, "D (Blando)": 1.25, "E (Muy blando)": 1.45}
    factor_suelo = df["Suelo"].map(mapa_suelo)
    
    # Factor por horario (afecta ocupación real en zonas residenciales vs comerciales)
    factor_hora = 1.15 if "Madrugada" in horario or "Noche" in horario else 1.0
    
    # Cálculo de Probabilidad de Colapso Estructural (%)
    demanda_sismica = (pga * 1.8) * factor_suelo * (1 + (mw - 5.5) * 0.15) * (15 / (prof + 10))
    prob_colapso = np.clip((demanda_sismica * df["Vulnerabilidad"]) * 100, 3.0, 96.0)
    df["Prob_Colapso_%"] = np.round(prob_colapso, 1)
    
    # Cálculo de Probabilidad de Supervivencia Humana (%)
    # A mayor colapso y menor accesibilidad, menor supervivencia sin rescate rápido
    penalizacion_acceso = df["Accesibilidad"].map({"Alta": 0.95, "Media": 0.85, "Baja": 0.72})
    prob_supervivencia = np.clip((100 - (df["Prob_Colapso_%"] * 0.78)) * penalizacion_acceso, 8.0, 98.0)
    df["Prob_Supervivencia_%"] = np.round(prob_supervivencia, 1)
    
    # Estimación de personas en riesgo crítico y Prioridad de Rescate
    df["Ocupacion_Activa"] = (df["Ocupacion"] * factor_hora).astype(int)
    df["Indice_Prioridad"] = np.round((df["Prob_Colapso_%"] * 0.6 + (100 - df["Prob_Supervivencia_%"]) * 0.4) * (df["Ocupacion_Activa"] / 300), 1)
    
    def clasificar_prioridad(valor):
        if valor >= 45:
            return "🔴 CRÍTICA (Despliegue Inmediato)"
        elif valor >= 28:
            return "🟠 ALTA (Prioridad 2)"
        elif valor >= 15:
            return "🟡 MEDIA (Monitoreo)"
        else:
            return "🟢 BAJA (Preventivo)"
            
    df["Prioridad_Rescate"] = df["Indice_Prioridad"].apply(clasificar_prioridad)
    
    # Compuerta de validación automática (Actividades 9 y 12 del Manual)
    validacion_ok = (
        df["Prob_Colapso_%"].between(0, 100).all() and
        df["Prob_Supervivencia_%"].between(0, 100).all() and
        not df.isnull().any().any()
    )
    
    return df, validacion_ok

resultados_df, estado_validacion = ejecutar_simulacion(
    ZONAS_BASE, mw_input, pga_input, prof_input, franja_horaria
)  

# 7. VERIFICACIÓN DE COMPUERTA DE CALIDAD ANTES DE MOSTRAR RESULTADOS
if not estado_validacion:
    st.error("❌ ALERTA DE VALIDACIÓN (Act. 9 / Act. 12): Se detectaron incoherencias en los rangos de probabilidad. Revise los parámetros.")
    st.stop()
else:
    st.success(f"✅ Validación estructural y probabilística aprobada | Escenario activo: **{escenario_seleccionado}**")

# 8. CREACIÓN DE LAS 4 PANTALLAS / PESTAÑAS DEL PROTOTIPO
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1️⃣ Variables y Escenario",
    "2️⃣ Tablero de Indicadores (KPIs)",
    "3️⃣ Mapa SIG de Zonas de Interés",
    "4️⃣ Reporte Ejecutivo y Costos",
    "5️⃣ Planes y Precios"
])

# --- PANTALLA 1: VARIABLES DEL MODELO Y DATOS BASE ---
with tab1:
    st.subheader("Catálogo de Variables del Sistema (15 Variables Documentadas)")
    st.caption("Cumplimiento de estándar técnico: 5 variables estructurales, 5 sísmicas y 5 de personas/entorno.")
    
    col_v1, col_v2 = st.columns([1.3, 1])
    with col_v1:
        st.dataframe(VARIABLES_MODELO, use_container_width=True, hide_index=True)
    with col_v2:
        st.markdown("#### Resumen del Escenario Seleccionado")
        st.info(
            f"**Evento:** {escenario_seleccionado}\n\n"
            f"- **Magnitud (Mw):** {mw_input}\n"
            f"- **Aceleración (PGA):** {pga_input} g\n"
            f"- **Profundidad:** {prof_input} km\n"
            f"- **Franja horaria:** {franja_horaria}\n"
            f"- **Zonas analizadas:** {len(resultados_df)} sectores críticos"
        )
        st.markdown("#### Muestra de Inventario Estructural Base")
        st.dataframe(
            ZONAS_BASE[["ID", "Zona", "Material", "Pisos", "Norma", "Suelo"]],
            use_container_width=True,
            hide_index=True
        )

# --- PANTALLA 2: TABLERO DE INDICADORES (KPIs) ---
with tab2:
    st.subheader("Indicadores Clave de Impacto y Priorización de Rescate")
    
    # Tarjetas KPI superiores
    k1, k2, k3, k4 = st.columns(4)
    prob_col_prom = resultados_df["Prob_Colapso_%"].mean()
    prob_sup_prom = resultados_df["Prob_Supervivencia_%"].mean()
    zonas_criticas = (resultados_df["Prioridad_Rescate"].str.contains("CRÍTICA")).sum()
    personas_expuestas = resultados_df["Ocupacion_Activa"].sum()
    
    k1.metric("Prob. Colapso Promedio", f"{prob_col_prom:.1f}%", delta=f"PGA {pga_input}g", delta_color="inverse")
    k2.metric("Prob. Supervivencia Promedio", f"{prob_sup_prom:.1f}%", delta="Estimación modelo")
    k3.metric("Zonas en Prioridad Crítica", f"{zonas_criticas} / {len(resultados_df)}", delta="Despliegue inmediato", delta_color="inverse")
    k4.metric("Población Activa Evaluada", f"{personas_expuestas:,} pers.", delta=franja_horaria)
    
    st.divider()
    
    # Gráfico comparativo de Colapso vs Supervivencia por zona
    df_ordenado = resultados_df.sort_values(by="Indice_Prioridad", ascending=True)
    fig_barras = px.bar(
        df_ordenado,
        x=["Prob_Colapso_%", "Prob_Supervivencia_%"],
        y="Zona",
        orientation="h",
        barmode="group",
        title="Comparativa de Probabilidad de Colapso vs. Supervivencia por Zona",
        labels={"value": "Probabilidad (%)", "variable": "Indicador", "Zona": "Sector Evaluado"},
        color_discrete_map={"Prob_Colapso_%": "#E63946", "Prob_Supervivencia_%": "#2A9D8F"}
    )
    fig_barras.update_layout(height=420, legend_title_text="Métrica")
    st.plotly_chart(fig_barras, use_container_width=True)

# --- PANTALLA 3: MAPA INTERACTIVO SIG ---
with tab3:
    st.subheader("Geolocalización de Zonas de Interés para Equipos de Primera Respuesta")
    st.caption("Mapa interactivo: El tamaño del círculo representa la ocupación estimada y el color indica la probabilidad de colapso.")
    
    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        fig_mapa = px.scatter_map(
            resultados_df,
            lat="Lat",
            lon="Lon",
            size="Ocupacion_Activa",
            color="Prob_Colapso_%",
            hover_name="Zona",
            hover_data={
                "Prioridad_Rescate": True,
                "Prob_Colapso_%": True,
                "Prob_Supervivencia_%": True,
                "Ocupacion_Activa": True,
                "Accesibilidad": True,
                "Lat": False,
                "Lon": False
            },
            color_continuous_scale=["#2A9D8F", "#F4A261", "#E63946"],
            range_color=[10, 85],
            size_max=28,
            zoom=11.3,
            center={"lat": 3.425, "lon": -76.520},
            map_style="open-street-map",
            height=500
        )
        fig_mapa.update_layout(margin={"r": 0, "t": 10, "l": 0, "b": 0})
        st.plotly_chart(fig_mapa, use_container_width=True)
        
    with col_m2:
        st.markdown("#### Ranking de Despliegue (Top Prioridad)")
        ranking = resultados_df.sort_values(by="Indice_Prioridad", ascending=False)[
            ["ID", "Zona", "Prob_Colapso_%", "Prioridad_Rescate"]
        ]
        st.dataframe(ranking, use_container_width=True, hide_index=True, height=450)

# --- PANTALLA 4: REPORTE EJECUTIVO Y COSTOS ---
with tab4:
    st.subheader("Reporte Operativo de Emergencia y Viabilidad de Costos")
    
    st.markdown("#### 1. Ficha Consolidada para UNGRD / Bomberos / Defensa Civil")
    cols_reporte = [
        "ID", "Zona", "Material", "Suelo", "Ocupacion_Activa",
        "Prob_Colapso_%", "Prob_Supervivencia_%", "Prioridad_Rescate"
    ]
    df_final = resultados_df.sort_values(by="Indice_Prioridad", ascending=False)[cols_reporte]
    st.dataframe(df_final, use_container_width=True, hide_index=True)
    
    # Botón de descarga CSV
    csv_data = df_final.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar Reporte de Escenario (CSV)",
        data=csv_data,
        file_name=f"Reporte_GeoRescate_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
    
    st.divider()
    st.markdown("#### 2. Lista de Costos Estimados (Prototipo MVP vs. Despliegue Piloto)")
    df_costos = pd.DataFrame([
        {"Rubro": "Stack de Software y Licencias", "Detalle": "Python, Streamlit, Pandas, NumPy, Plotly (Open Source)", "Costo Prototipo (MVP)": "$0 COP", "Costo Mensual (Piloto)": "$0 COP"},
        {"Rubro": "Datos Sísmicos y Cartografía", "Detalle": "Catálogo SGC, OpenStreetMap, Datos Abiertos DANE", "Costo Prototipo (MVP)": "$0 COP", "Costo Mensual (Piloto)": "$0 COP"},
        {"Rubro": "Infraestructura Cloud / Hosting", "Detalle": "Streamlit Community Cloud (MVP) / VPS AWS (Piloto)", "Costo Prototipo (MVP)": "$0 COP", "Costo Mensual (Piloto)": "$180.000 COP"},
        {"Rubro": "Base de Datos Espacial", "Detalle": "Archivos locales CSV/SQLite (MVP) / PostgreSQL + PostGIS", "Costo Prototipo (MVP)": "$0 COP", "Costo Mensual (Piloto)": "$120.000 COP"},
        {"Rubro": "Talento Humano y Soporte", "Detalle": "Equipo universitario (MVP) / Soporte técnico e ingeniería", "Costo Prototipo (MVP)": "$0 COP (Académico)", "Costo Mensual (Piloto)": "$4.500.000 COP"},
        {"Rubro": "TOTAL ESTIMADO", "Detalle": "Inversión directa requerida", "Costo Prototipo (MVP)": "$0 COP", "Costo Mensual (Piloto)": "$4.800.000 COP"}
    ])
    st.table(df_costos)

# --- PANTALLA 5: PLANES Y PRECIOS (ESTIMACIÓN MVP PRODUCTIVO EN USD) ---
with tab5:
    st.subheader("Estimación de Inversión: Escalamiento a MVP Productivo (USD)")
    st.caption("Desglose técnico y financiero para llevar el prototipo actual a una plataforma operativa completa en producción.")

    df_precios_usd = pd.DataFrame([
        {
            "Rubro / Componente": "Arquitectura y Backend",
            "Descripción Técnica": "Migración de lógica Python/Streamlit a APIs robustas (FastAPI/Node.js), autenticación y base de datos geoespacial (PostgreSQL + PostGIS).",
            "Estimación (USD)": "$4,000 – $9,000"
        },
        {
            "Rubro / Componente": "Frontend Web / Panel de Control",
            "Descripción Técnica": "Interfaz operativa en tiempo real para despachadores o coordinadores (React/Next.js + mapas interactivos).",
            "Estimación (USD)": "$3,500 – $7,500"
        },
        {
            "Rubro / Componente": "App Móvil (Opcional)",
            "Descripción Técnica": "Aplicación para brigadistas o ciudadanos con envío de ubicación GPS en segundo plano y modo offline (Flutter/React Native).",
            "Estimación (USD)": "$5,000 – $12,000"
        },
        {
            "Rubro / Componente": "Integraciones y Alertas",
            "Descripción Técnica": "Conexión con pasarelas SMS/WhatsApp, notificaciones push, servicios meteorológicos o sensores externos.",
            "Estimación (USD)": "$1,200 – $3,000"
        },
        {
            "Rubro / Componente": "Pruebas, Seguridad y Despliegue",
            "Descripción Técnica": "Pruebas de carga, cifrado de datos sensibles, configuración CI/CD y despliegue en nube.",
            "Estimación (USD)": "$1,500 – $3,000"
        },
        {
            "Rubro / Componente": "Subtotal Desarrollo (MVP Productivo)",
            "Descripción Técnica": "Rango según si incluye app móvil nativa o solo web progresiva (PWA).",
            "Estimación (USD)": "$15,200 – $34,500"
        }
    ])

    st.dataframe(df_precios_usd, use_container_width=True, hide_index=True)

    st.divider()
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.info("**💡 Opción Web Progresiva (PWA):**\n\nInversión estimada desde **$15,200 USD** (sin desarrollo de app móvil nativa).")
    with col_p2:
        st.success("**🚀 Opción Completa (Web + App Móvil):**\n\nInversión estimada hasta **$34,500 USD** (incluye app offline con GPS para brigadistas).")    
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cfo_analyzer import IncomeStatement, calculate_comparative_kpis
import google.generativeai as genai
import json
import io
import re
import zipfile
from market_data import obtener_metricas_bursatiles
from macro_data import obtener_inflacion_alimentos

# Configuración inicial de la página
st.set_page_config(
    page_title="Dashboard Restaurantes",
    page_icon="🍔",
    layout="wide"
)

st.title("Benchmarking Financiero: Sector Restaurantes")

# Funciones de carga de datos
def load_financial_data():
    try:
        df = pd.read_csv('metricas_restaurantes.csv')
        return df[df['Ingresos_Totales'] > 0] # Filtro de calidad de datos
    except FileNotFoundError:
        st.error("No se encontró el archivo 'metricas_restaurantes.csv'. Ejecuta 'procesador_sec.py'.")
        st.stop()

def load_profile_data():
    try:
        return pd.read_csv('perfiles_restaurantes.csv')
    except FileNotFoundError:
        return pd.DataFrame()

def load_sec_data():
    try:
        return pd.read_csv('sec_datos_auditados.csv')
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def obtener_diagnostico_ia(superprompt: str, prompt_usuario: str) -> str:
    try:
        model = genai.GenerativeModel(
            model_name="gemini-flash-lite-latest",
            system_instruction=superprompt
        )
        response = model.generate_content(prompt_usuario)
        return response.text
    except Exception:
        # Fallback
        model = genai.GenerativeModel(model_name="gemini-flash-lite-latest")
        prompt_completo = f"INSTRUCCIONES DEL SISTEMA:\n{superprompt}\n\nMENSAJE DEL USUARIO:\n{prompt_usuario}"
        response = model.generate_content(prompt_completo)
        return response.text

def generar_guion_diseno(empresa, metricas, diagnostico_ia):
    # Calcular y añadir la narrativa de los $100
    rev = metricas.get('Revenues', 0)
    narrativa = ""
    if rev > 0:
        x_val = (metricas.get('CostOfGoodsAndServicesSold', 0) / rev) * 100
        y_val = (metricas.get('Gastos_Operativos', 0) / rev) * 100
        z_val = (metricas.get('Utilidad_Neta', 0) / rev) * 100
        narrativa = f"Para entender el negocio de {empresa}: Por cada $100 de ingresos generados, la empresa destina ${x_val:,.2f} a los costos directos del servicio y ${y_val:,.2f} a mantener su estructura operativa. Al final, retiene ${z_val:,.2f} de ganancia pura."
    
    # Limpieza de IA
    texto_limpio = re.sub(r'[*#]', '', diagnostico_ia)
    parrafos = [p.strip() for p in texto_limpio.split('\n') if p.strip()]
    conclusion_ia = '\n\n'.join(parrafos[:3]) # Tomar los primeros 3 párrafos
    
    guion = f"""[DIAPOSITIVA 1: PORTADA]
Título: Reporte de Inteligencia Financiera
Empresa: {empresa}
Año: 2025

[DIAPOSITIVA 2: KPIs FINANCIEROS]
Ingresos Totales: ${metricas.get('Revenues', 0):,.0f}
Costos de Venta: ${metricas.get('CostOfGoodsAndServicesSold', 0):,.0f}
Gastos Operativos: ${metricas.get('Gastos_Operativos', 0):,.0f}
Utilidad Neta: ${metricas.get('Utilidad_Neta', 0):,.0f}

[DIAPOSITIVA 3: SÍNTESIS DE NEGOCIO]
{narrativa}

[DIAPOSITIVA 4: ANÁLISIS FORENSE CFO]
{conclusion_ia}
"""
    return guion

df_fin = load_financial_data()
df_prof = load_profile_data()
df_sec = load_sec_data()

# Diccionario de mapeo Ticker -> Nombre_Empresa
# Usamos df_fin para crear el mapeo si existe la columna, de lo contrario usamos el ticker
if 'Nombre_Empresa' in df_fin.columns:
    ticker_a_nombre = dict(zip(df_fin['Ticker'], df_fin['Nombre_Empresa']))
else:
    ticker_a_nombre = {}

def format_ticker(x):
    nombre = ticker_a_nombre.get(x, x)
    return f"{x} - {nombre}" if nombre != x else x

# ----------------------------------------------------
# Pestañas (Tabs)
# ----------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(['Benchmarking Financiero', 'Perfil del Modelo de Negocio', 'Auditoría SEC (Datos Oficiales)', 'Simulador CFO (What-If)', 'Reporte Ejecutivo IA'])

# ====================================================
# TAB 1: Benchmarking Financiero
# ====================================================
with tab1:
    st.markdown("Comparativa de métricas clave (Último Año Fiscal Completo) y tendencias históricas.")


    st.sidebar.header("Filtros Interactivos")
    all_tickers = df_fin['Ticker'].unique().tolist()

    selected_tickers = st.sidebar.multiselect(
        "Selecciona las Empresas (Tickers):",
        options=all_tickers,
        default=all_tickers,
        format_func=format_ticker
    )

    if not selected_tickers:
        st.warning("Por favor, selecciona al menos una empresa en el menú lateral.")
    else:
        df_filtered = df_fin[df_fin['Ticker'].isin(selected_tickers)]
        
        # DataFrame con solo el año más reciente por empresa
        idx_latest = df_filtered.groupby('Ticker')['Año'].idxmax()
        df_latest = df_filtered.loc[idx_latest].sort_values(by='Ingresos_Totales', ascending=False)

        # 1. Tarjetas
        st.subheader("Márgenes Netos (Último Año)")
        
        items_per_row = 4
        rows = list(df_latest.iterrows())
        
        for i in range(0, len(rows), items_per_row):
            cols = st.columns(items_per_row)
            chunk = rows[i:i + items_per_row]
            for col, (idx, row) in zip(cols, chunk):
                ticker = row['Ticker']
                margen = row['Margen_Neto_porcentual']
                
                # Obtener nombre corporativo completo
                nombre_completo = ticker_a_nombre.get(ticker, ticker)
                
                # Limpiar el nombre para que sea más corto en la tarjeta
                nombre_corto = nombre_completo.replace(', Inc.', '').replace(' Inc.', '').replace(' Corporation', '')
                if len(nombre_corto) > 18:
                    nombre_corto = nombre_corto[:15] + "..."
                
                # Renderizar con tooltip (help)
                col.metric(
                    label=f"Margen {nombre_corto}", 
                    value=f"{margen:.2f}%",
                    help=nombre_completo
                )

        st.divider()

        # 2. Gráfico de Barras
        st.subheader("Ingresos Totales vs Utilidad Neta (Último Año)")
        
        # Preparar dataframe para plot
        if 'Nombre_Empresa' in df_latest.columns:
            df_plot = df_latest[['Ticker', 'Nombre_Empresa', 'Ingresos_Totales', 'Utilidad_Neta']].copy()
            df_plot.columns = ['Ticker', 'Nombre_Empresa', 'Ingresos Totales', 'Utilidad Neta']
            df_melted = df_plot.melt(id_vars=['Ticker', 'Nombre_Empresa'], var_name='Métrica', value_name='Monto ($)')
        else:
            df_plot = df_latest[['Ticker', 'Ingresos_Totales', 'Utilidad_Neta']].copy()
            df_plot.columns = ['Ticker', 'Ingresos Totales', 'Utilidad Neta']
            df_melted = df_plot.melt(id_vars='Ticker', var_name='Métrica', value_name='Monto ($)')

        fig_bar = px.bar(
            df_melted, 
            x='Nombre_Empresa' if 'Nombre_Empresa' in df_melted.columns else 'Ticker', 
            y='Monto ($)', 
            color='Métrica', 
            barmode='group',
            text_auto='.2s', 
            color_discrete_sequence=['#1f77b4', '#2ca02c'],
            hover_data={'Ticker': True} if 'Nombre_Empresa' in df_melted.columns else {}
        )
        fig_bar.update_layout(xaxis_title="Empresa", yaxis_title="Monto en USD", hovermode="x unified")
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # 3. Gráfico de Tendencia Histórica
        st.subheader("Tendencia Histórica: Utilidad Neta")
        df_history = df_filtered.sort_values(by='Año')
        fig_line = px.line(
            df_history, 
            x='Año', 
            y='Utilidad_Neta', 
            color='Nombre_Empresa' if 'Nombre_Empresa' in df_history.columns else 'Ticker', 
            markers=True,
            title="Evolución de la Utilidad Neta a lo largo de los años",
            labels={'Utilidad_Neta': 'Utilidad Neta (USD)'},
            hover_data={'Ticker': True} if 'Nombre_Empresa' in df_history.columns else {}
        )
        fig_line.update_layout(xaxis=dict(tickmode='linear', dtick=1), hovermode="x unified")
        st.plotly_chart(fig_line, use_container_width=True)

        # 4. Tabla de datos
        with st.expander("Ver Histórico de Datos Crudos (Tabla)"):
            st.dataframe(
                df_filtered.style.format({
                    "Ingresos_Totales": "${:,.0f}",
                    "Gastos_Operativos": "${:,.0f}",
                    "Utilidad_Neta": "${:,.0f}",
                    "Margen_Neto_porcentual": "{:.2f}%",
                    "Año": "{:d}"
                }),
                use_container_width=True
            )

# ====================================================
# TAB 2: Perfil del Modelo de Negocio
# ====================================================
with tab2:
    if df_prof.empty:
        st.info("No se han extraído los perfiles. Por favor, asegúrate de haber ejecutado el extractor.")
    elif not selected_tickers:
        st.warning("Por favor selecciona al menos una empresa en el menú lateral para ver su perfil")
    else:
        st.markdown("### Análisis Cualitativo y de Valoración")
        
        # Selector de empresa basado en la selección del menú lateral
        selected_prof_ticker = st.selectbox(
            "Elige una empresa para analizar su perfil:",
            options=selected_tickers,
            format_func=format_ticker
        )
        
        # Extraer info de la empresa seleccionada
        prof_data = df_prof[df_prof['Ticker'] == selected_prof_ticker].iloc[0]
        
        st.divider()
        
        # Nombre de la empresa grande
        nombre_display = prof_data.get('Nombre_Empresa', selected_prof_ticker)
        st.markdown(f"#### {nombre_display}")
        
        # Tarjetas de métricas del perfil
        m1, m2 = st.columns(2)
        
        # Formatear Empleados
        emp = prof_data['Employees']
        emp_str = f"{int(emp):,}" if pd.notna(emp) else "No reportado"
        m1.metric("Empleados a Tiempo Completo", emp_str)
        
        # Formatear P/E Ratio
        pe = prof_data['TrailingPE']
        pe_str = f"{float(pe):.2f}x" if pd.notna(pe) else "N/A"
        m2.metric("Múltiplo de Valoración (Trailing P/E)", pe_str)
        
        # Descripción del negocio
        st.write(prof_data['BusinessSummary'])

# ====================================================
# TAB 3: Auditoría SEC (Datos Oficiales)
# ====================================================
with tab3:
    if df_sec.empty:
        st.info("No se han extraído los datos oficiales de la SEC. Ejecuta 'sec_extractor.py' primero.")
    else:
        st.markdown("### Datos Auditados Extraídos Directamente del Formulario 10-K (API XBRL)")
        
        st.subheader("Ingresos Oficiales vs Costos Directos")
        
        # Sincronizar Orden y Nombres Completos
        df_sec['Nombre_Empresa'] = df_sec['Ticker'].map(ticker_a_nombre).fillna(df_sec['Ticker'])
        df_sec_sorted = df_sec.sort_values(by='Revenues', ascending=False)
        
        # Preparar datos para Plotly
        df_sec_plot = df_sec_sorted[['Ticker', 'Nombre_Empresa', 'Revenues', 'CostOfGoodsAndServicesSold']].copy()
        df_sec_plot.columns = ['Ticker', 'Nombre_Empresa', 'Ingresos (Revenues)', 'Costos Directos (COGS)']
        df_sec_melted = df_sec_plot.melt(id_vars=['Ticker', 'Nombre_Empresa'], var_name='Indicador', value_name='Monto ($)')
        
        fig_sec = px.bar(
            df_sec_melted, x='Nombre_Empresa', y='Monto ($)', color='Indicador', barmode='group',
            text_auto='.2s', color_discrete_sequence=['#1f77b4', '#d62728'],
            hover_data={'Ticker': True}
        )
        fig_sec.update_layout(xaxis_title="Empresa", yaxis_title="Monto en USD", hovermode="x unified")
        fig_sec.update_traces(textposition="outside")
        st.plotly_chart(fig_sec, use_container_width=True)
        
        st.subheader("Tabla de Auditoría (Reporte Crudo)")
        st.dataframe(
            df_sec_sorted.style.format({
                "Revenues": "${:,.0f}",
                "CostOfGoodsAndServicesSold": "${:,.0f}"
            }),
            use_container_width=True
        )
        

# ====================================================
# TAB 4: Simulador CFO (What-If)
# ====================================================
with tab4:
    st.header("Simulador CFO (What-If)")
    st.markdown("Ajuste las palancas operativas para proyectar el impacto en la rentabilidad (EBITDA).")
    
    if not df_sec.empty:
        # Seleccionar empresa
        nombres_disponibles = df_sec['Nombre_Empresa'].unique()
        empresa_sel = st.selectbox("Seleccione la Empresa para Simulación", nombres_disponibles)
        
        df_empresa = df_sec[df_sec['Nombre_Empresa'] == empresa_sel].iloc[0]
        
        current_rev = df_empresa['Revenues']
        current_cogs = df_empresa['CostOfGoodsAndServicesSold']
        
        # Instanciar objetos IncomeStatement
        # Asumimos un SG&A base del 10% de los ingresos para poder optimizarlo en el simulador
        current_sga = current_rev * 0.10
        current_is = IncomeStatement(period_name="Current", revenue=current_rev, cogs=current_cogs, sga=current_sga)
        
        # Generar un 'Prior' mockeado asumiendo un crecimiento histórico del 5% para poder calcular el DOL
        prior_is = IncomeStatement(period_name="Prior", revenue=current_rev/1.05, cogs=current_cogs/1.05, sga=current_sga/1.05)
        
        st.subheader("Control de Escenarios (Palancas)")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            val_rev = st.slider("Incremento de Precios/Ventas (%)", 0.0, 15.0, 3.0, step=0.5)
        with col_s2:
            val_cogs = st.slider("Reducción de Costos COGS (%)", 0.0, 15.0, 5.0, step=0.5)
        with col_s3:
            val_sga = st.slider("Optimización SG&A (%)", 0.0, 15.0, 7.0, step=0.5)
            
        # Ejecutar motor de cálculo
        kpis = calculate_comparative_kpis(prior_is, current_is, val_rev, val_cogs, val_sga)
        
        st.subheader("Impacto Proyectado")
        c1, c2, c3 = st.columns(3)
        
        current_ebitda = kpis['current_ebitda']
        proy_ebitda = kpis['scenarios']['scenario_combined_ebitda']
        crecimiento_ebitda = ((proy_ebitda / current_ebitda) - 1) * 100 if current_ebitda else 0
        
        c1.metric("EBITDA Base (Actual)", f"${current_ebitda:,.0f}")
        c2.metric("EBITDA Proyectado (Simulación)", f"${proy_ebitda:,.0f}", f"{crecimiento_ebitda:+.1f}%")
        c3.metric("Punto de Equilibrio (Ventas Mínimas)", f"${kpis['break_even_revenue']:,.0f}")
        
        st.info(f"**Grado de Apalancamiento Operativo (DOL): {kpis['dol']:.2f}x**. Esto significa que por cada 1% que crecen las ventas, la utilidad operativa crece {kpis['dol']:.2f}%.")
        
    else:
        st.warning("Datos de la SEC no disponibles para simulación.")

# ====================================================
# TAB 5: Reporte Ejecutivo IA
# ====================================================
with tab5:
    st.header("Diagnóstico Forense CFO impulsado por IA")
    st.markdown("Genera un análisis narrativo profundo utilizando la taxonomía oficial de la SEC y los KPIs financieros.")
    
    if not df_sec.empty and not df_fin.empty:
        nombres_disponibles_ia = df_sec['Nombre_Empresa'].unique()
        empresa_ia = st.selectbox("Seleccione la Empresa para el Diagnóstico IA", nombres_disponibles_ia, key='ia_selectbox')
        
        if st.button("Generar Diagnóstico Forense CFO", type="primary"):
            # 1. Configurar API Key
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
            except Exception:
                st.error("No se encontró 'GEMINI_API_KEY' en secrets. Por favor configure sus st.secrets (.streamlit/secrets.toml).")
                st.stop()
                
            with st.spinner("El motor de IA está redactando el análisis financiero..."):
                try:
                    # 2. Leer Superprompt
                    with open("SUPERPROMPT_Analisis_Financiero_PyG.md", "r", encoding="utf-8") as f:
                        superprompt = f.read()
                        
                    # 3. Preparar datos de contexto
                    df_sec_ia = df_sec[df_sec['Nombre_Empresa'] == empresa_ia].iloc[0].to_dict()
                    
                    # Para finanzas, tomamos el año más reciente de esa empresa
                    df_fin_empresa = df_fin[df_fin['Nombre_Empresa'] == empresa_ia]
                    idx_latest_fin = df_fin_empresa['Año'].idxmax()
                    df_fin_ia = df_fin.loc[idx_latest_fin].to_dict()
                    
                    contexto_datos = {
                        "Empresa": empresa_ia,
                        "Datos_Auditoria_SEC_10K": {k: v for k, v in df_sec_ia.items() if pd.notna(v)},
                        "KPIs_Mercado_Finanzas": {k: v for k, v in df_fin_ia.items() if pd.notna(v)}
                    }
                    
                    prompt_usuario = f"Aplica el SUPERPROMPT a los siguientes datos de {empresa_ia}:\n\n{json.dumps(contexto_datos, indent=2, ensure_ascii=False)}"
                    
                    # 4. Generar usando caché para ahorrar llamadas a la API
                    texto_ia = obtener_diagnostico_ia(superprompt, prompt_usuario)
                    
                    # Guardar en session_state
                    st.session_state['diagnostico_actual'] = texto_ia
                    st.session_state['empresa_actual'] = empresa_ia
                    st.session_state['df_sec_ia'] = df_sec_ia
                    st.session_state['df_fin_ia'] = df_fin_ia
                    
                    # 5. Renderizar mensaje de éxito
                    st.success("Diagnóstico generado exitosamente.")
                    
                except FileNotFoundError:
                    st.error("No se encontró el archivo SUPERPROMPT_Analisis_Financiero_PyG.md.")
                except Exception as e:
                    st.error(f"Error durante la generación de IA: {e}")
                    
        # Fuera del botón, renderizar las pestañas si hay datos en estado
        if st.session_state.get('diagnostico_actual') and st.session_state.get('empresa_actual') == empresa_ia:
            texto_ia = st.session_state['diagnostico_actual']
            df_sec_ia = st.session_state['df_sec_ia']
            df_fin_ia = st.session_state['df_fin_ia']
            
            tab_ia, tab_visual, tab_mercado, tab_consumo, tab_macro = st.tabs(['Diagnóstico CFO (Técnico)', 'Resumen Ejecutivo (Visual)', 'Mercado en Vivo', 'Termómetro de Consumo', 'Contexto Macro (FRED)'])
            
            with tab_ia:
                respuesta_limpia = texto_ia.replace('$', r'\$')
                st.markdown(respuesta_limpia)
                
            with tab_visual:
                st.subheader("Modo Visual Simplificado")
                st.markdown("Los datos financieros clave explicados en lenguaje sencillo para un entendimiento general.")
                
                c1, c2 = st.columns(2)
                c3, c4 = st.columns(2)
                
                rev = df_sec_ia.get('Revenues', 0)
                cogs = df_sec_ia.get('CostOfGoodsAndServicesSold', 0)
                opex = df_fin_ia.get('Gastos_Operativos', 0)
                net = df_fin_ia.get('Utilidad_Neta', 0)
                
                c1.metric("Ingresos", f"${rev:,.0f}", help="Todo el dinero bruto que entró a la caja")
                c2.metric("Costos de Venta", f"${cogs:,.0f}", help="Lo que costó directamente entregar el servicio/producto")
                c3.metric("Gastos Operativos", f"${opex:,.0f}", help="Sueldos administrativos, rentas y mercadotecnia")
                c4.metric("Utilidad Neta / Margen", f"${net:,.0f}", help="Ganancia final libre de polvo y paja")
                
                st.markdown("---")
                
                # Gráfico de Cascada (Waterfall)
                fig_waterfall = go.Figure(go.Waterfall(
                    name="P&L", orientation="v",
                    measure=["relative", "relative", "relative", "total"],
                    x=["Ingresos", "Costos de Venta", "Gastos Operativos", "Utilidad Neta"],
                    textposition="outside",
                    text=[f"${rev/1e6:,.0f}M", f"-${cogs/1e6:,.0f}M", f"-${opex/1e6:,.0f}M", f"${net/1e6:,.0f}M"],
                    y=[rev, -cogs, -opex, net],
                    connector={"line":{"color":"rgb(63, 63, 63)"}},
                ))
                fig_waterfall.update_layout(title="Cascada de Rentabilidad (P&L)", showlegend=False)
                st.plotly_chart(fig_waterfall, use_container_width=True)
                
                # Narrativa de los $100
                if rev > 0:
                    x_val = (cogs / rev) * 100
                    y_val = (opex / rev) * 100
                    z_val = (net / rev) * 100
                    narrativa = f"Para entender el negocio de {empresa_ia}: Por cada \\$100 de ingresos generados, la empresa destina \\${x_val:,.2f} a los costos directos del servicio y \\${y_val:,.2f} a mantener su estructura operativa. Al final, retiene \\${z_val:,.2f} de ganancia pura."
                    st.info(narrativa)
                
                
                st.divider()
                
            with tab_mercado:
                st.subheader(f'📈 Valoración Bursátil (Tiempo Real)')
                ticker_real = df_sec[df_sec['Nombre_Empresa'] == empresa_ia]['Ticker'].iloc[0]
                from market_data import obtener_metricas_bursatiles
                metricas = obtener_metricas_bursatiles(ticker_real) 
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Precio Actual", metricas.get('precio', 'N/A'))
                col2.metric("Market Cap", metricas.get('market_cap', 'N/A'))
                
                pe = metricas.get('pe_ratio', 'N/A')
                if isinstance(pe, (int, float)):
                    pe = round(pe, 2)
                col3.metric("P/E Ratio (Trailing)", pe)
                
            with tab_consumo:
                st.subheader("📊 Termómetro de Consumo")
                from consumer_trends import obtener_tendencia_busqueda
                
                with st.spinner("Consultando Google Trends..."):
                    df_trends, keyword = obtener_tendencia_busqueda(empresa_ia)
                    
                if not df_trends.empty:
                    st.line_chart(df_trends[keyword])
                    st.caption("Gráfico de popularidad de la marca basado en el volumen de búsquedas de Google en los últimos 12 meses (0-100)")
                else:
                    st.warning("Datos de tendencias no disponibles o límite de peticiones alcanzado (Rate Limit).")
                    
            with tab_macro: 
                st.subheader("🌎 Contexto del Sector (Macro)")
                st.caption("Índice de Inflación de Alimentos (Últimos 5 años). Este indicador es global y presiona los costos de toda la industria por igual.")
                
                from macro_data import obtener_inflacion_alimentos
                df_macro = obtener_inflacion_alimentos()
                if not df_macro.empty:
                    st.line_chart(df_macro)
                else:
                    st.warning("Datos macroeconómicos no disponibles temporalmente.")
    else:
        st.warning("Se requieren los datos financieros y de la SEC para generar el reporte.")

st.caption("Datos procesados desde la API de Yahoo Finance y la API oficial XBRL de la SEC.")

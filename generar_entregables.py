import pandas as pd
import plotly.express as px
import markdown
import os

def generar_reporte_html():
    print("Generando Dashboard HTML estático...")
    
    # 1. Cargar datos
    df_fin = pd.read_csv('metricas_restaurantes.csv')
    df_fin = df_fin[df_fin['Ingresos_Totales'] > 0]
    df_sec = pd.read_csv('sec_datos_auditados.csv')
    
    ticker_a_nombre = dict(zip(df_fin['Ticker'], df_fin['Nombre_Empresa']))
    
    # 2. Generar Gráficos Plotly
    
    # Bar Chart (Finanzas)
    idx_latest = df_fin.groupby('Ticker')['Año'].idxmax()
    df_latest = df_fin.loc[idx_latest].sort_values(by='Ingresos_Totales', ascending=False)
    
    df_plot = df_latest[['Ticker', 'Nombre_Empresa', 'Ingresos_Totales', 'Utilidad_Neta']].copy()
    df_plot.columns = ['Ticker', 'Nombre_Empresa', 'Ingresos Totales', 'Utilidad Neta']
    df_melted = df_plot.melt(id_vars=['Ticker', 'Nombre_Empresa'], var_name='Métrica', value_name='Monto ($)')
    
    fig_bar = px.bar(
        df_melted, x='Nombre_Empresa', y='Monto ($)', color='Métrica', barmode='group',
        text_auto='.2s', color_discrete_sequence=['#1f77b4', '#2ca02c'],
        title='Benchmarking: Ingresos vs Utilidad Neta (Último Año)'
    )
    
    # Line Chart (Finanzas)
    df_history = df_fin.sort_values(by='Año')
    fig_line = px.line(
        df_history, x='Año', y='Utilidad_Neta', color='Nombre_Empresa', markers=True,
        title="Evolución Histórica de la Utilidad Neta (5 Años)"
    )
    
    # Bar Chart (SEC)
    df_sec['Nombre_Empresa'] = df_sec['Ticker'].map(ticker_a_nombre).fillna(df_sec['Ticker'])
    df_sec_sorted = df_sec.sort_values(by='Revenues', ascending=False)
    df_sec_plot = df_sec_sorted[['Ticker', 'Nombre_Empresa', 'Revenues', 'CostOfGoodsAndServicesSold']].copy()
    df_sec_plot.columns = ['Ticker', 'Nombre_Empresa', 'Ingresos (Revenues)', 'Costos Directos (COGS)']
    df_sec_melted = df_sec_plot.melt(id_vars=['Ticker', 'Nombre_Empresa'], var_name='Indicador', value_name='Monto ($)')
    
    fig_sec = px.bar(
        df_sec_melted, x='Nombre_Empresa', y='Monto ($)', color='Indicador', barmode='group',
        text_auto='.2s', color_discrete_sequence=['#1f77b4', '#d62728'],
        title='Auditoría SEC: Ingresos Oficiales vs Costos Directos'
    )
    
    # 3. Exportar a HTML
    html_content = f"""
    <html>
    <head><title>Dashboard Directivo: Restaurantes</title></head>
    <body style="font-family: Arial, sans-serif; padding: 20px; max-width: 1200px; margin: auto;">
        <h1 style="text-align: center; color: #2c3e50;">Dashboard de Inteligencia Financiera: Sector Restaurantes</h1>
        <p style="text-align: center; color: #7f8c8d;">Reporte Interactivo (Pase el ratón por las gráficas para ver detalles)</p>
        <hr>
        <h2>1. Benchmarking Financiero</h2>
        {fig_bar.to_html(full_html=False, include_plotlyjs='cdn')}
        <br>
        {fig_line.to_html(full_html=False, include_plotlyjs=False)}
        <hr>
        <h2>2. Auditoría SEC (Datos Oficiales 10-K)</h2>
        {fig_sec.to_html(full_html=False, include_plotlyjs=False)}
    </body>
    </html>
    """
    
    with open('Dashboard_Directivo_Interactivo.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("-> Dashboard HTML creado exitosamente.")

def generar_pdf_manual():
    print("Preparando el Manual para Exportación PDF...")
    try:
        with open('Manual_Dashboard_Usuario.md', 'r', encoding='utf-8') as f:
            texto_md = f.read()
            
        html_body = markdown.markdown(texto_md)
        
        # HTML con script para auto-imprimir a PDF
        html_page = f"""
        <html>
        <head><title>Manual Usuario</title></head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; max-width: 800px; margin: auto; line-height: 1.6; color: #333;">
            {html_body}
            <script>
                // Abre automáticamente el cuadro de diálogo para "Guardar como PDF"
                window.onload = function() {{
                    window.print();
                }}
            </script>
        </body>
        </html>
        """
        
        with open('Manual_Imprimible.html', 'w', encoding='utf-8') as f:
            f.write(html_page)
        print("-> Archivo HTML del Manual creado. (Ábralo para Guardar como PDF).")
        
    except Exception as e:
        print(f"Error generando el manual: {e}")

if __name__ == "__main__":
    generar_reporte_html()
    generar_pdf_manual()

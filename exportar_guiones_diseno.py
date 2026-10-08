import os
import json
import re
import pandas as pd
import google.generativeai as genai
import market_data

# Configuración API
# Intentamos obtenerla de streamlit secrets si es posible, o de una variable de entorno
try:
    from st_secrets_loader import get_secret
    api_key = get_secret("GEMINI_API_KEY") # This assumes a helper or we can just read from .streamlit/secrets.toml
except:
    pass

# Mejor leemos directo de .streamlit/secrets.toml
import toml
try:
    secrets = toml.load(".streamlit/secrets.toml")
    api_key = secrets.get("GEMINI_API_KEY")
except:
    api_key = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=api_key)

def obtener_diagnostico_ia(superprompt, prompt_usuario):
    model = genai.GenerativeModel(model_name="gemini-flash-lite-latest")
    prompt_completo = f"INSTRUCCIONES DEL SISTEMA:\n{superprompt}\n\nMENSAJE DEL USUARIO:\n{prompt_usuario}"
    response = model.generate_content(prompt_completo)
    return response.text

def generar_guion_diseno(empresa, metricas, diagnostico_ia, metricas_bursatiles):
    rev = metricas.get('Revenues', 0)
    narrativa = ""
    if rev > 0:
        x_val = (metricas.get('CostOfGoodsAndServicesSold', 0) / rev) * 100
        y_val = (metricas.get('Gastos_Operativos', 0) / rev) * 100
        z_val = (metricas.get('Utilidad_Neta', 0) / rev) * 100
        narrativa = f"Para entender el negocio de {empresa}: Por cada $100 de ingresos generados, la empresa destina ${x_val:,.2f} a los costos directos del servicio y ${y_val:,.2f} a mantener su estructura operativa. Al final, retiene ${z_val:,.2f} de ganancia pura."
    
    texto_limpio = re.sub(r'[*#]', '', diagnostico_ia)
    parrafos = [p.strip() for p in texto_limpio.split('\n') if p.strip()]
    conclusion_ia = '\n\n'.join(parrafos[:3])
    
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

[DIAPOSITIVA 5: VALORACIÓN DE MERCADO]
Precio Actual: {metricas_bursatiles.get('precio_actual', 'N/A')}
Market Cap: {metricas_bursatiles.get('market_cap', 'N/A')}
P/E Ratio (Trailing): {metricas_bursatiles.get('pe_ratio', 'N/A')}
"""
    return guion

def main():
    os.makedirs('guiones_para_canva', exist_ok=True)
    
    df_fin = pd.read_csv('metricas_restaurantes.csv')
    df_sec = pd.read_csv('sec_datos_auditados.csv')
    
    tickers_objetivo = ['CMG', 'UBER', 'DASH', 'QSR']
    
    try:
        with open("SUPERPROMPT_Analisis_Financiero_PyG.md", "r", encoding="utf-8") as f:
            superprompt = f.read()
    except FileNotFoundError:
        print("Error: No se encontró el SUPERPROMPT.")
        return
        
    for ticker in tickers_objetivo:
        # Extraemos nombre de empresa desde df_fin
        df_f_empresa = df_fin[df_fin['Ticker'] == ticker]
        if df_f_empresa.empty:
            print(f"Ticker {ticker} no encontrado en datos financieros.")
            continue
            
        empresa = df_f_empresa.iloc[0]['Nombre_Empresa']
        
        df_s_empresa = df_sec[df_sec['Ticker'] == ticker]
        if df_s_empresa.empty:
            print(f"Empresa {empresa} no encontrada en datos SEC.")
            continue
            
        df_s = df_s_empresa.iloc[0].to_dict()
        idx_l = df_f_empresa['Año'].idxmax()
        df_f = df_fin.loc[idx_l].to_dict()
        
        metricas_emp = {
            'Revenues': df_s.get('Revenues', 0),
            'CostOfGoodsAndServicesSold': df_s.get('CostOfGoodsAndServicesSold', 0),
            'Gastos_Operativos': df_f.get('Gastos_Operativos', 0),
            'Utilidad_Neta': df_f.get('Utilidad_Neta', 0)
        }
        
        contexto = {
            "Empresa": empresa,
            "Datos_Auditoria_SEC_10K": {k: v for k, v in df_s.items() if pd.notna(v)},
            "KPIs_Mercado_Finanzas": {k: v for k, v in df_f.items() if pd.notna(v)}
        }
        prompt_usuario = f"Aplica el SUPERPROMPT a los siguientes datos de {empresa}:\n\n{json.dumps(contexto, indent=2, ensure_ascii=False)}"
        
        print(f"Generando guion para {empresa} ({ticker})...")
        texto_ia = obtener_diagnostico_ia(superprompt, prompt_usuario)
        
        print(f"Obteniendo métricas bursátiles para {ticker}...")
        metricas_bursatiles = market_data.obtener_metricas_bursatiles(ticker)
        
        guion = generar_guion_diseno(empresa, metricas_emp, texto_ia, metricas_bursatiles)
        
        file_path = os.path.join('guiones_para_canva', f"guion_{ticker}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(guion)
        print(f"Guardado: {file_path}")

if __name__ == "__main__":
    main()

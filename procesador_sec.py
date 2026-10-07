import pandas as pd
import yfinance as yf
import os
import time
import textwrap
from deep_translator import GoogleTranslator, MyMemoryTranslator

def process_financials():
    tickers = ['CMG', 'MCD', 'QSR', 'DPZ', 'WEN', 'YUM', 'DRI', 'SHAK', 'SG']
    data_financials = []
    data_profiles = []

    for ticker_symbol in tickers:
        print(f"Obteniendo datos (financieros y perfil) para {ticker_symbol}...")
        ticker = yf.Ticker(ticker_symbol)
        
        # 1. Extracción del perfil cualitativo
        try:
            info = ticker.info
            summary = info.get('longBusinessSummary', 'No disponible')
            nombre_empresa = info.get('shortName', info.get('longName', ticker_symbol))
            
            if summary != 'No disponible':
                time.sleep(3)  # Pausa para evitar el límite de tasa de la API
                try:
                    summary = GoogleTranslator(source='en', target='es').translate(summary)
                except Exception as e:
                    print(f"Fallo GoogleTranslator para {ticker_symbol}. Intentando con MyMemoryTranslator (Chunker)...")
                    try:
                        chunks = textwrap.wrap(summary, width=490)
                        translated_chunks = []
                        for chunk in chunks:
                            time.sleep(1.5)  # Pausa entre fragmentos
                            trad = MyMemoryTranslator(source='english', target='spanish').translate(chunk)
                            translated_chunks.append(trad)
                        summary = ' '.join(translated_chunks)
                    except Exception as e2:
                        print(f"Ambos traductores fallaron para {ticker_symbol}. Conservando inglés. Error: {e2}")
                    
            employees = info.get('fullTimeEmployees', None)
            pe_ratio = info.get('trailingPE', None)
            
            data_profiles.append({
                'Ticker': ticker_symbol,
                'Nombre_Empresa': nombre_empresa,
                'BusinessSummary': summary,
                'Employees': employees,
                'TrailingPE': pe_ratio
            })
            print(f"-> Perfil extraído para {ticker_symbol}.")
        except Exception as e:
            print(f"Error extrayendo perfil de {ticker_symbol}: {e}")
        
        # 2. Extracción de los datos financieros históricos
        try:
            financials = ticker.financials
            
            if financials.empty:
                print(f"Advertencia: No se encontraron datos financieros para {ticker_symbol}.")
                continue
                
            for date_col in financials.columns:
                yearly_financials = financials[date_col]
                
                def get_metric(metric_names):
                    for name in metric_names:
                        if name in yearly_financials.index and pd.notna(yearly_financials[name]):
                            return float(yearly_financials[name])
                    return 0.0

                revenue = get_metric(['Total Revenue', 'Operating Revenue', 'Revenue'])
                operating_expenses = get_metric(['Operating Expense', 'Total Operating Expenses', 'Operating Costs'])
                net_income = get_metric(['Net Income', 'Net Income Common Stockholders', 'Net Income From Continuing Operations'])

                data_financials.append({
                    'Ticker': ticker_symbol,
                    'Nombre_Empresa': nombre_empresa,
                    'Año': date_col.year,
                    'Fecha': date_col.date(),
                    'Ingresos_Totales': revenue,
                    'Gastos_Operativos': operating_expenses,
                    'Utilidad_Neta': net_income
                })
            print(f"-> Datos financieros históricos extraídos para {ticker_symbol}.")
            
        except Exception as e:
            print(f"Error procesando finanzas de {ticker_symbol}: {e}")

    # Guardar perfiles en un CSV
    df_profiles = pd.DataFrame(data_profiles)
    if not df_profiles.empty:
        df_profiles.to_csv('perfiles_restaurantes.csv', index=False)
        print(f"Perfiles exportados a perfiles_restaurantes.csv")

    # Guardar métricas financieras (con la regla de calidad)
    df_fin = pd.DataFrame(data_financials)
    
    if not df_fin.empty:
        df_fin = df_fin[df_fin['Ingresos_Totales'] > 0]
        
        df_fin['Margen_Neto_porcentual'] = df_fin.apply(
            lambda row: (row['Utilidad_Neta'] / row['Ingresos_Totales'] * 100) if row['Ingresos_Totales'] > 0 else 0,
            axis=1
        )
        
        df_fin = df_fin.sort_values(by=['Ticker', 'Año'], ascending=[True, False])
        df_fin.to_csv('metricas_restaurantes.csv', index=False)
        print(f"Métricas financieras exportadas a metricas_restaurantes.csv")
    else:
        print("No se encontraron datos financieros para procesar.")

if __name__ == '__main__':
    process_financials()

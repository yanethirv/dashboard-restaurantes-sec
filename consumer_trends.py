import pandas as pd
from pytrends.request import TrendReq
import time

def obtener_tendencia_busqueda(nombre_empresa):
    try:
        # Extraer la primera palabra
        keyword = nombre_empresa.split()[0].replace(',', '')
        
        # Iniciar pytrends
        pytrend = TrendReq(hl='es-US', tz=360)
        
        # Construir payload para los últimos 12 meses
        pytrend.build_payload([keyword], timeframe='today 12-m')
        
        # Extraer datos de interés sobre el tiempo
        df = pytrend.interest_over_time()
        
        if not df.empty and 'isPartial' in df.columns:
            df = df.drop(columns=['isPartial'])
            
        return df, keyword
    except Exception as e:
        print(f"Error obteniendo tendencias para {nombre_empresa}: {e}")
        return pd.DataFrame(), nombre_empresa.split()[0]

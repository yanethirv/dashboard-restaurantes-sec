import pandas_datareader.data as web
import datetime
import pandas as pd

def obtener_inflacion_alimentos():
    try:
        end = datetime.date.today()
        start = end.replace(year=end.year - 5)
        # CPIUFDNS: Índice de Precios al Consumidor para Alimentos (FRED)
        df = web.DataReader('CPIUFDNS', 'fred', start, end)
        df.columns = ['Índice de Inflación de Alimentos']
        return df
    except Exception as e:
        return pd.DataFrame()

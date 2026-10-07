import requests
import pandas as pd
import time

def extract_sec_data():
    ciks = {
        'CMG': '0001058090',
        'MCD': '0000062709',
        'DPZ': '0001286681',
        'QSR': '0001618756',
        'WEN': '0000030697',
        'YUM': '0001041061',
        'DRI': '0000940944',
        'SHAK': '0001620533',
        'SG': '0001477815'
    }
    
    headers = {
        'User-Agent': 'Proyecto Analisis (proyectosec@ejemplo.com)',
        'Accept-Encoding': 'gzip, deflate'
    }
    
    resultados = []

    for ticker, cik in ciks.items():
        print(f"\nConsultando la API de la SEC para {ticker} (CIK: {cik})...")
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                facts = data.get('facts', {})
                
                us_gaap = facts.get('us-gaap', {})
                custom_namespace = facts.get(ticker.lower(), {})
                
                # Función interna robusta para buscar en ambos espacios de nombres
                def get_latest_10k_value(possible_tags):
                    # 1. Buscar en us-gaap
                    for tag in possible_tags:
                        if tag in us_gaap:
                            units = us_gaap[tag].get('units', {})
                            if 'USD' in units:
                                records = units['USD']
                                # Filtrar de forma estricta el reporte anual Formulario 10-K
                                records_10k = [r for r in records if r.get('form') == '10-K']
                                if records_10k:
                                    latest = sorted(records_10k, key=lambda x: x.get('end', ''))[-1]
                                    return latest.get('val'), latest.get('fy')
                                    
                    # 2. Buscar en el espacio de nombres propio (custom namespace)
                    for tag in possible_tags:
                        if tag in custom_namespace:
                            units = custom_namespace[tag].get('units', {})
                            if 'USD' in units:
                                records = units['USD']
                                records_10k = [r for r in records if r.get('form') == '10-K']
                                if records_10k:
                                    latest = sorted(records_10k, key=lambda x: x.get('end', ''))[-1]
                                    return latest.get('val'), latest.get('fy')
                                    
                    return None, None
                
                tags_revenues = ['RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues', 'SalesRevenueNet', 'SalesRevenueGoodsNet', 'RevenueFromContractWithCustomerIncludingAssessedTax', 'SalesRevenueServicesNet']
                tags_cogs = ['CostOfGoodsAndServicesSold', 'CostOfRevenue', 'CostOfSales', 'FoodAndBeverageCost', 'FoodAndPaperCosts', 'FoodAndBeverageCostOfSales', 'RestaurantOperatingCosts', 'CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization', 'OperatingExpenses']
                
                rev_val, rev_year = get_latest_10k_value(tags_revenues)
                cogs_val, cogs_year = get_latest_10k_value(tags_cogs)
                
                # MODO DEBUG: Sugerencia de llaves si los datos siguen fallando
                if rev_val is None or cogs_val is None:
                    print(f"ADVERTENCIA: Faltan datos para {ticker}. MODO DEBUG activado...")
                    todas_las_keys = list(us_gaap.keys()) + list(custom_namespace.keys())
                    posibles_revenue = [k for k in todas_las_keys if 'revenue' in k.lower() or 'sales' in k.lower()]
                    posibles_cost = [k for k in todas_las_keys if 'cost' in k.lower() or 'expense' in k.lower()]
                    
                    if rev_val is None:
                        print(f"[{ticker}] No se encontró 'Revenues'. Algunas etiquetas sugeridas:")
                        print(posibles_revenue[:40]) 
                        
                    if cogs_val is None:
                        print(f"[{ticker}] No se encontró 'CostOfGoods...'. Algunas etiquetas sugeridas:")
                        print(posibles_cost[:40])
                
                resultados.append({
                    'Ticker': ticker,
                    'CIK': cik,
                    'Año_Fiscal': rev_year or cogs_year,
                    'Revenues': rev_val,
                    'CostOfGoodsAndServicesSold': cogs_val
                })
                print(f"-> Extracción finalizada para {ticker}. Revenues: {rev_val}, COGS: {cogs_val}")
            else:
                print(f"Error HTTP {response.status_code} para {ticker}: {response.text}")
                
        except Exception as e:
            print(f"Error procesando {ticker}: {e}")
            
        time.sleep(1)

    # Exportación final
    df = pd.DataFrame(resultados)
    df.to_csv('sec_datos_auditados.csv', index=False)
    print("\nProceso concluido. Datos guardados en sec_datos_auditados.csv.")

if __name__ == "__main__":
    extract_sec_data()

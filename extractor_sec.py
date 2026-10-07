import os
from sec_edgar_downloader import Downloader

def download_10k_reports():
    # SEC EDGAR requires a User-Agent in the form of "Company Name email@example.com"
    # Por favor, actualiza estos valores con tu información real o del proyecto
    company_name = "Proyecto_Analisis_Financiero"
    email_address = "tu.email@ejemplo.com"
    
    # Directorio donde se guardarán los datos descargados
    download_folder = os.path.join(os.getcwd(), "datos_crudos_sec")
    os.makedirs(download_folder, exist_ok=True)
    
    # Inicializar el descargador
    dl = Downloader(company_name, email_address, download_folder)
    
    # Tickers de las empresas de comida rápida solicitadas
    # CMG: Chipotle Mexican Grill
    # QSR: Restaurant Brands International
    # MCD: McDonald's
    tickers = ["CMG", "QSR", "MCD"]
    
    for ticker in tickers:
        print(f"Descargando el último reporte 10-K para {ticker}...")
        try:
            # '10-K' es el tipo de reporte anual
            # limit=1 asegura que solo se descargue el último disponible
            dl.get("10-K", ticker, limit=1)
            print(f"Descarga completada con éxito para {ticker}\n")
        except Exception as e:
            print(f"Error al descargar los datos para {ticker}: {e}\n")

if __name__ == "__main__":
    print("Iniciando la extracción de datos de la SEC...")
    download_10k_reports()
    print("Extracción finalizada. Revisa la carpeta 'datos_crudos_sec'.")

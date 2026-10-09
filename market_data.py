import yfinance as yf
import urllib.request
import xml.etree.ElementTree as ET

def obtener_metricas_bursatiles(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # Extracción de precio ultra-robusta usando el historial oficial del día
        hist = stock.history(period="1d")
        precio = round(hist['Close'].iloc[-1], 2) if not hist.empty else "N/A"
        precio_str = f"${precio}" if precio != "N/A" else "N/A"
        
        info = stock.info
        
        # Extracción y formateo seguro
        mcap = info.get('marketCap', 'N/A')
        mcap_str = f"${mcap / 1e9:.2f}B" if isinstance(mcap, (int, float)) else "N/A"
        
        pe = info.get('trailingPE', 'N/A')
        pe_str = round(pe, 2) if isinstance(pe, (int, float)) else "N/A"
        
        return {"precio": precio_str, "market_cap": mcap_str, "pe_ratio": pe_str}
    except Exception as e:
        return {"precio": "N/A", "market_cap": "N/A", "pe_ratio": "N/A"}

def obtener_noticias_recientes(ticker):
    try:
        url = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US'
        # Simulamos ser un navegador web estándar para evitar el bloqueo del servidor
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        noticias = []
        
        # Extraemos los 5 titulares más recientes
        for item in root.findall('.//item')[:5]:
            titulo = item.find('title').text
            if titulo:
                noticias.append(f"- {titulo}")
                
        return "\n".join(noticias) if noticias else ""
    except Exception as e:
        return ""

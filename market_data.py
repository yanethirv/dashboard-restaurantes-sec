import yfinance as yf

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

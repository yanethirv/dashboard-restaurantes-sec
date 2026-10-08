import yfinance as yf

def obtener_metricas_bursatiles(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        precio = info.get('currentPrice', 'N/A')
        mcap = info.get('marketCap', 'N/A')
        pe = info.get('trailingPE', 'N/A')
        if mcap != 'N/A':
            mcap = f"${mcap / 1e9:.2f}B"
        return {"precio": f"${precio}", "market_cap": mcap, "pe_ratio": pe}
    except:
        return {"precio": "N/A", "market_cap": "N/A", "pe_ratio": "N/A"}

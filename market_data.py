import yfinance as yf

def format_market_cap(value):
    if value is None:
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f} Trillones"
    elif value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f} Billones"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f} Millones"
    else:
        return f"${value:,.2f}"

def obtener_metricas_bursatiles(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        precio_actual = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
        if precio_actual != 'N/A':
            precio_actual = f"${precio_actual:,.2f}"
            
        market_cap_raw = info.get('marketCap')
        market_cap = format_market_cap(market_cap_raw)
        
        pe_ratio = info.get('trailingPE', 'N/A')
        if pe_ratio != 'N/A':
            pe_ratio = f"{pe_ratio:.2f}"
            
        return {
            'precio_actual': precio_actual,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio
        }
    except Exception as e:
        print(f"Error extrayendo datos para {ticker_symbol}: {e}")
        return {
            'precio_actual': "N/A",
            'market_cap': "N/A",
            'pe_ratio': "N/A"
        }

import os
import requests
import yfinance as yf
import pandas as pd  # Por si hay problemas con la manipulación de datos

# Obtener variables desde los Secrets de GitHub
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Verificar que las variables de entorno existen
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("❌ Error: No se encontraron las credenciales de Telegram en los Secrets de GitHub.")

# Función para enviar mensaje por Telegram
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"⚠️ Error al enviar alerta: {response.text}")
        else:
            print(f"✅ Mensaje enviado: {message}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la solicitud HTTP: {e}")

# Enviar mensaje de prueba al principio
send_telegram_alert("✅ Prueba de alerta: el bot está funcionando correctamente.")

# Listas de empresas
argentinian_tickers = ['YPF', 'TS', 'GGAL', 'BBVA', 'LOMA', 'MELI']
international_tickers = ['AAPL', 'GOOG', 'MSFT', 'AMZN']
all_tickers = argentinian_tickers + international_tickers

# Descargar datos históricos (1 año)
dataframes = {}
for ticker in all_tickers:
    stock_data = yf.Ticker(ticker).history(period="1y")
    
    # Evitar procesar DataFrames vacíos
    if stock_data.empty:
        print(f"⚠️ Advertencia: No se encontraron datos para {ticker}. Saltando...")
        continue

    dataframes[ticker] = stock_data

# Función para detectar anomalías en volumen y precio
def detect_anomalies(df, ticker):
    df = df.copy()  # Para evitar advertencias de pandas

    if len(df) < 30:  # Evita cálculos si no hay suficientes datos
        return False, 0, 0, 0

    df["Rolling_Avg"] = df["Volume"].rolling(window=30).mean()
    
    latest_volume = df["Volume"].iloc[-1]
    rolling_avg = df["Rolling_Avg"].iloc[-1]

    # Evitar división por cero en el cálculo de variación porcentual
    if df["Close"].iloc[-2] == 0:
        price_change = 0
    else:
        price_change = abs((df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2])

    # Condición: volumen anómalo + precio sin mucho cambio (<1%)
    if latest_volume > 2 * rolling_avg and price_change < 0.01:
        return True, latest_volume, rolling_avg, price_change * 100
    return False, latest_volume, rolling_avg, price_change * 100

# Revisar todas las empresas y enviar alertas si hay anomalías
alertas = []
for ticker, df in dataframes.items():
    is_anomaly, latest_volume, avg_volume, price_change = detect_anomalies(df, ticker)

    if is_anomaly:
        msg = (f"🚨 Anomalía detectada en {ticker} 🚨\n"
               f"📈 Volumen: {latest_volume:,}\n"
               f"📊 Promedio 30 días: {avg_volume:,.2f}\n"
               f"📉 Cambio en precio: {price_change:.2f}%")
        alertas.append(msg)

# Enviar alertas por Telegram si hay anomalías
if alertas:
    for alerta in alertas:
        send_telegram_alert(alerta)
    print("✅ Alertas enviadas por Telegram.")
else:
    print("✅ No se detectaron anomalías en volumen/precio.")



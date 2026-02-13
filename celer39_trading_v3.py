import os
import asyncio
import re
import json
from datetime import datetime
from telethon import TelegramClient, events
from dotenv import load_dotenv
import MetaTrader5 as mt5
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

# --- CONFIGURACIÓN ---
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
MT5_ACCOUNT = int(os.getenv("MT5_ACCOUNT"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")
SHEET_ID = "1nJpBFKHPBMv7id465k0nuHtpnA6a5rGtg2_1gCEJS_A"
TARGET_CHANNELS = ['GoldSignals.io', 'Apex Bull', 'United Signals']
RISK_PERCENT = 0.01  # 1% por operación
DEFAULT_LOT = 0.01
MAGIC_NUMBER = 393939

# --- GOOGLE SHEETS SETUP ---
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'google_service_account.json'

def log_to_sheets(data):
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        
        values = [data]
        body = {'values': values}
        
        # Asumimos que la pestaña se llama 'Trading'
        result = sheet.values().append(
            spreadsheetId=SHEET_ID, range="Trading!A1",
            valueInputOption="RAW", body=body).execute()
        return True
    except Exception as e:
        print(f"❌ Error logging to Sheets: {e}")
        return False

# --- PARSING LOGIC ---
def parse_signal(text):
    text = text.upper().replace("*", "")
    signal = {'symbol': 'XAUUSD', 'raw': text}
    
    if "XAUUSD" in text or "GOLD" in text:
        # Tipo de Orden
        if "BUY" in text:
            signal['type'] = mt5.ORDER_TYPE_BUY
            signal['type_str'] = "BUY"
        elif "SELL" in text:
            signal['type'] = mt5.ORDER_TYPE_SELL
            signal['type_str'] = "SELL"
        else:
            return None
        
        # Precios (Regex mejorado para mayor sensibilidad)
        prices = re.findall(r"(\d{4}(?:\.\d+)?)", text)
        
        # Flexibilidad en la detección de parámetros
        entry_match = re.search(r"(?:ENTRY|@|PRICE|NOW|CMP|ZONE|AT)\s*[:\-\s]*(\d{4}(?:\.\d+)?)", text)
        sl_match = re.search(r"(?:SL|STOP|STOPLOSS|S/L)\s*[:\-\s]*(\d{4}(?:\.\d+)?)", text)
        tp_matches = re.findall(r"(?:TP|TARGET|TAKEPROFIT|T/P)\s*\d*[:\-\s]*(\d{4}(?:\.\d+)?)", text)
        
        if entry_match: 
            signal['price'] = float(entry_match.group(1))
        elif prices: 
            signal['price'] = float(prices[0])
        
        if sl_match: 
            signal['sl'] = float(sl_match.group(1))
        elif len(prices) > 1: 
            # Si hay dos precios y no hay SL explícito, el segundo suele ser SL si está lejos del TP
            p2 = float(prices[1])
            if signal['type'] == mt5.ORDER_TYPE_BUY and p2 < signal.get('price', 0):
                signal['sl'] = p2
            elif signal['type'] == mt5.ORDER_TYPE_SELL and p2 > signal.get('price', 0):
                signal['sl'] = p2
        
        if tp_matches: 
            signal['tp'] = float(tp_matches[0])
        
        return signal
    return None

# --- RISK MANAGEMENT ---
def calculate_lot(balance, entry, sl, type):
    if not sl or entry == sl:
        return DEFAULT_LOT
    
    risk_amount = balance * RISK_PERCENT
    price_diff = abs(entry - sl)
    
    # En XAUUSD, 1 lot = 100 oz. Un movimiento de 1.00 USD = $100.
    # Lote = Riesgo / (Diferencia de Precio * 100)
    try:
        lot = risk_amount / (price_diff * 100)
        return round(max(0.01, min(lot, 5.0)), 2) # Cap de 5 lotes por seguridad
    except:
        return DEFAULT_LOT

# --- MT5 EXECUTION ---
async def execute_trade(signal):
    if not mt5.initialize(login=MT5_ACCOUNT, password=MT5_PASSWORD, server=MT5_SERVER):
        print("❌ Error MT5 Init")
        return

    # Mapeo de Símbolo (Adaptabilidad)
    symbol = signal['symbol']
    found_symbol = None
    for s in [symbol, "XAUUSD.m", "XAUUSD+", "GOLD"]:
        if mt5.symbol_info(s):
            found_symbol = s
            break
    
    if not found_symbol:
        print(f"❌ Símbolo {symbol} no encontrado.")
        return

    mt5.symbol_select(found_symbol, True)
    account_info = mt5.account_info()
    balance = account_info.balance
    
    tick = mt5.symbol_info_tick(found_symbol)
    current_price = tick.ask if signal['type'] == mt5.ORDER_TYPE_BUY else tick.bid
    
    entry_price = signal.get('price', current_price)
    sl_price = signal.get('sl')
    tp_price = signal.get('tp')
    
    lot = calculate_lot(balance, entry_price, sl_price, signal['type'])
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": found_symbol,
        "volume": lot,
        "type": signal['type'],
        "price": current_price,
        "sl": sl_price if sl_price else 0.0,
        "tp": tp_price if tp_price else 0.0,
        "magic": MAGIC_NUMBER,
        "comment": "Celer39 V3 Auto",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    
    status = "SUCCESS" if result.retcode == mt5.TRADE_RETCODE_DONE else f"FAILED ({result.comment})"
    print(f"--- RESULTADO: {status} ---")
    
    # Log to Sheets
    log_data = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        signal['type_str'],
        found_symbol,
        lot,
        entry_price,
        sl_price if sl_price else "N/A",
        tp_price if tp_price else "N/A",
        status,
        signal['raw'][:100] # Primeros 100 caracteres del mensaje
    ]
    log_to_sheets(log_data)
    
    mt5.shutdown()

# --- MAIN ---
client = TelegramClient('celer39_listener', API_ID, API_HASH)

async def main():
    try:
        print("⚡ CELER39 TRADING V3 - ACTIVADO")
        await client.start()
        
        # Obtener IDs una sola vez
        dialogs = await client.get_dialogs()
        target_ids = []
        for dialog in dialogs:
            if any(t.upper() in dialog.name.upper() for t in TARGET_CHANNELS):
                print(f"✅ Escuchando a: {dialog.name}")
                target_ids.append(dialog.id)

        @client.on(events.NewMessage(chats=target_ids))
        async def handler(event):
            try:
                # Log local para debug
                with open("trading_events.log", "a") as f:
                    f.write(f"{datetime.now()}: Mensaje de {event.chat.title}\n")
                
                signal = parse_signal(event.raw_text)
                if signal:
                    print(f"🚀 SEÑAL VÁLIDA: {signal['type_str']}")
                    await execute_trade(signal)
            except Exception as e:
                print(f"❌ Error in handler: {e}")

        print("--- Sistema en espera de señales ---")
        await client.run_until_disconnected()
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        with open("crash_log.txt", "a") as f:
            f.write(f"{datetime.now()}: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())

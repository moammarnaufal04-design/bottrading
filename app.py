import os
import ccxt
import time
import threading
from datetime import datetime
import streamlit as st

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Tokocrypto Trading Bot Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Penyimpanan Log Global
if 'global_logs' not in st.session_state:
    st.session_state['global_logs'] = []

LOG_FILE = "bot_logs.txt"

def add_log(message):
    """Menulis log ke file dan konsol"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Gagal menulis log ke file: {e}")
    print(log_entry.strip())

def read_logs():
    """Membaca log dari file"""
    if not os.path.exists(LOG_FILE):
        return ["Belum ada log aktivitas."]
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            # Ambil 50 log terakhir
            return [line.strip() for line in lines[-50:]]
    except Exception:
        return ["Gagal membaca file log."]

def calculate_rsi(prices, period=14):
    """Menghitung RSI secara manual tanpa library eksternal"""
    if len(prices) < period + 1:
        return None
    
    deltas = []
    for i in range(len(prices) - 1):
        deltas.append(prices[i+1] - prices[i])
    
    gains = []
    losses = []
    for d in deltas:
        if d > 0:
            gains.append(d)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(d))
            
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
    if avg_loss == 0:
        return 100.0
        
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

def run_trading_bot():
    """Fungsi utama logika bot trading"""
    api_key = os.environ.get("TOKO_API_KEY")
    secret_key = os.environ.get("TOKO_SECRET_KEY")
    symbol = os.environ.get("SYMBOL", "BTC/BIDR")
    rsi_period = int(os.environ.get("RSI_PERIOD", "14"))
    rsi_overbought = float(os.environ.get("RSI_OVERBOUGHT", "70"))
    rsi_oversold = float(os.environ.get("RSI_OVERSOLD", "30"))
    trade_amount = float(os.environ.get("TRADE_AMOUNT", "0.0001"))
    dry_run = os.environ.get("DRY_RUN", "True").lower() == "true"

    add_log(f"--- Memulai Cek Pasar: {symbol} (Dry Run: {dry_run}) ---")

    if not api_key or not secret_key:
        add_log("Pemberitahuan: API Key belum diisi di Secrets. Bot berjalan dalam mode pantau pasar saja.")
        exchange = ccxt.tokocrypto()
    else:
        exchange = ccxt.tokocrypto({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True
        })

    try:
        # Ambil data harga historis (15m candles)
        timeframe = '15m'
        candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=50)
        if not candles:
            raise Exception("Gagal mengambil data candlestick.")
            
        close_prices = [candle[4] for candle in candles]
        current_price = close_prices[-1]
        add_log(f"Harga {symbol} saat ini: {current_price:.2f}")

        # Hitung RSI
        rsi = calculate_rsi(close_prices, period=rsi_period)
        if rsi is None:
            raise Exception("Data tidak cukup untuk menghitung RSI.")
        add_log(f"RSI ({rsi_period}): {rsi:.2f}")

        # Pengecekan saldo & transaksi (jika ada API Key)
        if api_key and secret_key:
            balance = exchange.fetch_balance()
            base_currency = symbol.split('/')[0]
            quote_currency = symbol.split('/')[1]
            
            base_balance = balance['free'].get(base_currency, 0.0)
            quote_balance = balance['free'].get(quote_currency, 0.0)
            
            add_log(f"Saldo {base_currency}: {base_balance} | Saldo {quote_currency}: {quote_balance}")
            estimated_cost = current_price * trade_amount

            # Logika keputusan order
            if rsi <= rsi_oversold:
                add_log(f"Sinyal: BELI (RSI {rsi:.2f} <= {rsi_oversold})")
                if quote_balance >= estimated_cost:
                    if dry_run:
                        add_log(f"[SIMULASI] Menempatkan Order Beli: {trade_amount} {base_currency}")
                    else:
                        order = exchange.create_market_buy_order(symbol, trade_amount)
                        add_log(f"SUKSES: Order Beli Terkirim. ID: {order['id']}")
                else:
                    add_log(f"Saldo {quote_currency} tidak cukup untuk beli.")
            
            elif rsi >= rsi_overbought:
                add_log(f"Sinyal: JUAL (RSI {rsi:.2f} >= {rsi_overbought})")
                if base_balance >= trade_amount:
                    if dry_run:
                        add_log(f"[SIMULASI] Menempatkan Order Jual: {trade_amount} {base_currency}")
                    else:
                        order = exchange.create_market_sell_order(symbol, trade_amount)
                        add_log(f"SUKSES: Order Jual Terkirim. ID: {order['id']}")
                else:
                    add_log(f"Saldo {base_currency} tidak cukup untuk jual.")
            else:
                add_log("Sinyal: Netral. Tidak ada aksi.")
        else:
            add_log("Mode pantau: Menghindari transaksi karena API Key kosong.")

    except Exception as e:
        add_log(f"ERROR: {str(e)}")
    
    add_log("--- Cek Pasar Selesai ---")

def bot_loop():
    """Loop yang berjalan di background thread setiap 15 menit"""
    add_log("Memulai Background Thread Bot...")
    while True:
        try:
            run_trading_bot()
        except Exception as e:
            add_log(f"Kesalahan pada loop bot: {e}")
        # Tidur selama 15 menit (900 detik)
        time.sleep(900)

# 2. Inisialisasi Thread Background agar hanya berjalan 1 kali
thread_name = "TradingBotThread"
thread_active = False
for t in threading.enumerate():
    if t.name == thread_name:
        thread_active = True
        break

if not thread_active:
    t = threading.Thread(target=bot_loop, name=thread_name, daemon=True)
    t.start()
    add_log("Thread Bot berhasil dijalankan.")

# 3. Tampilan Interface Streamlit (Dashboard)
st.title("🤖 Tokocrypto Auto Trading Bot Dashboard")
st.write("Aplikasi ini berjalan 24/7 di Hugging Face Spaces untuk mengawasi pasar Tokocrypto.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Konfigurasi Bot (Environment)")
    st.markdown(f"**Pasangan Koin (Symbol):** `{os.environ.get('SYMBOL', 'BTC/BIDR')}`")
    st.markdown(f"**RSI Period:** `{os.environ.get('RSI_PERIOD', '14')}`")
    st.markdown(f"**RSI Overbought (Jual):** `{os.environ.get('RSI_OVERBOUGHT', '70')}`")
    st.markdown(f"**RSI Oversold (Beli):** `{os.environ.get('RSI_OVERSOLD', '30')}`")
    st.markdown(f"**Jumlah Transaksi (Trade Amount):** `{os.environ.get('TRADE_AMOUNT', '0.0001')}`")
    
    dry_run_status = os.environ.get('DRY_RUN', 'True')
    if dry_run_status.lower() == 'true':
        st.warning("⚠️ Bot berjalan dalam mode SIMULASI (Dry Run: True). Uang asli Anda aman.")
    else:
        st.danger("🔥 Bot berjalan dalam mode ASLI (Dry Run: False). Transaksi riil aktif.")

    # Tombol Manual Trigger
    if st.button("Jalankan Cek Pasar Sekarang"):
        with st.spinner("Menjalankan analisis..."):
            run_trading_bot()
        st.success("Analisis selesai dijalankan!")

with col2:
    st.subheader("Aktivitas Bot (Logs Terbaru)")
    
    # Tombol Refresh Log
    if st.button("Refresh Logs"):
        st.rerun()

    # Tampilkan Logs
    logs = read_logs()
    log_text = "\n".join(logs)
    st.text_area(label="Log Output (50 Baris Terakhir)", value=log_text, height=400, disabled=True)

st.info("💡 Agar dashboard ini tidak tidur (sleep), Anda bisa memasukkan URL Space ini ke cron-job.org untuk di-ping setiap 15 menit.")

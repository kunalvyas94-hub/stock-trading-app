import streamlit as st
import pandas as pd
import yfinance as yf
from SmartApi import SmartConnect
import datetime

# Page Setup
st.set_page_config(page_title="My Trading Dashboard", layout="wide")

st.title("📈 Stock Support & Resistance")

# --- SIDEBAR: Settings & Login ---
st.sidebar.header("Settings")
market = st.sidebar.selectbox("Market Select Karein", ["NIFTY", "BANKNIFTY"])

st.sidebar.markdown("---")
st.sidebar.subheader("Angle One Login")
api_key = st.sidebar.text_input("API Key", type="password")
client_id = st.sidebar.text_input("Client ID")
pwd = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Connect to Broker"):
    st.sidebar.info("API connection logic yahan chalegi.")

# --- DATA FETCHING LOGIC ---
# Stable symbols for Yahoo Finance
# Updated Stable Symbols
if market == "NIFTY":
    symbol = "^NSEI"
else:
    symbol = "^NSEBANK"

# Optional: Agar upar wala kaam na kare toh niche wala try karein
# symbol = "NIFTY50.NS" if market == "NIFTY" else "BANKNIFTY.NS"

try:
    # Pichle 5 din ka data le rahe hain taaki Pivot levels nikal sakein
    df = yf.download(symbol, period="5d", interval="15m")

    if not df.empty:
        # Latest data points
        current_price = df['Close'].iloc[-1]
        last_day_high = df['High'].iloc[-2]
        last_day_low = df['Low'].iloc[-2]
        last_day_close = df['Close'].iloc[-1]

        # Standard Pivot Point Calculation
        pivot = (last_day_high + last_day_low + last_day_close) / 3
        r1 = (2 * pivot) - last_day_low
        s1 = (2 * pivot) - last_day_high

        # --- DISPLAY ---
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Live {market} Price", f"{current_price:.2f}")
        col2.metric("Resistance (R1)", f"{r1:.2f}")
        col3.metric("Support (S1)", f"{s1:.2f}")

        st.markdown("---")

        # Trading Signals
        if current_price <= s1:
            st.success(f"🔥 BUY SIGNAL: {market} Support ke paas hai!")
        elif current_price >= r1:
            st.error(f"⚠️ SELL SIGNAL: {market} Resistance ke paas hai!")
        else:
            st.info("Market abhi Range mein hai (No Signal).")

        # Basic Chart
        st.subheader(f"{market} Price Movement (15 min)")
        st.line_chart(df['Close'])

    else:
        st.warning("Market data abhi available nahi hai. Thodi der baad koshish karein.")

except Exception as e:
    st.error(f"Kuch galti hui hai: {e}")

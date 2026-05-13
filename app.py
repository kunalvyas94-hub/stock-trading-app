import streamlit as st
import pandas as pd
import yfinance as yf
from SmartApi import SmartConnect

st.set_page_config(page_title="My Trade App", layout="wide")

# --- Angle One Setup ---
st.sidebar.title("Login Details")
api_key = st.sidebar.text_input("API Key")
client_id = st.sidebar.text_input("Client ID")
pwd = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    st.sidebar.success("Koshish jari hai... (API Setup required)")

# --- Dashboard Logic ---
st.title("📈 Support & Resistance Dashboard")
market = st.selectbox("Market Choose Karein", ["NIFTY", "BANKNIFTY"])
symbol = "^NSEI" if market == "NIFTY" else "^NSEBANK"

# Data fetching
data = yf.download(symbol, period="2d", interval="15m")
if not data.empty:
    pivot = (data['High'].iloc[-2] + data['Low'].iloc[-2] + data['Close'].iloc[-2]) / 3
    s1 = (2 * pivot) - data['High'].iloc[-2]
    r1 = (2 * pivot) - data['Low'].iloc[-2]
    current = data['Close'].iloc[-1]

    st.metric("Live Price", f"{current:.2f}")
    st.write(f"**Support (S1):** {s1:.2f} | **Resistance (R1):** {r1:.2f}")

    if current <= s1:
        st.success("BUY SIGNAL: Price Support par hai!")
    elif current >= r1:
        st.error("SELL SIGNAL: Price Resistance par hai!")

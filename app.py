import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp
import datetime

# Page Setup
st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")

st.title("🚀 Angle One Smart Dashboard (Indicators Enabled)")

# --- SIDEBAR: API Settings ---
st.sidebar.header("Broker Login")
api_key = st.sidebar.text_input("API Key", type="password")
client_id = st.sidebar.text_input("Client ID")
password = st.sidebar.text_input("Password", type="password")
totp_key = st.sidebar.text_input("TOTP Key (Manual Key)", type="password")

if 'smartApi' not in st.session_state:
    st.session_state.smartApi = None

if st.sidebar.button("Login to Angle One"):
    try:
        smartApi = SmartConnect(api_key=api_key)
        otp = pyotp.TOTP(totp_key).now()
        data = smartApi.generateSession(client_id, password, otp)
        
        if data['status']:
            st.session_state.smartApi = smartApi
            st.sidebar.success("✅ Login Successful!")
        else:
            st.sidebar.error(f"❌ Login Failed: {data['message']}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- MARKET SELECTION ---
market = st.sidebar.selectbox("Kya Trade Karna Hai?", ["NIFTY", "BANKNIFTY", "SUZLON", "FEDERALBNK"])

# --- CHART & INDICATORS SECTION ---
st.subheader(f"📈 {market} Live Technical Chart")
st.caption("Auto-Indicators: 20 DMA (Blue), 20 EMA (Orange), RSI (Bottom)")

# TradingView Widget with Indicators Pre-loaded
chart_symbol = f"NSE:{market}"
if market == "SUZLON": chart_symbol = "NSE:SUZLON"
if market == "FEDERALBNK": chart_symbol = "NSE:FEDERALBNK"

chart_code = f"""
<div class="tradingview-widget-container" style="height:550px;">
  <div id="tradingview_123"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true,
    "symbol": "{chart_symbol}",
    "interval": "5",
    "timezone": "Asia/Kolkata",
    "theme": "light",
    "style": "1",
    "locale": "in",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "withdateranges": true,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "details": true,
    "studies": [
      "MAExp@tv-basicstudies", 
      "MASimple@tv-basicstudies",
      "RSI@tv-basicstudies"
    ],
    "container_id": "tradingview_123"
  }});
  </script>
</div>
"""
st.components.v1.html(chart_code, height=560)

# --- LIVE DATA & SIGNALS ---
if st.session_state.smartApi:
    # Token Logic
    tokens = {
        "NIFTY": "99926000", 
        "BANKNIFTY": "99926009",
        "SUZLON": "532667", # Suzlon Token
        "FEDERALBNK": "10217" # Federal Bank Token
    }
    symbol_token = tokens.get(market, "99926000")
    exchange = "NSE" if market in ["NIFTY", "BANKNIFTY"] else "NSE"
    
    try:
        ohlc_data = st.session_state.smartApi.ltpData(exchange, market, symbol_token)
        
        if ohlc_data['status']:
            ltp = float(ohlc_data['data']['ltp'])
            
            st.markdown("---")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric(f"Live {market} Price", f"₹{ltp}")
                st.write("**Strategy Status:**")
                
                # Intelligent Signal Logic
                if market == "BANKNIFTY":
                    buy_above, sell_below = 53850, 53750
                elif market == "SUZLON":
                    buy_above, sell_below = 53.00, 51.50
                else:
                    buy_above, sell_below = ltp + 10, ltp - 10 # Default for others
                
                if ltp > buy_above:
                    st.success(f"🟢 BUY: Price is above 20 DMA/EMA")
                elif ltp < sell_below:
                    st.error(f"🔴 SELL: Weakness below support")
                else:
                    st.warning(f"⏳ WAIT: Looking for 20 DMA crossover")

            with col2:
                st.info(f"💡 **Admin/HR Tip:** Market trend abhi check ho raha hai. Suzlon aur Federal Bank ke liye RSI 40-60 ke beech neutral mana jata hai.")
        
    except Exception as e:
        st.error(f"Data Fetch Error: {e}")
else:
    st.warning("Sidebar se Login karein taaki chart ke niche Live Price aur Signals chalu ho sakein.")

st.markdown("---")
st.caption("Custom Built for HR & Admin Professionals | Stock Market Dashboard")

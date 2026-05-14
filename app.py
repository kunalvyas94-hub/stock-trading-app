import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp
import datetime

# Page Setup
st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")

st.title("🚀 Angle One Smart Dashboard + Option Assistant")

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

# --- CHART SECTION ---
st.subheader(f"📈 {market} Live Technical Chart")
chart_symbol = f"NSE:{market}"
if market == "SUZLON": chart_symbol = "NSE:SUZLON"
if market == "FEDERALBNK": chart_symbol = "NSE:FEDERALBNK"

chart_code = f"""
<div class="tradingview-widget-container" style="height:500px;">
  <div id="tradingview_123"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true, "symbol": "{chart_symbol}", "interval": "5", "timezone": "Asia/Kolkata",
    "theme": "light", "style": "1", "locale": "in", "toolbar_bg": "#f1f3f6",
    "studies": ["MAExp@tv-basicstudies", "MASimple@tv-basicstudies", "RSI@tv-basicstudies"],
    "container_id": "tradingview_123"
  }});
  </script>
</div>
"""
st.components.v1.html(chart_code, height=510)

# --- LIVE DATA & AI OPTION ASSISTANT ---
if st.session_state.smartApi:
    tokens = {"NIFTY": "99926000", "BANKNIFTY": "99926009", "SUZLON": "532667", "FEDERALBNK": "10217"}
    symbol_token = tokens.get(market, "99926000")
    
    try:
        ohlc_data = st.session_state.smartApi.ltpData("NSE", market, symbol_token)
        if ohlc_data['status']:
            ltp = float(ohlc_data['data']['ltp'])
            
            st.markdown("---")
            col_price, col_ai = st.columns([1, 1])
            
            with col_price:
                st.metric(f"Live {market} Price", f"₹{ltp}")
                # Signal Logic
                if ltp > 53850 or (market=="SUZLON" and ltp > 52.5):
                    st.success("🟢 TREND: BULLISH (Above 20 DMA)")
                    trend = "UP"
                elif ltp < 53750 or (market=="SUZLON" and ltp < 51.5):
                    st.error("🔴 TREND: BEARISH (Below 20 DMA)")
                    trend = "DOWN"
                else:
                    st.warning("⏳ TREND: SIDEWAYS")
                    trend = "SIDE"

            # --- NEW: AI OPTION ASSISTANT BOX ---
            with col_ai:
                st.subheader("🤖 AI Option Assistant")
                if st.button(f"Puchhein: Kaunsa Option lein?"):
                    st.info(f"Analyzing {market} current levels...")
                    
                    if market == "SUZLON":
                        strike = round(ltp)
                        if trend == "UP":
                            st.write(f"✅ **Suggested Trade:** Buy **SUZLON {strike} CE** (Call Option)")
                            st.write("📝 **Reason:** Price 20 DMA ke upar nikal raha hai, momentum strong hai.")
                        else:
                            st.write(f"⚠️ **Suggestion:** Abhi wait karein, Suzlon mein fresh entry 52.50 ke upar hi banegi.")
                            
                    elif market == "BANKNIFTY":
                        strike = round(ltp / 100) * 100
                        if trend == "UP":
                            st.write(f"🚀 **Suggested Trade:** Buy **BANKNIFTY {strike} CE**")
                            st.write(f"🎯 Target: {strike + 300} | 🛡️ SL: {strike - 150}")
                        elif trend == "DOWN":
                            st.write(f"📉 **Suggested Trade:** Buy **BANKNIFTY {strike} PE**")
                            st.write(f"🎯 Target: {strike - 300} | 🛡️ SL: {strike + 150}")
                    
                    elif market == "FEDERALBNK":
                        st.write(f"✅ **Suggested Trade:** Focus on **290 CE** or **300 CE** if price crosses 292.")
                        
                    st.caption("Note: Ye suggestions sirf calculation par adharit hain. Trade lene se pehle chart zarur check karein.")

    except Exception as e:
        st.error(f"Data Fetch Error: {e}")
else:
    st.warning("Sidebar se Login karein taaki AI Assistant activate ho sake.")

st.markdown("---")
st.caption("Designed for HR & Admin Pros | Technical Trading Engine")

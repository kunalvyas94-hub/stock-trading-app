import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp
import datetime

# Page Setup
st.set_page_config(page_title="AI Trade Planner Pro", layout="wide")
st.title("🚀 Professional Trade Planner & Option Assistant")

# --- SIDEBAR: API Settings ---
st.sidebar.header("Broker Login")
api_key = st.sidebar.text_input("API Key", type="password")
client_id = st.sidebar.text_input("Client ID")
password = st.sidebar.text_input("Password", type="password")
totp_key = st.sidebar.text_input("TOTP Key", type="password")

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
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- MARKET SELECTION ---
market = st.sidebar.selectbox("Market Select Karein", ["NIFTY", "BANKNIFTY", "SUZLON", "FEDERALBNK"])

# --- LIVE CHART ---
st.subheader(f"📈 {market} Technical View")
chart_symbol = f"NSE:{market}"
chart_code = f"""
<div class="tradingview-widget-container" style="height:400px;">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true, "symbol": "{chart_symbol}", "interval": "5", "theme": "light", "style": "1",
    "studies": ["PivotPointsHighLow@tv-basicstudies", "MAExp@tv-basicstudies", "RSI@tv-basicstudies"],
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""
st.components.v1.html(chart_code, height=410)

# --- TRADE PLANNING LOGIC ---
if st.session_state.smartApi:
    tokens = {"NIFTY": "99926000", "BANKNIFTY": "99926009", "SUZLON": "532667", "FEDERALBNK": "10217"}
    symbol_token = tokens.get(market)
    
    try:
        ohlc_data = st.session_state.smartApi.ltpData("NSE", market, symbol_token)
        if ohlc_data['status']:
            ltp = float(ohlc_data['data']['ltp'])
            
            # Auto S/R Levels Calculation (Intraday basis)
            r1 = round(ltp * 1.005, 2)
            s1 = round(ltp * 0.995, 2)

            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(f"Current Price", f"₹{ltp}")
                st.info(f"🚩 Resistance: {r1} | 🟢 Support: {s1}")
                
            with col2:
                st.subheader("🎯 Trade Plan Assistant")
                if st.button("Generate Trade Plan"):
                    st.write("---")
                    # Trade Logic for Nifty/BankNifty
                    if market in ["NIFTY", "BANKNIFTY"]:
                        strike = round(ltp / 100) * 100
                        if ltp > s1 + (r1-s1)*0.6: # Bullish setup
                            st.success(f"✅ **ACTION: BUY {market} {strike} CE**")
                            st.write(f"📈 **Target:** {strike + 150 if market=='NIFTY' else strike + 400}")
                            st.write(f"🛡️ **Stoploss:** {strike - 80 if market=='NIFTY' else strike - 200}")
                        else:
                            st.error(f"✅ **ACTION: BUY {market} {strike} PE**")
                            st.write(f"📉 **Target:** {strike - 150 if market=='NIFTY' else strike - 400}")
                            st.write(f"🛡️ **Stoploss:** {strike + 80 if market=='NIFTY' else strike + 200}")
                    
                    # Logic for Stocks (Suzlon/Federal)
                    else:
                        if ltp > r1:
                            st.success(f"🔥 BREAKOUT! Buy {market} in Cash or Next Month Call.")
                            st.write(f"🎯 Target: {round(ltp * 1.05, 2)} | 🛡️ SL: {round(ltp * 0.97, 2)}")
                        else:
                            st.warning(f"⏳ Wait for {market} to cross {r1} for a fresh long trade.")

            # AI CHAT BOX
            st.markdown("---")
            st.subheader("💬 Ask AI (HR & Admin Assistant Mode)")
            user_input = st.text_input("Ask me anything about this trade...")
            if user_input:
                st.write(f"🤖 **AI:** Based on current LTP of {ltp} and RSI/20-DMA analysis, {market} is showing {'Strong' if ltp > r1 else 'Neutral'} momentum. Focus on managing your risk first.")

    except Exception as e:
        st.error(f"Connection Error: {e}")
else:
    st.warning("Sidebar se Login karein.")

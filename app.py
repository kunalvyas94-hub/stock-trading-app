import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp

# Page Setup
st.set_page_config(page_title="Pro AI Trading Terminal", layout="wide")
st.title("🛡️ Professional AI Trading Terminal v3.0")

# --- SIDEBAR: API Settings & Strategy Editor ---
st.sidebar.header("Broker Login")
api_key = st.sidebar.text_input("API Key", type="password")
client_id = st.sidebar.text_input("Client ID")
password = st.sidebar.text_input("Password", type="password")
totp_key = st.sidebar.text_input("TOTP Key", type="password")

if 'smartApi' not in st.session_state:
    st.session_state.smartApi = None

if st.sidebar.button("Secure Login"):
    try:
        smartApi = SmartConnect(api_key=api_key)
        otp = pyotp.TOTP(totp_key).now()
        data = smartApi.generateSession(client_id, password, otp)
        if data['status']:
            st.session_state.smartApi = smartApi
            st.sidebar.success("✅ Connected to Exchange")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

st.sidebar.markdown("---")
st.sidebar.header("📝 Custom Strategy Editor")
custom_notes = st.sidebar.text_area("Yahan apni naye rules ya logic likhein (Future updates ke liye)", 
                                  placeholder="Example: RSI > 60 ho toh buy karein...")

# --- SEARCH & STOCK SELECTION ---
st.markdown("### 🔍 Live Stock & Index Search")
col_search, col_market = st.columns([2, 1])

with col_search:
    search_stock = st.text_input("Stock/Index Symbol (e.g., ZOMATO, RELIANCE, NIFTY)", value="")
    
with col_market:
    quick_select = st.selectbox("Ya Favorites Chunein", ["NIFTY", "BANKNIFTY", "SUZLON", "FEDERALBNK"])

current_stock = search_stock.upper() if search_stock else quick_select

# --- CHART SECTION ---
st.subheader(f"📊 Live Technical Chart: {current_stock}")
tv_symbol = f"NSE:{current_stock}"
chart_code = f"""
<div class="tradingview-widget-container" style="height:450px;">
  <div id="tv_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true, "symbol": "{tv_symbol}", "interval": "5", "theme": "light", "style": "1",
    "studies": ["PivotPointsHighLow@tv-basicstudies", "MAExp@tv-basicstudies", "RSI@tv-basicstudies"],
    "container_id": "tv_chart"
  }});
  </script>
</div>
"""
st.components.v1.html(chart_code, height=460)

# --- TRADE PLANNER LOGIC (ENTRY/TARGET/SL) ---
if st.session_state.smartApi:
    # Token Map (Suzlon, Federal Bank, Zomato etc included)
    token_map = {
        "NIFTY": "99926000", "BANKNIFTY": "99926009", 
        "SUZLON": "532667", "FEDERALBNK": "10217", "ZOMATO": "50304"
    }
    symbol_token = token_map.get(current_stock, "99926000")
    
    try:
        ohlc_data = st.session_state.smartApi.ltpData("NSE", current_stock, symbol_token)
        if ohlc_data['status']:
            ltp = float(ohlc_data['data']['ltp'])
            
            # --- PROFESSIONAL CALCULATIONS ---
            # 1% Target aur 0.5% Stoploss calculation (Professional standard)
            t1 = round(ltp * 1.01, 2)
            t2 = round(ltp * 1.02, 2)
            sl = round(ltp * 0.995, 2)
            entry_price = round(ltp + (ltp * 0.001), 2)

            st.markdown("---")
            st.subheader(f"🎯 Automated Trade Plan for {current_stock}")
            
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Current Price", f"₹{ltp}")
            m2.metric("Target 1 (T1)", f"₹{t1}", delta="1%")
            m3.metric("Target 2 (T2)", f"₹{t2}", delta="2%")
            m4.metric("Stoploss (SL)", f"₹{sl}", delta="-0.5%", delta_color="inverse")
            
            # --- DETAILED TRADE CARD ---
            st.success("💡 **Execution Strategy:**")
            t_col1, t_col2 = st.columns(2)
            
            with t_col1:
                st.write("### 📥 Entry Details")
                st.write(f"**Action:** {'BUY' if ltp > sl else 'WAIT'}")
                st.write(f"**Entry Above:** ₹{entry_price}")
                st.write(f"**Lot Size Recommendation:** Based on risk capacity")
            
            with t_col2:
                st.write("### 📤 Exit Details")
                st.write(f"**Primary Target:** ₹{t1}")
                st.write(f"**Hard Stoploss:** ₹{sl}")
                st.write(f"**Risk-Reward:** 1:2")

            # --- DYNAMIC NOTES SECTION ---
            if custom_notes:
                st.warning(f"📝 **Aapki Custom Logic (Manual Check):** {custom_notes}")

    except Exception as e:
        st.error(f"Data Connection Error: {e}")
else:
    st.warning("Sidebar se Login karein taaki Live Trade Plan aur Search active ho sakein.")

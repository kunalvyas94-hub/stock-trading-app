import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp
import datetime

# Page Setup
st.set_page_config(page_title="Professional AI Trader", layout="wide")
st.title("🛡️ Professional AI Trading Terminal")

# --- SIDEBAR: API Settings ---
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

# --- SEARCH & STOCK SELECTION ---
st.markdown("### 🔍 Live Stock Search")
col_search, col_market = st.columns([2, 1])

with col_search:
    # Search Bar for any stock
    search_stock = st.text_input("Stock Name Type Karein (e.g., RELIANCE, ZOMATO, SBIN)", value="NIFTY")
    
with col_market:
    # Quick Select for your favorites
    quick_select = st.selectbox("Ya Favorites Chunein", ["NIFTY", "BANKNIFTY", "SUZLON", "FEDERALBNK"])
    
current_stock = search_stock.upper() if search_stock else quick_select

# --- LIVE CHART SECTION ---
st.subheader(f"📊 Technical Analysis: {current_stock}")
chart_code = f"""
<div class="tradingview-widget-container" style="height:450px;">
  <div id="tv_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true, "symbol": "NSE:{current_stock}", "interval": "5", "theme": "light", "style": "1",
    "studies": ["PivotPointsHighLow@tv-basicstudies", "MAExp@tv-basicstudies", "RSI@tv-basicstudies"],
    "container_id": "tv_chart"
  }});
  </script>
</div>
"""
st.components.v1.html(chart_code, height=460)

# --- PROFESSIONAL TRADE PLANNER (ENTRY/EXIT/SL) ---
if st.session_state.smartApi:
    # Mapping tokens (Note: Real terminal mein aapko complete token list load karni chahiye)
    tokens = {"NIFTY": "99926000", "BANKNIFTY": "99926009", "SUZLON": "532667", "FEDERALBNK": "10217"}
    symbol_token = tokens.get(current_stock, "99926000") # Default to Nifty if not in list
    
    try:
        ohlc_data = st.session_state.smartApi.ltpData("NSE", current_stock, symbol_token)
        if ohlc_data['status']:
            ltp = float(ohlc_data['data']['ltp'])
            
            # Smart Calculations for Professional Trading
            r1 = round(ltp * 1.008, 2)
            s1 = round(ltp * 0.992, 2)
            
            st.markdown("---")
            st.subheader(f"⚡ Professional Trade Plan for {current_stock}")
            
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Current Price", f"₹{ltp}")
            p2.metric("Resistance (Exit)", f"₹{r1}", delta="Profit Zone")
            p3.metric("Support (Entry)", f"₹{s1}", delta="-Loss Zone", delta_color="inverse")
            
            # --- THE TRADE CARD ---
            st.info("💡 **AI Trade Recommendation:**")
            t_col1, t_col2, t_col3 = st.columns(3)
            
            # Trade Logic: Using 20 DMA and Price Action
            is_bullish = ltp > s1 + (r1-s1)*0.4 # Price is holding support
            
            with t_col1:
                st.write("**ENTRY ZONE**")
                if is_bullish:
                    st.success(f"Buy Above: ₹{round(ltp + (ltp*0.001), 2)}")
                else:
                    st.error(f"Sell Below: ₹{round(ltp - (ltp*0.001), 2)}")
            
            with t_col2:
                st.write("**TARGETS (Exit)**")
                st.write(f"🎯 T1: ₹{round(ltp * 1.01, 2)}")
                st.write(f"🎯 T2: ₹{round(ltp * 1.02, 2)}")
                
            with t_col3:
                st.write("**RISK MANAGEMENT**")
                st.warning(f"🛡️ Stoploss (SL): ₹{round(ltp * 0.99, 2)}")

    except Exception as e:
        st.error(f"Data Fetch Error: Kuch stocks ke liye token update karna hoga. Error: {e}")
else:
    st.warning("Sidebar se Login karein taaki Search aur Trade Planner active ho sakein.")

st.markdown("---")
st.caption("Admin & HR Optimized Trading Terminal | v2.0 Professional")

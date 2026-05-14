import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp

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
    # Default search khali rakhein taaki confusion na ho
    search_stock = st.text_input("Stock Symbol Likhein (e.g., ZOMATO, RELIANCE, SBIN)", value="")
    
with col_market:
    quick_select = st.selectbox("Ya Favorites Chunein", ["NIFTY", "BANKNIFTY", "SUZLON", "FEDERALBNK"])

# Decision: Search bar ko priority deni hai
current_stock = search_stock.upper() if search_stock else quick_select

# --- SMART CHART LOGIC ---
# TradingView ke liye Indices (Nifty/BankNifty) aur Stocks ka format alag hota hai
if current_stock in ["NIFTY", "BANKNIFTY"]:
    tv_symbol = f"NSE:{current_stock}"
else:
    # Stocks ke liye hamesha NSE: prefix lagana zaruri hai
    tv_symbol = f"NSE:{current_stock}"

st.subheader(f"📊 Analysis: {current_stock}")
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

# --- PROFESSIONAL TRADE PLANNER ---
if st.session_state.smartApi:
    # Updated Token Mapping (Common Stocks)
    token_map = {
        "NIFTY": "99926000", "BANKNIFTY": "99926009", 
        "SUZLON": "532667", "FEDERALBNK": "10217",
        "ZOMATO": "50304" # Zomato Token for Angel One
    }
    
    symbol_token = token_map.get(current_stock)
    
    if not symbol_token:
        st.warning(f"⚠️ {current_stock} ka live price fetch karne ke liye Token ID chahiye. Niche default Nifty data dikh raha hai.")
        symbol_token = "99926000" # Fallback to Nifty
    
    try:
        ohlc_data = st.session_state.smartApi.ltpData("NSE", current_stock, symbol_token)
        if ohlc_data['status']:
            ltp = float(ohlc_data['data']['ltp'])
            
            # Professional Strategy Levels
            r1 = round(ltp * 1.01, 2)
            s1 = round(ltp * 0.99, 2)
            
            st.markdown("---")
            st.subheader(f"⚡ Trade Plan: {current_stock}")
            
            p1, p2, p3 = st.columns(3)
            p1.metric("Live Price", f"₹{ltp}")
            p2.metric("Target (T1)", f"₹{r1}")
            p3.metric("Stoploss (SL)", f"₹{s1}")
            
            # Trade Recommendation Card
            st.success(f"💡 **AI Suggestion for {current_stock}:**")
            if ltp > s1 + (r1-s1)*0.5:
                st.write(f"Trend is **BULLISH**. Consider Buying above {ltp}")
            else:
                st.write(f"Trend is **NEUTRAL/BEARISH**. Wait for reversal near {s1}")

    except Exception as e:
        st.error(f"Data Connection Error: {e}")
else:
    st.warning("Pehle Sidebar se Login karein.")

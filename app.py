import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp
import datetime

# Page Setup
st.set_page_config(page_title="AI Dual-Side Trader", layout="wide")
st.title("⚖️ Dual-Side AI Trade Planner (Call & Put)")

# --- SIDEBAR: API Settings (Wahi purana setup) ---
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
            st.sidebar.success("✅ Connected")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- SEARCH & SELECTION ---
search_query = st.text_input("🔍 Search Stock/Index (NIFTY, BANKNIFTY, SUZLON, etc.)", value="NIFTY")
current_symbol = search_query.upper()

# --- DUAL-SIDE TRADE PLANNING ---
if st.session_state.smartApi:
    # Token Mapping
    tokens = {"NIFTY": "99926000", "BANKNIFTY": "99926009", "SUZLON": "532667", "FEDERALBNK": "10217"}
    symbol_token = tokens.get(current_symbol, "99926000")
    
    try:
        ohlc_data = st.session_state.smartApi.ltpData("NSE", current_symbol, symbol_token)
        if ohlc_data['status']:
            ltp = float(ohlc_data['data']['ltp'])
            
            # Level Calculation (Pivot Based)
            # R1: Resistance (Yahan se PE ka sochein)
            # S1: Support (Yahan se CE ka sochein)
            r1 = round(ltp * 1.006, 2)
            s1 = round(ltp * 0.994, 2)
            
            st.markdown("---")
            col_l, col_r = st.columns(2)
            col_l.metric("LIVE PRICE", f"₹{ltp}")
            col_r.info(f"Market Range: {s1} (Support) - {r1} (Resistance)")

            st.subheader("🎯 Trade Entry Points")
            
            # --- CALL SIDE (BUY) LOGIC ---
            ce_col, pe_col = st.columns(2)
            
            with ce_col:
                st.success("🟢 CALL SIDE (CE) PLAN")
                st.write(f"**Condition:** Buy if price holds above {s1}")
                st.write(f"**Entry:** Above ₹{round(ltp + (ltp*0.0005), 2)}")
                st.write(f"**Target 1:** ₹{round(ltp + (ltp*0.01), 2)}")
                st.write(f"**Target 2:** ₹{round(ltp + (ltp*0.02), 2)}")
                st.write(f"**Stoploss:** ₹{round(s1 - (s1*0.002), 2)}")
                
            # --- PUT SIDE (SELL) LOGIC ---
            with pe_col:
                st.error("🔴 PUT SIDE (PE) PLAN")
                st.write(f"**Condition:** Buy if price rejects from {r1}")
                st.write(f"**Entry:** Below ₹{round(ltp - (ltp*0.0005), 2)}")
                st.write(f"**Target 1:** ₹{round(ltp - (ltp*0.01), 2)}")
                st.write(f"**Target 2:** ₹{round(ltp - (ltp*0.02), 2)}")
                st.write(f"**Stoploss:** ₹{round(r1 + (r1*0.002), 2)}")

            # --- AI ASSISTANT CHAT ---
            st.markdown("---")
            st.subheader("💬 AI Chat Assistant")
            user_input = st.text_input("Ask about current trend...")
            if user_input:
                if ltp > r1:
                    st.write(f"🤖 **AI:** {current_symbol} Resistance tod raha hai. PE se bachein, CE mein trailing SL lagayein.")
                elif ltp < s1:
                    st.write(f"🤖 **AI:** Support toot raha hai. CE se nikal jayein, PE active ho sakta hai.")
                else:
                    st.write(f"🤖 **AI:** Market range mein hai. {s1} par aaye toh CE aur {r1} par aaye toh PE ka setup dekhein.")

    except Exception as e:
        st.error(f"Error fetching data: {e}")
else:
    st.warning("Pehle Sidebar se Login karein.")

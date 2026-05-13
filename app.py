import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp # TOTP ke liye extra library
import datetime

# Page Setup
st.set_page_config(page_title="Angle One Trading Dashboard", layout="wide")

st.title("🚀 Angle One Live Trading Dashboard")

# --- SIDEBAR: API Settings ---
st.sidebar.header("Broker Login")
api_key = st.sidebar.text_input("API Key", type="password")
client_id = st.sidebar.text_input("Client ID (Username)")
password = st.sidebar.text_input("Password", type="password")
totp_key = st.sidebar.text_input("TOTP Key (Authenticator Token)", type="password")

# Session state to keep login active
if 'smartApi' not in st.session_state:
    st.session_state.smartApi = None

if st.sidebar.button("Login to Angle One"):
    try:
        smartApi = SmartConnect(api_key=api_key)
        # Generating TOTP
        otp = pyotp.TOTP(totp_key).now()
        data = smartApi.generateSession(client_id, password, otp)
        
        if data['status']:
            st.session_state.smartApi = smartApi
            st.sidebar.success("Login Successful!")
        else:
            st.sidebar.error(f"Login Failed: {data['message']}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- MARKET SELECTION ---
market = st.sidebar.selectbox("Market Select Karein", ["NIFTY", "BANKNIFTY"])

# --- DATA FETCHING & DISPLAY ---
if st.session_state.smartApi:
    st.info(f"Fetching live data for {market} via SmartAPI...")
    
    # Token selection (Nifty/BankNifty tokens for Angle One)
    # Nifty: 99926000, BankNifty: 99926009 (NSE Indices)
    symbol_token = "99926000" if market == "NIFTY" else "99926009"
    
    try:
        # OHLC Data fetch karne ka logic
        # Note: Market band hone par ye 'None' dikha sakta hai
        ohlc_data = st.session_state.smartApi.ltpData("NSE", market, symbol_token)
        
        if ohlc_data['status']:
            ltp = ohlc_data['data']['ltp']
            
            # Display Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Live LTP", f"₹{ltp}")
            
            # Dummy R1/S1 for calculation (Actual API se bhi nikal sakte hain)
            pivot = ltp # Simple logic for display
            st.success(f"{market} connection active. Current LTP is {ltp}")
        else:
            st.warning("API connected but data not available (Market closed?)")
            
    except Exception as e:
        st.error(f"Data Fetch Error: {e}")
else:
    st.warning("Pehle Sidebar se Login karein taaki live data mil sake.")

st.markdown("---")
st.caption("Designed for HR & Admin Pros - Easy Trading Access")

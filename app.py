import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp
import requests

# Page Setup
st.set_page_config(page_title="Professional AI Trader", layout="wide")
st.title("🛡️ Universal AI Trading Terminal")

# --- 1. SMART TOKEN LOADER (Universal Library) ---
@st.cache_data # Isse baar-baar download nahi hoga, speed badhegi
def get_universal_tokens():
    try:
        url = "https://margincalculator.angelbroking.com/OpenAPI_Standard/token/OpenAPIScripMaster.json"
        response = requests.get(url).json()
        df = pd.DataFrame(response)
        # Humein sirf NSE stocks chahiye
        df = df[df['exch_seg'] == 'NSE']
        # Dictionary banate hain: Symbol -> Token
        token_map = dict(zip(df['symbol'], df['token']))
        return token_map
    except:
        st.error("Token library load nahi ho saki. Internet check karein.")
        return {}

token_library = get_universal_tokens()

# --- SIDEBAR: Login ---
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

# --- SEARCH BAR ---
st.markdown("### 🔍 Search Any NSE Stock")
# Search me ab aap kuch bhi likh sakte hain
search_input = st.text_input("Stock Symbol Likhein (e.g., RELIANCE-EQ, ZOMATO-EQ, SBIN-EQ)", value="SBIN-EQ")
current_stock = search_input.upper()

# --- TRADE PLANNER ---
if st.session_state.smartApi:
    # Library se token nikalna
    symbol_token = token_library.get(current_stock)
    
    if symbol_token:
        try:
            # LTP Data mangwana
            ohlc_data = st.session_state.smartApi.ltpData("NSE", current_stock, symbol_token)
            
            if ohlc_data['status']:
                ltp = float(ohlc_data['data']['ltp'])
                
                # --- AAPKI BEST STRATEGY LOGIC ---
                r1 = round(ltp * 1.008, 2)
                s1 = round(ltp * 0.992, 2)
                
                st.markdown("---")
                st.subheader(f"⚡ Professional Trade Plan: {current_stock}")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Live Price", f"₹{ltp}")
                c2.metric("Target Zone (R1)", f"₹{r1}")
                c3.metric("Entry Zone (S1)", f"₹{s1}")
                
                # Recommendation Box
                st.info(f"📊 Strategy for {current_stock}")
                t1, t2, t3 = st.columns(3)
                
                with t1:
                    st.write("**ACTION**")
                    st.success(f"Buy Above: ₹{round(ltp * 1.001, 2)}")
                with t2:
                    st.write("**TARGETS**")
                    st.write(f"🎯 T1: ₹{round(ltp * 1.01, 2)}")
                    st.write(f"🎯 T2: ₹{round(ltp * 1.02, 2)}")
                with t3:
                    st.write("**RISK**")
                    st.warning(f"🛡️ SL: ₹{round(ltp * 0.99, 2)}")
                    
        except Exception as e:
            st.error(f"Price fetch nahi ho paya: {e}")
    else:
        st.warning(f"⚠️ Stock '{current_stock}' nahi mila. NSE format use karein (e.g., SBIN-EQ).")
else:
    st.warning("Pehle Sidebar se Login karein.")

st.markdown("---")
st.caption("Universal Library Enabled | Admin & HR Optimized Terminal")

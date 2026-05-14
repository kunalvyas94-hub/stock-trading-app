import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp
import requests

# Page Setup
st.set_page_config(page_title="AI Trading Terminal Pro", layout="wide")
st.title("🛡️ Universal AI Trading Terminal")

# --- 1. TOKEN LOADER (Universal Library) ---
@st.cache_data
def get_universal_tokens():
    try:
        url = "https://margincalculator.angelbroking.com/OpenAPI_Standard/token/OpenAPIScripMaster.json"
        response = requests.get(url, timeout=5).json()
        df = pd.DataFrame(response)
        df = df[df['exch_seg'] == 'NSE']
        return dict(zip(df['symbol'], df['token']))
    except:
        # Fallback list agar API fail ho jaye
        return {"NIFTY": "99926000", "BANKNIFTY": "99926009", "SUZLON-EQ": "532667", "ZOMATO-EQ": "50304", "SBIN-EQ": "3045"}

token_library = get_universal_tokens()

# --- 2. SESSION STATE MANAGEMENT ---
# Isse button click karne par stock change ho jayega
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = "SBIN-EQ"

# --- 3. SIDEBAR: Login & High Volume ---
st.sidebar.header("🔑 Broker Login")
api_key = st.sidebar.text_input("API Key", type="password")
client_id = st.sidebar.text_input("Client ID")
password = st.sidebar.text_input("Password", type="password")
totp_key = st.sidebar.text_input("TOTP Key", type="password")

if 'smartApi' not in st.session_state:
    st.session_state.smartApi = None

if st.sidebar.button("Establish Connection"):
    try:
        smartApi = SmartConnect(api_key=api_key)
        otp = pyotp.TOTP(totp_key).now()
        data = smartApi.generateSession(client_id, password, otp)
        if data['status']:
            st.session_state.smartApi = smartApi
            st.sidebar.success("✅ Online")
    except:
        st.sidebar.error("Login Failed")

st.sidebar.markdown("---")
st.sidebar.header("🔥 High Volume Today")
# Yeh stocks click karne par niche ka data change karenge
vol_list = ["ZOMATO-EQ", "SUZLON-EQ", "RELIANCE-EQ", "TATAMOTORS-EQ", "FEDERALBNK-EQ"]

for s in vol_list:
    if st.sidebar.button(f"📊 {s}"):
        st.session_state.selected_stock = s

# --- 4. MAIN SEARCH ---
st.markdown("### 🔍 Stock Analyzer")
search_val = st.text_input("Symbol Likhein (E.g. SBIN-EQ)", value=st.session_state.selected_stock)
current_stock = search_val.upper()

# --- 5. AUTOMATIC ENTRY/TARGET/SL CALCULATOR ---
if st.session_state.smartApi:
    # "Eternal" check for Zomato
    lookup = "ZOMATO-EQ" if "ETERNAL" in current_stock else current_stock
    token = token_library.get(lookup)
    
    if token:
        try:
            data = st.session_state.smartApi.ltpData("NSE", lookup, token)
            if data['status']:
                ltp = float(data['data']['ltp'])
                
                # --- YOUR BEST CALCULATION LOGIC ---
                r1 = round(ltp * 1.008, 2)
                s1 = round(ltp * 0.992, 2)
                t1 = round(ltp * 1.01, 2)
                t2 = round(ltp * 1.02, 2)
                sl = round(ltp * 0.99, 2)
                entry = round(ltp * 1.001, 2)

                st.markdown(f"---")
                st.header(f"📈 {lookup} Analysis Report")
                
                # Display Metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Live Price", f"₹{ltp}")
                col2.metric("Resistance (R1)", f"₹{r1}", delta="Target Area")
                col3.metric("Support (S1)", f"₹{s1}", delta="Entry Area", delta_color="inverse")
                
                # Trade Execution Card
                st.success(f"✅ **Trade Plan for {lookup}:**")
                res_col1, res_col2, res_col3 = st.columns(3)
                
                with res_col1:
                    st.write("📍 **ENTRY**")
                    st.code(f"Buy Above: ₹{entry}")
                
                with res_col2:
                    st.write("🎯 **TARGETS**")
                    st.write(f"T1: ₹{t1}")
                    st.write(f"T2: ₹{t2}")
                
                with res_col3:
                    st.write("🛡️ **PROTECTION**")
                    st.error(f"Stoploss: ₹{sl}")

        except Exception as e:
            st.error("Data Fetch Error. Token mismatch ho sakta hai.")
    else:
        st.warning(f"⚠️ '{current_stock}' ka token nahi mila. Kripya '-EQ' suffix check karein.")
else:
    st.info("Sidebar mein details dalkar Connect karein.")

st.markdown("---")
st.caption("Auto-Calculated Entry/Exit System | HR & Admin Optimized")

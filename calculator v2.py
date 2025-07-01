import yfinance as yf
import streamlit as st

st.set_page_config(page_title="Futures vs CFD Price Calculator", layout="centered")

st.title("📈 Futures vs CFD Price Difference Calculator")

st.markdown("""
This app fetches the **latest prices** of a selected **futures contract** and its **CFD equivalent** to calculate the price difference.
""")

# --- Symbol Mappings ---
symbol_map = {
    "ES=F": "^GSPC",          # S&P 500 E-mini
    "NQ=F": "^NDX",           # Nasdaq 100 E-mini
    "YM=F": "^DJI",           # Dow Jones E-mini
    "RTY=F": "^RUT",          # Russell 2000 E-mini
    "GC=F": "XAUUSD=X",       # Gold
    "SI=F": "XAGUSD=X",       # Silver
    "CL=F": "XTIUSD=X",       # Crude Oil (WTI)
    "BZ=F": "XBRUSD=X",       # Brent Crude Oil
    "NG=F": "NG=F",           # Natural Gas (no clear CFD)
    "ZC=F": "ZC=F",           # Corn (no CFD equivalent)
    "ZS=F": "ZS=F",           # Soybeans (no CFD equivalent)
    "ZW=F": "ZW=F",           # Wheat (no CFD equivalent)
    "6E=F": "EURUSD=X",       # Euro
    "6B=F": "GBPUSD=X",       # British Pound
    "6J=F": "JPY=X",          # Japanese Yen
    "6A=F": "AUDUSD=X",       # Australian Dollar
    "6C=F": "CAD=X",          # Canadian Dollar
    "6S=F": "CHF=X",          # Swiss Franc
    "6M=F": "MXN=X",          # Mexican Peso
}

# --- Symbol input ---
col1, col2 = st.columns(2)

with col1:
    futures_symbol = st.selectbox("Futures Symbol (Yahoo Finance)", list(symbol_map.keys()), index=0)
    if futures_symbol:
        try:
            fut_price_preview = yf.Ticker(futures_symbol).history(period="1d", interval="1m").Close.dropna().iloc[-1]
            st.caption(f"Current Price: {fut_price_preview:.2f}")
        except:
            st.caption("Could not fetch preview price.")

with col2:
    # Auto-select CFD based on selected futures
    cfd_symbol = symbol_map.get(futures_symbol, "")
    st.text_input("CFD Symbol (Auto-filled)", value=cfd_symbol, key="cfd_input", disabled=True)
    if cfd_symbol:
        try:
            cfd_price_preview = yf.Ticker(cfd_symbol).history(period="1d", interval="1m").Close.dropna().iloc[-1]
            st.caption(f"Current Price: {cfd_price_preview:.2f}")
        except:
            st.caption("Could not fetch preview price.")

if st.button("Calculate Difference"):
    try:
        with st.spinner("Fetching data..."):
            fut = yf.Ticker(futures_symbol)
            cfd = yf.Ticker(cfd_symbol)

            fut_price = fut.history(period="1d", interval="1m").Close.dropna().iloc[-1]
            cfd_price = cfd.history(period="1d", interval="1m").Close.dropna().iloc[-1]

        spread = fut_price - cfd_price

        st.success("Prices fetched successfully!")
        st.metric(label="Futures Price", value=f"{fut_price:.2f}")
        st.metric(label="CFD Price", value=f"{cfd_price:.2f}")
        st.metric(label="Spread (Futures - CFD)", value=f"{spread:.2f}")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

st.markdown("""
---
Example Symbols:
- **Futures:** `ES=F`, `NQ=F`, `YM=F`, `RTY=F`, `GC=F`, `SI=F`, `CL=F`, `BZ=F`, `NG=F`, `ZC=F`, `ZS=F`, `ZW=F`, `6E=F`, `6B=F`, `6J=F`, `6A=F`, `6C=F`, `6S=F`, `6M=F`
- **CFDs/Indices/FX:** `^GSPC`, `^NDX`, `^DJI`, `^RUT`, `XAUUSD=X`, `XAGUSD=X`, `XTIUSD=X`, `XBRUSD=X`, `EURUSD=X`, `GBPUSD=X`, `JPY=X`, `AUDUSD=X`, `CAD=X`, `CHF=X`, `MXN=X`
""")

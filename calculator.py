import yfinance as yf
import streamlit as st

st.set_page_config(page_title="Futures vs CFD Price Calculator", layout="centered")

st.title("📈 Futures vs CFD Price Difference Calculator")

st.markdown("""
This app fetches the **latest prices** of a selected **FUTURES contract** and its **CFD equivalent** to calculate the price difference and help you adjust your trading levels accordingly.
""")

# --- Symbol Categories and Mappings ---
symbol_categories = {
    "Currency Futures": {
        "Euro (6E=F)": "EURUSD=X",
        "British Pound (6B=F)": "GBPUSD=X",
        "Swiss Franc (6S=F)": "CHF=X",
        "Japanese Yen (6J=F)": "JPY=X",
        "Australian Dollar (6A=F)": "AUDUSD=X",
        "New Zealand Dollar (6N=F)": "NZDUSD=X",
        "Canadian Dollar (6C=F)": "CAD=X",
        "Mexican Peso (6M=F)": "MXN=X",
    },
    "Index Futures": {
        "S&P 500 E-mini (ES=F)": "^GSPC",
        "Nasdaq 100 E-mini (NQ=F)": "^NDX",
        "Dow Jones E-mini (YM=F)": "^DJI",
        "Russell 2000 E-mini (RTY=F)": "^RUT",
    },
    "Metals": {
        "Gold (GC=F)": "",
        "Silver (SI=F)": "",
        "Platinum (PL=F)": "",
        "Palladium (PA=F)": "",
        "Copper (HG=F)": "",
    },
    "Energy": {
        "Crude Oil WTI (CL=F)": "",
        "Brent Crude Oil (BZ=F)": "",
        "Natural Gas (NG=F)": "",
    },
    "Agriculturals": {
        "Corn (ZC=F)": "",
        "Soybeans (ZS=F)": "",
        "Wheat (ZW=F)": "",
        "Oats (ZO=F)": "",
        "Rough Rice (ZR=F)": "",
        "Soybean Meal (ZM=F)": "",
        "Soybean Oil (ZL=F)": "",
        "Coffee (KC=F)": "",
        "Cocoa (CC=F)": "",
        "Cotton (CT=F)": "",
        "Sugar (SB=F)": "",
        "Orange Juice (OJ=F)": "",
        "Lumber (LBS=F)": "",
        "Feeder Cattle (GF=F)": "",
        "Lean Hogs (HE=F)": "",
        "Live Cattle (LE=F)": "",
    },
    "Crypto": {
        "Bitcoin Futures (BTC=F)": "BTC-USD",
        "Ethereum Futures (ETH=F)": "ETH-USD",
    }
}

# Define inverted pairs (when CFD is quoted inversely)
inverted_pairs = {"JPY=X", "CAD=X", "CHF=X", "MXN=X"}  # inverse CFD quotes

# Combine into one lookup map
symbol_map = {}
symbol_lookup = {}
for category in symbol_categories.values():
    for name_with_ticker, cfd in category.items():
        ticker = name_with_ticker.split('(')[-1].replace(')', '')
        symbol_map[name_with_ticker] = cfd
        symbol_lookup[name_with_ticker] = ticker

# --- Symbol input ---
col1, col2 = st.columns(2)

with col1:
    selected_category = st.selectbox("Category", list(symbol_categories.keys()), index=0)
    futures_label = st.selectbox("Futures Instrument", list(symbol_categories[selected_category].keys()))
    futures_symbol = symbol_lookup.get(futures_label, futures_label)
    if futures_symbol:
        try:
            fut_price_preview = yf.Ticker(futures_symbol).history(period="1d", interval="1m").Close.dropna().iloc[-1]
            st.caption(f"**Futures Current Price:** {fut_price_preview}")
        except:
            st.caption(":grey_question: Could not fetch preview price.")

manual_cfd_price = None

with col2:
    cfd_symbol = symbol_map.get(futures_label, "")
    if cfd_symbol:
        st.text_input("CFD Symbol", value=cfd_symbol, key="cfd_input", disabled=True, help="Auto-filled CFD symbol")
        try:
            cfd_price_preview = yf.Ticker(cfd_symbol).history(period="1d", interval="1m").Close.dropna().iloc[-1]
            st.caption(f"**CFD Current Price:** {cfd_price_preview}")
        except:
            st.caption(":grey_question: Could not fetch preview price.")
    else:
        manual_cfd_price = st.number_input("Enter CFD Price manually", min_value=0.0, step=0.01, help="No CFD equivalent available for this instrument.")
        st.caption(":grey_exclamation: No CFD equivalent available for this instrument.")

st.markdown("---")

# --- User Entry Fields for Price Calculations ---
with st.expander("🔧 Adjust Your Trade Levels by Spread", expanded=True):
    st.markdown("Enter your planned trade levels for the **futures** instrument. The app will show the equivalent CFD levels after applying the spread.")
    col_entry, col_sl, col_profit = st.columns(3)
    with col_entry:
        entry_price = st.number_input("Entry Price", min_value=0.0, step=0.0001, format="%.4f", help="Your planned entry price for the futures instrument.")
    with col_sl:
        stop_loss = st.number_input("Stop Loss", min_value=0.0, step=0.0001, format="%.4f", help="Your planned stop loss for the futures instrument.")
    with col_profit:
        profit = st.number_input("Profit Target", min_value=0.0, step=0.0001, format="%.4f", help="Your planned profit target for the futures instrument.")

st.markdown("---")

# --- Calculation and Results ---
if st.button("Calculate Difference", use_container_width=True):
    try:
        with st.spinner("Fetching latest prices..."):
            fut = yf.Ticker(futures_symbol)
            fut_price = fut.history(period="1d", interval="1m").Close.dropna().iloc[-1]

            if not cfd_symbol:
                if manual_cfd_price is None or manual_cfd_price == 0:
                    raise ValueError("Manual CFD price required for this instrument.")
                cfd_price = manual_cfd_price
            else:
                cfd = yf.Ticker(cfd_symbol)
                cfd_price = cfd.history(period="1d", interval="1m").Close.dropna().iloc[-1]
                if cfd_symbol in inverted_pairs and cfd_price != 0:
                    cfd_price = 1 / cfd_price

        spread = fut_price - cfd_price

        st.success("Prices fetched successfully!")
        st.markdown("### 📊 Price Comparison")
        col_fut, col_cfd, col_spread = st.columns(3)
        col_fut.metric(label="Futures Price", value=f"{fut_price:,.4f}")
        col_cfd.metric(label="CFD Price", value=f"{cfd_price:,.4f}")
        col_spread.metric(label="Spread (Futures - CFD)", value=f"{spread:,.4f}")

        # --- Adjusted Trade Levels ---
        if entry_price > 0 or stop_loss > 0 or profit > 0:
            st.markdown("### 🧮 Adjusted CFD Levels")
            st.info("These are your CFD-equivalent levels after applying the spread.")

            if cfd_symbol in inverted_pairs and cfd_price != 0:
                # For inverted pairs, convert futures entry/SL/profit to CFD price by 1/value, then apply spread
                adj_entry = 1 / (entry_price - spread) if entry_price > 0 else None
                adj_sl = 1 / (stop_loss - spread) if stop_loss > 0 else None
                adj_profit = 1 / (profit - spread) if profit > 0 else None
            else:
                adj_entry = entry_price - spread if entry_price > 0 else None
                adj_sl = stop_loss - spread if stop_loss > 0 else None
                adj_profit = profit - spread if profit > 0 else None

            col_adj_entry, col_adj_sl, col_adj_profit = st.columns(3)
            col_adj_entry.metric("Adjusted Entry", f"{adj_entry:,.4f}" if adj_entry is not None else "-")
            col_adj_sl.metric("Adjusted Stop Loss", f"{adj_sl:,.4f}" if adj_sl is not None else "-")
            col_adj_profit.metric("Adjusted Profit", f"{adj_profit:,.4f}" if adj_profit is not None else "-")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

st.markdown("""
---
#### Example Categories
- **Index Futures:** S&P 500 E-mini (ES=F), Nasdaq 100 E-mini (NQ=F), Dow Jones E-mini (YM=F), Russell 2000 E-mini (RTY=F), Nikkei 225 (NI=F)
- **Metals:** Gold (GC=F), Silver (SI=F), Platinum (PL=F), Palladium (PA=F), Copper (HG=F)
- **Energy:** Crude Oil WTI (CL=F), Brent Crude Oil (BZ=F), Natural Gas (NG=F)
- **Agriculturals:** Corn (ZC=F), Soybeans (ZS=F), Wheat (ZW=F), Oats (ZO=F), Rough Rice (ZR=F), Soybean Meal (ZM=F), Soybean Oil (ZL=F), Coffee (KC=F), Cocoa (CC=F), Cotton (CT=F), Sugar (SB=F), Orange Juice (OJ=F), Lumber (LBS=F), Feeder Cattle (GF=F), Lean Hogs (HE=F), Live Cattle (LE=F)
- **Currency Futures:** Euro (6E=F), British Pound (6B=F), Japanese Yen (6J=F), Australian Dollar (6A=F), Canadian Dollar (6C=F), Swiss Franc (6S=F), Mexican Peso (6M=F)
- **Crypto:** Bitcoin Futures (BTC=F), Ethereum Futures (ETH=F)
""")
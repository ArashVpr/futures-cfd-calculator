import yfinance as yf
import streamlit as st
import time

# Cache timeout for fetched prices (30 seconds)
CACHE_TIMEOUT = 30

st.set_page_config(
    page_title="Futures vs CFD Calculator", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("Futures vs CFD Calculator")
st.markdown("**Compare futures and CFD prices to optimize your trading levels**")

# Add visual separator
st.markdown("---")

# --- Symbol Categories and Mappings ---
symbol_categories = {
    "Currency Futures": {
        "Euro": "EURUSD=X",
        "British Pound": "GBPUSD=X",
        "Swiss Franc": "CHF=X",
        "Japanese Yen": "JPY=X",
        "Australian Dollar": "AUDUSD=X",
        "New Zealand Dollar": "NZDUSD=X",
        "Canadian Dollar": "CAD=X",
        "Mexican Peso": "MXN=X",
    },
    "Index Futures": {
        "S&P 500 E-mini": "^GSPC",
        "Nasdaq 100 E-mini": "^NDX",
        "Dow Jones E-mini": "^DJI",
        "Russell 2000 E-mini": "^RUT",
    },
    "Metals": {
        "Gold": "",
        "Silver": "",
        "Platinum": "",
        "Palladium": "",
        "Copper": "",
    },
    "Energy": {
        "Crude Oil WTI": "",
        "Brent Crude Oil": "",
        "Natural Gas": "",
    },
    "Agriculturals": {
        "Corn": "",
        "Soybeans": "",
        "Wheat": "",
        "Oats": "",
        "Rough Rice": "",
        "Soybean Meal": "",
        "Soybean Oil": "",
        "Coffee": "",
        "Cocoa": "",
        "Cotton": "",
        "Sugar": "",
        "Orange Juice": "",
        "Lumber": "",
        "Feeder Cattle": "",
        "Lean Hogs": "",
        "Live Cattle": "",
    },
    "Crypto": {
        "Bitcoin Futures": "BTC-USD",
        "Ethereum Futures": "ETH-USD",
    }
}

# Futures ticker symbol mappings
futures_tickers = {
    "Euro": "6E=F",
    "British Pound": "6B=F",
    "Swiss Franc": "6S=F",
    "Japanese Yen": "6J=F",
    "Australian Dollar": "6A=F",
    "New Zealand Dollar": "6N=F",
    "Canadian Dollar": "6C=F",
    "Mexican Peso": "6M=F",
    "S&P 500 E-mini": "ES=F",
    "Nasdaq 100 E-mini": "NQ=F",
    "Dow Jones E-mini": "YM=F",
    "Russell 2000 E-mini": "RTY=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Platinum": "PL=F",
    "Palladium": "PA=F",
    "Copper": "HG=F",
    "Crude Oil WTI": "CL=F",
    "Brent Crude Oil": "BZ=F",
    "Natural Gas": "NG=F",
    "Corn": "ZC=F",
    "Soybeans": "ZS=F",
    "Wheat": "ZW=F",
    "Oats": "ZO=F",
    "Rough Rice": "ZR=F",
    "Soybean Meal": "ZM=F",
    "Soybean Oil": "ZL=F",
    "Coffee": "KC=F",
    "Cocoa": "CC=F",
    "Cotton": "CT=F",
    "Sugar": "SB=F",
    "Orange Juice": "OJ=F",
    "Lumber": "LBS=F",
    "Feeder Cattle": "GF=F",
    "Lean Hogs": "HE=F",
    "Live Cattle": "LE=F",
    "Bitcoin Futures": "BTC=F",
    "Ethereum Futures": "ETH=F",
}

# Define inverted pairs (when CFD is quoted inversely)
inverted_pairs = {"JPY=X", "CAD=X", "CHF=X", "MXN=X"}  # inverse CFD quotes

# Define decimal precision for different asset categories
decimal_precision = {
    "Currency Futures": 5,  # Forex typically uses 4-5 decimals
    "Index Futures": 2,     # Stock indices typically use 2 decimals  
    "Metals": 2,            # Gold, Silver etc. typically use 2 decimals
    "Energy": 2,            # Oil, Gas etc. typically use 2 decimals
    "Agriculturals": 3,     # Commodities typically use 2-3 decimals
    "Crypto": 2             # Crypto typically uses 2 decimals for major pairs
}

# Combine into one lookup map
symbol_map = {}
symbol_lookup = {}
for category in symbol_categories.values():
    for name, cfd in category.items():
        symbol_map[name] = cfd
        symbol_lookup[name] = futures_tickers.get(name, name)

# Helper function to format price based on category
def format_price(price, category):
    if price is None:
        return "—"
    decimals = decimal_precision.get(category, 6)  # Default to 6 if category not found
    return f"{price:,.{decimals}f}"

# --- Symbol input ---
st.markdown("## 1. Select Instrument")
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox(
            "Market Category",
            list(symbol_categories.keys()),
            index=0,
            help="Choose the type of futures market"
        )
    with col2:
        futures_label = st.selectbox(
            "Futures Contract",
            list(symbol_categories[selected_category].keys()),
            help="Select the specific futures instrument"
        )
    
    futures_symbol = symbol_lookup.get(futures_label, futures_label)
    cfd_symbol = symbol_map.get(futures_label, "")
    
    st.info(f"**Associated CFD:** `{cfd_symbol if cfd_symbol else 'N/A'}`")

# --- Price Configuration ---
st.markdown("## 2. Configure Prices")
with st.container(border=True):
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("#### Futures Price")
        futures_mode = st.radio(
            "Source",
            ["Auto-fetch", "Manual"],
            key="futures_mode",
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if futures_mode == "Auto-fetch":
            if futures_symbol:
                cache_key = f"fut_price_{futures_symbol}"
                timestamp_key = f"fut_time_{futures_symbol}"
                
                # Check if cache is still valid (30 seconds)
                cache_valid = False
                if cache_key in st.session_state and timestamp_key in st.session_state:
                    cache_age = time.time() - st.session_state[timestamp_key]
                    cache_valid = cache_age < CACHE_TIMEOUT
                
                if not cache_valid:
                    with st.spinner("Fetching..."):
                        try:
                            fut_price_preview = yf.Ticker(futures_symbol).history(period="1d", interval="1m").Close.dropna().iloc[-1]
                            st.session_state[cache_key] = fut_price_preview
                            st.session_state[timestamp_key] = time.time()
                        except:
                            st.session_state[cache_key] = None
                            st.session_state[timestamp_key] = time.time()
                
                if st.session_state[cache_key] is not None:
                    st.success(f"**{format_price(st.session_state[cache_key], selected_category)}**")
                else:
                    st.error("Fetch failed")
                manual_futures_price = None
            else:
                st.warning("No market data")
                manual_futures_price = None
        else:
            manual_futures_price = st.number_input(
                "Enter price:",
                min_value=0.0,
                step=0.000001,
                format="%.6f",
                placeholder="0.000000",
                label_visibility="collapsed"
            )
            if manual_futures_price > 0:
                st.info(f"**{format_price(manual_futures_price, selected_category)}**")

    with col2:
        st.markdown("#### CFD Price")
        
        # Check if CFD symbol is available to determine default radio button state
        cfd_available = bool(cfd_symbol)
        default_cfd_mode = "Auto-fetch" if cfd_available else "Manual"
        
        cfd_mode = st.radio(
            "Source",
            ["Auto-fetch", "Manual"],
            key="cfd_mode",
            horizontal=True,
            label_visibility="collapsed",
            index=0 if cfd_available else 1  # Auto-select Manual if no CFD symbol
        )
        
        if cfd_mode == "Auto-fetch":
            if cfd_symbol:
                cache_key = f"cfd_price_{cfd_symbol}"
                timestamp_key = f"cfd_time_{cfd_symbol}"
                
                # Check if cache is still valid (30 seconds)
                cache_valid = False
                if cache_key in st.session_state and timestamp_key in st.session_state:
                    cache_age = time.time() - st.session_state[timestamp_key]
                    cache_valid = cache_age < CACHE_TIMEOUT
                
                if not cache_valid:
                    with st.spinner("Fetching..."):
                        try:
                            cfd_price_preview = yf.Ticker(cfd_symbol).history(period="1d", interval="1m").Close.dropna().iloc[-1]
                            st.session_state[cache_key] = cfd_price_preview
                            st.session_state[timestamp_key] = time.time()
                        except:
                            st.session_state[cache_key] = None
                            st.session_state[timestamp_key] = time.time()
                
                if st.session_state[cache_key] is not None:
                    st.success(f"**{format_price(st.session_state[cache_key], selected_category)}**")
                else:
                    st.error("Fetch failed")
                manual_cfd_price = None
            else:
                st.warning("No CFD data available. Add manually.")
                manual_cfd_price = None
        else:
            manual_cfd_price = st.number_input(
                "Enter price:",
                min_value=0.0,
                step=0.000001,
                format="%.6f",
                key="cfd_manual_manual",
                placeholder="0.000000",
                label_visibility="collapsed"
            )
            if manual_cfd_price > 0:
                st.info(f"**{format_price(manual_cfd_price, selected_category)}**")

    # Refresh button for fetched data
    if st.button("Refresh Data", use_container_width=True, type="secondary"):
        # Clear all cached prices and timestamps
        keys_to_remove = [key for key in st.session_state.keys() if key.startswith(('fut_price_', 'cfd_price_', 'fut_time_', 'cfd_time_'))]
        for key in keys_to_remove:
            del st.session_state[key]
        st.rerun()

# --- Trading Levels Section ---
st.markdown("## 3. Trading Levels")
with st.container(border=True):
    st.markdown("**Enter your planned futures levels to get adjusted CFD levels.**")
    
    col_entry, col_sl, col_profit = st.columns(3, gap="medium")
    
    with col_entry:
        entry_price = st.number_input(
            "Entry Price",
            min_value=0.0,
            step=0.000001,
            format="%.6f",
            placeholder="0.000000",
            help="Your planned entry price for futures"
        )
    
    with col_sl:
        stop_loss = st.number_input(
            "Stop Loss",
            min_value=0.0,
            step=0.000001,
            format="%.6f",
            placeholder="0.000000",
            help="Your planned stop loss for futures"
        )
    
    with col_profit:
        profit = st.number_input(
            "Take Profit",
            min_value=0.0,
            step=0.000001,
            format="%.6f",
            placeholder="0.000000",
            help="Your planned profit target for futures"
        )
    
    # Calculate button
    calculate_clicked = st.button(
        "Calculate Delta",
        use_container_width=True,
        type="primary",
    )

# --- Results Section ---
if calculate_clicked:
    try:
        with st.spinner("Calculating..."):
            # Get futures price based on selected method
            if futures_mode == "Auto-fetch":
                if not futures_symbol:
                    raise ValueError("No futures symbol available for auto-fetch.")
                fut_price = st.session_state.get(f"fut_price_{futures_symbol}")
                if fut_price is None:
                    raise ValueError("Futures price not fetched. Please refresh data.")
            else:
                if manual_futures_price is None or manual_futures_price == 0:
                    raise ValueError("Please enter a futures price for manual entry.")
                fut_price = manual_futures_price

            # Get CFD price based on selected method
            if cfd_mode == "Auto-fetch":
                if not cfd_symbol:
                    raise ValueError("No CFD symbol available for auto-fetch.")
                cfd_price = st.session_state.get(f"cfd_price_{cfd_symbol}")
                if cfd_price is None:
                    raise ValueError("CFD price not fetched. Please refresh data.")
                if cfd_symbol in inverted_pairs and cfd_price != 0:
                    cfd_price = 1 / cfd_price
            else:
                if manual_cfd_price is None or manual_cfd_price == 0:
                    raise ValueError("Please enter a CFD price for manual entry.")
                cfd_price = manual_cfd_price

        spread = abs(fut_price - cfd_price)
        spread_percentage = (spread / fut_price) * 100 if fut_price != 0 else 0

        st.markdown("## Results")
        with st.container(border=True):
            # Price comparison with better visual hierarchy
            st.markdown("### Price Comparison")
            col_fut, col_cfd, col_spread = st.columns(3, gap="medium")
            
            with col_fut:
                st.metric(
                    label="Futures Price",
                    value=format_price(fut_price, selected_category),
                    help="Current futures contract price"
                )
            
            with col_cfd:
                st.metric(
                    label="CFD Price",
                    value=format_price(cfd_price, selected_category),
                    help="Current CFD equivalent price"
                )
            
            with col_spread:
                st.metric(
                    label="Price Difference",
                    value=format_price(spread, selected_category),
                    help="Absolute difference between futures and CFD"
                )

            # Show adjusted levels only if user entered any trading levels
            if entry_price > 0 or stop_loss > 0 or profit > 0:
                st.markdown("---")  # Visual separator
                st.markdown("### 🎯 Your CFD Trading Levels")
                
                # Enhanced info box with better styling
                # st.success("✅ **Ready to Trade!** Use these exact levels for your CFD positions to match your futures strategy.")

                if cfd_symbol in inverted_pairs and cfd_price != 0:
                    adj_entry = 1 / (entry_price - spread) if entry_price > 0 else None
                    adj_sl = 1 / (stop_loss - spread) if stop_loss > 0 else None
                    adj_profit = 1 / (profit - spread) if profit > 0 else None
                else:
                    adj_entry = entry_price - spread if entry_price > 0 else None
                    adj_sl = stop_loss - spread if stop_loss > 0 else None
                    adj_profit = profit - spread if profit > 0 else None

                # Create highlighted container for the trading levels
                with st.container(border=True):
                    
                    col_adj_entry, col_adj_sl, col_adj_profit = st.columns(3, gap="medium")
                    
                    with col_adj_entry:
                        if adj_entry is not None and entry_price > 0:
                            st.markdown("**🔵 ENTRY PRICE**")
                            entry_value = format_price(adj_entry, selected_category)
                            
                            # Display clean number for copying
                            clean_entry = entry_value.replace(',', '')
                            st.code(clean_entry, language=None)
                        else:
                            st.markdown("**🔵 ENTRY PRICE**")
                            st.markdown("### `—`")
                            st.caption("No entry price set")
                    
                    with col_adj_sl:
                        if adj_sl is not None and stop_loss > 0:
                            st.markdown("**🔴 STOP LOSS**")
                            sl_value = format_price(adj_sl, selected_category)
                            
                            # Display clean number for copying
                            clean_sl = sl_value.replace(',', '')
                            st.code(clean_sl, language=None)
                        else:
                            st.markdown("**🔴 STOP LOSS**")
                            st.markdown("### `—`")
                            st.caption("No stop loss set")
                    
                    with col_adj_profit:
                        if adj_profit is not None and profit > 0:
                            st.markdown("**🟢 TAKE PROFIT**")
                            tp_value = format_price(adj_profit, selected_category)
                            
                            # Display clean number for copying
                            clean_tp = tp_value.replace(',', '')
                            st.code(clean_tp, language=None)
                        else:
                            st.markdown("**🟢 TAKE PROFIT**")
                            st.markdown("### `—`")
                            st.caption("No take profit set")
                
                # Add a summary box
                st.info(f"💡 **Spread Adjustment Applied:** {format_price(spread, selected_category)} price difference factored into all levels.")

    except Exception as e:
        st.error(f"Calculation Error: {str(e)}")
        st.markdown("**Troubleshooting:**")
        st.markdown("• Ensure prices are entered or fetched successfully before calculating.")
        st.markdown("• Try refreshing the data if auto-fetch fails.")


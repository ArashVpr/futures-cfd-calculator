![image](https://github.com/user-attachments/assets/ae232405-7f5c-4d89-9f40-d2d11ee9658a)

![image](https://github.com/user-attachments/assets/9ba2d78a-d4f4-4419-a43e-d173e91e4a0d)


**📈 Futures vs CFD Price Difference Calculator**

This Streamlit app helps traders compare the latest prices of selected futures contracts and their CFD equivalents. It calculates the price difference (spread) and helps you adjust your trading levels accordingly.

🚀 Features
✅ Live Price Fetching
Retrieves the most recent prices for both futures and CFD instruments using Yahoo Finance.

✅ Category Selection
Choose from multiple asset classes:

Currency Futures

Index Futures

Metals

Energy

Agriculturals

Crypto

**✅ Automatic Symbol Mapping**

For most instruments, the app auto-fills the CFD symbol.

If no CFD equivalent is available, you can enter the CFD price manually.

**✅ Inverted Pairs Handling**

For certain currency pairs (e.g., JPY, CAD, CHF, MXN), the app automatically inverts the CFD price to match the futures quote format.

**💡 How to Use**

1. Select Category and Instrument
Choose a category (e.g., Currency Futures).

Select a futures instrument (e.g., Euro (6E=F)).

2. View Current Prices
The app shows the latest prices for both futures and CFD instruments.

If no CFD is available, enter it manually.

3. Enter Trade Levels (optional enhancement)
You may enter your planned entry price, stop loss, and profit target for the futures instrument.

4. Calculate Difference
Click “Calculate Difference”.

The app displays:

**Futures Price

CFD Price

Spread (Futures - CFD)**

🧾 Example Categories

📊 Index Futures
S&P 500 E-mini (ES=F)

Nasdaq 100 E-mini (NQ=F)

Dow Jones E-mini (YM=F)

Russell 2000 E-mini (RTY=F)

Nikkei 225 (NI=F)

🪙 Metals
Gold (GC=F), Silver (SI=F), Platinum (PL=F), Palladium (PA=F), Copper (HG=F)

🔋 Energy
Crude Oil WTI (CL=F), Brent Crude Oil (BZ=F), Natural Gas (NG=F)

🌾 Agriculturals
Corn (ZC=F), Soybeans (ZS=F), Wheat (ZW=F), Oats (ZO=F), Coffee (KC=F), etc.

💱 Currency Futures
Euro (6E=F), British Pound (6B=F), Japanese Yen (6J=F), Australian Dollar (6A=F), Canadian Dollar (6C=F)

₿ Crypto
Bitcoin Futures (BTC=F), Ethereum Futures (ETH=F)

⚙️ Technical Notes
Data Source: yfinance for real-time market data

UI Framework: Streamlit

Special Handling: JPY, CAD, CHF, MXN CFDs are inverted to align with futures format

▶️ Running the App
1. Install Dependencies
bash
Copy
Edit
pip install streamlit yfinance
2. Run the App
bash
Copy
Edit
streamlit run calculator.py

📁 File Reference
calculator.py — Main application file

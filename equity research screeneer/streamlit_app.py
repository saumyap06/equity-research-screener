"""
Company Analyzer — Streamlit Web App
--------------------------------------
A simple web interface for your equity research tool.

Setup (run once in your terminal):
    pip install streamlit yfinance pandas

Run:
    streamlit run streamlit_app.py

This will open a browser tab automatically. Type a ticker
(e.g. BAJFINANCE.NS) in the box and click "Analyze".

DISCLAIMER: This is a student/academic project for learning purposes only.
It is NOT real investment advice. The recommendation logic below is a
simplified rule-based scoring system, not a professional research process.
"""

import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Equity Research Screener", page_icon="📊", layout="wide")


# ---------------------------------------------------------------------
# DATA FUNCTIONS (same logic as your original script)
# ---------------------------------------------------------------------
def get_key_ratios(info):
    return {
        "P/E (trailing)": info.get("trailingPE"),
        "P/E (forward)": info.get("forwardPE"),
        "P/B": info.get("priceToBook"),
        "ROE": info.get("returnOnEquity"),
        "ROA": info.get("returnOnAssets"),
        "Debt/Equity": info.get("debtToEquity"),
        "Net Profit Margin": info.get("profitMargins"),
        "Revenue Growth (YoY)": info.get("revenueGrowth"),
        "Earnings Growth (YoY)": info.get("earningsGrowth"),
        "Dividend Yield": info.get("dividendYield"),
    }


def get_stock_status(ticker_obj, info):
    hist = ticker_obj.history(period="1y")
    current_price = info.get("currentPrice") or (hist["Close"].iloc[-1] if not hist.empty else None)
    ma50 = hist["Close"].rolling(50).mean().iloc[-1] if len(hist) >= 50 else None
    ma200 = hist["Close"].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None
    return {
        "current_price": current_price,
        "week52_high": info.get("fiftyTwoWeekHigh"),
        "week52_low": info.get("fiftyTwoWeekLow"),
        "ma50": ma50,
        "ma200": ma200,
    }, hist


def generate_recommendation(ratios, stock_status):
    score = 0
    reasons = []

    roe = ratios.get("ROE")
    if roe is not None:
        if roe > 0.15:
            score += 1
            reasons.append(f"✅ Strong ROE of {roe*100:.1f}% (healthy profitability)")
        elif roe < 0.05:
            score -= 1
            reasons.append(f"⚠️ Weak ROE of {roe*100:.1f}%")

    rev_growth = ratios.get("Revenue Growth (YoY)")
    if rev_growth is not None:
        if rev_growth > 0.10:
            score += 1
            reasons.append(f"✅ Solid revenue growth of {rev_growth*100:.1f}% YoY")
        elif rev_growth < 0:
            score -= 1
            reasons.append(f"⚠️ Revenue declining ({rev_growth*100:.1f}% YoY)")

    de = ratios.get("Debt/Equity")
    if de is not None:
        if de > 150:
            score -= 1
            reasons.append(f"⚠️ High Debt/Equity of {de:.1f} (leverage risk)")
        elif de < 50:
            score += 1
            reasons.append(f"✅ Low Debt/Equity of {de:.1f} (conservative balance sheet)")

    pe = ratios.get("P/E (trailing)")
    if pe is not None:
        if pe < 15:
            score += 1
            reasons.append(f"✅ Attractive valuation, P/E of {pe:.1f}")
        elif pe > 40:
            score -= 1
            reasons.append(f"⚠️ Expensive valuation, P/E of {pe:.1f}")

    price = stock_status.get("current_price")
    ma200 = stock_status.get("ma200")
    if price and ma200 and not pd.isna(ma200):
        if price > ma200:
            score += 1
            reasons.append("✅ Price trading above 200-day average (positive trend)")
        else:
            score -= 1
            reasons.append("⚠️ Price trading below 200-day average (negative trend)")

    if score >= 2:
        call, color = "BUY", "green"
    elif score <= -2:
        call, color = "SELL", "red"
    else:
        call, color = "HOLD", "orange"

    return call, color, score, reasons


# ---------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------
st.title("📊 Equity Research Screener")
st.caption("Type any stock ticker to get a company overview, financials, ratios, and a rule-based recommendation.")

col1, col2 = st.columns([3, 1])
with col1:
    ticker_symbol = st.text_input("Enter ticker (e.g. BAJFINANCE.NS, TCS.NS, INFY.NS)", value="BAJFINANCE.NS")
with col2:
    st.write("")
    st.write("")
    analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

if analyze_clicked and ticker_symbol:
    with st.spinner(f"Fetching data for {ticker_symbol}..."):
        try:
            ticker_obj = yf.Ticker(ticker_symbol)
            info = ticker_obj.info

            if not info or info.get("longName") is None:
                st.error("Could not find data for this ticker. Double-check the symbol (e.g. add .NS for NSE stocks).")
            else:
                # --- Company Overview ---
                st.header(f"{info.get('longName', 'N/A')} ({info.get('symbol', '')})")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Sector", info.get("sector", "N/A"))
                c2.metric("Industry", info.get("industry", "N/A"))
                c3.metric("Country", info.get("country", "N/A"))
                c4.metric("Employees", info.get("fullTimeEmployees", "N/A"))

                with st.expander("📖 Business Summary / History"):
                    st.write(info.get("longBusinessSummary", "No summary available."))

                # --- Financial Statements ---
                st.subheader("📑 Financial Statements")
                tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
                with tab1:
                    try:
                        st.dataframe(ticker_obj.financials, use_container_width=True)
                    except Exception:
                        st.write("Not available.")
                with tab2:
                    try:
                        st.dataframe(ticker_obj.balance_sheet, use_container_width=True)
                    except Exception:
                        st.write("Not available.")
                with tab3:
                    try:
                        st.dataframe(ticker_obj.cashflow, use_container_width=True)
                    except Exception:
                        st.write("Not available.")

                # --- Ratios ---
                st.subheader("📐 Key Financial Ratios")
                ratios = get_key_ratios(info)
                ratio_cols = st.columns(5)
                ratio_items = list(ratios.items())
                for i, (k, v) in enumerate(ratio_items):
                    with ratio_cols[i % 5]:
                        if v is None:
                            st.metric(k, "N/A")
                        elif any(x in k for x in ["Margin", "Growth", "ROE", "ROA", "Yield"]):
                            st.metric(k, f"{v*100:.2f}%")
                        else:
                            st.metric(k, f"{v:.2f}")

                # --- Stock Status + Chart ---
                st.subheader("📈 Stock Status")
                stock_status, hist = get_stock_status(ticker_obj, info)
                s1, s2, s3 = st.columns(3)
                s1.metric("Current Price", stock_status["current_price"])
                s2.metric("52-Week High", stock_status["week52_high"])
                s3.metric("52-Week Low", stock_status["week52_low"])

                if not hist.empty:
                    st.line_chart(hist["Close"])

                # --- Recommendation ---
                st.subheader("🎯 Recommendation")
                call, color, score, reasons = generate_recommendation(ratios, stock_status)
                st.markdown(f"### :{color}[{call}]  (score: {score})")
                for r in reasons:
                    st.write(r)

                st.info("Disclaimer: Educational/academic project only. Not investment advice.")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
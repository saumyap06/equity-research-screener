"""
Company Analyzer — a mini equity-research assistant
-----------------------------------------------------
Type in a company's stock ticker and get:
  1. Company overview & history
  2. Key financial statements (income statement, balance sheet, cash flow)
  3. Key financial ratios (P/E, ROE, ROA, Debt/Equity, margins, growth)
  4. Current stock status (price, 52-week range, moving averages)
  5. A rule-based BUY / HOLD / SELL recommendation with reasoning

Setup (run once in your terminal):
    pip install yfinance pandas

Run:
    python company_analyzer.py

Note: Use the Yahoo Finance ticker symbol.
  Examples -> Bajaj Finance: BAJFINANCE.NS | Minda Corp: MINDACORP.NS
             Reliance: RELIANCE.NS | Infosys: INFY.NS | TCS: TCS.NS
  (Indian NSE stocks need the ".NS" suffix; BSE stocks use ".BO")

DISCLAIMER: This is a student/academic project for learning purposes only.
It is NOT real investment advice. The recommendation logic below is a
simplified rule-based scoring system, not a professional research process.
"""

import yfinance as yf
import pandas as pd

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")


# ---------------------------------------------------------------------
# 1. COMPANY OVERVIEW
# ---------------------------------------------------------------------
def get_company_overview(info):
    print("\n" + "=" * 70)
    print(f"  {info.get('longName', 'N/A')}  ({info.get('symbol', '')})")
    print("=" * 70)
    print(f"Sector      : {info.get('sector', 'N/A')}")
    print(f"Industry    : {info.get('industry', 'N/A')}")
    print(f"Country     : {info.get('country', 'N/A')}")
    print(f"Employees   : {info.get('fullTimeEmployees', 'N/A')}")
    print(f"Website     : {info.get('website', 'N/A')}")
    summary = info.get("longBusinessSummary", "No summary available.")
    print("\nBusiness Summary / History:")
    print(summary)


# ---------------------------------------------------------------------
# 2. FINANCIAL STATEMENTS
# ---------------------------------------------------------------------
def get_financial_statements(ticker_obj):
    print("\n" + "-" * 70)
    print("INCOME STATEMENT (last periods, in company's reporting currency)")
    print("-" * 70)
    try:
        print(ticker_obj.financials.iloc[:, :3])
    except Exception as e:
        print(f"Could not fetch income statement: {e}")

    print("\n" + "-" * 70)
    print("BALANCE SHEET")
    print("-" * 70)
    try:
        print(ticker_obj.balance_sheet.iloc[:, :3])
    except Exception as e:
        print(f"Could not fetch balance sheet: {e}")

    print("\n" + "-" * 70)
    print("CASH FLOW STATEMENT")
    print("-" * 70)
    try:
        print(ticker_obj.cashflow.iloc[:, :3])
    except Exception as e:
        print(f"Could not fetch cash flow statement: {e}")


# ---------------------------------------------------------------------
# 3. KEY RATIOS
# ---------------------------------------------------------------------
def get_key_ratios(info):
    ratios = {
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
    print("\n" + "-" * 70)
    print("KEY FINANCIAL RATIOS")
    print("-" * 70)
    for k, v in ratios.items():
        if v is None:
            print(f"{k:<25}: N/A")
        elif "Margin" in k or "Growth" in k or "ROE" in k or "ROA" in k or "Yield" in k:
            print(f"{k:<25}: {v * 100:.2f}%")
        else:
            print(f"{k:<25}: {v:.2f}")
    return ratios


# ---------------------------------------------------------------------
# 4. STOCK STATUS
# ---------------------------------------------------------------------
def get_stock_status(ticker_obj, info):
    hist = ticker_obj.history(period="1y")
    current_price = info.get("currentPrice") or (hist["Close"].iloc[-1] if not hist.empty else None)
    week52_high = info.get("fiftyTwoWeekHigh")
    week52_low = info.get("fiftyTwoWeekLow")
    ma50 = hist["Close"].rolling(50).mean().iloc[-1] if len(hist) >= 50 else None
    ma200 = hist["Close"].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None

    print("\n" + "-" * 70)
    print("STOCK STATUS")
    print("-" * 70)
    print(f"Current Price       : {current_price}")
    print(f"52-Week High        : {week52_high}")
    print(f"52-Week Low         : {week52_low}")
    print(f"50-Day Moving Avg   : {ma50:.2f}" if ma50 else "50-Day Moving Avg   : N/A")
    print(f"200-Day Moving Avg  : {ma200:.2f}" if ma200 else "200-Day Moving Avg  : N/A")

    return {
        "current_price": current_price,
        "week52_high": week52_high,
        "week52_low": week52_low,
        "ma50": ma50,
        "ma200": ma200,
    }


# ---------------------------------------------------------------------
# 5. RULE-BASED RECOMMENDATION
# ---------------------------------------------------------------------
def generate_recommendation(ratios, stock_status):
    score = 0
    reasons = []

    roe = ratios.get("ROE")
    if roe is not None:
        if roe > 0.15:
            score += 1
            reasons.append(f"+ Strong ROE of {roe*100:.1f}% (healthy profitability)")
        elif roe < 0.05:
            score -= 1
            reasons.append(f"- Weak ROE of {roe*100:.1f}%")

    rev_growth = ratios.get("Revenue Growth (YoY)")
    if rev_growth is not None:
        if rev_growth > 0.10:
            score += 1
            reasons.append(f"+ Solid revenue growth of {rev_growth*100:.1f}% YoY")
        elif rev_growth < 0:
            score -= 1
            reasons.append(f"- Revenue declining ({rev_growth*100:.1f}% YoY)")

    de = ratios.get("Debt/Equity")
    if de is not None:
        if de > 150:
            score -= 1
            reasons.append(f"- High Debt/Equity of {de:.1f} (leverage risk)")
        elif de < 50:
            score += 1
            reasons.append(f"+ Low Debt/Equity of {de:.1f} (conservative balance sheet)")

    pe = ratios.get("P/E (trailing)")
    if pe is not None:
        if pe < 15:
            score += 1
            reasons.append(f"+ Attractive valuation, P/E of {pe:.1f}")
        elif pe > 40:
            score -= 1
            reasons.append(f"- Expensive valuation, P/E of {pe:.1f}")

    price = stock_status.get("current_price")
    ma200 = stock_status.get("ma200")
    if price and ma200 and not pd.isna(ma200):
        if price > ma200:
            score += 1
            reasons.append("+ Price trading above 200-day average (positive trend)")
        else:
            score -= 1
            reasons.append("- Price trading below 200-day average (negative trend)")

    if score >= 2:
        call = "BUY"
    elif score <= -2:
        call = "SELL"
    else:
        call = "HOLD"

    print("\n" + "=" * 70)
    print(f"  RECOMMENDATION: {call}   (score: {score})")
    print("=" * 70)
    for r in reasons:
        print(r)
    print("\nDisclaimer: Educational/academic project only. Not investment advice.")
    return call, reasons


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def analyze_company(ticker_symbol):
    ticker_obj = yf.Ticker(ticker_symbol)
    info = ticker_obj.info
    get_company_overview(info)
    get_financial_statements(ticker_obj)
    ratios = get_key_ratios(info)
    stock_status = get_stock_status(ticker_obj, info)
    generate_recommendation(ratios, stock_status)


if __name__ == "__main__":
    ticker = input("Enter stock ticker (e.g. BAJFINANCE.NS): ").strip()
    analyze_company(ticker)
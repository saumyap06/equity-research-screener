# Equity Research Screener

A Python + Streamlit tool that pulls live financial data for any stock and generates an automated BUY/HOLD/SELL recommendation.

## Features
- Company overview and business summary
- Income statement, balance sheet, and cash flow statements
- Key financial ratios (P/E, P/B, ROE, ROA, Debt/Equity, margins, growth)
- 1-year stock price chart with moving averages
- Rule-based recommendation with clear reasoning

## How to run
pip install streamlit yfinance pandas
streamlit run streamlit_app.py
Enter any stock ticker (e.g. `BAJFINANCE.NS`, `TCS.NS`) and click Analyze.

## Disclaimer
Educational/academic project only. Not investment advice.

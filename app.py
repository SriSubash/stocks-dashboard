import yfinance as yf
import pandas as pd
import ta
import streamlit as st
import plotly.graph_objects as go

NIFTY_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "ITC.NS", "LT.NS", "BHARTIARTL.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS"
]

BANKNIFTY_STOCKS = [
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS",
    "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS"
]


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Indian Stocks Buy-on-Dip",
    layout="wide"
)

st.title("📉 Indian Stocks That Fell Today (Buy-on-Dip Scanner)")
st.caption("Educational only. Not financial advice.")

# -----------------------------
# NSE Stocks
# -----------------------------
stocks = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "LT.NS", "ITC.NS",
    "HINDUNILVR.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "M&M.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "SUNPHARMA.NS",
    "DRREDDY.NS", "CIPLA.NS", "ULTRACEMCO.NS", "NTPC.NS",
    "POWERGRID.NS", "ONGC.NS", "COALINDIA.NS", "HCLTECH.NS",
    "WIPRO.NS", "TECHM.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS",
    "INDUSINDBK.NS", "TITAN.NS", "NESTLEIND.NS"
]

# -----------------------------
# Analysis Function
# -----------------------------
@st.cache_data(ttl=3600)
def analyze_stocks():
    results = []

    for symbol in stocks:
        try:
            df = yf.download(
                symbol,
                period="3mo",
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if df.empty or len(df) < 30:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df["Close"]

            df["RSI"] = ta.momentum.RSIIndicator(close, window=14).rsi()
            df["MA20"] = close.rolling(20).mean()

            today = df.iloc[-1]
            yesterday = df.iloc[-2]

            pct_change = ((today["Close"] - yesterday["Close"]) / yesterday["Close"]) * 100

            # Buy-on-dip logic
            if pct_change < 0 and today["RSI"] < 50:
                results.append({
                    "Stock": symbol,
                    "Price": round(today["Close"], 2),
                    "% Change": round(pct_change, 2),
                    "RSI": round(today["RSI"], 2),
                    "Data": df
                })

        except Exception:
            continue

    return results

# -----------------------------
# Run Analysis
# -----------------------------
data = analyze_stocks()

if not data:
    st.warning("No good buy-on-dip candidates today.")
    st.stop()

# -----------------------------
# Table View
# -----------------------------
table_df = pd.DataFrame([
    {k: v for k, v in d.items() if k != "Data"} for d in data
])

st.subheader("📋 Stocks Down Today")
st.dataframe(table_df, use_container_width=True)

# -----------------------------
# Chart Section
# -----------------------------
st.subheader("📊 Stock Charts")

selected_stock = st.selectbox(
    "Select a stock to view chart",
    table_df["Stock"]
)

stock_data = next(item for item in data if item["Stock"] == selected_stock)
df = stock_data["Data"]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df.index, y=df["Close"],
    name="Close Price",
    line=dict(color="blue")
))

fig.add_trace(go.Scatter(
    x=df.index, y=df["MA20"],
    name="MA20",
    line=dict(color="orange")
))

fig.update_layout(
    height=500,
    title=f"{selected_stock} Price Chart",
    xaxis_title="Date",
    yaxis_title="Price"
)

st.plotly_chart(fig, use_container_width=True)

# RSI Chart
fig_rsi = go.Figure()

fig_rsi.add_trace(go.Scatter(
    x=df.index, y=df["RSI"],
    name="RSI",
    line=dict(color="purple")
))

fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")

fig_rsi.update_layout(
    height=300,
    title="RSI Indicator"
)

st.plotly_chart(fig_rsi, use_container_width=True)

@st.cache_data(ttl=3600)
def most_bought_stocks():
    results = []

    for symbol in stocks:
        try:
            df = yf.download(
                symbol,
                period="3mo",
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if df.empty or len(df) < 30:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
            df["AvgVol"] = df["Volume"].rolling(20).mean()

            today = df.iloc[-1]
            yesterday = df.iloc[-2]

            price_change = ((today["Close"] - yesterday["Close"]) / yesterday["Close"]) * 100

            if (
                today["Volume"] > 1.5 * today["AvgVol"] and
                price_change > 1 and
                55 <= today["RSI"] <= 70
            ):
                results.append({
                    "Stock": symbol,
                    "Price": round(today["Close"], 2),
                    "% Change": round(price_change, 2),
                    "Volume": int(today["Volume"]),
                    "RSI": round(today["RSI"], 2)
                })

        except Exception:
            continue

    return results

st.divider()
st.subheader("🔥 Most Bought / High Demand Stocks Today")

hot_stocks = most_bought_stocks()

if hot_stocks:
    st.dataframe(pd.DataFrame(hot_stocks), use_container_width=True)
else:
    st.info("No strong buying pressure detected today.")


@st.cache_data(ttl=3600)
def top_3_stocks_today():
    results = []

    for symbol in stocks:
        try:
            df = yf.download(
                symbol,
                period="3mo",
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if df.empty or len(df) < 30:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df["Close"]

            df["RSI"] = ta.momentum.RSIIndicator(close, window=14).rsi()
            df["MA20"] = close.rolling(20).mean()
            df["AvgVol"] = df["Volume"].rolling(20).mean()

            today = df.iloc[-1]
            yesterday = df.iloc[-2]

            pct_change = ((today["Close"] - yesterday["Close"]) / yesterday["Close"]) * 100
            score = 0

            # Dip logic
            if pct_change < 0:
                score += 2
            if today["RSI"] < 45:
                score += 2
            if abs(today["Close"] - today["MA20"]) / today["MA20"] < 0.02:
                score += 1

            # Momentum logic
            if pct_change > 0:
                score += 2
            if today["Volume"] > 1.5 * today["AvgVol"]:
                score += 2
            if 55 <= today["RSI"] <= 70:
                score += 2

            if score >= 5:
                results.append({
                    "Stock": symbol,
                    "Price": round(today["Close"], 2),
                    "% Change": round(pct_change, 2),
                    "RSI": round(today["RSI"], 2),
                    "Score": score
                })

        except Exception:
            continue

    results = sorted(results, key=lambda x: x["Score"], reverse=True)
    return results[:3]


st.divider()
st.subheader("🏆 Top 3 Stocks Today (Dip + Momentum)")

top3 = top_3_stocks_today()

if top3:
    st.dataframe(pd.DataFrame(top3), use_container_width=True)
else:
    st.info("No strong combined opportunities today.")


@st.cache_data(ttl=3600)
def index_leaders(stock_list):
    leaders = []

    for symbol in stock_list:
        try:
            df = yf.download(
                symbol,
                period="1mo",
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if df.empty or len(df) < 10:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

            today = df.iloc[-1]
            yesterday = df.iloc[-2]

            pct_change = ((today["Close"] - yesterday["Close"]) / yesterday["Close"]) * 100

            if pct_change > 1 and today["RSI"] > 55:
                leaders.append({
                    "Stock": symbol,
                    "Price": round(today["Close"], 2),
                    "% Change": round(pct_change, 2),
                    "RSI": round(today["RSI"], 2)
                })

        except Exception:
            continue

    return leaders

st.divider()
st.subheader("📈 NIFTY Leaders Today")

nifty_leaders = index_leaders(NIFTY_STOCKS)
if nifty_leaders:
    st.dataframe(pd.DataFrame(nifty_leaders), use_container_width=True)
else:
    st.info("No strong NIFTY leaders today.")

st.subheader("🏦 BANKNIFTY Leaders Today")

banknifty_leaders = index_leaders(BANKNIFTY_STOCKS)
if banknifty_leaders:
    st.dataframe(pd.DataFrame(banknifty_leaders), use_container_width=True)
else:
    st.info("No strong BankNifty leaders today.")

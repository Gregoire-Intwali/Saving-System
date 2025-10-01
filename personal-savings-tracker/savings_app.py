import streamlit as st
import pandas as pd
from datetime import datetime
from investments.techniques import long_investment_strategy
import sqlite3
import os

# ---------------------- SQLite Setup ----------------------
DB_FILE = os.path.join("data", "savings.db")

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Savings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS savings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        note TEXT
    )
    """)
    # Investments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        date TEXT,
        close_price REAL,
        ma_200 REAL,
        signal INTEGER
    )
    """)
    conn.commit()
    conn.close()

# ---------------------- DB Functions ----------------------
def add_transaction(date, category, amount, note):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO savings (date, category, amount, note) VALUES (?, ?, ?, ?)",
        (date, category, amount, note)
    )
    conn.commit()
    conn.close()

def load_transactions():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM savings ORDER BY date ASC", conn)
    conn.close()
    return df

def save_investments(ticker, df_stock):
    if "Date" not in df_stock.columns:
        df_stock = df_stock.reset_index()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for _, row in df_stock.iterrows():
        cursor.execute("""
        INSERT INTO investments (ticker, date, close_price, ma_200, signal)
        VALUES (?, ?, ?, ?, ?)
        """, (
            ticker,
            str(row["Date"]),  
            float(row["Close"]),
            float(row["200_MA"]),
            int(row["Signal"])
        ))
    conn.commit()
    conn.close()

def load_investments(ticker=None):
    conn = sqlite3.connect(DB_FILE)
    query = "SELECT * FROM investments"
    if ticker:
        query += f" WHERE ticker='{ticker}'"
    query += " ORDER BY date ASC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---------------------- Initialize DB ----------------------
init_db()

# ---------------------- Streamlit App ----------------------
st.sidebar.title("💰 Savings & Investment Tracker")
page = st.sidebar.radio("Choose a section:", ["📊 My Savings", "📈 Investment Strategy"])

# ---------------------- Savings Section ----------------------
if page == "📊 My Savings":
    st.title("💰 Personal Savings Tracker")

    st.subheader("Add Transaction")
    amount = st.number_input("Amount:", step=0.01)
    category = st.text_input("Category (e.g., Emergency, Travel, etc.)")
    note = st.text_input("Note (optional)")
    transaction_type = st.radio("Type:", ["Deposit", "Withdrawal"])

    if st.button("Add Transaction"):
        if transaction_type == "Withdrawal":
            amount = -abs(amount)
        add_transaction(datetime.now().strftime("%Y-%m-%d %H:%M"), category, amount, note)
        st.success("Transaction added!")

    df = load_transactions()
    if not df.empty:
        df["Cumulative"] = df["amount"].cumsum()

        st.subheader("📊 Summary")
        st.metric("Current Balance", f"€{df['amount'].sum():,.2f}")
        st.bar_chart(df.groupby("category")["amount"].sum())

        st.subheader("💹 Savings Growth")
        st.line_chart(df.set_index("date")["Cumulative"])

        st.subheader("📜 Transactions")
        st.dataframe(df)
    else:
        st.info("No transactions yet. Add one above!")

# ---------------------- Investment Section ----------------------
elif page == "📈 Investment Strategy":
    st.title("📈 Long-Term Stock Investment Strategy")

    ticker = st.text_input("Enter stock symbol:", "AAPL")
    start_date = st.date_input("Start Date", pd.to_datetime("2015-01-01"))
    end_date = st.date_input("End Date", pd.to_datetime(datetime.today()))

    if st.button("Run Strategy"):
        try:
            df_stock = long_investment_strategy(
                ticker,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d")
            )
            if df_stock.index.name == "Date":
                df_stock = df_stock.reset_index()
            elif df_stock.index.dtype == "datetime64[ns]":
                df_stock = df_stock.reset_index()
            if "date" in df_stock.columns:
                df_stock.rename(columns={"date": "Date"}, inplace=True)
            if "index" in df_stock.columns:
                df_stock.rename(columns={"index": "Date"}, inplace=True)
        except Exception as e:
            st.error(f"Failed to load stock data: {e}")
        else:
            st.success(f"Loaded {ticker} data successfully!")

            save_investments(ticker, df_stock)
            df_db = load_investments(ticker)

            st.subheader("📈 Price vs 200-Day MA")
            st.line_chart(df_db.set_index("date")[["close_price", "ma_200"]])

            st.subheader("📊 Last 10 Days of Signals")
            st.dataframe(df_db.tail(10)[["date", "close_price", "ma_200", "signal"]])

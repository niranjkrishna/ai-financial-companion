import streamlit as st
st.write("API Key Loaded:", "GEMINI_API_KEY" in st.secrets)
import google.generativeai as genai
import os
genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("gemini-3.6-flash")
def ai_cfo(question):

    q = question.lower()

    if q in ["profit", "what is my profit", "current profit"]:
        return f"Current profit is ₹{profit:,.0f}"

    elif q in ["revenue", "what is my revenue"]:
        return f"Current revenue is ₹{revenue:,.0f}"

    elif q in ["expenses", "expense", "what are my expenses"]:
        return f"Current expenses are ₹{expenses:,.0f}"

    elif q in ["credit", "outstanding credit"]:
        return f"Outstanding credit is ₹{total_pending:,.0f}"

    else:
        prompt = f"""
        You are an expert CFO.

        Revenue = {revenue}
        Expenses = {expenses}
        Profit = {profit}
        Outstanding Credit = {total_pending}

        Question:
        {question}
        """
        response = model.generate_content(prompt)
        return response.text
import streamlit as st
import sqlite3
import pandas as pd

# Database Connection
conn = sqlite3.connect("business.db")

st.set_page_config(
    page_title="AI Financial Companion",
    page_icon="",
    layout="wide"
)

st.title("SwipeRight")
st.write("Your AI CFO for Small Businesses")

# Financial Metrics
revenue = pd.read_sql_query(
    "SELECT SUM(total_amount) AS revenue FROM Sales",
    conn
).iloc[0]["revenue"]

expenses = pd.read_sql_query(
    "SELECT SUM(amount) AS expenses FROM Expenses",
    conn
).iloc[0]["expenses"]

revenue = revenue if revenue else 0
expenses = expenses if expenses else 0

profit = revenue - expenses

# Dashboard Metrics
col1, col2, col3 = st.columns(3)

col1.metric("Revenue", f"₹{revenue:,.0f}")
col2.metric("Expenses", f"₹{expenses:,.0f}")
col3.metric("Profit", f"₹{profit:,.0f}")

st.divider()

# Health Score
health_score = 78

st.subheader("Business Health Score")
st.progress(health_score / 100)
st.metric("Health Score", f"{health_score}/100")

st.divider()

# Inventory
st.subheader("Inventory Status")

inventory_df = pd.read_sql_query(
    "SELECT product_name, stock_quantity FROM Inventory",
    conn
)

st.dataframe(inventory_df, use_container_width=True)

st.divider()

st.divider()

st.subheader("Credit Recovery Dashboard")

credit_df = pd.read_sql_query("""
SELECT
    c.customer_name,
    cp.credit_amount,
    cp.paid_amount,
    cp.due_date,
    cp.status
FROM Customers c
JOIN Credit_Payments cp
ON c.customer_id = cp.customer_id
""", conn)

credit_df["balance"] = (
    credit_df["credit_amount"]
    - credit_df["paid_amount"]
)

st.dataframe(
    credit_df,
    use_container_width=True
)

total_pending = credit_df["balance"].sum()

st.metric(
    "Outstanding Credit",
    f"₹{total_pending:,.0f}"
)
if total_pending > 0:
    st.warning(
        f"⚠ ₹{total_pending:,.0f} is pending from customers. Follow up immediately."
    )
else:
    st.success(
        "No outstanding credit."
    )

# AI CFO Recommendations
st.subheader("AI Recommendations")

st.info("""
• Recover pending credit payments

• Monitor inventory levels

• Review operational expenses

• Focus on top-selling products
""")

st.divider()


st.subheader("🎤 Ask Your AI CFO")

question = st.text_input(
    "Ask in English, Malayalam or Tamil"
)

audio_file = st.audio_input(
    "Or speak your question"
)

if question:
    answer = ai_cfo(question)
    st.success(answer)

import streamlit as st
import sqlite3
import pandas as pd
import speech_recognition as sr
import tempfile
import google.generativeai as genai
import re

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="SWIPE RIGHT",
    layout="wide"
)

# -----------------------------
# GEMINI
# -----------------------------

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-3.6-flash"
)

# -----------------------------
# DATABASE
# -----------------------------

conn = sqlite3.connect(
    "business.db",
    check_same_thread=False
)

cursor = conn.cursor()

st.title("SWIPE RIGHT")
st.caption("Voice-enabled CFO for Small Businesses")
def process_voice_command(text):

    text = text.lower().strip()

    try:

        # -------------------------
        # ADD CUSTOMER
        # -------------------------
        if text.startswith("add customer"):

            match = re.search(
                r"add customer\s+(.+)\s+phone\s+(\d+)",
                text
            )

            if not match:
                return " Format: Add customer Rahul Kumar phone 9876543210"

            name = match.group(1).strip()
            phone = match.group(2)

            cursor.execute(
                """
                INSERT INTO Customers
                (customer_name, phone)
                VALUES (?, ?)
                """,
                (name, phone)
            )

            conn.commit()

            return f"Customer {name} added"

        # -------------------------
        # ADD EXPENSE
        # -------------------------
        elif text.startswith("add expense"):

            match = re.search(
                r"add expense\s+(\w+)\s+(\d+)",
                text
            )

            if not match:
                return "Format: Add expense Rent 5000"

            category = match.group(1)
            amount = float(match.group(2))

            cursor.execute(
                """
                INSERT INTO Expenses
                (expense_category, description, amount)
                VALUES (?, ?, ?)
                """,
                (category, category, amount)
            )

            conn.commit()

            return f"Expense ₹{amount} added"

        # -------------------------
        # ADD CREDIT
        # -------------------------
        elif text.startswith("add credit"):

            match = re.search(
                r"add credit\s+(\d+)\s+for\s+(.+)",
                text
            )

            if not match:
                return "Format: Add credit 5000 for Rahul Kumar"

            amount = float(match.group(1))
            customer_name = match.group(2).strip()

            customer = cursor.execute(
                """
                SELECT customer_id
                FROM Customers
                WHERE LOWER(customer_name)=?
                """,
                (customer_name.lower(),)
            ).fetchone()

            if not customer:
                return f"Customer {customer_name} not found"

            cursor.execute(
                """
                INSERT INTO Credit_Payments
                (customer_id, credit_amount, paid_amount)
                VALUES (?, ?, ?)
                """,
                (customer[0], amount, 0)
            )

            conn.commit()

            return f"Credit ₹{amount} added for {customer_name}"

        # -------------------------
        # RECORD SALE
        # -------------------------
        elif text.startswith("record sale"):

            match = re.search(
                r"record sale\s+(\d+)\s+for\s+(.+)",
                text
            )

            if not match:
                return "Format: Record sale 5000 for Rahul Kumar"

            amount = float(match.group(1))
            customer_name = match.group(2).strip()

            customer = cursor.execute(
                """
                SELECT customer_id
                FROM Customers
                WHERE LOWER(customer_name)=?
                """,
                (customer_name.lower(),)
            ).fetchone()

            if not customer:
                return f"Customer {customer_name} not found"

            cursor.execute(
                """
                INSERT INTO Sales
                (customer_id, total_amount, payment_method)
                VALUES (?, ?, ?)
                """,
                (customer[0], amount, "Cash")
            )

            conn.commit()

            return f"Sale ₹{amount} recorded for {customer_name}"

        # -------------------------
        # ADD INVENTORY
        # -------------------------
        elif text.startswith("add inventory"):

            match = re.search(
                r"add inventory\s+(.+)\s+qty\s+(\d+)",
                text
            )

            if not match:
                return "Format: Add inventory Rice qty 50"

            product = match.group(1).strip()
            qty = int(match.group(2))

            cursor.execute(
                """
                INSERT INTO Inventory
                (product_name, stock_quantity)
                VALUES (?, ?)
                """,
                (product, qty)
            )

            conn.commit()

            return f"Inventory updated: {product} ({qty})"

        # -------------------------
        # PAY CREDIT
        # -------------------------
        elif text.startswith("pay credit"):

            match = re.search(
                r"pay credit\s+(\d+)\s+for\s+(.+)",
                text
            )

            if not match:
                return "Format: Pay credit 1000 for Rahul Kumar"

            amount = float(match.group(1))
            customer_name = match.group(2).strip()

            customer = cursor.execute(
                """
                SELECT customer_id
                FROM Customers
                WHERE LOWER(customer_name)=?
                """,
                (customer_name.lower(),)
            ).fetchone()

            if not customer:
                return f"Customer {customer_name} not found"

            cursor.execute(
                """
                UPDATE Credit_Payments
                SET paid_amount = paid_amount + ?
                WHERE customer_id = ?
                """,
                (amount, customer[0])
            )

            conn.commit()

            return f"Received ₹{amount} from {customer_name}"

        # -------------------------
        # CLEAR ALL CREDITS
        # -------------------------
        elif text.startswith("clear credit"):

            match = re.search(
                r"clear credit\s+for\s+(.+)",
                text
        )

        if not match:
            return "❌ Format: Clear credit for Rahul Kumar"

        customer_name = match.group(1).strip()

        customer = cursor.execute(
            """
            SELECT customer_id
            FROM Customers
            WHERE LOWER(customer_name)=?
            """,
            (customer_name.lower(),)
        ).fetchone()

        if not customer:
            return f"❌ Customer {customer_name} not found"

        cursor.execute(
            """
            UPDATE Credit_Payments
            SET paid_amount = credit_amount
            WHERE customer_id = ?
            """,
            (customer[0],)
        )

        conn.commit()

        return f"✅ Credit cleared for {customer_name}"

        return None

    except Exception as e:
        return f"❌ {e}"
    except Exception as e:
        return f"❌ {e}"
    except Exception as e:

        return f"❌ {e}"

    except Exception as e:

        return f"❌ {e}"
import re

def ai_cfo(question, revenue, expenses, profit, total_pending):

    q = re.sub(r"[^\w\s]", "", question.lower()).strip()

    # Local answers (NO Gemini call)
    if q == "profit":
        return f"Current profit is ₹{profit:,.0f}"

    elif q == "revenue":
        return f"Current revenue is ₹{revenue:,.0f}"

    elif q == "expenses":
        return f"Current expenses are ₹{expenses:,.0f}"

    elif q == "credit":
        return f"Outstanding credit is ₹{total_pending:,.0f}"

    # Only complex questions go to Gemini
    prompt = f"""
    You are an expert CFO.

    Revenue: ₹{revenue}
    Expenses: ₹{expenses}
    Profit: ₹{profit}
    Outstanding Credit: ₹{total_pending}

    Question:
    {question}

    Instructions:
    - Give a short business answer
    - Use simple bullet points
    - Use Indian Rupees (₹)
    - Keep answer under 150 words
    """

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception:
        return "Gemini quota exceeded. Please try again later."
# REVENUE
# -----------------------------
revenue_df = pd.read_sql_query(
    """
    SELECT SUM(total_amount) AS revenue
    FROM Sales
    """,
    conn
)

revenue = revenue_df.iloc[0]["revenue"]

if revenue is None:
    revenue = 0

# -----------------------------
# EXPENSES
# -----------------------------

expense_df = pd.read_sql_query(
    """
    SELECT SUM(amount) AS expenses
    FROM Expenses
    """,
    conn
)

expenses = expense_df.iloc[0]["expenses"]

if expenses is None:
    expenses = 0

# -----------------------------
# PROFIT
# -----------------------------

profit = revenue - expenses
st.divider()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Revenue",
    f"₹{revenue:,.0f}"
)

col2.metric(
    "Expenses",
    f"₹{expenses:,.0f}"
)

col3.metric(
    "Profit",
    f"₹{profit:,.0f}"
)
st.divider()

st.subheader(" Inventory Status")

inventory_df = pd.read_sql_query(
    """
    SELECT
        product_name,
        stock_quantity
    FROM Inventory
    """,
    conn
)

st.dataframe(
    inventory_df,
    use_container_width=True
)
st.divider()

st.subheader(" Credit Recovery Dashboard")

credit_df = pd.read_sql_query(
    """
    SELECT
        c.customer_name,
        cp.credit_amount,
        cp.paid_amount
    FROM Customers c
    JOIN Credit_Payments cp
    ON c.customer_id = cp.customer_id
    """,
    conn
)

credit_df["balance"] = (
    credit_df["credit_amount"]
    -
    credit_df["paid_amount"]
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
st.divider()

st.subheader("Business Health Score")

health_score = 78

st.progress(
    health_score / 100
)

st.metric(
    "Health Score",
    f"{health_score}/100"
)
st.divider()

st.subheader("AI Recommendations")

st.info("""
• Recover pending credit payments

• Reduce unnecessary expenses

• Monitor inventory regularly

• Focus on top-selling products
""")
st.divider()

st.subheader("🎤 Ask Your AI CFO")

language = st.selectbox(
    "Select Language",
    [
        "English",
        "Malayalam",
        "Tamil"
    ]
)

lang_code = {
    "English": "en-IN",
    "Malayalam": "ml-IN",
    "Tamil": "ta-IN"
}[language]
question = st.text_input(
    "Ask in English, Malayalam or Tamil"
)
audio_file = st.audio_input(
    "Or speak your question"
)
if audio_file:

    st.success(" Audio received")

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as tmp:

        tmp.write(
            audio_file.getvalue()
        )

        temp_path = tmp.name

    recognizer = sr.Recognizer()

    try:

        with sr.AudioFile(
            temp_path
        ) as source:

            audio_data = recognizer.record(
                source
            )

        question = recognizer.recognize_google(
            audio_data,
            language=lang_code
        )

        st.write(
            "You said:",
            question
        )

    except Exception as e:

        st.error(
            f"Speech recognition failed: {e}"
        )

if question:

    result = process_voice_command(
        question
    )

    if result:

        st.success(result)

    else:

        answer = ai_cfo(
            question,
            revenue,
            expenses,
            profit,
            total_pending
        )

        st.markdown(
            "###  AI CFO Advice"
        )

        st.write(answer)


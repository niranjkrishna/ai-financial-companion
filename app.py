
import streamlit as st

st.title("💰 AI Financial Companion")

st.write("Welcome to your AI CFO")

if st.button("Generate Report"):
    st.write("Revenue: ₹16950")
    st.write("Expenses: ₹27500")
    st.write("Profit: -₹10550")


from pyngrok import ngrok

ngrok.set_auth_token("3IaW6ryv9v0nqRUP2JjDqcEtZ2o_5a7L11vYDStaCqfRq4Vrh")
public_url = ngrok.connect(8501)

print(public_url)

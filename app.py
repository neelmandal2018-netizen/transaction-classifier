import streamlit as st
import pandas as pd
from sms_parser import extract_amount, extract_type, extract_date, extract_merchant, categorize
from database import init_db, insert_transaction, get_all_transactions

init_db()

st.title("💰 Transaction Classifier")
st.write("Paste your bank/UPI SMS messages below (one per line) to parse and categorize them.")

user_input = st.text_area("Paste SMS messages here", height=200)

if st.button("Parse & Save"):
    lines = [line.strip() for line in user_input.split('\n') if line.strip()]
    for sms in lines:
        amount = extract_amount(sms)
        txn_type = extract_type(sms)
        date = extract_date(sms)
        merchant = extract_merchant(sms, txn_type)
        category = categorize(merchant)
        insert_transaction(amount, txn_type, date, merchant, category, sms)
    st.success(f"Parsed and saved {len(lines)} message(s)!")

st.subheader("All Transactions")
rows = get_all_transactions()

if rows:
    df = pd.DataFrame(rows, columns=["id", "amount", "type", "date", "merchant", "category", "raw_message"])
    st.dataframe(df[["date", "amount", "type", "merchant", "category"]])

    st.subheader("Spend by Category")
    debit_df = df[df["type"] == "debit"]
    if not debit_df.empty:
        category_totals = debit_df.groupby("category")["amount"].sum()
        st.bar_chart(category_totals)
else:
    st.info("No transactions yet. Paste some SMS messages above and click Parse & Save.")
import re
import os
import requests
from dotenv import load_dotenv
from sample_messages import sample_sms
from database import init_db, insert_transaction, get_all_transactions

load_dotenv()

def extract_amount(message):
    match = re.search(r'(?:Rs\.?|INR)\s?([\d,]+\.?\d*)', message)
    if match:
        amount_str = match.group(1).replace(',', '')
        return float(amount_str)
    return None

def extract_type(message):
    message_lower = message.lower()
    if 'credited' in message_lower or '/cr/' in message_lower:
        return 'credit'
    elif 'debited' in message_lower or '/dr/' in message_lower:
        return 'debit'
    return 'unknown'

def extract_date(message):
    match = re.search(r'(\d{1,2}-(?:[A-Za-z]{3}|\d{1,2})-\d{2,4})', message)
    if match:
        return match.group(1)
    return None

def extract_merchant(message, txn_type):
    slash_match = re.search(r'UPI/(?:DR|CR)/\d+/([A-Za-z0-9 ]+?)/', message)
    if slash_match:
        return slash_match.group(1).strip()
    if txn_type == 'debit':
        match = re.search(r'\bto\s+([A-Za-z0-9 ]+?)(?:\s+via|\.|,|$)', message)
        if match:
            return match.group(1).strip()
    elif txn_type == 'credit':
        match = re.search(r'\bfrom\s+([A-Za-z0-9 ]+?)(?:\.|,|$)', message)
        if match:
            return match.group(1).strip()
        match = re.search(r'\btowards\s+([A-Za-z0-9 ]+?)(?:\s+on|\.|,|$)', message)
        if match:
            return match.group(1).strip()
    return None

CATEGORY_RULES = {
    'Food': ['SWIGGY', 'ZOMATO', 'DOMINOS', 'MCDONALD'],
    'Shopping': ['AMAZON', 'FLIPKART', 'MYNTRA'],
    'Transport': ['UBER', 'OLA', 'RAPIDO'],
    'Bills': ['ELECTRICITY', 'AIRTEL', 'JIO', 'BROADBAND'],
    'Income': ['SALARY', 'REFUND', 'INTEREST'],
    'Transfer': ['UPI', 'PAYTM', 'PHONEPE', 'GPAY'],
}

CATEGORIES = ["Food", "Shopping", "Transport", "Bills", "Income", "Transfer", "Person-to-person", "Other"]

def categorize_with_llm(merchant, raw_message):
    api_key = os.getenv("OPENROUTER_API_KEY")
    prompt = f"""Classify this bank transaction into exactly one of these categories: {', '.join(CATEGORIES)}.

Merchant/recipient: {merchant}
Full message: {raw_message}

Reply with ONLY the category name, nothing else."""

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "openrouter/free",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        result = response.json()
        category = result["choices"][0]["message"]["content"].strip()
        if category in CATEGORIES:
            return category
        return "Other"
    except Exception as e:
        print(f"LLM categorization failed: {e}")
        return "Uncategorized"

def categorize(merchant, raw_message=None):
    if not merchant:
        return "Uncategorized"
    merchant_upper = merchant.upper()
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in merchant_upper:
                return category
    if raw_message:
        return categorize_with_llm(merchant, raw_message)
    return "Uncategorized"

if __name__ == "__main__":
    init_db()
    for sms in sample_sms:
        amount = extract_amount(sms)
        txn_type = extract_type(sms)
        date = extract_date(sms)
        merchant = extract_merchant(sms, txn_type)
        category = categorize(merchant, sms)
        insert_transaction(amount, txn_type, date, merchant, category, sms)

    print("All transactions stored. Fetching from database:\n")
    for row in get_all_transactions():
        print(row)
import re
from sample_messages import sample_sms

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

def categorize(merchant):
    if not merchant:
        return 'Uncategorized'
    merchant_upper = merchant.upper()
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in merchant_upper:
                return category
    return 'Uncategorized'

if __name__ == "__main__":
    for sms in sample_sms:
        amount = extract_amount(sms)
        txn_type = extract_type(sms)
        date = extract_date(sms)
        merchant = extract_merchant(sms, txn_type)
        category = categorize(merchant)
        print(f"Amount: {amount} | Type: {txn_type} | Date: {date} | Merchant: {merchant} | Category: {category}")
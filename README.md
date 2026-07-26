\# 💰 Transaction Classifier



A live app that parses bank/UPI SMS messages, extracts transaction details, and classifies them into spending categories using a hybrid rule-based + LLM approach.



\*\*Live demo:\*\* https://transaction-classifiergit-s2panr3hjdw4n3bpassewy.streamlit.app/



\## What it does



Paste in bank/UPI SMS notifications, and the app will:

\- Extract the amount, transaction type (debit/credit), date, and merchant/recipient using regex

\- Categorize each transaction (Food, Shopping, Transport, Bills, Income, Transfer, Person-to-person, etc.)

\- Store everything persistently in a SQLite database

\- Display all transactions in a table and a spend-by-category bar chart



\## How categorization works



1\. \*\*Rule-based first\*\* — checks the merchant name against a keyword dictionary (e.g. "SWIGGY" → Food, "AMAZON" → Shopping). Fast and free.

2\. \*\*LLM fallback\*\* — for merchants the rules don't recognize (e.g. a person's name like "RAVI KUMAR"), the app calls an LLM via OpenRouter to classify it intelligently instead of leaving it "Uncategorized."



This mirrors how real-world transaction categorization systems are built — cheap deterministic rules for common cases, LLM reasoning for the long tail.



\## Tech stack



\- \*\*Python\*\* — core logic

\- \*\*re (regex)\*\* — SMS parsing

\- \*\*SQLite\*\* — persistent storage

\- \*\*Streamlit\*\* — web UI

\- \*\*OpenRouter API\*\* — LLM-based fallback categorization



\## Example



Input:Rs.450.00 debited from A/c XX1234 on 23-Jul-26 to SWIGGY via UPI. Avl Bal Rs.12,300.00 -HDFC Bank



Output:

| Date | Amount | Type | Merchant | Category |

|------|--------|------|----------|----------|

| 23-Jul-26 | 450.0 | debit | SWIGGY | Food |



\## Known limitations



\- SMS format coverage is currently tuned to common Indian bank formats (HDFC, ICICI, SBI style messages); other formats may need additional regex patterns

\- No de-duplication yet — pasting the same message twice creates duplicate entries

\- On Streamlit Community Cloud's free tier, the SQLite database resets periodically since it isn't persistent cloud storage — a production version would use a hosted database (e.g. PostgreSQL)



\## Running locally



```bash

git clone https://github.com/neelmandal2018-netizen/transaction-classifier.git

cd transaction-classifier

pip install -r requirements.txt

```



Create a `.env` file with:OPENROUTER\_API\_KEY=your\_key\_here



Then run:

```bash

streamlit run app.py

```


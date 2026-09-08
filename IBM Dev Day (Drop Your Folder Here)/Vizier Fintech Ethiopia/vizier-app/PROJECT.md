# AI Personal Finance Coach — Project Brief

## 1. Project Overview

Build a fast MVP of an AI-powered personal finance and investment intelligence app.

The MVP should help a user:

- Enter monthly income and expenses
- View basic financial health metrics
- See spending by category
- Track a savings goal
- Receive AI-generated or rule-based financial coaching
- Enter a small NSE investment portfolio
- Calculate current value, profit/loss, and return percentage

This is a **2-hour prototype**, not a production-ready fintech platform.

---

## 2. Core Product Idea

The long-term vision is an AI Personal Finance & Investment Intelligence Platform that combines:

- Personal budgeting
- Spending analysis
- Savings goals
- Portfolio tracking
- NSE market data
- Investment research
- Financial news
- AI financial coaching

For the 2-hour MVP, only a small subset is implemented.

---

## 3. MVP Scope

### Personal Finance

Users should be able to enter:

- Monthly income
- Rent
- Food
- Transport
- Utilities
- Entertainment
- Other expenses
- Savings goal

The app should calculate:

- Total expenses
- Monthly savings
- Savings rate
- Largest expense category
- Budget/spending breakdown

### AI Finance Coach

The app should provide a short financial assessment based on the user's data.

Recommended output:

- Overall financial assessment
- Biggest spending concern
- Two practical recommendations
- Savings-rate feedback

If an LLM API is available, use it.

If API setup becomes a blocker, use rule-based recommendations.

### Investment Tracker

The MVP should allow users to enter:

- NSE stock/ticker
- Number of shares
- Purchase price

Use clearly labelled **sample/demo prices** for the MVP.

Example tickers:

- SCOM
- KCB
- EQTY
- EABL

The app should calculate:

- Cost basis
- Current portfolio value
- Profit/loss
- Percentage return

---

## 4. Out of Scope for the 2-Hour MVP

Do not implement:

- Authentication
- User accounts
- PostgreSQL
- Mobile app
- M-Pesa integration
- Bank integrations
- Live NSE market feeds
- Automated web scraping
- News aggregation
- ML credit scoring
- Advanced forecasting
- Automated trading
- Personalized stock buy/sell recommendations
- Complex multi-agent AI systems

These can be presented as future features.

---

## 5. Technology Stack

Use the fastest possible stack.

### Recommended

- Python
- Streamlit
- Pandas
- Plotly
- OpenAI API or another LLM API if available

### Installation

```bash
pip install streamlit pandas plotly openai
```

### Run

```bash
streamlit run app.py
```

---

## 6. Suggested Project Structure

```text
finance-coach/
├── app.py
├── finance.py
├── investments.py
├── coach.py
├── requirements.txt
├── PROJECT.md
├── AGENTS.md
└── README.md
```

---

## 7. Module Responsibilities

### app.py

Owns:

- Streamlit UI
- Navigation
- User inputs
- Metrics display
- Charts
- Calling functions from other modules

Only the integration lead should make major structural edits to this file during the 2-hour sprint.

### finance.py

Contains personal-finance calculations.

Suggested interface:

```python
def calculate_finances(income: float, expenses: dict) -> dict:
    ...
```

Expected output:

```python
{
    "income": 80000,
    "expenses": 58000,
    "savings": 22000,
    "savings_rate": 27.5,
    "largest_expense_category": "Rent"
}
```

### investments.py

Contains investment calculations and sample NSE prices.

Suggested sample data:

```python
STOCKS = {
    "SCOM": 25.50,
    "KCB": 58.00,
    "EQTY": 65.25,
    "EABL": 210.00,
}
```

Suggested interface:

```python
def calculate_investment(
    shares: float,
    purchase_price: float,
    current_price: float
) -> dict:
    ...
```

Expected output:

```python
{
    "cost": 1500,
    "value": 2550,
    "profit": 1050,
    "return_pct": 70.0
}
```

### coach.py

Contains AI or rule-based coaching logic.

Suggested interface:

```python
def generate_financial_advice(finances: dict, expenses: dict) -> str:
    ...
```

If using an LLM, the model should receive **calculated financial metrics**, not perform core financial calculations itself.

---

## 8. UI Layout

Suggested dashboard:

```text
------------------------------------------------
           AI PERSONAL FINANCE COACH
------------------------------------------------

Income       Expenses       Savings       Rate
KES 80,000   KES 58,000     KES 22,000    27.5%

------------------------------------------------
Spending Breakdown

[ Pie or Bar Chart ]

------------------------------------------------
AI Finance Coach

"Your savings rate is healthy, but food spending
is relatively high..."

------------------------------------------------
Investment Portfolio

Ticker | Shares | Buy Price | Demo Price | Return

Portfolio Value: KES XX,XXX
Profit/Loss:     KES X,XXX
Return:          X.X%
------------------------------------------------
```

Use Streamlit components such as:

```python
st.metric()
st.columns()
st.number_input()
st.selectbox()
st.dataframe()
st.plotly_chart()
st.success()
st.warning()
```

---

## 9. Suggested Demo Data

Use a realistic sample scenario:

```text
Monthly income:       KES 80,000
Rent:                 KES 25,000
Food:                 KES 15,000
Transport:            KES 8,000
Utilities:            KES 5,000
Entertainment:        KES 5,000

Total expenses:       KES 58,000
Savings:              KES 22,000
Savings rate:         27.5%
```

Example investment:

```text
Ticker: SCOM
Shares: 100
Purchase price: KES 20
Demo market price: KES 25.50
```

---

## 10. Demo Flow

The final demo should show:

1. Enter monthly income
2. Enter expenses
3. Dashboard updates
4. Spending chart appears
5. Savings and savings rate are calculated
6. AI Coach gives financial feedback
7. Enter an NSE holding
8. Portfolio value and return are calculated

If these steps work reliably, the MVP is complete.

---

## 11. 2-Hour Sprint Plan

### 0:00–0:10

- Create repository
- Create base files
- Install dependencies
- Agree on function interfaces

### 0:10–1:10

Parallel development:

- Person 1: UI + integration
- Person 2: personal finance calculations
- Person 3: investment module
- Person 4: AI coach + presentation

### 1:10–1:30

Integration:

- Merge modules
- Connect Streamlit UI
- Fix import/interface issues

### 1:30–1:45

Testing:

- Run full demo
- Fix crashes
- Validate calculations
- Improve labels

### 1:45–2:00

Stop feature development.

- Prepare demo
- Prepare short presentation
- Rehearse once

---

## 12. Team Responsibilities

### Person 1 — UI / Integration Lead

Deliver:

- `app.py`
- Streamlit layout
- Inputs
- Metrics
- Charts
- Integration of other modules

### Person 2 — Personal Finance Engine

Deliver:

- `finance.py`
- Expense calculations
- Savings calculations
- Savings-rate logic
- Largest-category detection

### Person 3 — Investment Module

Deliver:

- `investments.py`
- Sample NSE stock prices
- Portfolio calculations
- Profit/loss
- Return percentage

### Person 4 — AI + Presentation

Deliver:

- `coach.py`
- AI prompt or rule-based advice
- README summary
- Demo/presentation outline

---

## 13. Important Design Rule

Financial calculations should be deterministic.

Correct architecture:

```text
User Data
   |
   v
Python Financial Engine
   |
   v
Calculated Metrics
   |
   v
AI Coach
   |
   v
Natural-language explanation
```

The AI should explain calculated results rather than invent financial numbers.

---

## 14. Future Expansion

Future versions can add:

- M-Pesa transaction parsing
- Bank statement import
- Bank APIs
- Live NSE data
- Company fundamentals
- NSE company announcements
- CBK economic data
- CMA information
- Government securities
- MMFs
- Financial news
- Portfolio diversification analysis
- Risk profiling
- Goal-based investing
- Cash-flow forecasting
- Recurring-expense detection
- Multi-market investing

Long-term architecture:

```text
M-Pesa --------Banks ----------NSE ------------- > Financial Data Layer
CBK -------------/          |
News ------------/          v
                        Analysis Engine
                              |
                              v
                      AI Financial Copilot
```

---

## 15. MVP Definition of Done

The project is done when:

- Streamlit launches without errors
- User can input income and expenses
- Total expenses are calculated correctly
- Savings are calculated correctly
- Savings rate is calculated correctly
- Spending visualization renders
- AI/rule-based coach returns useful feedback
- User can enter an NSE holding
- Portfolio value is calculated
- Profit/loss is calculated
- Return percentage is calculated
- Demo flow can be completed without a crash

Anything beyond this is optional.

"""NiceGUI interface for Vizier."""

from __future__ import annotations

import os
import asyncio
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from nicegui import app, ui

load_dotenv()
app.add_static_files("/assets", Path(__file__).with_name("assets"))

from ai_service import (answer_question, build_context, explain_transaction,
                        screen_scam, spending_summary)
from budgeting import (budget_status, emergency_fund_months,
                       monthly_comparison, trend_points)
from coach import generate_financial_advice
from database import (add_account, add_debt, add_holding, add_savings_goal,
                      add_watchlist_item, authenticate_user, create_user,
                      delete_category_budget, delete_debt, delete_holding,
                      delete_financial_account, delete_savings_goal, delete_user,
                      delete_watchlist_item, export_user_csv, get_user,
                      import_transactions, initialize_database,
                      list_accounts, list_category_budgets, list_debts,
                      list_holdings, list_import_batches, list_records,
                      list_savings_goals, list_transactions,
                      list_watchlist, save_month,
                      update_profile, upsert_category_budget)
from finance import calculate_finances
from investments import STOCKS, calculate_investment, calculate_portfolio
from health_score import calculate_health_score
from market_data import get_quotes
from settings import COUNTRY, CURRENCY, money, validate_runtime
from statement_import import detect_columns, normalize_rows, read_csv_raw
from auth_security import clear_failures, is_blocked, record_failure

EXPENSE_DEFAULTS = {"Rent": 25_000, "Food": 15_000, "Transport": 8_000,
                    "Utilities": 5_000, "Entertainment": 5_000, "Other": 0}


def signed_in_user() -> dict | None:
    user_id = app.storage.user.get("user_id")
    return get_user(int(user_id)) if user_id else None


def add_styles() -> None:
    ui.colors(primary="#D4AF37", secondary="#0B0B0C", accent="#F6DC87",
              dark="#080808", positive="#2EAD73", negative="#D9534F", warning="#D79724")
    ui.add_head_html("""
    <style>
      :root{--gold:#D4AF37;--gold-light:#F6DC87;--ink:#0B0B0C;--ivory:#F7F1E3;--paper:#FFFCF4;--muted:#766B52}
      body{background:var(--ivory);color:#1B170E;transition:background .25s,color .25s}.nicegui-content{padding:0!important}
      .shell{max-width:1240px;margin:0 auto;padding:24px 22px 48px}
      .hero{background:radial-gradient(circle at 85% 15%,#3B2D0D 0,#151108 32%,#050505 75%);color:#FFF4C7;border:1px solid #8F7224;border-radius:24px;padding:28px 32px;box-shadow:0 18px 45px #17110535}
      .eyebrow{letter-spacing:.16em;text-transform:uppercase;opacity:.7;font-size:.72rem}
      .card{background:var(--paper);border:1px solid #D8C58F;border-radius:18px;box-shadow:0 8px 25px #2C210E12;transition:background .25s,border .25s}
      .metric{padding:18px;min-height:108px}.metric-label{color:var(--muted);font-size:.8rem}
      .metric-value{font-size:1.4rem;font-weight:700;margin-top:9px}.section-title{font-size:1.15rem;font-weight:700;color:#1B170E}
      .section-copy{color:var(--muted);font-size:.88rem}.positive{color:#168557}.negative{color:#C23B36}
      .brand-text{color:#9A7614!important}.brand-logo{border:1px solid #A88429;box-shadow:0 8px 25px #D4AF3730;background:#000}
      .gold-rule{height:1px;background:linear-gradient(90deg,transparent,#D4AF37,transparent)}
      .q-btn.bg-primary{color:#0A0A0A!important;font-weight:700}.q-tab--active{color:#9A7614!important}
      .body--dark{--paper:#121211;--muted:#B8AA84;background:#080808!important;color:#F3E7C3}
      .body--dark .card{background:#121211;border-color:#3E331A;box-shadow:0 8px 30px #0008}
      .body--dark .section-title{color:#F5E5B2}.body--dark .metric-label,.body--dark .section-copy{color:#B8AA84}
      .body--dark .brand-text{color:#E2C45F!important}.body--dark .positive{color:#55C994}.body--dark .negative{color:#F17670}
      .body--dark .bg-slate-50{background:#1B1914!important}.body--dark .text-slate-400{color:#9C9175!important}
      .body--dark .text-slate-500,.body--dark .text-slate-600,.body--dark .text-slate-700{color:#C8BA96!important}
      .body--dark .q-field__native,.body--dark .q-field__input,.body--dark .q-field__label{color:#E9DDAF!important}
      .body--dark .q-table__container,.body--dark .q-table{background:#121211;color:#E9DDAF}
      .body--dark .q-table th{color:#D4AF37}.body--dark .q-separator{background:#3A301A}
      @media(max-width:700px){.shell{padding:14px 12px 30px}.hero{padding:22px}}
    </style>""")


def theme_control() -> None:
    initial = bool(app.storage.user.get("dark_mode", True))
    dark = ui.dark_mode(value=initial)

    def set_theme(event) -> None:
        dark.value = bool(event.value)
        app.storage.user["dark_mode"] = bool(event.value)

    ui.switch("Dark mode", value=initial, on_change=set_theme).props("color=primary dense")


@ui.page("/login")
def login_page() -> None:
    if signed_in_user():
        ui.navigate.to("/")
        return
    add_styles()
    with ui.column().classes("w-full min-h-screen items-center justify-center p-4"):
        with ui.column().classes("card w-full max-w-md p-7 gap-5"):
            with ui.row().classes("w-full justify-between items-start"):
                with ui.row().classes("items-center gap-4"):
                    ui.image("/assets/vizier-logo.jpeg").classes("brand-logo w-20 h-20 rounded-2xl")
                    with ui.column().classes("gap-0"):
                        ui.label("Vizier").classes("text-3xl font-bold brand-text")
                        ui.label("Your money, made clearer.").classes("text-slate-500")
                theme_control()
            ui.element("div").classes("gold-rule w-full")
            with ui.tabs().classes("w-full") as tabs:
                login_tab, register_tab = ui.tab("Sign in"), ui.tab("Create account")
            with ui.tab_panels(tabs, value=login_tab).classes("w-full bg-transparent"):
                with ui.tab_panel(login_tab).classes("px-0 gap-4"):
                    login_email = ui.input("Email").props("outlined type=email").classes("w-full")
                    login_password = ui.input("Password", password=True, password_toggle_button=True).props("outlined").classes("w-full")

                    def sign_in() -> None:
                        if is_blocked(login_email.value or ""):
                            ui.notify("Too many failed attempts. Try again in 15 minutes.", type="negative")
                            return
                        user = authenticate_user(login_email.value or "", login_password.value or "")
                        if not user:
                            record_failure(login_email.value or "")
                            ui.notify("Email or password is incorrect.", type="negative")
                            return
                        clear_failures(login_email.value or "")
                        app.storage.user["user_id"] = user["id"]
                        ui.navigate.to("/")

                    ui.button("Sign in", on_click=sign_in, icon="login").props("color=primary unelevated").classes("w-full")
                with ui.tab_panel(register_tab).classes("px-0 gap-4"):
                    register_name = ui.input("Full name").props("outlined").classes("w-full")
                    register_email = ui.input("Email").props("outlined type=email").classes("w-full")
                    register_password = ui.input("Password", password=True, password_toggle_button=True).props("outlined hint='At least 12 characters'").classes("w-full")

                    def register() -> None:
                        try:
                            user_id = create_user(register_email.value or "", register_name.value or "", register_password.value or "")
                        except ValueError as error:
                            ui.notify(str(error), type="negative")
                            return
                        app.storage.user["user_id"] = user_id
                        ui.navigate.to("/")

                    ui.button("Create my account", on_click=register, icon="person_add").props("color=primary unelevated").classes("w-full")
            ui.label("Prototype data is stored locally in Vizier's SQLite database.").classes("text-xs text-slate-400 text-center")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "vizier"}


@ui.page("/")
def dashboard_page() -> None:
    user = signed_in_user()
    if not user:
        ui.navigate.to("/login")
        return
    user_id = int(user["id"])
    add_styles()
    accounts = list_accounts(user_id)
    category_budgets = list_category_budgets(user_id)
    expense_categories = [item["category"] for item in category_budgets]
    account_options = {item["id"]: f'{item["name"]} · {item["account_type"]}' for item in accounts}
    quote_state = {"quotes": {ticker: {"ticker": ticker, "issuer": ticker, "price": price,
                   "change": 0, "change_pct": 0, "open": price, "high": price,
                   "low": price, "volume": 0, "trades": 0, "market_cap": 0}
                   for ticker, price in STOCKS.items()},
                   "meta": {"source": "Demo fallback prices", "live": False, "fetched_at": None}}

    with ui.column().classes("shell w-full gap-5"):
        with ui.row().classes("w-full justify-between items-center"):
            with ui.row().classes("items-center gap-3"):
                ui.image("/assets/vizier-logo.jpeg").classes("brand-logo w-14 h-14 rounded-xl")
                with ui.column().classes("gap-0"):
                    ui.label("VIZIER").classes("text-xl font-bold brand-text tracking-wider")
                    ui.label("FINANCIAL INTELLIGENCE").classes("eyebrow brand-text")
            with ui.row().classes("items-center gap-2"):
                ui.label(f'Hello, {user["full_name"].split()[0]}').classes("text-sm text-slate-500")
                theme_control()

                def sign_out() -> None:
                    dark_preference = app.storage.user.get("dark_mode", True)
                    app.storage.user.clear()
                    app.storage.user["dark_mode"] = dark_preference
                    ui.navigate.to("/login")

                ui.button(icon="logout", on_click=sign_out).props("flat round color=grey")
        with ui.column().classes("hero w-full gap-2"):
            ui.label(f"VIZIER · PERSONAL FINANCE · {COUNTRY.upper()}").classes("eyebrow brand-text")
            ui.label("Your money, made clearer.").classes("text-3xl md:text-4xl font-bold")
            ui.label("Plan your month, preserve your history, and understand your habits.").classes("opacity-80")
        with ui.tabs().classes("w-full brand-text") as main_tabs:
            overview_tab = ui.tab("Overview", icon="dashboard")
            history_tab = ui.tab("Monthly history", icon="calendar_month")
            budget_tab = ui.tab("Advanced budgeting", icon="account_balance_wallet")
            ai_tab = ui.tab("AI workspace", icon="auto_awesome")
            investments_tab = ui.tab("Investments", icon="donut_large")
            market_tab = ui.tab("Market data", icon="show_chart")
            statements_tab = ui.tab("Statements", icon="upload_file")
            data_tab = ui.tab("Accounts & data", icon="database")
        with ui.tab_panels(main_tabs, value=overview_tab).classes("w-full bg-transparent"):
            with ui.tab_panel(overview_tab).classes("p-0 gap-5"):
                with ui.row().classes("w-full items-end gap-4"):
                    selected_account = ui.select(account_options, value=accounts[0]["id"], label="Financial account").props("outlined").classes("w-64")
                    month_input = ui.input("Month", value=date.today().strftime("%Y-%m")).props("outlined mask='####-##'").classes("w-40")
                    save_button = ui.button("Save month", icon="save").props("color=primary unelevated")
                with ui.row().classes("w-full items-start gap-5"):
                    with ui.column().classes("card p-5 gap-4").style("flex:1 1 330px"):
                        ui.label("Monthly plan").classes("section-title")
                        income_input = ui.number("Monthly income", value=80_000, min=0, step=1_000, format="%.0f").props(f"outlined prefix='{CURRENCY}'").classes("w-full")
                        goal_input = ui.number("Monthly savings goal", value=20_000, min=0, step=1_000, format="%.0f").props(f"outlined prefix='{CURRENCY}'").classes("w-full")
                        ui.separator()
                        expense_inputs = {}
                        with ui.grid(columns=2).classes("w-full gap-3"):
                            for category in expense_categories:
                                default = EXPENSE_DEFAULTS.get(category, 0)
                                expense_inputs[category] = ui.number(category, value=default, min=0, step=500, format="%.0f").props(f"outlined dense prefix='{CURRENCY}'").classes("w-full")
                    with ui.column().classes("gap-5").style("flex:2 1 580px"):
                        with ui.grid(columns=2).classes("w-full gap-4 md:grid-cols-4"):
                            metric_values = []
                            for label in ["Monthly income", "Total expenses", "Monthly savings", "Savings rate"]:
                                with ui.column().classes("card metric gap-0"):
                                    ui.label(label).classes("metric-label")
                                    metric_values.append(ui.label("—").classes("metric-value"))
                        with ui.column().classes("card p-5 w-full gap-3"):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("Spending breakdown").classes("section-title")
                                largest_badge = ui.badge("Largest: —").props("color=primary text-color=black")
                            spending_chart = ui.echart({"tooltip": {"trigger": "item"}, "legend": {"bottom": 0, "type": "scroll"},
                                "series": [{"type": "pie", "radius": ["45%", "68%"], "center": ["50%", "43%"], "data": []}],
                                "color": ["#D4AF37", "#8D6E18", "#F6DC87", "#B98A2E", "#6E5520", "#E8C65A"]}).classes("w-full h-72")
                        with ui.column().classes("card p-5 w-full gap-2"):
                            ui.label("Finance coach").classes("section-title")
                            assessment_label = ui.label().classes("text-lg font-semibold")
                            biggest_label, rate_label = ui.label().classes("text-slate-600"), ui.label().classes("text-slate-600")
                            recommendations_box = ui.column().classes("gap-1")
                            goal_progress_label = ui.label().classes("text-sm text-slate-500 mt-2")
                            goal_progress = ui.linear_progress(value=0).props("color=primary track-color=grey-8 rounded")
                with ui.column().classes("card p-5 w-full gap-4"):
                    with ui.row().classes("w-full justify-between"):
                        ui.label("Ethiopian asset snapshot").classes("section-title")
                        ui.badge("DEMO MARKET PRICE").props("outline color=orange")
                    with ui.grid(columns=1).classes("w-full gap-4 md:grid-cols-3"):
                        ticker_input = ui.select(list(STOCKS), value="ETH-TBILL", label="Demo asset").props("outlined").classes("w-full")
                        shares_input = ui.number("Number of shares", value=100, min=0, step=1).props("outlined").classes("w-full")
                        purchase_input = ui.number("Purchase price", value=100, min=0, step=0.5).props(f"outlined prefix='{CURRENCY}'").classes("w-full")
                    with ui.grid(columns=2).classes("w-full gap-4 md:grid-cols-4"):
                        investment_labels = []
                        for label in ["Cost basis", "Current value", "Profit / loss", "Return"]:
                            with ui.column().classes("rounded-xl bg-slate-50 p-4 gap-1"):
                                ui.label(label).classes("metric-label")
                                investment_labels.append(ui.label("—").classes("text-xl font-bold"))
                    demo_price_label = ui.label().classes("text-sm text-slate-500")

                def current_expenses() -> dict[str, float]:
                    return {name: float(field.value or 0) for name, field in expense_inputs.items()}

                def update_finances() -> None:
                    expenses = current_expenses()
                    finances = calculate_finances(float(income_input.value or 0), expenses)
                    advice = generate_financial_advice(finances, expenses)
                    displays = [money(float(finances["income"])), money(float(finances["expenses"])), money(float(finances["savings"])), f'{float(finances["savings_rate"]):.1f}%']
                    for label, value in zip(metric_values, displays): label.text = value
                    largest_badge.text = f'Largest: {finances["largest_expense_category"]}'
                    spending_chart.options["series"][0]["data"] = [{"name": name, "value": amount} for name, amount in expenses.items() if amount > 0]
                    spending_chart.update()
                    assessment_label.text, biggest_label.text, rate_label.text = str(advice["assessment"]), str(advice["biggest"]), str(advice["rate_feedback"])
                    recommendations_box.clear()
                    with recommendations_box:
                        for recommendation in advice["recommendations"]: ui.label(f"• {recommendation}").classes("text-slate-700")
                    goal, savings = float(goal_input.value or 0), max(float(finances["savings"]), 0)
                    progress = min(savings / goal, 1) if goal else 0
                    goal_progress.value = progress
                    goal_progress_label.text = f"Savings goal: {money(savings)} of {money(goal)} · {progress * 100:.0f}%"

                def update_investment() -> None:
                    ticker = ticker_input.value or "ETH-TBILL"
                    result = calculate_investment(float(shares_input.value or 0), float(purchase_input.value or 0), STOCKS[ticker])
                    for label, value in zip(investment_labels, [money(result["cost"]), money(result["value"]), money(result["profit"]), f'{result["return_pct"]:.1f}%']): label.text = value
                    demo_price_label.text = f"{ticker} demo market price: {money(STOCKS[ticker])} per share"

                def persist_month() -> None:
                    try:
                        save_month(user_id, int(selected_account.value), month_input.value or "", float(income_input.value or 0), float(goal_input.value or 0), current_expenses())
                        ui.notify("Monthly record saved.", type="positive")
                    except ValueError as error: ui.notify(str(error), type="negative")

                save_button.on_click(persist_month)
                for field in [income_input, goal_input, *expense_inputs.values()]: field.on_value_change(lambda _: update_finances())
                for field in [ticker_input, shares_input, purchase_input]: field.on_value_change(lambda _: update_investment())
                update_finances(); update_investment()

            with ui.tab_panel(history_tab).classes("p-0 gap-4"):
                with ui.column().classes("card p-5 w-full gap-3"):
                    ui.label("Monthly history").classes("section-title")
                    ui.label("Saved snapshots across all your financial accounts.").classes("section-copy")
                    history_rows = []
                    for record in list_records(user_id):
                        finances = calculate_finances(record["income"], record["expenses"])
                        history_rows.append({"account": record["account_name"], "month": record["month"], "income": money(record["income"]),
                            "expenses": money(float(finances["expenses"])), "savings": money(float(finances["savings"])), "rate": f'{float(finances["savings_rate"]):.1f}%'})
                    ui.table(columns=[{"name": key, "label": label, "field": key, "align": "left"} for key, label in [
                        ("account", "Account"), ("month", "Month"), ("income", "Income"), ("expenses", "Expenses"), ("savings", "Savings"), ("rate", "Rate")]],
                        rows=history_rows, row_key="month").props("flat bordered").classes("w-full")
                    if not history_rows: ui.label("No saved months yet. Save one from Overview.").classes("text-slate-400")

            with ui.tab_panel(budget_tab).classes("p-0 gap-5"):
                records = list_records(user_id)
                latest_expenses = records[0]["expenses"] if records else {}
                statuses = budget_status(latest_expenses, category_budgets)
                comparison = monthly_comparison(records)
                goals = list_savings_goals(user_id)
                debts = list_debts(user_id)
                latest_income = float(records[0]["income"]) if records else 0
                health = calculate_health_score(latest_income, latest_expenses, category_budgets, goals, debts)
                with ui.grid(columns=1).classes("w-full gap-4 md:grid-cols-4"):
                    with ui.column().classes("card metric gap-1"):
                        ui.label("Budget alerts").classes("metric-label")
                        active_alerts = [row for row in statuses if row["status"] != "ok"]
                        ui.label(str(len(active_alerts))).classes("metric-value negative" if active_alerts else "metric-value positive")
                        ui.label("categories need attention" if active_alerts else "all configured limits look good").classes("text-xs text-slate-500")
                    with ui.column().classes("card metric gap-1"):
                        ui.label("Emergency-fund cover").classes("metric-label")
                        emergency_saved = sum(goal["saved_amount"] for goal in goals if "emergency" in goal["name"].lower())
                        cover = emergency_fund_months(emergency_saved, latest_expenses)
                        ui.label(f"{cover:.1f} months").classes("metric-value")
                        ui.label("based on essential recorded expenses").classes("text-xs text-slate-500")
                    with ui.column().classes("card metric gap-1"):
                        ui.label("Total debt").classes("metric-label")
                        ui.label(money(sum(debt["balance"] for debt in debts))).classes("metric-value")
                        ui.label(f"Minimum payments: {money(sum(debt['minimum_payment'] for debt in debts))}").classes("text-xs text-slate-500")
                    with ui.column().classes("card metric gap-1"):
                        ui.label("Financial health").classes("metric-label")
                        ui.label(f"{health['score']} / 100").classes("metric-value positive" if health["score"] >= 65 else "metric-value negative")
                        ui.label(health["rating"]).classes("text-xs text-slate-500")

                with ui.column().classes("card p-5 w-full gap-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.column().classes("gap-0"):
                            ui.label("Explainable financial-health score").classes("section-title")
                            ui.label("Five deterministic components; no AI-generated numbers.").classes("section-copy")
                        ui.knob(value=health["score"], min=0, max=100, show_value=True).props("color=primary readonly size=90px")
                    with ui.grid(columns=1).classes("w-full gap-3 md:grid-cols-5"):
                        maximums = {"Savings rate": 35, "Positive cash flow": 20, "Budget adherence": 15,
                                    "Emergency fund": 15, "Debt load": 15}
                        for component, points in health["components"].items():
                            with ui.column().classes("rounded-xl bg-slate-50 p-3 gap-1"):
                                ui.label(component).classes("text-xs text-slate-500")
                                ui.label(f"{points:g} / {maximums[component]}").classes("font-bold")
                    for recommendation in health["recommendations"]:
                        ui.label(f"• {recommendation}").classes("text-sm text-slate-600")

                with ui.column().classes("card p-5 w-full gap-4"):
                    ui.label("Category budgets and alerts").classes("section-title")
                    ui.label("An alert appears at 80% of a configured monthly limit.").classes("section-copy")
                    with ui.grid(columns=1).classes("w-full gap-3 md:grid-cols-2"):
                        for row in statuses:
                            color = "negative" if row["status"] == "over" else "warning" if row["status"] == "near" else "primary"
                            with ui.column().classes("rounded-xl bg-slate-50 p-4 gap-2"):
                                with ui.row().classes("w-full justify-between"):
                                    ui.label(row["category"]).classes("font-semibold")
                                    with ui.row().classes("items-center gap-1"):
                                        ui.badge(row["status"].upper()).props(f"color={color}")
                                        def remove_category(category_id=row["id"]):
                                            delete_category_budget(user_id, category_id); ui.navigate.reload()
                                        ui.button(icon="close", on_click=remove_category).props("flat round dense color=grey")
                                ui.label(f"{money(row['spent'])} spent · {money(row['limit'])} limit").classes("text-sm text-slate-500")
                                ui.linear_progress(value=min(row["percentage"] / 100, 1) if row["limit"] else 0).props(f"color={color} rounded")
                    ui.separator()
                    with ui.row().classes("w-full items-end gap-3"):
                        category_name = ui.input("Category").props("outlined dense").style("flex:1")
                        category_limit = ui.number("Monthly limit", min=0, value=0).props(f"outlined dense prefix='{CURRENCY}'").style("width:190px")

                        def save_category() -> None:
                            try:
                                upsert_category_budget(user_id, category_name.value or "", float(category_limit.value or 0))
                                ui.notify("Category budget saved. Reloading dashboard.", type="positive")
                                ui.navigate.reload()
                            except ValueError as error: ui.notify(str(error), type="negative")
                        ui.button("Save category", on_click=save_category, icon="add").props("color=primary")

                with ui.row().classes("w-full items-start gap-5"):
                    with ui.column().classes("card p-5 gap-4").style("flex:1 1 450px"):
                        ui.label("Savings goals").classes("section-title")
                        for goal in goals:
                            progress = min(goal["saved_amount"] / goal["target_amount"], 1)
                            with ui.column().classes("w-full rounded-xl bg-slate-50 p-3 gap-2"):
                                with ui.row().classes("w-full justify-between"):
                                    ui.label(goal["name"]).classes("font-medium")
                                    with ui.row().classes("items-center gap-1"):
                                        ui.label(f"{progress * 100:.0f}%").classes("text-sm brand-text")
                                        def remove_goal(goal_id=goal["id"]):
                                            delete_savings_goal(user_id, goal_id); ui.navigate.reload()
                                        ui.button(icon="close", on_click=remove_goal).props("flat round dense color=grey")
                                ui.linear_progress(value=progress).props("color=primary rounded")
                                ui.label(f"{money(goal['saved_amount'])} of {money(goal['target_amount'])} · target {goal['target_date'] or 'open'}").classes("text-xs text-slate-500")
                        with ui.expansion("Add a savings goal", icon="add").classes("w-full"):
                            goal_name = ui.input("Goal name").props("outlined dense").classes("w-full")
                            goal_target = ui.number("Target amount", min=1).props(f"outlined dense prefix='{CURRENCY}'").classes("w-full")
                            goal_saved = ui.number("Already saved", min=0, value=0).props(f"outlined dense prefix='{CURRENCY}'").classes("w-full")
                            goal_date = ui.input("Target date", placeholder="YYYY-MM-DD").props("outlined dense").classes("w-full")
                            def create_goal() -> None:
                                try:
                                    add_savings_goal(user_id, goal_name.value or "", float(goal_target.value or 0), float(goal_saved.value or 0), goal_date.value)
                                    ui.navigate.reload()
                                except ValueError as error: ui.notify(str(error), type="negative")
                            ui.button("Add goal", on_click=create_goal).props("color=primary")
                    with ui.column().classes("card p-5 gap-4").style("flex:1 1 450px"):
                        ui.label("Debt and loan tracker").classes("section-title")
                        for debt in debts:
                            with ui.row().classes("w-full justify-between items-center rounded-xl bg-slate-50 p-3"):
                                with ui.column().classes("gap-0"):
                                    ui.label(debt["name"]).classes("font-medium")
                                    ui.label(f"{money(debt['balance'])} · {debt['annual_rate']:.1f}% APR · min {money(debt['minimum_payment'])}").classes("text-xs text-slate-500")
                                def remove_debt(debt_id=debt["id"]):
                                    delete_debt(user_id, debt_id); ui.navigate.reload()
                                ui.button(icon="delete_outline", on_click=remove_debt).props("flat round color=negative")
                        with ui.expansion("Add a debt or loan", icon="add").classes("w-full"):
                            debt_name = ui.input("Debt name").props("outlined dense").classes("w-full")
                            debt_balance = ui.number("Balance", min=0).props(f"outlined dense prefix='{CURRENCY}'").classes("w-full")
                            debt_rate = ui.number("Annual interest rate", min=0).props("outlined dense suffix='%'").classes("w-full")
                            debt_minimum = ui.number("Minimum monthly payment", min=0).props(f"outlined dense prefix='{CURRENCY}'").classes("w-full")
                            def create_debt() -> None:
                                try:
                                    add_debt(user_id, debt_name.value or "", float(debt_balance.value or 0), float(debt_rate.value or 0), float(debt_minimum.value or 0))
                                    ui.navigate.reload()
                                except ValueError as error: ui.notify(str(error), type="negative")
                            ui.button("Add debt", on_click=create_debt).props("color=primary")

                with ui.column().classes("card p-5 w-full gap-4"):
                    ui.label("Monthly comparison and trends").classes("section-title")
                    if comparison:
                        ui.label(f"{comparison['current_month']} compared with {comparison['previous_month']}: expenses {money(comparison['expense_change'])}, savings {money(comparison['savings_change'])}, savings rate {comparison['rate_change']:+.1f} points.").classes("text-slate-600")
                    else:
                        ui.label("Save at least two monthly records to unlock comparisons.").classes("text-slate-400")
                    points = trend_points(records)
                    ui.echart({"tooltip": {"trigger": "axis"}, "legend": {"data": ["Expenses", "Savings"]},
                        "xAxis": {"type": "category", "data": [point["month"] for point in points]}, "yAxis": {"type": "value"},
                        "series": [{"name": "Expenses", "type": "line", "smooth": True, "data": [point["expenses"] for point in points]},
                                   {"name": "Savings", "type": "line", "smooth": True, "data": [point["savings"] for point in points]}],
                        "color": ["#D9534F", "#D4AF37"]}).classes("w-full h-72")

            with ui.tab_panel(ai_tab).classes("p-0 gap-5"):
                def fresh_context() -> dict:
                    return build_context(list_records(user_id), list_category_budgets(user_id), list_savings_goals(user_id), list_debts(user_id))
                with ui.column().classes("card p-5 w-full gap-4"):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("Vizier AI coach").classes("section-title")
                        ai_enabled = os.environ.get("WATSONX_API_KEY") or os.environ.get("OPENAI_API_KEY")
                        provider = "WATSONX / GRANITE" if os.environ.get("WATSONX_API_KEY") else "OPENAI" if os.environ.get("OPENAI_API_KEY") else "OFFLINE MODE"
                        ui.badge(provider).props("color=primary text-color=black" if ai_enabled else "color=grey")
                    ui.label(spending_summary(fresh_context())).classes("text-slate-600")
                    question_input = ui.textarea("Ask about your budget, savings goals, debts, or spending", placeholder="Where am I overspending?").props("outlined autogrow").classes("w-full")
                    answer_box = ui.markdown("Ask a question to get a context-aware explanation.").classes("w-full rounded-xl bg-slate-50 p-4")
                    source_label = ui.label().classes("text-xs text-slate-400")
                    def ask_vizier() -> None:
                        if not (question_input.value or "").strip():
                            ui.notify("Enter a question first.", type="warning"); return
                        answer, source = answer_question(question_input.value, fresh_context())
                        answer_box.content = answer; source_label.text = f"Response source: {source}"
                    ui.button("Ask Vizier", on_click=ask_vizier, icon="send").props("color=primary")
                with ui.row().classes("w-full items-start gap-5"):
                    with ui.column().classes("card p-5 gap-4").style("flex:1 1 450px"):
                        ui.label("Transaction explainer").classes("section-title")
                        transaction_text = ui.input("Transaction description", placeholder="e.g. NAIVAS WESTLANDS").props("outlined").classes("w-full")
                        transaction_amount = ui.number("Amount", min=0).props(f"outlined prefix='{CURRENCY}'").classes("w-full")
                        transaction_result = ui.label().classes("text-slate-600")
                        ui.button("Explain transaction", on_click=lambda: setattr(transaction_result, "text", explain_transaction(transaction_text.value or "", float(transaction_amount.value or 0)))).props("outline color=primary")
                    with ui.column().classes("card p-5 gap-4").style("flex:1 1 450px"):
                        ui.label("Financial scam screener").classes("section-title")
                        ui.label("Paste suspicious text. This heuristic check is not a guarantee of safety.").classes("section-copy")
                        scam_text = ui.textarea("Message or email text").props("outlined autogrow").classes("w-full")
                        scam_result = ui.column().classes("w-full gap-1")
                        def check_scam() -> None:
                            result = screen_scam(scam_text.value or "")
                            scam_result.clear()
                            with scam_result:
                                ui.label(f"Risk: {result['risk']} · {result['score']}%").classes("text-xl font-bold negative" if result["risk"] == "HIGH" else "text-xl font-bold")
                                for reason in result["reasons"]: ui.label(f"• {reason}")
                        ui.button("Screen message", on_click=check_scam, icon="shield").props("outline color=primary")

            with ui.tab_panel(investments_tab).classes("p-0 gap-5"):
                with ui.row().classes("w-full justify-between items-center"):
                    with ui.column().classes("gap-0"):
                        ui.label("Investment portfolio").classes("section-title")
                        ui.label("Persistent Ethiopian assets, total return, income, allocation, and concentration.").classes("section-copy")
                    portfolio_source = ui.badge("DEMO FALLBACK").props("color=orange")
                portfolio_box = ui.column().classes("w-full gap-5")

                def render_portfolio() -> None:
                    portfolio_box.clear()
                    holdings = list_holdings(user_id)
                    portfolio = calculate_portfolio(holdings, quote_state["quotes"])
                    with portfolio_box:
                        with ui.grid(columns=2).classes("w-full gap-4 md:grid-cols-4"):
                            for label, value in [("Portfolio value", money(portfolio["value"])),
                                                 ("Total gain / loss", money(portfolio["gain"])),
                                                 ("Total return", f'{portfolio["return_pct"]:.1f}%'),
                                                 ("Dividends received", money(portfolio["dividends"]))]:
                                with ui.column().classes("card metric gap-0"):
                                    ui.label(label).classes("metric-label"); ui.label(value).classes("metric-value")
                        if holdings:
                            with ui.row().classes("w-full items-start gap-5"):
                                with ui.column().classes("card p-5 gap-3").style("flex:2 1 620px"):
                                    rows = []
                                    for row in portfolio["rows"]:
                                        rows.append({"ticker": row["ticker"], "shares": f'{row["shares"]:,.0f}',
                                            "price": money(row["current_price"]), "value": money(row["value"]),
                                            "gain": money(row["gain"]), "return": f'{row["return_pct"]:.1f}%',
                                            "allocation": f'{row["allocation_pct"]:.1f}%', "id": row["id"]})
                                    table = ui.table(columns=[{"name": key, "label": label, "field": key, "align": "left"} for key, label in [
                                        ("ticker", "Ticker"), ("shares", "Shares"), ("price", "Public/demo price"),
                                        ("value", "Value"), ("gain", "Total gain"), ("return", "Return"),
                                        ("allocation", "Allocation")]], rows=rows, row_key="id").props("flat bordered").classes("w-full")
                                    table.add_slot("body-cell-ticker", """
                                        <q-td :props="props"><strong>{{ props.row.ticker }}</strong></q-td>
                                    """)
                                with ui.column().classes("card p-5 gap-3").style("flex:1 1 300px"):
                                    ui.label("Allocation").classes("section-title")
                                    ui.echart({"tooltip": {"trigger": "item"}, "series": [{"type": "pie", "radius": ["45%", "70%"],
                                        "data": [{"name": row["ticker"], "value": row["value"]} for row in portfolio["rows"]]}]}).classes("w-full h-60")
                                    ui.label(f"Largest position: {portfolio['concentration_pct']:.1f}% · {portfolio['sectors']} sector(s)").classes("text-sm text-slate-500")
                                    if portfolio["concentration_pct"] > 50:
                                        ui.label("High concentration: one holding exceeds half the portfolio.").classes("text-sm negative")
                            with ui.expansion("Manage holdings", icon="edit").classes("card w-full"):
                                for holding in holdings:
                                    with ui.row().classes("w-full justify-between items-center p-2"):
                                        ui.label(f"{holding['ticker']} · {holding['shares']:,.0f} shares")
                                        def remove_holding(holding_id=holding["id"]):
                                            delete_holding(user_id, holding_id); render_portfolio()
                                        ui.button(icon="delete_outline", on_click=remove_holding).props("flat round color=negative")
                        else:
                            with ui.column().classes("card p-8 w-full items-center gap-2"):
                                ui.icon("donut_large", size="42px", color="grey")
                                ui.label("No holdings yet").classes("text-lg font-semibold")
                                ui.label("Add your first asset below.").classes("text-slate-400")
                render_portfolio()
                with ui.column().classes("card p-5 w-full gap-4"):
                    ui.label("Add a holding").classes("section-title")
                    with ui.grid(columns=1).classes("w-full gap-3 md:grid-cols-5"):
                        holding_ticker = ui.input("Asset symbol", placeholder="ETH-TBILL").props("outlined").classes("w-full")
                        holding_shares = ui.number("Shares", min=0).props("outlined").classes("w-full")
                        holding_price = ui.number("Purchase price", min=0).props(f"outlined prefix='{CURRENCY}'").classes("w-full")
                        holding_dividends = ui.number("Income received", min=0, value=0).props(f"outlined prefix='{CURRENCY}'").classes("w-full")
                        holding_date = ui.input("Acquired", placeholder="YYYY-MM-DD").props("outlined").classes("w-full")
                    def create_holding() -> None:
                        try:
                            add_holding(user_id, holding_ticker.value or "", float(holding_shares.value or 0),
                                        float(holding_price.value or 0), float(holding_dividends.value or 0), holding_date.value)
                            holding_ticker.value = ""; render_portfolio(); ui.notify("Holding added.", type="positive")
                        except ValueError as error: ui.notify(str(error), type="negative")
                    with ui.row().classes("gap-2"):
                        ui.button("Add holding", on_click=create_holding, icon="add").props("color=primary")
                        ui.button("Refresh public quotes", on_click=lambda: refresh_market(), icon="refresh").props("outline color=primary")

            with ui.tab_panel(market_tab).classes("p-0 gap-5"):
                with ui.column().classes("card p-5 w-full gap-4"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.column().classes("gap-0"):
                            ui.label("Ethiopian asset reference board").classes("section-title")
                            market_status = ui.label("Public quotes have not been refreshed in this session.").classes("section-copy")
                        ui.button("Refresh quotes", on_click=lambda: refresh_market(), icon="refresh").props("color=primary")
                    with ui.row().classes("w-full items-end gap-3"):
                        market_search = ui.input("Filter by symbol or issuer", placeholder="ETH-TBILL").props("outlined dense clearable").style("flex:1")
                        ui.badge("PUBLIC / MAY BE DELAYED").props("outline color=orange")
                    market_columns = [{"name": key, "label": label, "field": key, "align": "left", "sortable": True} for key, label in [
                        ("ticker", "Ticker"), ("price", "Last price"), ("change", "Change"), ("open", "Open"),
                        ("high", "High"), ("low", "Low"), ("volume", "Volume"), ("trades", "Trades")]]
                    market_table = ui.table(columns=market_columns, rows=[], row_key="ticker", pagination=15).props("flat bordered").classes("w-full")

                    def quote_rows() -> list[dict]:
                        query = (market_search.value or "").lower()
                        return [{"ticker": quote["ticker"], "price": f"{CURRENCY} {quote['price']:,.2f}",
                                 "change": f"{quote['change_pct']:+.2f}%", "open": f"{quote['open']:,.2f}",
                                 "high": f"{quote['high']:,.2f}", "low": f"{quote['low']:,.2f}",
                                 "volume": f"{quote['volume']:,}", "trades": f"{quote['trades']:,}"}
                                for quote in quote_state["quotes"].values()
                                if not query or query in quote["ticker"].lower() or query in str(quote["issuer"]).lower()]

                    def filter_market() -> None:
                        market_table.rows = quote_rows(); market_table.update()
                    market_search.on_value_change(lambda _: filter_market())
                    filter_market()

                with ui.row().classes("w-full items-start gap-5"):
                    with ui.column().classes("card p-5 gap-4").style("flex:1 1 500px"):
                        ui.label("Watchlist").classes("section-title")
                        watchlist_box = ui.column().classes("w-full gap-2")
                        def render_watchlist() -> None:
                            watchlist_box.clear()
                            with watchlist_box:
                                items = list_watchlist(user_id)
                                if not items: ui.label("No watched tickers yet.").classes("text-slate-400")
                                for item in items:
                                    quote = quote_state["quotes"].get(item["ticker"], {})
                                    with ui.row().classes("w-full justify-between items-center rounded-xl bg-slate-50 p-3"):
                                        ui.label(item["ticker"]).classes("font-bold")
                                        ui.label(f"{CURRENCY} {quote.get('price', 0):,.2f} · {quote.get('change_pct', 0):+.2f}%")
                                        def remove_watch(item_id=item["id"]):
                                            delete_watchlist_item(user_id, item_id); render_watchlist()
                                        ui.button(icon="close", on_click=remove_watch).props("flat round dense")
                        render_watchlist()
                        with ui.row().classes("w-full items-end gap-2"):
                            watch_ticker = ui.input("Add ticker").props("outlined dense").style("flex:1")
                            def add_watch() -> None:
                                try:
                                    add_watchlist_item(user_id, watch_ticker.value or ""); watch_ticker.value = ""; render_watchlist()
                                except ValueError as error: ui.notify(str(error), type="negative")
                            ui.button("Add", on_click=add_watch).props("color=primary")
                    with ui.column().classes("card p-5 gap-4").style("flex:1 1 500px"):
                        ui.label("Market data notes").classes("section-title")
                        ui.label("Reference values are illustrative unless an approved market feed is explicitly configured. They must not be used for trading decisions.").classes("text-slate-600")
                        ui.label("Vizier caches successful responses for five minutes and falls back to clearly labelled demo prices if the source is unavailable.").classes("text-slate-600")

                async def refresh_market() -> None:
                    ui.notify("Refreshing configured market quotes…")
                    quotes, meta = await asyncio.to_thread(get_quotes, True, 60)
                    quote_state["quotes"], quote_state["meta"] = quotes, meta
                    timestamp = meta["fetched_at"].strftime("%Y-%m-%d %H:%M UTC") if meta.get("fetched_at") else "unknown"
                    market_status.text = f"{meta['source']} · refreshed {timestamp} · {len(quotes)} instruments"
                    portfolio_source.text = "PUBLIC / DELAYED" if meta["live"] else "DEMO FALLBACK"
                    filter_market(); render_watchlist(); render_portfolio()
                    ui.notify("Quotes refreshed." if meta["live"] else "Public feed unavailable; demo prices are shown.",
                              type="positive" if meta["live"] else "warning")

            with ui.tab_panel(statements_tab).classes("p-0 gap-5"):
                upload_state = {"filename": "", "headers": [], "rows": [], "transactions": [], "errors": []}
                with ui.column().classes("card p-5 w-full gap-4"):
                    ui.label("Import a CSV statement").classes("section-title")
                    ui.label("Upload, map, preview, and confirm. Files are limited to 5 MB and 5,000 rows.").classes("section-copy")
                    import_account = ui.select(account_options, value=accounts[0]["id"], label="Destination account").props("outlined").classes("w-72")
                    upload_status = ui.label("Choose a CSV file to begin.").classes("text-sm text-slate-500")
                    mapping_selects = {}
                    with ui.grid(columns=1).classes("w-full gap-3 md:grid-cols-5"):
                        for field, label in [("date", "Date*"), ("description", "Description*"),
                                             ("amount", "Signed amount"), ("debit", "Debit"), ("credit", "Credit")]:
                            mapping_selects[field] = ui.select({}, label=label).props("outlined dense").classes("w-full")
                    preview_table = ui.table(columns=[{"name": key, "label": label, "field": key, "align": "left"} for key, label in [
                        ("date", "Date"), ("description", "Description"), ("amount", "Amount"),
                        ("category", "Suggested category"), ("status", "Status")]], rows=[], row_key="index").props("flat bordered").classes("w-full")
                    validation_label = ui.label().classes("text-sm text-slate-500")

                    def current_mapping() -> dict[str, str | None]:
                        return {field: selector.value or None for field, selector in mapping_selects.items()}

                    def preview_import() -> None:
                        if not upload_state["rows"]:
                            ui.notify("Upload a CSV file first.", type="warning"); return
                        try:
                            transactions, errors = normalize_rows(upload_state["rows"], current_mapping())
                        except ValueError as error:
                            ui.notify(str(error), type="negative"); return
                        upload_state["transactions"], upload_state["errors"] = transactions, errors
                        preview_table.rows = [{**row, "index": index, "amount": f"{row['amount']:+,.2f}", "status": "Ready"}
                                              for index, row in enumerate(transactions[:20], 1)]
                        preview_table.update()
                        validation_label.text = f"{len(transactions):,} valid rows · {len(errors):,} rejected rows" + (f" · First error: {errors[0]}" if errors else "")

                    import_columns = [{"name": key, "label": label, "field": key, "align": "left"} for key, label in [
                        ("file", "File"), ("account", "Account"), ("imported", "Imported"),
                        ("duplicates", "Duplicates"), ("created", "Imported at")]]
                    transaction_columns = [{"name": key, "label": label, "field": key, "align": "left"} for key, label in [
                        ("date", "Date"), ("account", "Account"), ("description", "Description"),
                        ("amount", "Amount"), ("category", "Category")]]
                    ui.separator(); ui.label("Import history").classes("section-title")
                    import_history_table = ui.table(columns=import_columns, rows=[], row_key="id", pagination=10).props("flat bordered").classes("w-full")
                    ui.separator(); ui.label("Imported transactions").classes("section-title")
                    ui.label("Positive amounts are inflows; negative amounts are outflows.").classes("section-copy")
                    transactions_table = ui.table(columns=transaction_columns, rows=[], row_key="id", pagination=15).props("flat bordered").classes("w-full")

                    def refresh_statement_tables() -> None:
                        import_history_table.rows = [{"id": row["id"], "file": row["filename"], "account": row["account_name"],
                            "imported": row["imported_count"], "duplicates": row["duplicate_count"], "created": row["created_at"]}
                            for row in list_import_batches(user_id)]
                        transactions_table.rows = [{"id": row["id"], "date": row["transaction_date"], "account": row["account_name"],
                            "description": row["description"], "amount": f"{row['amount']:+,.2f}", "category": row["category"]}
                            for row in list_transactions(user_id)]
                        import_history_table.update(); transactions_table.update()

                    async def receive_statement(event) -> None:
                        if not event.file.name.lower().endswith(".csv"):
                            ui.notify("Only CSV files are accepted.", type="negative"); return
                        try:
                            headers, rows = read_csv_raw(await event.file.text())
                        except (ValueError, UnicodeDecodeError) as error:
                            ui.notify(f"Could not read CSV: {error}", type="negative"); return
                        upload_state.update({"filename": event.file.name, "headers": headers, "rows": rows,
                                             "transactions": [], "errors": []})
                        options = {"Not mapped": None, **{header: header for header in headers}}
                        detected = detect_columns(headers)
                        for field, selector in mapping_selects.items():
                            selector.options = options; selector.value = detected.get(field); selector.update()
                        upload_status.text = f"{event.file.name} · {len(rows):,} rows · {len(headers)} columns"
                        preview_import()

                    ui.upload(on_upload=receive_statement, auto_upload=True, max_file_size=5_000_000,
                              label="Select CSV statement").props("accept=.csv").classes("w-full")
                    with ui.row().classes("gap-2"):
                        ui.button("Refresh preview", on_click=preview_import, icon="preview").props("outline color=primary")

                        def confirm_import() -> None:
                            preview_import()
                            transactions = upload_state["transactions"]
                            if not transactions:
                                ui.notify("There are no valid rows to import.", type="negative"); return
                            result = import_transactions(user_id, int(import_account.value), upload_state["filename"], transactions)
                            refresh_statement_tables()
                            ui.notify(f"Imported {result['imported']} transactions; skipped {result['duplicates']} duplicates.", type="positive")
                        ui.button("Import valid rows", on_click=confirm_import, icon="download_done").props("color=primary")

                refresh_statement_tables()

            with ui.tab_panel(data_tab).classes("p-0 gap-5"):
                with ui.row().classes("w-full items-start gap-5"):
                    with ui.column().classes("card p-5 gap-4").style("flex:1 1 330px"):
                        ui.label("Profile").classes("section-title")
                        profile_name = ui.input("Full name", value=user["full_name"]).props("outlined").classes("w-full")
                        ui.input("Email", value=user["email"]).props("outlined readonly").classes("w-full")

                        def save_profile() -> None:
                            try:
                                update_profile(user_id, profile_name.value or "")
                                ui.notify("Profile updated.", type="positive")
                            except ValueError as error: ui.notify(str(error), type="negative")
                        ui.button("Save profile", on_click=save_profile, icon="save").props("outline color=primary")
                    with ui.column().classes("card p-5 gap-4").style("flex:2 1 500px"):
                        ui.label("Financial accounts").classes("section-title")
                        account_list = ui.column().classes("w-full gap-2")

                        def render_accounts() -> None:
                            account_list.clear()
                            with account_list:
                                for item in list_accounts(user_id):
                                    with ui.row().classes("w-full items-center justify-between rounded-xl bg-slate-50 p-3"):
                                        with ui.column().classes("gap-0"):
                                            ui.label(item["name"]).classes("font-medium")
                                            ui.label(item["account_type"]).classes("text-xs text-slate-500")
                                        def remove(account_id=item["id"]) -> None:
                                            try:
                                                delete_financial_account(user_id, account_id); render_accounts(); ui.notify("Financial account deleted.")
                                            except ValueError as error: ui.notify(str(error), type="negative")
                                        ui.button(icon="delete_outline", on_click=remove).props("flat round color=negative")
                        render_accounts(); ui.separator()
                        with ui.row().classes("w-full items-end gap-3"):
                            new_account_name = ui.input("New account name").props("outlined dense").style("flex:1")
                            new_account_type = ui.select(["Personal", "telebirr", "Bank", "Cash", "Business"], value="Personal", label="Type").props("outlined dense").style("width:150px")
                            def create_financial_account() -> None:
                                try:
                                    add_account(user_id, new_account_name.value or "", new_account_type.value or "Personal")
                                    new_account_name.value = ""; render_accounts(); ui.notify("Financial account added.", type="positive")
                                except ValueError as error: ui.notify(str(error), type="negative")
                            ui.button("Add", on_click=create_financial_account, icon="add").props("color=primary")
                with ui.column().classes("card p-5 w-full gap-4"):
                    ui.label("Your data").classes("section-title")
                    ui.label("Download all saved monthly records as a CSV file.").classes("section-copy")
                    ui.button("Export my data", on_click=lambda: ui.download.content(export_user_csv(user_id), "vizier-data.csv", "text/csv"), icon="download").props("outline color=primary")
                    ui.separator(); ui.label("Danger zone").classes("font-semibold text-red-700")
                    ui.label("Deleting your Vizier account permanently removes your profile, financial accounts, and monthly history.").classes("text-sm text-slate-500")
                    with ui.dialog() as delete_dialog, ui.card().classes("p-5 gap-4"):
                        ui.label("Delete your Vizier account?").classes("text-xl font-bold")
                        ui.label("This cannot be undone. All locally stored data will be removed.")
                        with ui.row().classes("w-full justify-end gap-2"):
                            ui.button("Cancel", on_click=delete_dialog.close).props("flat")
                            def confirm_delete() -> None:
                                delete_user(user_id); app.storage.user.clear(); ui.navigate.to("/login")
                            ui.button("Delete permanently", on_click=confirm_delete).props("color=negative")
                    ui.button("Delete my account", on_click=delete_dialog.open, icon="delete_forever").props("outline color=negative")
        ui.label("Educational prototype · Demo prices are not live market data or financial advice.").classes("text-center text-xs text-slate-400")


initialize_database()
ui.run(title="Vizier", favicon=Path(__file__).with_name("assets") / "vizier-logo.jpeg", reload=False,
       port=int(os.environ.get("VIZIER_PORT", "8080")),
       storage_secret=validate_runtime())

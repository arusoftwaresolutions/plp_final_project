import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
from typing import Optional

# --------------------
# Configuration
# --------------------
st.set_page_config(
    page_title="Financial Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --------------------
# Styles (modern, subtle)
# --------------------
st.markdown(
    """
    <style>
    /* Page background & font */
    .stApp {
        background: #f6f8fa;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Header */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 22px;
        border-radius: 12px;
        background: linear-gradient(90deg,#0f172a,#1e293b);
        color: #ffffff;
        margin-bottom: 18px;
        box-shadow: 0 6px 20px rgba(2,6,23,0.08);
    }
    .app-title {
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 0.2px;
    }
    .app-sub {
        font-size: 13px;
        color: rgba(255,255,255,0.85);
    }

    /* Auth card */
    .auth-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 8px 30px rgba(2,6,23,0.06);
        border: 1px solid #eef2f7;
    }

    /* Generic card */
    .card {
        background: #ffffff;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 6px 24px rgba(2,6,23,0.04);
        border: 1px solid #f1f5f9;
    }

    /* Metric cards grid */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
    }

    /* Tabs: fade in content for smooth transition */
    [data-testid="stTabs"] [role="tabpanel"] {
        animation: fadeIn 420ms ease;
        -webkit-animation: fadeIn 420ms ease;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Small tweaks for progress & campaign items */
    .campaign-title {
        font-weight: 700;
        margin-bottom: 6px;
    }
    .campaign-desc {
        font-size: 13px;
        color: #334155;
        margin-bottom: 8px;
    }

    /* Sidebar user badge */
    .user-badge {
        display:flex;
        gap:12px;
        align-items:center;
        margin-bottom:8px;
    }
    .avatar {
        background:#1f2937;
        color:#fff;
        width:44px;
        height:44px;
        border-radius:50%;
        display:flex;
        align-items:center;
        justify-content:center;
        font-weight:700;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------
# API Client
# --------------------
class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None

    def set_token(self, token: str):
        self.token = token

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _post(self, path: str, payload: dict, auth: bool = False):
        try:
            resp = requests.post(f"{self.base_url}{path}", json=payload, headers=self._get_headers(), timeout=12)
            return resp
        except requests.RequestException as e:
            st.error(f"Network error: {e}")
            return None

    def _get(self, path: str, auth: bool = False):
        try:
            resp = requests.get(f"{self.base_url}{path}", headers=self._get_headers(), timeout=12)
            return resp
        except requests.RequestException as e:
            st.error(f"Network error: {e}")
            return None

    def login(self, email: str, password: str):
        resp = self._post("/api/auth/login", {"email": email, "password": password})
        if resp and resp.status_code in (200, 201):
            try:
                data = resp.json()
            except ValueError:
                st.error("Unexpected login response from server.")
                return None
            token = data.get("access_token") or data.get("token")
            if token:
                self.set_token(token)
            return data
        return None

    def register(self, email: str, password: str, full_name: str, user_type: str):
        resp = self._post("/api/auth/register", {"email": email, "password": password, "full_name": full_name, "user_type": user_type})
        if resp and resp.status_code in (200, 201, 204):
            return True
        # try to show useful message
        if resp is not None:
            try:
                j = resp.json()
                msg = j.get("detail") or j.get("message") or str(j)
                st.error(f"Registration failed: {msg}")
            except ValueError:
                st.error(f"Registration failed with status {resp.status_code}")
        return False

    def get_user_info(self):
        resp = self._get("/api/auth/me")
        if resp and resp.status_code in (200, 201):
            try:
                return resp.json()
            except ValueError:
                return None
        return None

    def get_family_dashboard(self):
        resp = self._get("/api/families/dashboard")
        if resp and resp.status_code == 200:
            return resp.json()
        return None

    def get_transactions(self):
        resp = self._get("/api/families/transactions")
        if resp and resp.status_code == 200:
            return resp.json()
        return None

    def create_transaction(self, transaction_data):
        resp = self._post("/api/families/transactions", transaction_data)
        return resp is not None and resp.status_code in (200, 201, 204)

    def get_campaigns(self):
        resp = self._get("/api/donors/campaigns")
        if resp and resp.status_code == 200:
            return resp.json()
        return None

    def make_donation(self, donation_data):
        resp = self._post("/api/donors/donate", donation_data)
        return resp is not None and resp.status_code in (200, 201, 204)

    def get_ai_recommendations(self):
        resp = self._get("/api/ai/recommendations")
        if resp and resp.status_code == 200:
            return resp.json()
        return None

    def get_map_data(self):
        resp = self._get("/api/geospatial/map")
        if resp and resp.status_code == 200:
            return resp.json()
        return None


# API client instance
api_client = APIClient(BACKEND_URL)

# --------------------
# Auth UI (replaces login_page)
# --------------------
def login_page():
    st.markdown(
        """
        <div class="app-header">
            <div>
                <div class="app-title">Financial Platform</div>
                <div class="app-sub">Manage family finances, donations and insights</div>
            </div>
            <div>
                <small style="opacity:0.85">Secure & responsive · Built with Streamlit</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main centered auth card
    col_left, col_center, col_right = st.columns([1, 2.2, 1])
    with col_center:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        tabs = st.tabs(["Login", "Register"])

        # --------- LOGIN TAB ---------
        with tabs[0]:
            st.subheader("Sign in to your account")
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Login")

                if submitted:
                    with st.spinner("Signing in..."):
                        result = api_client.login(email.strip(), password)
                        if result:
                            user_info = api_client.get_user_info()
                            st.session_state.logged_in = True
                            st.session_state.user_info = user_info or result
                            st.success("Login successful")
                            st.experimental_rerun()
                        else:
                            st.error("Invalid credentials or server error. Check backend URL and try again.")

            st.markdown("---")
            st.markdown("If you don't have an account, switch to the Register tab.")

        # --------- REGISTER TAB ---------
        with tabs[1]:
            st.subheader("Create a new account")
            with st.form("register_form", clear_on_submit=True):
                reg_name = st.text_input("Full name", key="reg_name")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                reg_type = st.selectbox("User type", ["family", "donor", "business", "admin"], key="reg_type")
                reg_submitted = st.form_submit_button("Register")

                if reg_submitted:
                    if not (reg_email and reg_password and reg_name):
                        st.error("Please fill all required fields.")
                    else:
                        with st.spinner("Creating account..."):
                            success = api_client.register(reg_email.strip(), reg_password, reg_name.strip(), reg_type)
                            if success:
                                st.success("Registration successful. You may now login.")
                            else:
                                st.error("Registration failed. See the error message above.")

        st.markdown("</div>", unsafe_allow_html=True)

# --------------------
# Dashboards & Pages
# --------------------
def family_dashboard():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Family Dashboard")

    with st.spinner("Loading dashboard..."):
        dashboard_data = api_client.get_family_dashboard()

    if not dashboard_data:
        st.error("Failed to load dashboard data")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Metrics (styled)
    metrics_container = st.container()
    with metrics_container:
        st.markdown('<div class="card-grid">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        try:
            c1.metric("Total Income", f"${dashboard_data.get('total_income', 0):,.2f}")
            c2.metric("Total Expenses", f"${dashboard_data.get('total_expenses', 0):,.2f}")
            c3.metric("Net Income", f"${dashboard_data.get('net_income', 0):,.2f}")
            c4.metric("Transactions", dashboard_data.get('transaction_count', 0))
        except Exception:
            # fallback if numeric conversion fails
            c1.metric("Total Income", dashboard_data.get('total_income', 0))
            c2.metric("Total Expenses", dashboard_data.get('total_expenses', 0))
            c3.metric("Net Income", dashboard_data.get('net_income', 0))
            c4.metric("Transactions", dashboard_data.get('transaction_count', 0))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Charts and recommendations
    left_col, right_col = st.columns([2, 1])
    with left_col:
        st.subheader("Recent Transactions")
        recent = dashboard_data.get("recent_transactions", [])
        if recent:
            transactions_df = pd.DataFrame(recent)
            if "date" in transactions_df.columns:
                transactions_df["date"] = pd.to_datetime(transactions_df["date"])
                fig = px.bar(
                    transactions_df.sort_values("date"),
                    x="date",
                    y="amount",
                    color="transaction_type",
                    title="Recent Transactions",
                )
            else:
                fig = px.bar(transactions_df, x=transactions_df.index, y="amount", title="Recent Transactions")
            fig.update_layout(template="plotly_white", margin=dict(t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("### All transactions")
            transactions_df_display = transactions_df[["date", "amount", "category", "transaction_type", "description"]].sort_values("date", ascending=False) if "date" in transactions_df.columns else transactions_df
            st.dataframe(transactions_df_display.reset_index(drop=True))
        else:
            st.info("No transactions available.")

    with right_col:
        st.subheader("AI Recommendations")
        recs = dashboard_data.get("ai_recommendations") or []
        if recs:
            for rec in recs:
                prio = rec.get("priority", "low").lower()
                color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}.get(prio, "#6b7280")
                st.markdown(f"**{rec.get('title','Untitled')}**")
                st.markdown(f"{rec.get('description','')}")
                st.markdown(f"<small style='color:{color}; font-weight:700'>Priority: {prio.title()}</small>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No AI recommendations at this time.")

    st.markdown("</div>", unsafe_allow_html=True)


def add_transaction():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Add Transaction")
    with st.form("transaction_form", clear_on_submit=True):
        amount = st.number_input("Amount (USD)", min_value=0.01, step=0.01)
        transaction_type = st.selectbox("Type", ["income", "expense"])
        category = st.text_input("Category")
        description = st.text_area("Description (optional)")
        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            payload = {
                "amount": amount,
                "transaction_type": transaction_type,
                "category": category,
                "description": description,
            }
            with st.spinner("Saving transaction..."):
                ok = api_client.create_transaction(payload)
            if ok:
                st.success("Transaction added successfully.")
                st.experimental_rerun()
            else:
                st.error("Failed to add transaction.")
    st.markdown("</div>", unsafe_allow_html=True)


def donor_dashboard():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Donor Dashboard")

    with st.spinner("Loading campaigns..."):
        campaigns = api_client.get_campaigns()

    if not campaigns:
        st.info("No campaigns found.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for campaign in campaigns:
        st.markdown('<div class="card" style="margin-bottom:10px">', unsafe_allow_html=True)
        st.markdown(f"<div class='campaign-title'>{campaign.get('title')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='campaign-desc'>{campaign.get('description')}</div>", unsafe_allow_html=True)
        current = campaign.get("current_amount", 0)
        target = campaign.get("target_amount", 1)
        progress = min(1.0, current / target if target else 0)
        st.progress(progress)
        st.markdown(f"${current:,.2f} of ${target:,.2f}")
        col1, col2 = st.columns([3, 1])
        with col1:
            # nothing
            pass
        with col2:
            if st.button("Donate", key=f"donate_trigger_{campaign.get('id')}"):
                st.session_state.selected_campaign = campaign
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Donation form appears if selected
    if st.session_state.get("selected_campaign"):
        sel = st.session_state["selected_campaign"]
        st.markdown("---")
        st.subheader(f"Donate to: {sel.get('title')}")
        with st.form("donation_form", clear_on_submit=True):
            amount = st.number_input("Donation Amount (USD)", min_value=1.0, step=1.0)
            is_anonymous = st.checkbox("Donate anonymously")
            submitted = st.form_submit_button("Donate")
            if submitted:
                payload = {"campaign_id": sel.get("id"), "amount": amount, "is_anonymous": is_anonymous}
                with st.spinner("Processing donation..."):
                    ok = api_client.make_donation(payload)
                if ok:
                    st.success("Thank you! Donation successful.")
                    st.session_state.pop("selected_campaign", None)
                    st.experimental_rerun()
                else:
                    st.error("Donation failed.")
    st.markdown("</div>", unsafe_allow_html=True)


def business_dashboard():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Business Dashboard")

    st.subheader("Loan Applications")
    loan_applications = [
        {
            "id": "1",
            "amount": 25000,
            "purpose": "Equipment purchase for expansion",
            "status": "pending",
            "created_at": "2024-01-15",
        },
        {
            "id": "2",
            "amount": 15000,
            "purpose": "Working capital",
            "status": "approved",
            "created_at": "2024-01-10",
        },
    ]
    for loan in loan_applications:
        st.markdown('<div style="padding:10px;border-radius:8px;margin-bottom:8px;background:#fbfbfd">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown(f"**${loan['amount']:,.2f}** - {loan['purpose']}")
        with c2:
            st.markdown(f"Status: **{loan['status'].title()}**")
        with c3:
            st.markdown(f"Applied: {loan['created_at']}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Apply for New Loan")
    with st.form("loan_form", clear_on_submit=True):
        amount = st.number_input("Loan Amount", min_value=1000, step=1000)
        purpose = st.text_area("Purpose of Loan")
        submitted = st.form_submit_button("Submit Application")
        if submitted:
            st.success("Loan application submitted successfully!")
    st.markdown("</div>", unsafe_allow_html=True)


def admin_dashboard():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Admin Dashboard")
    stats = {
        "total_families": 45,
        "total_campaigns": 12,
        "total_donations": 156,
        "total_loans": 8,
        "pending_loans": 3,
        "approved_loans": 5,
        "total_donated": 125000,
    }
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Families", stats["total_families"])
    c2.metric("Total Campaigns", stats["total_campaigns"])
    c3.metric("Total Donations", stats["total_donations"])
    c4.metric("Total Donated", f"${stats['total_donated']:,.2f}")

    st.markdown("---")
    st.subheader("Pending Loan Applications")
    pending_loans = [
        {
            "id": "3",
            "business": "Tech Startup LLC",
            "amount": 50000,
            "purpose": "Product development",
            "applied_date": "2024-01-20",
        }
    ]
    for loan in pending_loans:
        st.markdown('<div style="padding:10px;border-radius:8px;margin-bottom:8px;background:#fbfbfd">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{loan['business']}** - ${loan['amount']:,.2f}")
            st.markdown(loan["purpose"])
        with col2:
            st.markdown(f"Applied: {loan['applied_date']}")
        with col3:
            col_approve, col_reject = st.columns(2)
            with col_approve:
                if st.button("Approve", key=f"approve_{loan['id']}"):
                    st.success("Loan approved!")
            with col_reject:
                if st.button("Reject", key=f"reject_{loan['id']}"):
                    st.error("Loan rejected!")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def map_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Poverty Hotspots Map")
    with st.spinner("Loading map..."):
        map_data = api_client.get_map_data()
    if not map_data:
        st.error("Failed to load map data")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    st.markdown(f"**Hotspots:** {map_data.get('hotspots_count', 0)} | **Families:** {map_data.get('families_count', 0)}")
    components.html(map_data.get("map_html", "<p>No map available</p>"), height=600)
    st.markdown("</div>", unsafe_allow_html=True)


# --------------------
# Main
# --------------------
def main():
    # Initialize session state keys
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "selected_campaign" not in st.session_state:
        st.session_state.selected_campaign = None

    # If not logged in, show auth page
    if not st.session_state.logged_in:
        login_page()
        return

    # Logged-in: get user_info (ensure it's fresh if none)
    user_info = st.session_state.get("user_info") or api_client.get_user_info() or {}
    st.session_state.user_info = user_info

    # Top header (small and compact for logged-in)
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <div style="font-weight:700;font-size:18px">Financial Platform</div>
            <div style="font-size:13px;color:#374151">Signed in as <strong>{user_info.get('full_name','User')}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        name = user_info.get("full_name", "User")
        user_type = user_info.get("user_type", "")
        initials = "".join([p[0].upper() for p in name.split()][:2]) or "U"
        st.markdown(f"""
            <div class="user-badge">
                <div class="avatar">{initials}</div>
                <div>
                    <div style="font-weight:700">{name}</div>
                    <div style="font-size:12px;color:#64748b">{user_type.title() if user_type else "Member"}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.experimental_rerun()

        st.markdown("---")

        # Navigation per user type
        if user_type == "family":
            page = st.selectbox("Navigation", ["Dashboard", "Add Transaction", "AI Recommendations", "Map"])
        elif user_type == "donor":
            page = st.selectbox("Navigation", ["Dashboard", "Map"])
        elif user_type == "business":
            page = st.selectbox("Navigation", ["Dashboard", "Map"])
        elif user_type == "admin":
            page = st.selectbox("Navigation", ["Dashboard", "Map"])
        else:
            page = st.selectbox("Navigation", ["Dashboard", "Map"])

    # Main content switch
    if page == "Dashboard":
        if user_type == "family":
            family_dashboard()
        elif user_type == "donor":
            donor_dashboard()
        elif user_type == "business":
            business_dashboard()
        elif user_type == "admin":
            admin_dashboard()
        else:
            # fallback to family-like dashboard if unknown
            family_dashboard()
    elif page == "Add Transaction" and user_type == "family":
        add_transaction()
    elif page == "AI Recommendations" and user_type == "family":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("AI Recommendations")
        recommendations = api_client.get_ai_recommendations() or []
        if recommendations:
            for rec in recommendations:
                st.markdown(f"**{rec.get('title','')}**")
                st.markdown(rec.get("description",""))
                st.markdown("---")
        else:
            st.info("No AI recommendations available.")
        st.markdown("</div>", unsafe_allow_html=True)
    elif page == "Map":
        map_page()


if __name__ == "__main__":
    main()

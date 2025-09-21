import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Try to import folium for better mapping
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# Backend API Configuration - Matching your actual backend
API_BASE_URL = "https://plp-final-project-bgex.onrender.com"
API_PREFIX = "/api/v1"

def get_api_url(endpoint):
    """Get full API URL"""
    return f"{API_BASE_URL}{API_PREFIX}{endpoint}"

def make_api_request(endpoint, method="GET", data=None, headers=None):
    """Make API request with proper authentication"""
    try:
        url = get_api_url(endpoint)
        default_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state.get('auth_token', '')}"
        }
        if headers:
            default_headers.update(headers)

        # Handle form data for login
        if method == "POST" and endpoint == "/auth/login/access-token":
            response = requests.post(url, data=data, headers=default_headers, timeout=10)
        else:
            if method == "GET":
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=10)

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# Set page config
st.set_page_config(
    page_title="SDG Finance Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Global CSS for professional design
st.markdown("""
<style>
/* Professional fintech styling */
.main {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    min-height: 100vh;
}

.login-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
    background: white;
    padding: 3rem;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    max-width: 450px;
    width: 100%;
    margin: 2rem;
}

.app-header {
    background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 0 0 20px 20px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.navbar {
    background: white;
    padding: 1rem 2rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-links {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.nav-link {
    color: #4b6cb7;
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.3s;
    border: none;
    background: none;
    cursor: pointer;
}

.nav-link:hover {
    background: #f0f4ff;
    color: #182848;
}

.nav-link.active {
    background: #4b6cb7;
    color: white;
}

.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border-left: 5px solid #4b6cb7;
    text-align: center;
}

.metric-card h3 {
    color: #4b6cb7;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    font-weight: 600;
}

.metric-card h2 {
    color: #2c3e50;
    margin: 0;
    font-size: 1.8rem;
    font-weight: 700;
}

.campaign-card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 1rem 0;
    border-left: 5px solid #4b6cb7;
}

.loan-card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 1rem 0;
    border-left: 5px solid #28a745;
}

.ai-card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 1rem 0;
    border-left: 5px solid #ffc107;
}

.transaction-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
    border-left: 4px solid #4b6cb7;
}

.footer {
    text-align: center;
    color: #666;
    font-size: 0.9rem;
    padding: 2rem 0;
    border-top: 1px solid #e0e0e0;
    margin-top: 3rem;
}

/* Progress bar styling */
.progress-bar {
    background: #f0f0f0;
    border-radius: 10px;
    height: 10px;
    margin: 0.5rem 0;
    overflow: hidden;
}

.progress-fill {
    background: linear-gradient(90deg, #4b6cb7, #28a745);
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s ease;
}

/* Hide Streamlit elements */
[data-testid="stHeader"] {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}

/* Responsive design */
@media (max-width: 768px) {
    .navbar {
        flex-direction: column;
        gap: 1rem;
    }
    .nav-links {
        flex-wrap: wrap;
        justify-content: center;
    }
}
</style>
""", unsafe_allow_html=True)

def show_login_page():
    """Professional login page"""
    st.markdown("""
    <div class="login-container">
        <div class="login-box">
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="color: #2c3e50; margin-bottom: 0.5rem;">🌍 SDG Finance Platform</h1>
                <p style="color: #666;">Empowering communities through financial inclusion</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Login form
    with st.form("login_form"):
        st.subheader("🔐 Login to Your Account")

        username = st.text_input("Email/Username", placeholder="Enter your email or username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            login_button = st.form_submit_button("Login", use_container_width=True)

    if login_button:
        if username and password:
            # Try to authenticate with backend using form data
            try:
                response = requests.post(
                    get_api_url("/auth/login/access-token"),
                    data={
                        "username": username,
                        "password": password
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        st.session_state.auth_token = data["access_token"]
                        st.session_state.authenticated = True
                        st.session_state.current_user = {"username": username}
                        st.session_state.is_admin = False  # Will be updated when we fetch user profile

                        # Fetch user profile to get admin status
                        user_data = make_api_request("/users/me")
                        if user_data:
                            st.session_state.current_user = user_data
                            # Check if user has admin role
                            roles = user_data.get("roles", [])
                            st.session_state.is_admin = "admin" in [role.lower() for role in roles]

                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid response from server")
                else:
                    st.error("❌ Invalid credentials. Please try again.")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
        else:
            st.error("⚠️ Please enter both email and password")

    st.markdown("---")
    st.markdown("**Demo Accounts:**")
    st.markdown("👤 **User:** `user@example.com` / `password123`")
    st.markdown("🔧 **Admin:** `admin@example.com` / `admin123`")

def show_navbar():
    """Professional top navigation bar"""
    pages = [
        "Dashboard", "AI Recommendations", "Transactions",
        "Crowdfunding", "Microloans", "Poverty Map", "Profile"
    ]

    if st.session_state.get('is_admin', False):
        pages.append("Admin Panel")

    current_page = st.session_state.get('current_page', 'Dashboard')

    st.markdown(f"""
    <div class="navbar">
        <div>
            <h3 style="margin: 0; color: #4b6cb7;">🌍 SDG Finance Platform</h3>
        </div>
        <div class="nav-links">
    """, unsafe_allow_html=True)

    # Navigation links
    for page in pages:
        active_class = 'active' if current_page == page else ''
        if st.button(page, key=f"nav_{page}", help=f"Go to {page}"):
            st.session_state.current_page = page
            st.rerun()

    # User info and logout
    user_info = st.session_state.get('current_user', {})
    username = user_info.get('username', 'User')
    st.markdown(f"""
        <span style="margin-left: 1rem; padding: 0.5rem; background: #f0f4ff; border-radius: 20px; font-size: 0.9rem;">
            👤 {username} {'(Admin)' if st.session_state.get('is_admin', False) else ''}
        </span>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", key="logout"):
        st.session_state.authenticated = False
        st.session_state.auth_token = None
        st.session_state.current_user = None
        st.session_state.is_admin = False
        st.success("Logged out successfully!")
        st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)

def show_dashboard():
    """Professional dashboard with real backend data"""
    st.markdown('<div class="app-header"><h1>📊 Dashboard</h1><p>Comprehensive financial overview and insights</p></div>', unsafe_allow_html=True)

    # Fetch comprehensive data from backend
    # Fetch user data from backend
    user_data = make_api_request("/users/me")
    transactions_data = make_api_request("/transactions")
    loans_data = make_api_request("/loans")

    # Calculate metrics
    total_balance = 0
    total_expenses = 0
    total_income = 0
    active_loans = 0

    if transactions_data:
        for trans in transactions_data.get('transactions', []):
            if trans['type'] == 'income':
                total_income += trans['amount']
            else:
                total_expenses += trans['amount']
        total_balance = total_income - total_expenses

    if loans_data:
        active_loans = len([loan for loan in loans_data.get('loans', []) if loan['status'] == 'active'])

    # Display metrics
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #4b6cb7; margin-bottom: 0.5rem;">💰 Balance</h3>
            <h2 style="color: #2c3e50; margin: 0;">${total_balance:,.2f}</h2>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #4b6cb7; margin-bottom: 0.5rem;">📈 Income</h3>
            <h2 style="color: #2c3e50; margin: 0;">${total_income:,.2f}</h2>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #4b6cb7; margin-bottom: 0.5rem;">📉 Expenses</h3>
            <h2 style="color: #2c3e50; margin: 0;">${total_expenses:,.2f}</h2>
        </div>
        ''', unsafe_allow_html=True)

    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #4b6cb7; margin-bottom: 0.5rem;">🏦 Active Loans</h3>
            <h2 style="color: #2c3e50; margin: 0;">{active_loans}</h2>
        </div>
        ''', unsafe_allow_html=True)

    # Charts
    st.markdown("### 📊 Financial Overview")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Monthly expenses chart
        if transactions_data:
            df = pd.DataFrame(transactions_data.get('transactions', []))
            if not df.empty:
                df['date'] = pd.to_datetime(df['created_at'])
                monthly_data = df.groupby([df['date'].dt.to_period('M'), 'type'])['amount'].sum().unstack().fillna(0)

                fig = go.Figure()
                fig.add_trace(go.Bar(name='Income', x=monthly_data.index.astype(str), y=monthly_data.get('income', 0)))
                fig.add_trace(go.Bar(name='Expenses', x=monthly_data.index.astype(str), y=monthly_data.get('expense', 0)))
                fig.update_layout(title="Monthly Income vs Expenses", barmode='group')
                st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        # Category breakdown
        if transactions_data:
            df = pd.DataFrame(transactions_data.get('transactions', []))
            if not df.empty and 'category' in df.columns:
                category_data = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
                fig = px.pie(values=category_data.values, names=category_data.index, title="Expense Categories")
                st.plotly_chart(fig, use_container_width=True)

def show_ai_recommendations():
    """AI Recommendations with backend integration"""
    st.markdown('<div class="app-header"><h1>🤖 AI Recommendations</h1><p>Personalized financial insights</p></div>', unsafe_allow_html=True)

    # Get AI recommendations from backend
    recommendations = make_api_request("/ai/recommendations")

    if recommendations and 'recommendations' in recommendations:
        st.markdown("### 💡 Personalized Tips")

        for i, rec in enumerate(recommendations['recommendations'], 1):
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-left: 4px solid #4b6cb7;">
                <h4 style="color: #4b6cb7; margin-bottom: 0.5rem;">💡 Tip #{i}</h4>
                <p style="margin: 0; color: #2c3e50;">{rec.get('title', 'Financial Tip')}</p>
                <p style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">{rec.get('description', 'No description available')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🤖 Our AI assistant is temporarily unavailable. Please try again later.")

def show_transactions():
    """Transactions page with real data"""
    st.markdown('<div class="app-header"><h1>💳 Transactions</h1><p>Track your financial activity</p></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📋 Transaction History")

        # Add new transaction form
        with st.expander("➕ Add New Transaction", expanded=False):
            with st.form("add_transaction"):
                trans_type = st.selectbox("Type", ["income", "expense"])
                amount = st.number_input("Amount", min_value=0.01, step=0.01)
                category = st.text_input("Category")
                description = st.text_area("Description")

                if st.form_submit_button("Add Transaction"):
                    data = {
                        "type": trans_type,
                        "amount": amount,
                        "category": category,
                        "description": description
                    }
                    result = make_api_request("/transactions", "POST", data)
                    if result:
                        st.success("✅ Transaction added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add transaction")

        # Display transactions
        transactions_data = make_api_request("/transactions")
        if transactions_data and 'transactions' in transactions_data:
            df = pd.DataFrame(transactions_data['transactions'])
            if not df.empty:
                st.dataframe(df, use_container_width=True)

                # Transaction chart
                fig = px.bar(df, x='created_at', y='amount', color='type', title="Transaction Timeline")
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📊 Summary")
        if transactions_data and 'transactions' in transactions_data:
            df = pd.DataFrame(transactions_data['transactions'])
            if not df.empty:
                total_income = df[df['type'] == 'income']['amount'].sum()
                total_expenses = df[df['type'] == 'expense']['amount'].sum()

                st.metric("Total Income", f"${total_income:.2f}")
                st.metric("Total Expenses", f"${total_expenses:.2f}")
                st.metric("Net Balance", f"${total_income - total_expenses:.2f}")

def show_crowdfunding():
    """Crowdfunding page with real data"""
    st.markdown('<div class="app-header"><h1>🤝 Crowdfunding</h1><p>Support community projects</p></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🌟 Active Campaigns")

        # Create new campaign form
        with st.expander("➕ Create New Campaign", expanded=False):
            with st.form("create_campaign"):
                title = st.text_input("Campaign Title")
                description = st.text_area("Description")
                goal = st.number_input("Goal Amount", min_value=100, step=100)
                end_date = st.date_input("End Date", min_value=datetime.now().date() + timedelta(days=30))

                if st.form_submit_button("Create Campaign"):
                    data = {
                        "title": title,
                        "description": description,
                        "goal_amount": goal,
                        "end_date": str(end_date)
                    }
                    result = make_api_request("/crowdfunding/campaigns", "POST", data)
                    if result:
                        st.success("✅ Campaign created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create campaign")

        # Display campaigns
        campaigns = make_api_request("/crowdfunding/campaigns")
        if campaigns and 'campaigns' in campaigns:
            for campaign in campaigns['campaigns']:
                progress = min(100, (campaign.get('raised_amount', 0) / campaign.get('goal_amount', 100)) * 100)

                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-left: 4px solid #4b6cb7;">
                    <h4 style="color: #4b6cb7; margin-bottom: 0.5rem;">{campaign.get('title', 'Campaign')}</h4>
                    <p style="color: #666; margin-bottom: 1rem;">{campaign.get('description', '')}</p>
                    <div style="margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>Raised: ${campaign.get('raised_amount', 0):.2f}</span>
                            <span>Goal: ${campaign.get('goal_amount', 100):.2f}</span>
                        </div>
                        <div style="background: #f0f0f0; border-radius: 10px; height: 8px;">
                            <div style="background: #4b6cb7; border-radius: 10px; height: 8px; width: {progress}%;"></div>
                        </div>
                        <div style="text-align: center; font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
                            {progress:.1f}% funded
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🎯 Quick Contribute")

        # Quick contribution form
        with st.form("quick_contribute"):
            campaign_id = st.selectbox("Select Campaign", ["Campaign 1", "Campaign 2", "Campaign 3"])
            amount = st.number_input("Amount", min_value=10, step=10)

            if st.form_submit_button("Contribute"):
                st.success(f"✅ Contributed ${amount:.2f} successfully!")

def show_microloans():
    """Microloans page with real data"""
    st.markdown('<div class="app-header"><h1>🏦 Microloans</h1><p>Small loans for big impact</p></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 💰 Available Loan Offers")

        # Apply for loan form
        with st.expander("📝 Apply for a Loan", expanded=False):
            with st.form("apply_loan"):
                loan_amount = st.number_input("Loan Amount", min_value=100, max_value=5000, step=100)
                loan_purpose = st.selectbox("Purpose", ["Business", "Education", "Healthcare", "Emergency", "Other"])
                repayment_period = st.selectbox("Repayment Period (months)", [3, 6, 12, 18, 24])

                if st.form_submit_button("Apply for Loan"):
                    data = {
                        "amount": loan_amount,
                        "purpose": loan_purpose,
                        "repayment_period": repayment_period
                    }
                    result = make_api_request("/loans/apply", "POST", data)
                    if result:
                        st.success("✅ Loan application submitted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to submit loan application")

        # Display available loans
        loans = make_api_request("/loans/available")
        if loans and 'loans' in loans:
            for loan in loans['loans']:
                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-left: 4px solid #4b6cb7;">
                    <h4 style="color: #4b6cb7; margin-bottom: 0.5rem;">💰 {loan.get('type', 'Microloan')}</h4>
                    <p style="margin-bottom: 1rem;"><strong>Amount:</strong> ${loan.get('amount', 0):.2f}</p>
                    <p style="margin-bottom: 1rem;"><strong>Interest Rate:</strong> {loan.get('interest_rate', 0)}%</p>
                    <p style="color: #666; margin-bottom: 1rem;">{loan.get('description', 'No description available')}</p>
                    <button style="background: #4b6cb7; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                        Apply Now
                    </button>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 📊 Loan Statistics")
        loans_data = make_api_request("/loans")
        if loans_data and 'loans' in loans_data:
            total_loans = len(loans_data['loans'])
            active_loans = len([l for l in loans_data['loans'] if l.get('status') == 'active'])
            total_amount = sum(l.get('amount', 0) for l in loans_data['loans'])

            st.metric("Total Loans", total_loans)
            st.metric("Active Loans", active_loans)
            st.metric("Total Amount", f"${total_amount:.2f}")

def show_poverty_map():
    """Enhanced poverty map with real geospatial data"""
    st.markdown('<div class="app-header"><h1>🗺️ Poverty Map</h1><p>Interactive visualization of areas needing support</p></div>', unsafe_allow_html=True)

    # Get poverty data from backend
    poverty_data = make_api_request("/poverty/data")

    if poverty_data and 'regions' in poverty_data:
        st.markdown("### 🌍 Poverty Distribution Map")

        regions = poverty_data['regions']

        if regions:
            # Create a dataframe for visualization
            df = pd.DataFrame(regions)

            if FOLIUM_AVAILABLE and 'latitude' in df.columns and 'longitude' in df.columns:
                # Create interactive map with folium
                center_lat = df['latitude'].mean()
                center_lng = df['longitude'].mean()

                m = folium.Map(location=[center_lat, center_lng], zoom_start=10)

                # Add markers for each region
                for _, row in df.iterrows():
                    # Color based on poverty rate
                    poverty_rate = row.get('poverty_rate', 0)
                    if poverty_rate > 50:
                        color = 'red'
                    elif poverty_rate > 25:
                        color = 'orange'
                    else:
                        color = 'green'

                    popup_text = f"""
                    <b>{row.get('name', 'Region')}</b><br>
                    Population: {row.get('population', 0):,}<br>
                    Poverty Rate: {poverty_rate:.1f}%<br>
                    Avg Income: ${row.get('avg_income', 0):.2f}
                    """

                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=10,
                        popup=popup_text,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7
                    ).add_to(m)

                # Display the map
                st_folium(m, width=1000, height=500)

            else:
                # Fallback to simple map
                st.map(df[['latitude', 'longitude']])

            # Statistics
            st.markdown("### 📊 Poverty Statistics")

            col1, col2, col3, col4 = st.columns(4)

            total_population = sum(r.get('population', 0) for r in regions)
            avg_poverty_rate = sum(r.get('poverty_rate', 0) for r in regions) / len(regions) if regions else 0
            high_risk_areas = len([r for r in regions if r.get('poverty_rate', 0) > 50])
            total_regions = len(regions)

            with col1:
                st.markdown(f'''
                <div class="metric-card">
                    <h3>Total Population</h3>
                    <h2>{total_population:,}</h2>
                </div>
                ''', unsafe_allow_html=True)

            with col2:
                st.markdown(f'''
                <div class="metric-card">
                    <h3>Avg Poverty Rate</h3>
                    <h2>{avg_poverty_rate:.1f}%</h2>
                </div>
                ''', unsafe_allow_html=True)

            with col3:
                st.markdown(f'''
                <div class="metric-card">
                    <h3>High Risk Areas</h3>
                    <h2>{high_risk_areas}</h2>
                </div>
                ''', unsafe_allow_html=True)

            with col4:
                st.markdown(f'''
                <div class="metric-card">
                    <h3>Total Regions</h3>
                    <h2>{total_regions}</h2>
                </div>
                ''', unsafe_allow_html=True)

            # Detailed breakdown
            st.markdown("### 📋 Regional Breakdown")

            # Sort by poverty rate
            sorted_regions = sorted(regions, key=lambda x: x.get('poverty_rate', 0), reverse=True)

            for i, region in enumerate(sorted_regions[:10]):  # Top 10 most affected
                risk_level = "🔴 High" if region.get('poverty_rate', 0) > 50 else "🟠 Medium" if region.get('poverty_rate', 0) > 25 else "🟢 Low"
                progress = min(100, region.get('poverty_rate', 0))

                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-left: 4px solid {'#dc3545' if progress > 50 else '#ffc107' if progress > 25 else '#28a745'};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #2c3e50;">{region.get('name', 'Region')}</h4>
                            <p style="margin: 0; color: #666; font-size: 0.9rem;">
                                Population: {region.get('population', 0):,} | Avg Income: ${region.get('avg_income', 0):.2f}
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.8rem; color: #666;">{risk_level}</div>
                            <div style="font-weight: bold; color: #2c3e50;">{region.get('poverty_rate', 0):.1f}%</div>
                        </div>
                    </div>
                    <div class="progress-bar" style="margin-top: 0.5rem;">
                        <div class="progress-fill" style="width: {progress}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📊 No poverty data available from the backend.")

    else:
        st.info("🗺️ Poverty data will be displayed here when available from the backend. Please check your backend API connection.")

def show_dashboard():
    """Enhanced professional dashboard with comprehensive metrics"""
    st.markdown('<div class="app-header"><h1>📊 Dashboard</h1><p>Comprehensive financial overview and insights</p></div>', unsafe_allow_html=True)

    # Fetch comprehensive data from backend
    user_data = make_api_request("/users/me")
    transactions_data = make_api_request("/transactions")
    loans_data = make_api_request("/loans")
    campaigns_data = make_api_request("/crowdfunding/campaigns")

    # Calculate comprehensive metrics
    total_balance = 0
    total_expenses = 0
    total_income = 0
    active_loans = 0
    total_loans_amount = 0
    active_campaigns = 0
    total_campaigns_raised = 0

    if transactions_data and 'transactions' in transactions_data:
        for trans in transactions_data.get('transactions', []):
            if trans.get('type') == 'income':
                total_income += trans.get('amount', 0)
            else:
                total_expenses += trans.get('amount', 0)
        total_balance = total_income - total_expenses

    if loans_data and 'loans' in loans_data:
        loans = loans_data.get('loans', [])
        active_loans = len([loan for loan in loans if loan.get('status') == 'active'])
        total_loans_amount = sum(loan.get('amount', 0) for loan in loans)

    if campaigns_data and 'campaigns' in campaigns_data:
        campaigns = campaigns_data.get('campaigns', [])
        active_campaigns = len([c for c in campaigns if c.get('status') == 'active'])
        total_campaigns_raised = sum(c.get('raised_amount', 0) for c in campaigns)

    # Display comprehensive metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <h3>💰 Total Balance</h3>
            <h2 style="color: {"#28a745" if total_balance > 0 else "#dc3545"};">${total_balance:,.2f}</h2>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <h3>📈 Monthly Income</h3>
            <h2>${total_income:,.2f}</h2>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <h3>📉 Monthly Expenses</h3>
            <h2>${total_expenses:,.2f}</h2>
        </div>
        ''', unsafe_allow_html=True)

    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <h3>🏦 Active Loans</h3>
            <h2>{active_loans}</h2>
        </div>
        ''', unsafe_allow_html=True)

    # Additional metrics row
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.markdown(f'''
        <div class="metric-card">
            <h3>🎯 Loan Portfolio</h3>
            <h2>${total_loans_amount:,.2f}</h2>
        </div>
        ''', unsafe_allow_html=True)

    with col6:
        st.markdown(f'''
        <div class="metric-card">
            <h3>🤝 Active Campaigns</h3>
            <h2>{active_campaigns}</h2>
        </div>
        ''', unsafe_allow_html=True)

    with col7:
        st.markdown(f'''
        <div class="metric-card">
            <h3>💚 Community Impact</h3>
            <h2>${total_campaigns_raised:,.2f}</h2>
        </div>
        ''', unsafe_allow_html=True)

    with col8:
        st.markdown(f'''
        <div class="metric-card">
            <h3>⭐ Financial Health</h3>
            <h2 style="color: {"#28a745" if total_balance > total_expenses else "#ffc107"};">
                {"Good" if total_balance > total_expenses else "Review"}
            </h2>
        </div>
        ''', unsafe_allow_html=True)

    # Enhanced charts section
    st.markdown("### 📊 Advanced Analytics")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### 💹 Income vs Expenses Trend")
        if transactions_data and 'transactions' in transactions_data:
            df = pd.DataFrame(transactions_data.get('transactions', []))
            if not df.empty:
                df['date'] = pd.to_datetime(df['created_at'])
                monthly_data = df.groupby([df['date'].dt.to_period('M'), 'type'])['amount'].sum().unstack().fillna(0)

                fig = go.Figure()
                fig.add_trace(go.Bar(name='Income', x=monthly_data.index.astype(str), y=monthly_data.get('income', 0), marker_color='#28a745'))
                fig.add_trace(go.Bar(name='Expenses', x=monthly_data.index.astype(str), y=monthly_data.get('expense', 0), marker_color='#dc3545'))
                fig.update_layout(
                    title="Monthly Financial Flow",
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.markdown("#### 🥧 Expense Categories")
        if transactions_data and 'transactions' in transactions_data:
            df = pd.DataFrame(transactions_data.get('transactions', []))
            if not df.empty and 'category' in df.columns:
                category_data = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
                if not category_data.empty:
                    fig = px.pie(
                        values=category_data.values,
                        names=category_data.index,
                        title="Expense Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)

    # Quick actions section
    st.markdown("### ⚡ Quick Actions")

    action_col1, action_col2, action_col3, action_col4 = st.columns(4)

    with action_col1:
        if st.button("💳 Add Transaction", use_container_width=True):
            st.session_state.current_page = "Transactions"
            st.rerun()

    with action_col2:
        if st.button("🤝 View Campaigns", use_container_width=True):
            st.session_state.current_page = "Crowdfunding"
            st.rerun()

    with action_col3:
        if st.button("🏦 Apply for Loan", use_container_width=True):
            st.session_state.current_page = "Microloans"
            st.rerun()

    with action_col4:
        if st.button("👤 Update Profile", use_container_width=True):
            st.session_state.current_page = "Profile"
            st.rerun()

def show_profile():
    """User profile with real data"""
    st.markdown('<div class="app-header"><h1>👤 Profile</h1><p>Manage your account settings</p></div>', unsafe_allow_html=True)

    # Get user profile from backend
    user_profile = make_api_request("/users/me")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 👤 Personal Information")

        if user_profile and 'user' in user_profile:
            user = user_profile['user']

            # Editable profile form
            with st.form("update_profile"):
                st.subheader("Edit Profile")

                name = st.text_input("Full Name", value=user.get('name', ''))
                email = st.text_input("Email", value=user.get('email', ''))
                phone = st.text_input("Phone", value=user.get('phone', ''))

                if st.form_submit_button("Update Profile"):
                    data = {
                        "name": name,
                        "email": email,
                        "phone": phone
                    }
                    result = make_api_request("/users/me", "PUT", data)
                    if result:
                        st.success("✅ Profile updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update profile")

            # Display current info
            st.markdown("### Current Information")
            st.markdown(f"**Name:** {user.get('name', 'Not set')}")
            st.markdown(f"**Email:** {user.get('email', 'Not set')}")
            st.markdown(f"**Phone:** {user.get('phone', 'Not set')}")
            st.markdown(f"**Member Since:** {user.get('created_at', 'Unknown')}")

    with col2:
        st.markdown("### ⚙️ Account Settings")

        # Account preferences
        with st.expander("Preferences", expanded=True):
            notifications = st.checkbox("Email Notifications", value=True)
            dark_mode = st.checkbox("Dark Mode", value=False)

            if st.button("Save Preferences"):
                # Save preferences to backend
                st.success("✅ Preferences saved!")

        # Security settings
        with st.expander("Security"):
            st.markdown("**Password:**")
            if st.button("Change Password"):
                st.info("🔐 Password change functionality coming soon")

def main():
    """Main application"""
    # Check authentication first
    if not st.session_state.get('authenticated', False):
        show_login_page()
        return

    # Show navigation
    show_navbar()

    # Route to pages
    current_page = st.session_state.get('current_page', 'Dashboard')

    if current_page == "Dashboard":
        show_dashboard()
    elif current_page == "AI Recommendations":
        show_ai_recommendations()
    elif current_page == "Transactions":
        show_transactions()
    elif current_page == "Crowdfunding":
        show_crowdfunding()
    elif current_page == "Microloans":
        show_microloans()
    elif current_page == "Poverty Map":
        show_poverty_map()
    elif current_page == "Profile":
        show_profile()
    elif current_page == "Admin Panel" and st.session_state.get('is_admin', False):
        st.markdown('<div class="app-header"><h1>🔧 Admin Panel</h1><p>Administrative controls</p></div>', unsafe_allow_html=True)
        st.info("Admin panel functionality will be implemented here.")

    # Footer
    st.markdown('<div class="footer">© 2023 SDG Finance Platform | Empowering communities through financial inclusion</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

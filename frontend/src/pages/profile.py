from datetime import datetime, timedelta
import random

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import get_auth_headers, API_BASE_URL

def get_user_profile():
    """Fetch user profile data from the backend."""
    # In a real app, this would call your backend API with authentication
    # For now, we'll return mock data
    
    # Get user data from session state
    if 'current_user' in st.session_state and st.session_state.current_user:
        email = st.session_state.current_user.get('email', 'user@example.com')
        username = email.split('@')[0]
    else:
        email = "user@example.com"
        username = "demo_user"
    
    return {
        "id": 1,
        "email": email,
        "username": username,
        "full_name": "John Doe",
        "phone": "+255 712 345 678",
        "address": "123 Main St, Dar es Salaam, Tanzania",
        "date_of_birth": "1985-06-15",
        "gender": "Male",
        "occupation": "Small Business Owner",
        "monthly_income": 1500.00,
        "profile_picture": "https://randomuser.me/api/portraits/men/32.jpg",
        "account_created": "2022-01-15T10:30:00Z",
        "last_login": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "account_status": "Active",
        "verification_status": "Verified",
        "preferences": {
            "language": "English",
            "currency": "USD",
            "theme": "Light",
            "notifications": {
                "email": True,
                "sms": True,
                "push": True
            },
            "privacy": {
                "show_balance": True,
                "show_profile": "Friends Only",
                "activity_feed": True
            }
        },
        "stats": {
            "total_savings": 3250.75,
            "total_loans": 5000.00,
            "loans_repaid": 2,
            "active_loans": 1,
            "credit_score": 725,
            "community_impact": {
                "families_helped": 5,
                "jobs_created": 3,
                "projects_supported": 7
            }
        },
        "documents": [
            {"id": 1, "name": "National ID", "type": "ID", "upload_date": "2022-01-20", "status": "Verified"},
            {"id": 2, "name": "Proof of Address", "type": "Utility Bill", "upload_date": "2022-01-21", "status": "Verified"},
            {"id": 3, "name": "Tax Certificate", "type": "Tax", "upload_date": "2022-06-15", "status": "Pending"}
        ],
        "linked_accounts": [
            {"id": 1, "bank_name": "CRDB Bank", "account_type": "Savings", "last_four": "7890", "linked_date": "2022-02-10"},
            {"id": 2, "bank_name": "M-Pesa", "account_type": "Mobile Money", "last_four": "4321", "linked_date": "2022-01-25"}
        ]
    }

def get_transaction_history():
    """Fetch user's transaction history."""
    # In a real app, this would call your backend API
    # For now, we'll generate mock data
    
    categories = ["Food & Dining", "Shopping", "Transportation", "Bills & Utilities", 
                 "Housing", "Entertainment", "Healthcare", "Education", "Income", "Transfer"]
    
    transactions = []
    for i in range(30):
        is_income = random.random() > 0.7
        amount = round(random.uniform(5, 500), 2) * (-1 if not is_income else 1)
        category = random.choice(categories)
        
        transactions.append({
            "id": i + 1,
            "date": (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
            "description": f"{category} Purchase" if not is_income else f"{category} Income",
            "category": category,
            "amount": amount,
            "status": random.choice(["Completed", "Completed", "Completed", "Pending"]),
            "type": "Credit" if amount > 0 else "Debit"
        })
    
    # Sort by date descending
    return sorted(transactions, key=lambda x: x["date"], reverse=True)

def get_savings_goals():
    """Fetch user's savings goals."""
    return [
        {
            "id": 1,
            "name": "Emergency Fund",
            "target_amount": 5000.00,
            "current_amount": 3250.75,
            "target_date": "2023-12-31",
            "status": "In Progress",
            "monthly_contribution": 500.00,
            "category": "Emergency"
        },
        {
            "id": 2,
            "name": "New Laptop",
            "target_amount": 1200.00,
            "current_amount": 450.00,
            "target_date": "2023-08-15",
            "status": "In Progress",
            "monthly_contribution": 150.00,
            "category": "Electronics"
        },
        {
            "id": 3,
            "name": "Vacation",
            "target_amount": 3000.00,
            "current_amount": 0.00,
            "target_date": "2024-06-01",
            "status": "Not Started",
            "monthly_contribution": 250.00,
            "category": "Travel"
        }
    ]

def show():
    """Show the profile page."""
    # Check if user is authenticated
    if 'current_user' not in st.session_state or not st.session_state.current_user:
        st.warning("Please log in to view your profile.")
        return
    
    # Load user data
    user = get_user_profile()
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Personal Info", "Security", "Preferences"])
    
    with tab1:  # Overview tab
        st.header("Profile Overview")
        
        # Profile header with avatar and basic info
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(user["profile_picture"], width=150)
            st.markdown(f"**Account Status:** {user['account_status']}")
            st.markdown(f"**Member Since:** {user['account_created'][:10]}")
            st.markdown(f"**Last Login:** {user['last_login'].replace('T', ' ')[:16]} UTC")
        
        with col2:
            st.markdown(f"# {user.get('full_name', user['username'])}")
            st.markdown(f"**{user['occupation']}**")
            
            # Contact info
            st.markdown("### Contact Information")
            st.markdown(f"📧 {user['email']}")
            st.markdown(f"📱 {user['phone']}")
            st.markdown(f"🏠 {user['address']}")
            
            # Quick stats
            st.markdown("### Quick Stats")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Savings", f"${user['stats']['total_savings']:,.2f}")
            
            with col2:
                st.metric("Active Loans", f"{user['stats']['active_loans']}")
            
            with col3:
                st.metric("Credit Score", user['stats']['credit_score'])
        
        # Financial Overview
        st.markdown("---")
        st.subheader("Financial Overview")
        
        # Savings Goals
        st.markdown("### Savings Goals")
        goals = get_savings_goals()
        
        for goal in goals:
            progress = (goal["current_amount"] / goal["target_amount"]) * 100
            days_remaining = (datetime.strptime(goal["target_date"], "%Y-%m-%d") - datetime.now()).days
            
            st.markdown(f"**{goal['name']}** - ${goal['current_amount']:,.2f} of ${goal['target_amount']:,.2f}")
            st.progress(int(progress))
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Progress:** {progress:.1f}%")
            
            with col2:
                st.markdown(f"**Monthly:** ${goal['monthly_contribution']:,.2f}")
            
            with col3:
                st.markdown(f"**Due:** {goal['target_date']} ({days_remaining} days)")
            
            st.markdown("---")
        
        # Recent Transactions
        st.subheader("Recent Transactions")
        transactions = get_transaction_history()[:10]  # Get last 10 transactions
        
        if transactions:
            for txn in transactions:
                amount_color = "green" if txn["amount"] > 0 else "red"
                st.markdown(
                    f"""
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 0.75rem;
                        border-radius: 8px;
                        background: #f9fafb;
                        margin-bottom: 0.5rem;
                    ">
                        <div>
                            <div style="font-weight: 500;">{txn['description']}</div>
                            <div style="font-size: 0.8rem; color: #6b7280;">
                                {txn['date']} • {txn['category']} • {txn['status']}
                            </div>
                        </div>
                        <div style="font-weight: 600; color: {amount_color};">
                            {'+' if txn['amount'] > 0 else ''}{txn['amount']:,.2f}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No recent transactions found.")
        
        # Community Impact
        st.markdown("---")
        st.subheader("Community Impact")
        
        if user['stats']['community_impact']:
            impact = user['stats']['community_impact']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Families Helped", impact["families_helped"])
            
            with col2:
                st.metric("Jobs Created", impact["jobs_created"])
            
            with col3:
                st.metric("Projects Supported", impact["projects_supported"])
            
            # Add a simple chart for visualization
            impact_data = pd.DataFrame({
                'Category': ['Families Helped', 'Jobs Created', 'Projects Supported'],
                'Count': [impact["families_helped"], impact["jobs_created"], impact["projects_supported"]]
            })
            
            fig = px.bar(
                impact_data, 
                x='Category', 
                y='Count',
                color='Category',
                title="Your Community Impact"
            )
            
            fig.update_layout(
                showlegend=False,
                xaxis_title="",
                yaxis_title="Count",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:  # Personal Info tab
        st.header("Personal Information")
        
        with st.form("personal_info"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name", value=user["full_name"].split()[0])
                email = st.text_input("Email Address", value=user["email"])
                date_of_birth = st.date_input("Date of Birth", value=datetime.strptime(user["date_of_birth"], "%Y-%m-%d").date())
            
            with col2:
                last_name = st.text_input("Last Name", value=user["full_name"].split()[-1] if len(user["full_name"].split()) > 1 else "")
                phone = st.text_input("Phone Number", value=user["phone"])
                gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"], 
                                   index=["Male", "Female", "Other", "Prefer not to say"].index(user["gender"]))
            
            address = st.text_area("Address", value=user["address"])
            occupation = st.text_input("Occupation", value=user["occupation"])
            monthly_income = st.number_input("Monthly Income (USD)", min_value=0.0, value=float(user["monthly_income"]), step=100.0)
            
            # Profile picture upload
            new_profile_pic = st.file_uploader("Update Profile Picture", type=["jpg", "jpeg", "png"])
            
            if st.form_submit_button("Save Changes"):
                # In a real app, this would update the user's profile in the backend
                st.success("Profile updated successfully!")
                
                # Update the profile picture if a new one was uploaded
                if new_profile_pic is not None:
                    st.session_state.profile_picture = new_profile_pic
                    st.rerun()
        
        # Documents section
        st.markdown("---")
        st.subheader("Identity Documents")
        
        documents = user.get("documents", [])
        
        if documents:
            for doc in documents:
                status_color = "green" if doc["status"] == "Verified" else "orange"
                
                st.markdown(
                    f"""
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 1rem;
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                        margin-bottom: 0.5rem;
                    ">
                        <div>
                            <div style="font-weight: 500;">{doc['name']}</div>
                            <div style="font-size: 0.8rem; color: #6b7280;">
                                {doc['type']} • Uploaded on {doc['upload_date']}
                            </div>
                        </div>
                        <div>
                            <span style="
                                background: {'#ecfdf5' if doc['status'] == 'Verified' else '#fffbeb'};
                                color: {'#065f46' if doc['status'] == 'Verified' else '#92400e'};
                                padding: 0.25rem 0.75rem;
                                border-radius: 1rem;
                                font-size: 0.8rem;
                                font-weight: 500;
                            ">
                                {doc['status']}
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No documents uploaded yet.")
        
        # Add document button
        if st.button("+ Add Document"):
            st.session_state.show_document_upload = True
        
        if st.session_state.get("show_document_upload", False):
            with st.form("document_upload"):
                st.subheader("Upload New Document")
                
                doc_type = st.selectbox(
                    "Document Type",
                    ["National ID", "Passport", "Driver's License", "Utility Bill", "Bank Statement", "Other"]
                )
                
                doc_file = st.file_uploader("Upload Document", type=["jpg", "jpeg", "png", "pdf"])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Upload"):
                        if doc_file is not None:
                            # In a real app, this would upload the file to a server
                            st.success("Document uploaded successfully!")
                            st.session_state.show_document_upload = False
                            st.rerun()
                        else:
                            st.error("Please select a file to upload.")
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_document_upload = False
                        st.rerun()
        
        # Linked Accounts section
        st.markdown("---")
        st.subheader("Linked Bank Accounts")
        
        linked_accounts = user.get("linked_accounts", [])
        
        if linked_accounts:
            for account in linked_accounts:
                st.markdown(
                    f"""
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 1rem;
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                        margin-bottom: 0.5rem;
                    ">
                        <div>
                            <div style="font-weight: 500;">{account['bank_name']}</div>
                            <div style="font-size: 0.8rem; color: #6b7280;">
                                {account['account_type']} • • • • {account['last_four']}
                            </div>
                        </div>
                        <div style="font-size: 0.8rem; color: #6b7280;">
                            Linked on {account['linked_date']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No bank accounts linked yet.")
        
        # Add bank account button
        if st.button("+ Link Bank Account"):
            st.session_state.show_bank_linking = True
        
        if st.session_state.get("show_bank_linking", False):
            with st.form("link_bank"):
                st.subheader("Link New Bank Account")
                
                bank_name = st.selectbox(
                    "Select Bank",
                    ["CRDB Bank", "NMB Bank", "Standard Chartered", "Equity Bank", "Other"]
                )
                
                account_type = st.selectbox(
                    "Account Type",
                    ["Savings", "Current", "Fixed Deposit"]
                )
                
                account_number = st.text_input("Account Number")
                account_name = st.text_input("Account Holder's Name")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Link Account"):
                        # In a real app, this would connect to the bank's API
                        if account_number and account_name:
                            st.success("Bank account linked successfully!")
                            st.session_state.show_bank_linking = False
                            st.rerun()
                        else:
                            st.error("Please fill in all required fields.")
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_bank_linking = False
                        st.rerun()
    
    with tab3:  # Security tab
        st.header("Security Settings")
        
        # Change Password
        st.subheader("Change Password")
        
        with st.form("change_password"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if not current_password or not new_password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("New passwords do not match.")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters long.")
                else:
                    # In a real app, this would update the password in the backend
                    st.success("Password updated successfully!")
        
        # Two-Factor Authentication
        st.markdown("---")
        st.subheader("Two-Factor Authentication")
        
        two_fa_enabled = st.toggle("Enable Two-Factor Authentication", value=True)
        
        if two_fa_enabled:
            st.success("Two-factor authentication is enabled.")
            st.info("You'll be asked to enter a verification code when logging in from a new device.")
            
            # Show backup codes (in a real app, these would be generated securely)
            if st.button("View Backup Codes"):
                backup_codes = [str(random.randint(100000, 999999)) for _ in range(10)]
                st.warning("Save these backup codes in a secure place. Each code can only be used once.")
                
                # Display codes in a grid
                cols = st.columns(2)
                for i, code in enumerate(backup_codes):
                    with cols[i % 2]:
                        st.code(f"{i+1}. {code}", language="text")
                
                if st.download_button(
                    label="Download Backup Codes",
                    data="\n".join([f"{i+1}. {code}" for i, code in enumerate(backup_codes)]),
                    file_name="backup_codes.txt",
                    mime="text/plain"
                ):
                    st.success("Backup codes downloaded successfully!")
        else:
            st.warning("Two-factor authentication is disabled. Your account is less secure.")
        
        # Active Sessions
        st.markdown("---")
        st.subheader("Active Sessions")
        
        # In a real app, this would show all active login sessions
        sessions = [
            {
                "device": "Chrome on Windows 10",
                "location": "Dar es Salaam, Tanzania",
                "ip": "192.168.1.1",
                "last_active": "5 minutes ago",
                "current": True
            },
            {
                "device": "Safari on iPhone",
                "location": "Nairobi, Kenya",
                "ip": "154.123.45.67",
                "last_active": "2 days ago",
                "current": False
            },
            {
                "device": "Firefox on Linux",
                "location": "Kampala, Uganda",
                "ip": "41.210.123.45",
                "last_active": "1 week ago",
                "current": False
            }
        ]
        
        for session in sessions:
            st.markdown(
                f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                    background: {'#f0f9ff' if session['current'] else 'white'};
                ">
                    <div>
                        <div style="font-weight: 500;">
                            {session['device']} {session['current'] and '(This Device)' or ''}
                        </div>
                        <div style="font-size: 0.8rem; color: #6b7280;">
                            {session['location']} • {session['ip']} • Last active {session['last_active']}
                        </div>
                    </div>
                    <button style="
                        background: none;
                        border: 1px solid #ef4444;
                        color: #ef4444;
                        padding: 0.25rem 0.75rem;
                        border-radius: 0.375rem;
                        cursor: pointer;
                        font-size: 0.875rem;
                        {'' if not session['current'] else 'display: none;'}
                    " onclick="alert('This would sign out the session in a real app.')">
                        Sign Out
                    </button>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Account Deletion
        st.markdown("---")
        st.subheader("Danger Zone")
        
        if st.button("Delete My Account", type="primary"):
            st.session_state.show_delete_confirmation = True
        
        if st.session_state.get("show_delete_confirmation", False):
            st.warning("Are you sure you want to delete your account? This action cannot be undone.")
            st.markdown("**All your data will be permanently deleted, including:**")
            st.markdown("- Personal information")
            st.markdown("- Transaction history")
            st.markdown("- Linked bank accounts")
            st.markdown("- Savings goals")
            
            confirm_text = st.text_input("Type 'DELETE' to confirm")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Permanently Delete Account", disabled=confirm_text != "DELETE", type="primary"):
                    # In a real app, this would delete the user's account
                    st.session_state.authenticated = False
                    st.session_state.current_user = None
                    st.success("Your account has been deleted successfully.")
                    st.rerun()
            
            with col2:
                if st.button("Cancel"):
                    st.session_state.show_delete_confirmation = False
                    st.rerun()
    
    with tab4:  # Preferences tab
        st.header("Account Preferences")
        
        # Notification Preferences
        st.subheader("Notification Preferences")
        
        with st.form("notification_preferences"):
            st.markdown("**Email Notifications**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                email_transactions = st.checkbox("Transaction alerts", value=user["preferences"]["notifications"]["email"])
                email_newsletter = st.checkbox("Newsletter", value=True)
                email_security = st.checkbox("Security alerts", value=True)
            
            with col2:
                email_offers = st.checkbox("Special offers", value=True)
                email_updates = st.checkbox("Product updates", value=True)
            
            st.markdown("**Push Notifications**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                push_transactions = st.checkbox("Transaction alerts", value=user["preferences"]["notifications"]["push"])
            
            with col2:
                push_security = st.checkbox("Security alerts", value=True)
            
            if st.form_submit_button("Save Preferences"):
                # In a real app, this would update the user's preferences in the backend
                st.success("Notification preferences updated successfully!")
        
        # Display Preferences
        st.markdown("---")
        st.subheader("Display Preferences")
        
        with st.form("display_preferences"):
            col1, col2 = st.columns(2)
            
            with col1:
                language = st.selectbox(
                    "Language",
                    ["English", "Swahili", "French", "Spanish"],
                    index=["English", "Swahili", "French", "Spanish"].index(user["preferences"]["language"])
                )
                
                theme = st.selectbox(
                    "Theme",
                    ["Light", "Dark", "System Default"],
                    index=["Light", "Dark", "System Default"].index(user["preferences"]["theme"])
                )
            
            with col2:
                currency = st.selectbox(
                    "Currency",
                    ["USD - US Dollar", "TZS - Tanzanian Shilling", "KES - Kenyan Shilling", "UGX - Ugandan Shilling"],
                    index={"USD": 0, "TZS": 1, "KES": 2, "UGX": 3}.get(user["preferences"]["currency"], 0)
                )
                
                date_format = st.selectbox(
                    "Date Format",
                    ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"],
                    index=0
                )
            
            if st.form_submit_button("Save Display Settings"):
                # In a real app, this would update the user's display preferences
                st.success("Display preferences updated successfully!")
        
        # Privacy Settings
        st.markdown("---")
        st.subheader("Privacy Settings")
        
        with st.form("privacy_settings"):
            st.markdown("**Profile Visibility**")
            
            profile_visibility = st.radio(
                "Who can see your profile?",
                ["Public", "Friends Only", "Private"],
                index=["Public", "Friends Only", "Private"].index(user["preferences"]["privacy"]["show_profile"]),
                horizontal=True
            )
            
            st.markdown("**Activity Feed**")
            
            show_balance = st.checkbox(
                "Show account balance in dashboard",
                value=user["preferences"]["privacy"]["show_balance"]
            )
            
            show_activity = st.checkbox(
                "Show my activity in public feeds",
                value=user["preferences"]["privacy"]["activity_feed"]
            )
            
            st.markdown("**Data Sharing**")
            
            share_analytics = st.checkbox(
                "Share anonymous usage data to help improve our services",
                value=True
            )
            
            if st.form_submit_button("Save Privacy Settings"):
                # In a real app, this would update the user's privacy settings
                st.success("Privacy settings updated successfully!")
        
        # Export Data
        st.markdown("---")
        st.subheader("Data Export")
        
        st.markdown("Download a copy of your personal data.")
        
        if st.button("Request Data Export"):
            # In a real app, this would generate a data export
            st.success("Your data export has been queued. You'll receive an email with a download link when it's ready.")
    
    # Add custom styles
    st.markdown("""
        <style>
            /* Style the tab buttons */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: nowrap;
                padding: 0 16px;
                background-color: #f1f5f9;
                border-radius: 8px 8px 0 0;
                margin-right: 0 !important;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: #3b82f6;
                color: white;
            }
            
            /* Style form elements */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stNumberInput > div > div > input,
            .stSelectbox > div > div > div {
                border-radius: 8px;
                padding: 0.5rem 0.75rem;
                border: 1px solid #e2e8f0;
            }
            
            .stButton > button {
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: 500;
                transition: all 0.2s;
            }
            
            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            
            /* Style the file uploader */
            .stFileUploader > div > div > button {
                width: 100%;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                border: 1px dashed #94a3b8;
                background: #f8fafc;
                color: #64748b;
                transition: all 0.2s;
            }
            
            .stFileUploader > div > div > button:hover {
                border-color: #3b82f6;
                color: #3b82f6;
                background: #eff6ff;
            }
            
            /* Style the toggle */
            .stCheckbox > div > label {
                margin: 0;
                padding: 0.5rem 0;
            }
            
            /* Style the radio buttons */
            .stRadio > div > label {
                margin: 0;
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                background: #f1f5f9;
                transition: all 0.2s;
                width: 100%;
                text-align: center;
            }
            
            .stRadio > div > label:hover {
                background: #e2e8f0;
            }
            
            .stRadio > div > div[data-baseweb="radio"] {
                margin-right: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)

from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import get_auth_headers, format_currency, format_date, API_BASE_URL

def get_loans():
    """Fetch microloans data from the backend."""
    # In a real app, this would call your backend API
    # For now, we'll use mock data
    loans = [
        {
            "id": 1,
            "borrower": "Jane Mwende",
            "purpose": "Expand small grocery business",
            "amount": 1500,
            "term_months": 12,
            "interest_rate": 8.5,
            "status": "Active",
            "amount_paid": 875,
            "next_payment_date": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
            "next_payment_amount": 125.50,
            "start_date": (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
            "category": "Business"
        },
        {
            "id": 2,
            "borrower": "James Omondi",
            "purpose": "Purchase farming equipment",
            "amount": 3000,
            "term_months": 24,
            "interest_rate": 7.5,
            "status": "Active",
            "amount_paid": 1200,
            "next_payment_date": (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d'),
            "next_payment_amount": 150.00,
            "start_date": (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d'),
            "category": "Agriculture"
        },
        {
            "id": 3,
            "borrower": "Sarah Johnson",
            "purpose": "School fees for children",
            "amount": 2000,
            "term_months": 18,
            "interest_rate": 6.0,
            "status": "Repaid",
            "amount_paid": 2000,
            "next_payment_date": None,
            "next_payment_amount": 0,
            "start_date": (datetime.now() - timedelta(days=540)).strftime('%Y-%m-%d'),
            "end_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "category": "Education"
        },
        {
            "id": 4,
            "borrower": "David Kimani",
            "purpose": "Medical expenses",
            "amount": 2500,
            "term_months": 12,
            "interest_rate": 5.5,
            "status": "Active",
            "amount_paid": 1750,
            "next_payment_date": (datetime.now() + timedelta(days=22)).strftime('%Y-%m-%d'),
            "next_payment_amount": 250.00,
            "start_date": (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
            "category": "Healthcare"
        },
        {
            "id": 5,
            "borrower": "Grace Auma",
            "purpose": "Purchase inventory for clothing shop",
            "amount": 4000,
            "term_months": 24,
            "interest_rate": 9.0,
            "status": "Active",
            "amount_paid": 1500,
            "next_payment_date": (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            "next_payment_amount": 200.00,
            "start_date": (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
            "category": "Business"
        }
    ]
    
    # Add some calculated fields
    for loan in loans:
        loan['amount_remaining'] = loan['amount'] - loan['amount_paid']
        loan['progress'] = (loan['amount_paid'] / loan['amount']) * 100
        loan['monthly_payment'] = loan['amount'] / loan['term_months']
        loan['total_interest'] = (loan['amount'] * (loan['interest_rate'] / 100) * (loan['term_months'] / 12))
        loan['total_repayment'] = loan['amount'] + loan['total_interest']
        
        if loan['status'] == 'Repaid':
            loan['months_remaining'] = 0
        else:
            months_paid = int(loan['amount_paid'] / loan['monthly_payment'])
            loan['months_remaining'] = loan['term_months'] - months_paid
    
    return loans

def get_available_loans():
    """Get available loans for investment."""
    return [
        {
            "id": 101,
            "borrower": "Farmers Collective",
            "purpose": "Purchase seeds and fertilizers for the planting season",
            "amount": 5000,
            "term_months": 18,
            "interest_rate": 9.5,
            "funded_percent": 65,
            "category": "Agriculture",
            "location": "Nakuru, Kenya",
            "risk_rating": "B+",
            "lenders": 24,
            "days_left": 15
        },
        {
            "id": 102,
            "borrower": "Women's Textile Co-op",
            "purpose": "Purchase new sewing machines and materials",
            "amount": 7500,
            "term_months": 24,
            "interest_rate": 11.0,
            "funded_percent": 32,
            "category": "Business",
            "location": "Kampala, Uganda",
            "risk_rating": "A-",
            "lenders": 18,
            "days_left": 22
        },
        {
            "id": 103,
            "borrower": "EduCare School",
            "purpose": "Construct new classrooms for primary school students",
            "amount": 15000,
            "term_months": 36,
            "interest_rate": 7.5,
            "funded_percent": 45,
            "category": "Education",
            "location": "Arusha, Tanzania",
            "risk_rating": "A",
            "lenders": 42,
            "days_left": 8
        },
        {
            "id": 104,
            "borrower": "Green Energy Solutions",
            "purpose": "Install solar panels for rural households",
            "amount": 10000,
            "term_months": 24,
            "interest_rate": 8.0,
            "funded_percent": 78,
            "category": "Energy",
            "location": "Kigali, Rwanda",
            "risk_rating": "A+",
            "lenders": 56,
            "days_left": 5
        },
        {
            "id": 105,
            "borrower": "Fresh Harvest Fisheries",
            "purpose": "Expand fish farming operations with new ponds",
            "amount": 8000,
            "term_months": 18,
            "interest_rate": 10.5,
            "funded_percent": 22,
            "category": "Aquaculture",
            "location": "Mwanza, Tanzania",
            "risk_rating": "B",
            "lenders": 12,
            "days_left": 30
        }
    ]

def show():
    """Show the microloans page."""
    st.title("Microloans")
    
    # Add tabs for different sections
    tab1, tab2, tab3 = st.tabs(["My Loans", "Apply for Loan", "Invest"])
    
    with tab1:
        st.subheader("My Loan Portfolio")
        
        # Summary cards
        loans = get_loans()
        active_loans = [loan for loan in loans if loan['status'] == 'Active']
        total_borrowed = sum(loan['amount'] for loan in loans)
        total_repaid = sum(loan['amount_paid'] for loan in loans)
        total_remaining = sum(loan['amount_remaining'] for loan in loans if loan['status'] == 'Active')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Loans", f"${total_borrowed:,.2f}")
        
        with col2:
            st.metric("Amount Repaid", f"${total_repaid:,.2f}")
        
        with col3:
            st.metric("Remaining Balance", f"${total_remaining:,.2f}")
        
        with col4:
            st.metric("Active Loans", len(active_loans))
        
        # Active loans
        st.subheader("Active Loans")
        
        if not active_loans:
            st.info("You don't have any active loans.")
        else:
            for loan in active_loans:
                with st.expander(f"{loan['purpose']} - ${loan['amount']:,.2f}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Borrower", loan['borrower'])
                        st.metric("Loan Amount", f"${loan['amount']:,.2f}")
                        st.metric("Interest Rate", f"{loan['interest_rate']}%")
                    
                    with col2:
                        st.metric("Term", f"{loan['term_months']} months")
                        st.metric("Amount Paid", f"${loan['amount_paid']:,.2f}")
                        st.metric("Amount Remaining", f"${loan['amount_remaining']:,.2f}")
                    
                    # Progress bar
                    st.markdown("**Repayment Progress**")
                    st.progress(min(100, int(loan['progress'])))
                    st.caption(f"{loan['progress']:.1f}% repaid ({loan['months_remaining']} months remaining)")
                    
                    # Next payment
                    if loan['next_payment_date']:
                        st.markdown(f"**Next Payment:** ${loan['next_payment_amount']:,.2f} due on {loan['next_payment_date']}")
                        
                        # Make payment button
                        if st.button(f"Make Payment - ${loan['next_payment_amount']:,.2f}", key=f"pay_{loan['id']}"):
                            st.success(f"Payment of ${loan['next_payment_amount']:,.2f} processed successfully!")
                            st.balloons()
                    
                    # View details button
                    if st.button("View Loan Details", key=f"details_{loan['id']}"):
                        st.session_state.view_loan_id = loan['id']
                        st.experimental_rerun()
        
        # Loan history
        st.subheader("Loan History")
        
        # Filter out active loans
        past_loans = [loan for loan in loans if loan['status'] == 'Repaid']
        
        if not past_loans:
            st.info("No past loans found.")
        else:
            # Create a DataFrame for display
            history_data = []
            for loan in past_loans:
                history_data.append({
                    "ID": loan['id'],
                    "Borrower": loan['borrower'],
                    "Purpose": loan['purpose'],
                    "Amount": f"${loan['amount']:,.2f}",
                    "Term": f"{loan['term_months']} months",
                    "Interest Rate": f"{loan['interest_rate']}%",
                    "Status": loan['status'],
                    "Start Date": loan['start_date'],
                    "End Date": loan.get('end_date', 'N/A')
                })
            
            st.dataframe(
                pd.DataFrame(history_data),
                use_container_width=True,
                hide_index=True
            )
    
    with tab2:
        st.subheader("Apply for a New Loan")
        st.markdown("Fill out the form below to apply for a microloan.")
        
        with st.form("loan_application"):
            # Personal Information
            st.markdown("### Personal Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name*")
                email = st.text_input("Email Address*")
                id_number = st.text_input("National ID/Passport*")
            
            with col2:
                last_name = st.text_input("Last Name*")
                phone = st.text_input("Phone Number*")
                date_of_birth = st.date_input("Date of Birth*", max_value=datetime.now() - timedelta(days=18*365))
            
            # Loan Details
            st.markdown("### Loan Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                loan_purpose = st.selectbox(
                    "Loan Purpose*",
                    ["Business Expansion", "Agriculture", "Education", "Healthcare", "Housing", "Other"]
                )
                
                loan_amount = st.number_input(
                    "Loan Amount (USD)*",
                    min_value=100,
                    max_value=10000,
                    step=100,
                    value=1000
                )
                
                loan_term = st.slider(
                    "Loan Term (months)*",
                    min_value=3,
                    max_value=36,
                    value=12,
                    step=1
                )
            
            with col2:
                business_type = st.selectbox(
                    "Type of Business/Activity*",
                    ["Retail", "Agriculture", "Services", "Manufacturing", "Other"]
                )
                
                monthly_income = st.number_input(
                    "Monthly Income (USD)*",
                    min_value=0,
                    step=50,
                    value=500
                )
                
                # Calculate estimated monthly payment
                interest_rate = 12.0  # Example interest rate
                monthly_interest_rate = interest_rate / 12 / 100
                if monthly_interest_rate > 0 and loan_term > 0:
                    monthly_payment = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term) / \
                                    ((1 + monthly_interest_rate) ** loan_term - 1)
                    st.metric("Estimated Monthly Payment", f"${monthly_payment:,.2f}")
            
            # Business/Project Details
            st.markdown("### Business/Project Details")
            
            business_name = st.text_input("Business/Project Name (if applicable)")
            business_description = st.text_area(
                "Describe your business/project and how you plan to use the loan*",
                height=150
            )
            
            # Collateral/Security
            st.markdown("### Collateral/Security")
            
            has_collateral = st.radio(
                "Do you have any collateral to secure this loan?*",
                ["Yes", "No"]
            )
            
            if has_collateral == "Yes":
                collateral_type = st.selectbox(
                    "Type of Collateral",
                    ["Land/Property", "Vehicle", "Equipment", "Other"]
                )
                collateral_value = st.number_input(
                    "Estimated Value of Collateral (USD)",
                    min_value=0,
                    step=100,
                    value=0
                )
            
            # Terms and Conditions
            st.markdown("### Terms and Conditions")
            
            terms_accepted = st.checkbox(
                "I agree to the Terms and Conditions and Privacy Policy*"
            )
            
            # Submit button
            submit_button = st.form_submit_button("Submit Application")
            
            if submit_button:
                # Basic validation
                required_fields = [
                    (first_name, "First Name"),
                    (last_name, "Last Name"),
                    (email, "Email Address"),
                    (phone, "Phone Number"),
                    (id_number, "National ID/Passport"),
                    (loan_purpose, "Loan Purpose"),
                    (business_description, "Business/Project Description")
                ]
                
                missing_fields = [field_name for field, field_name in required_fields if not field]
                
                if missing_fields:
                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
                elif not terms_accepted:
                    st.error("Please accept the Terms and Conditions")
                else:
                    # In a real app, this would submit to your backend
                    st.success("✅ Your loan application has been submitted successfully!")
                    st.balloons()
                    
                    # Show a summary
                    st.subheader("Application Summary")
                    st.write(f"**Name:** {first_name} {last_name}")
                    st.write(f"**Email:** {email}")
                    st.write(f"**Phone:** {phone}")
                    st.write(f"**Loan Amount:** ${loan_amount:,.2f}")
                    st.write(f"**Loan Term:** {loan_term} months")
                    st.write(f"**Purpose:** {loan_purpose}")
                    st.write("\nWe will review your application and contact you within 2-3 business days.")
    
    with tab3:
        st.subheader("Invest in Microloans")
        st.markdown("Browse available loans and help entrepreneurs in need while earning a return on your investment.")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_amount = st.number_input("Minimum Amount", min_value=25, max_value=10000, value=100, step=25)
        
        with col2:
            max_risk = st.select_slider(
                "Maximum Risk",
                options=["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-"],
                value="B"
            )
        
        with col3:
            min_interest = st.slider("Minimum Interest Rate", 5.0, 20.0, 7.5, 0.5)
        
        # Available loans
        st.markdown("### Available Loans")
        
        loans = get_available_loans()
        
        # Apply filters
        filtered_loans = [
            loan for loan in loans 
            if loan['amount'] >= min_amount and 
               loan['interest_rate'] >= min_interest and
               ord(loan['risk_rating'][0]) <= ord(max_risk[0]) and
               (len(loan['risk_rating']) == 1 or 
                (loan['risk_rating'][1] == '+' and max_risk[1] == '+') or
                (loan['risk_rating'][1] == '-' and max_risk[1] != '+'))
        ]
        
        if not filtered_loans:
            st.info("No loans match your criteria. Try adjusting your filters.")
        else:
            for loan in filtered_loans:
                with st.container():
                    st.markdown(f"""
                        <div style="
                            background: white;
                            border-radius: 10px;
                            padding: 1.5rem;
                            margin-bottom: 1.5rem;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                                <div>
                                    <h3 style="margin: 0 0 0.5rem 0;">{loan['purpose']}</h3>
                                    <div style="display: flex; gap: 1rem; color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                        <span>💼 {loan['borrower']}</span>
                                        <span>📍 {loan['location']}</span>
                                        <span>🏷️ {loan['category']}</span>
                                    </div>
                                </div>
                                <div style="
                                    background: #f0fdf4;
                                    color: #166534;
                                    padding: 0.25rem 0.75rem;
                                    border-radius: 1rem;
                                    font-weight: 600;
                                    font-size: 0.9rem;
                                    display: flex;
                                    align-items: center;
                                    gap: 0.5rem;
                                ">
                                    <span>Risk: {loan['risk_rating']}</span>
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 1.5rem;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9rem;">
                                    <span>Amount: <strong>${loan['amount']:,.2f}</strong></span>
                                    <span>Interest: <strong>{loan['interest_rate']}%</strong></span>
                                    <span>Term: <strong>{loan['term_months']} months</strong></span>
                                </div>
                                
                                <div style="height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; margin-bottom: 0.5rem;">
                                    <div style="width: {loan['funded_percent']}%; height: 100%; background: #3b82f6;"></div>
                                </div>
                                
                                <div style="display: flex; justify-content: space-between; color: #6b7280; font-size: 0.8rem;">
                                    <span>{loan['funded_percent']}% funded</span>
                                    <span>{loan['lenders']} lenders</span>
                                    <span>{loan['days_left']} days left</span>
                                </div>
                            </div>
                            
                            <div style="display: flex; gap: 1rem;">
                                <button style="
                                    flex: 1;
                                    background: #3b82f6;
                                    color: white;
                                    border: none;
                                    padding: 0.75rem 1.5rem;
                                    border-radius: 0.5rem;
                                    font-weight: 500;
                                    cursor: pointer;
                                    transition: background 0.2s;
                                " onmouseover="this.style.background='#2563eb'" onmouseout="this.style.background='#3b82f6'"
                                onclick="alert('This would open the investment form in a real app.')">
                                    Invest Now
                                </button>
                                
                                <button style="
                                    background: white;
                                    color: #3b82f6;
                                    border: 1px solid #3b82f6;
                                    padding: 0.75rem 1.5rem;
                                    border-radius: 0.5rem;
                                    font-weight: 500;
                                    cursor: pointer;
                                    transition: all 0.2s;
                                " onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='white'"
                                onclick="alert('This would show more details in a real app.')">
                                    View Details
                                </button>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
    
    # Add custom styles
    st.markdown("""
        <style>
            /* Style the tab buttons */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: normal;
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
                width: 100%;
                border-radius: 8px;
                padding: 0.75rem 1.5rem;
                font-weight: 500;
                transition: all 0.2s;
            }
            
            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            
            /* Style the slider */
            .stSlider > div > div > div > div {
                background-color: #3b82f6;
            }
            
            /* Style the progress bar */
            .stProgress > div > div > div {
                background-color: #3b82f6;
            }
            
            /* Style the expander */
            .stExpander > div > div > div {
                background: #f8fafc;
                border-radius: 8px;
                padding: 1rem;
                margin: 1rem 0;
                border: 1px solid #e2e8f0;
            }
            
            .stExpander > div > div > div:hover {
                border-color: #3b82f6;
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
            
            /* Style the checkboxes */
            .stCheckbox > div > label {
                margin: 0;
                padding: 0.5rem 0;
            }
        </style>
    """, unsafe_allow_html=True)

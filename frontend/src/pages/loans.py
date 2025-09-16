import streamlit as st
import pandas as pd
from datetime import datetime
from ..services import api

def show():
    """Display the loans management page."""
    st.title("Microloans")
    
    # Tabs for different loan operations
    tab1, tab2 = st.tabs(["My Loans", "Apply for Loan"])
    
    with tab1:
        show_my_loans()
    
    with tab2:
        show_loan_application()

def show_my_loans():
    """Display user's current loans."""
    try:
        # Get loan status
        loan_status = api.get_loan_status()
        
        if not loan_status or 'active_loans' not in loan_status or loan_status['active_loans'] == 0:
            st.info("You don't have any active loans.")
            return
        
        # Display active loans
        st.subheader("Active Loans")
        
        # Create a DataFrame for the loan data
        loans_data = []
        for loan in loan_status.get('loans', []):
            loans_data.append({
                'Loan ID': loan['id'],
                'Amount': f"${loan['amount']:,.2f}",
                'Term': f"{loan['term_months']} months",
                'Interest Rate': f"{loan['interest_rate']}%",
                'Monthly Payment': f"${loan['monthly_payment']:,.2f}",
                'Remaining Amount': f"${loan['remaining_amount']:,.2f}",
                'Next Payment': loan['next_payment_date'],
                'Status': loan['status'].title()
            })
        
        if loans_data:
            df = pd.DataFrame(loans_data)
            st.dataframe(
                df,
                column_config={
                    'Loan ID': 'Loan ID',
                    'Amount': 'Amount',
                    'Term': 'Term',
                    'Interest Rate': 'Interest Rate',
                    'Monthly Payment': 'Monthly Payment',
                    'Remaining Amount': 'Remaining',
                    'Next Payment': 'Next Payment',
                    'Status': 'Status'
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Show payment history for selected loan
            if 'selected_loan_id' not in st.session_state:
                st.session_state.selected_loan_id = loans_data[0]['Loan ID']
            
            selected_loan = st.selectbox(
                "Select loan to view payment history",
                [loan['Loan ID'] for loan in loans_data],
                index=0
            )
            
            if selected_loan:
                show_payment_history(selected_loan)
        
    except Exception as e:
        st.error(f"Error loading loan information: {str(e)}")

def show_payment_history(loan_id: int):
    """Display payment history for a specific loan."""
    try:
        # In a real app, this would fetch from the API
        # payments = api.get_loan_payments(loan_id)
        
        # Mock data for demonstration
        payments = [
            {
                'date': '2023-10-15',
                'amount': 125.00,
                'status': 'Completed',
                'principal': 100.00,
                'interest': 25.00
            },
            {
                'date': '2023-09-15',
                'amount': 125.00,
                'status': 'Completed',
                'principal': 95.00,
                'interest': 30.00
            }
        ]
        
        if not payments:
            st.info("No payment history found for this loan.")
            return
        
        st.subheader(f"Payment History - Loan #{loan_id}")
        
        # Create a DataFrame for the payment data
        payment_data = []
        for payment in payments:
            payment_data.append({
                'Date': payment['date'],
                'Amount': f"${payment['amount']:,.2f}",
                'Principal': f"${payment['principal']:,.2f}",
                'Interest': f"${payment['interest']:,.2f}",
                'Status': payment['status']
            })
        
        df = pd.DataFrame(payment_data)
        st.dataframe(
            df,
            column_config={
                'Date': 'Date',
                'Amount': 'Amount',
                'Principal': 'Principal',
                'Interest': 'Interest',
                'Status': 'Status'
            },
            hide_index=True,
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Error loading payment history: {str(e)}")

def show_loan_application():
    """Display loan application form."""
    st.subheader("Apply for a Microloan")
    
    with st.form("loan_application"):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input(
                "Loan Amount ($)",
                min_value=100.0,
                max_value=10000.0,
                step=100.0,
                value=1000.0
            )
            
            term_months = st.selectbox(
                "Loan Term",
                options=[6, 12, 18, 24, 36],
                format_func=lambda x: f"{x} months"
            )
        
        with col2:
            purpose = st.selectbox(
                "Loan Purpose",
                options=[
                    "Business Capital",
                    "Education",
                    "Medical Expenses",
                    "Home Improvement",
                    "Debt Consolidation",
                    "Other"
                ]
            )
            
            income = st.number_input(
                "Monthly Income ($)",
                min_value=0.0,
                step=100.0,
                value=2000.0
            )
        
        # Check eligibility
        if st.form_submit_button("Check Eligibility"):
            try:
                # In a real app, this would call the API
                # eligibility = api.check_loan_eligibility(amount, term_months, purpose)
                
                # Mock eligibility check
                st.session_state.eligibility = {
                    'eligible': True,
                    'amount': amount,
                    'term_months': term_months,
                    'purpose': purpose,
                    'interest_rate': 12.5,
                    'monthly_payment': (amount * 1.125) / term_months
                }
                
            except Exception as e:
                st.error(f"Error checking eligibility: {str(e)}")
    
    # Display eligibility results if available
    if 'eligibility' in st.session_state:
        eligibility = st.session_state.eligibility
        
        if eligibility['eligible']:
            st.success("You are eligible for this loan!")
            
            st.subheader("Loan Offer")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Loan Amount", f"${eligibility['amount']:,.2f}")
            with col2:
                st.metric("Interest Rate", f"{eligibility['interest_rate']}%")
            with col3:
                st.metric("Monthly Payment", f"${eligibility['monthly_payment']:,.2f}")
            
            # Loan application form
            with st.form("confirm_loan"):
                st.write("Please confirm your details:")
                st.write(f"- Purpose: {eligibility['purpose']}")
                st.write(f"- Term: {eligibility['term_months']} months")
                
                if st.form_submit_button("Submit Application"):
                    try:
                        # In a real app, this would call the API
                        # result = api.apply_for_loan(
                        #     amount=eligibility['amount'],
                        #     term_months=eligibility['term_months'],
                        #     purpose=eligibility['purpose']
                        # )
                        st.success("Loan application submitted successfully!")
                        del st.session_state.eligibility
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error submitting application: {str(e)}")
        else:
            st.warning("Based on your current financial situation, you may not be eligible for this loan.")
            st.write("Consider applying for a smaller amount or a shorter term.")

if __name__ == "__main__":
    show()

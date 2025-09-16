import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from ..services import api

def show():
    """Display the admin dashboard."""
    if not st.session_state.state.get('is_admin', False):
        st.error("You don't have permission to access the admin dashboard.")
        return
    
    st.title("Admin Dashboard")
    
    # Tabs for different admin sections
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "User Management", "Campaign Management", "Analytics"])
    
    with tab1:
        show_admin_overview()
    
    with tab2:
        show_user_management()
    
    with tab3:
        show_campaign_management()
    
    with tab4:
        show_analytics()

def show_admin_overview():
    """Display admin overview with key metrics."""
    try:
        # In a real app, this would fetch from the API
        # metrics = api.get_admin_metrics()
        
        # Mock data for demonstration
        metrics = {
            'total_users': 1245,
            'active_users': 876,
            'pending_loans': 42,
            'active_campaigns': 18,
            'total_donations': 125000,
            'recent_activity': [
                {'user': 'user123', 'action': 'login', 'timestamp': '2023-10-16T08:30:00'},
                {'user': 'admin', 'action': 'user_approved', 'timestamp': '2023-10-16T08:15:00'},
                {'user': 'donor456', 'action': 'donation', 'timestamp': '2023-10-16T07:45:00'},
                {'user': 'borrower789', 'action': 'loan_application', 'timestamp': '2023-10-16T07:30:00'},
                {'user': 'campaigner101', 'action': 'campaign_created', 'timestamp': '2023-10-15T16:20:00'},
            ]
        }
        
        # Key metrics
        st.subheader("Platform Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", metrics['total_users'])
        with col2:
            st.metric("Active Users (30d)", metrics['active_users'])
        with col3:
            st.metric("Pending Loans", metrics['pending_loans'])
        with col4:
            st.metric("Active Campaigns", metrics['active_campaigns'])
        
        # Recent activity
        st.subheader("Recent Activity")
        
        # Convert to DataFrame for display
        activity_df = pd.DataFrame(metrics['recent_activity'])
        activity_df['timestamp'] = pd.to_datetime(activity_df['timestamp'])
        activity_df = activity_df.sort_values('timestamp', ascending=False)
        
        st.dataframe(
            activity_df,
            column_config={
                'user': 'User',
                'action': 'Action',
                'timestamp': 'Timestamp'
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Quick actions
        st.subheader("Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Approve Pending Users"):
                # In a real app, this would call the API
                st.session_state.show_pending_users = True
        with col2:
            if st.button("Review Loan Applications"):
                st.session_state.show_pending_loans = True
        with col3:
            if st.button("View System Logs"):
                st.session_state.show_system_logs = True
        
        # Show pending users if requested
        if st.session_state.get('show_pending_users', False):
            show_pending_users()
        
        # Show pending loans if requested
        if st.session_state.get('show_pending_loans', False):
            show_pending_loans()
        
        # Show system logs if requested
        if st.session_state.get('show_system_logs', False):
            show_system_logs()
    
    except Exception as e:
        st.error(f"Error loading admin overview: {str(e)}")

def show_user_management():
    """Display user management interface."""
    try:
        st.subheader("User Management")
        
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("Search users", "")
        with col2:
            user_status = st.selectbox(
                "Status",
                ["All", "Active", "Inactive", "Pending", "Suspended"]
            )
        
        # In a real app, this would fetch from the API with filters
        # users = api.get_users(search=search_query, status=user_status if user_status != "All" else None)
        
        # Mock data for demonstration
        users = [
            {
                'id': 1,
                'username': 'user123',
                'email': 'user123@example.com',
                'role': 'borrower',
                'status': 'active',
                'created_at': '2023-01-15',
                'last_login': '2023-10-16T08:30:00'
            },
            {
                'id': 2,
                'username': 'donor456',
                'email': 'donor456@example.com',
                'role': 'donor',
                'status': 'active',
                'created_at': '2023-03-22',
                'last_login': '2023-10-15T14:20:00'
            },
            {
                'id': 3,
                'username': 'new_user',
                'email': 'new@example.com',
                'role': 'borrower',
                'status': 'pending',
                'created_at': '2023-10-16',
                'last_login': None
            }
        ]
        
        # Apply filters to mock data
        if search_query:
            users = [u for u in users if search_query.lower() in u['username'].lower() or search_query.lower() in u['email'].lower()]
        
        if user_status != "All":
            users = [u for u in users if u['status'] == user_status.lower()]
        
        # Display users in a data table
        if not users:
            st.info("No users found matching the criteria.")
        else:
            # Convert to DataFrame for display
            user_data = []
            for user in users:
                user_data.append({
                    'ID': user['id'],
                    'Username': user['username'],
                    'Email': user['email'],
                    'Role': user['role'].title(),
                    'Status': user['status'].title(),
                    'Created At': user['created_at'],
                    'Last Login': user['last_login'].split('T')[0] if user['last_login'] else 'Never'
                })
            
            df = pd.DataFrame(user_data)
            
            # Display the data table with checkboxes for selection
            selected_indices = st.data_editor(
                df,
                column_config={
                    "select": st.column_config.CheckboxColumn(
                        "Select",
                        help="Select users to perform batch actions",
                        default=False,
                    )
                },
                disabled=df.columns.tolist(),
                hide_index=True,
                use_container_width=True,
                key="user_selection"
            )
            
            # Get selected users
            selected_users = selected_indices[selected_indices.select].index.tolist()
            
            # Bulk actions
            st.subheader("Bulk Actions")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Activate Selected"):
                    update_user_status([users[i]['id'] for i in selected_users], 'active')
            with col2:
                if st.button("Deactivate Selected"):
                    update_user_status([users[i]['id'] for i in selected_users], 'inactive')
            with col3:
                if st.button("Suspend Selected"):
                    update_user_status([users[i]['id'] for i in selected_users], 'suspended')
            with col4:
                if st.button("Delete Selected"):
                    delete_users([users[i]['id'] for i in selected_users])
            
            # User details and edit form
            if selected_users and len(selected_users) == 1:
                user = users[selected_users[0]]
                with st.expander(f"Edit User: {user['username']}"):
                    with st.form(f"edit_user_{user['id']}"):
                        username = st.text_input("Username", value=user['username'])
                        email = st.text_input("Email", value=user['email'])
                        role = st.selectbox(
                            "Role",
                            ['borrower', 'donor', 'admin'],
                            index=['borrower', 'donor', 'admin'].index(user['role'])
                        )
                        status = st.selectbox(
                            "Status",
                            ['active', 'inactive', 'pending', 'suspended'],
                            index=['active', 'inactive', 'pending', 'suspended'].index(user['status'])
                        )
                        
                        if st.form_submit_button("Update User"):
                            # In a real app, this would call the API
                            # api.update_user(user['id'], {
                            #     'username': username,
                            #     'email': email,
                            #     'role': role,
                            #     'status': status
                            # })
                            st.success(f"User {username} updated successfully!")
                            st.experimental_rerun()
    
    except Exception as e:
        st.error(f"Error in user management: {str(e)}")

def update_user_status(user_ids, status):
    """Update status of multiple users."""
    if not user_ids:
        st.warning("No users selected.")
        return
    
    try:
        # In a real app, this would call the API
        # for user_id in user_ids:
        #     api.update_user_status(user_id, status)
        st.success(f"Updated {len(user_ids)} user(s) to {status} status.")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Error updating users: {str(e)}")

def delete_users(user_ids):
    """Delete multiple users."""
    if not user_ids:
        st.warning("No users selected.")
        return
    
    if st.checkbox(f"Are you sure you want to permanently delete {len(user_ids)} user(s)?"):
        try:
            # In a real app, this would call the API
            # for user_id in user_ids:
            #     api.delete_user(user_id)
            st.success(f"Deleted {len(user_ids)} user(s) successfully.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error deleting users: {str(e)}")

def show_campaign_management():
    """Display campaign management interface."""
    st.subheader("Campaign Management")
    st.info("Campaign management features will be implemented in a future update.")

def show_analytics():
    """Display platform analytics."""
    st.subheader("Platform Analytics")
    st.info("Analytics dashboard will be implemented in a future update.")

def show_pending_users():
    """Display pending user approvals."""
    with st.expander("Pending User Approvals", expanded=True):
        st.info("Pending user approvals will be implemented in a future update.")

def show_pending_loans():
    """Display pending loan applications."""
    with st.expander("Pending Loan Applications", expanded=True):
        st.info("Pending loan applications will be implemented in a future update.")

def show_system_logs():
    """Display system logs."""
    with st.expander("System Logs", expanded=True):
        st.info("System logs will be implemented in a future update.")

import streamlit as st
import pandas as pd
from datetime import datetime
from ..services import api

def show():
    """Display the crowdfunding page."""
    st.title("Crowdfunding")
    
    # Tabs for different operations
    tab1, tab2 = st.tabs(["Explore Campaigns", "My Campaigns"])
    
    with tab1:
        show_explore_campaigns()
    
    with tab2:
        show_my_campaigns()

def show_explore_campaigns():
    """Display all active crowdfunding campaigns."""
    try:
        # In a real app, this would fetch from the API
        # campaigns = api.get_campaigns()
        
        # Mock data for demonstration
        campaigns = [
            {
                'id': 1,
                'title': 'Clean Water Initiative',
                'description': 'Help provide clean drinking water to rural communities.',
                'current_amount': 12500,
                'target_amount': 50000,
                'end_date': '2023-12-31',
                'category': 'Community'
            },
            {
                'id': 2,
                'title': 'Education for All',
                'description': 'Support education for underprivileged children.',
                'current_amount': 8750,
                'target_amount': 20000,
                'end_date': '2023-11-30',
                'category': 'Education'
            }
        ]
        
        if not campaigns:
            st.info("No active campaigns found.")
            return
        
        st.subheader("Active Campaigns")
        
        # Display campaigns in a grid
        cols = st.columns(2)
        for idx, campaign in enumerate(campaigns):
            with cols[idx % 2]:
                with st.container():
                    st.subheader(campaign['title'])
                    st.caption(f"{campaign['category']}")
                    
                    # Progress bar
                    progress = (campaign['current_amount'] / campaign['target_amount']) * 100
                    st.progress(min(progress / 100, 1.0))
                    
                    # Campaign stats
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Raised", f"${campaign['current_amount']:,.0f}")
                    with col2:
                        st.metric("Goal", f"${campaign['target_amount']:,.0f}")
                    
                    # View and Donate buttons
                    view_btn, donate_btn = st.columns([2, 1])
                    with view_btn:
                        if st.button("View Details", key=f"view_{campaign['id']}"):
                            st.session_state.view_campaign = campaign
                    with donate_btn:
                        if st.button("Donate", key=f"donate_{campaign['id']}"):
                            st.session_state.donate_campaign = campaign
                    
                    st.markdown("---")
    
    except Exception as e:
        st.error(f"Error loading campaigns: {str(e)}")

def show_my_campaigns():
    """Display campaigns created by the current user."""
    try:
        # In a real app, this would fetch from the API
        # my_campaigns = api.get_my_campaigns()
        
        # Mock data for demonstration
        my_campaigns = [
            {
                'id': 3,
                'title': 'Local Food Bank Support',
                'current_amount': 3200,
                'target_amount': 10000,
                'end_date': '2023-12-15',
                'status': 'active'
            }
        ]
        
        if not my_campaigns:
            st.info("You haven't created any campaigns yet.")
            if st.button("Create a Campaign"):
                st.session_state.show_create_campaign = True
        else:
            if st.button("Create New Campaign"):
                st.session_state.show_create_campaign = True
            
            st.subheader("My Campaigns")
            
            # Display campaigns in a table
            campaign_data = []
            for campaign in my_campaigns:
                progress = (campaign['current_amount'] / campaign['target_amount']) * 100
                campaign_data.append({
                    'Title': campaign['title'],
                    'Raised': campaign['current_amount'],
                    'Goal': campaign['target_amount'],
                    'Progress': progress,
                    'Status': campaign['status'].title(),
                    'End Date': campaign['end_date']
                })
            
            if campaign_data:
                df = pd.DataFrame(campaign_data)
                st.dataframe(
                    df,
                    column_config={
                        'Title': 'Campaign',
                        'Raised': st.column_config.NumberColumn('Raised', format='$%.2f'),
                        'Goal': st.column_config.NumberColumn('Goal', format='$%.2f'),
                        'Progress': st.column_config.ProgressColumn(
                            'Progress',
                            format='%f%%',
                            min_value=0,
                            max_value=100
                        ),
                        'Status': 'Status',
                        'End Date': 'End Date'
                    },
                    hide_index=True,
                    use_container_width=True
                )
        
        # Show create campaign form if button is clicked
        if st.session_state.get('show_create_campaign', False):
            show_create_campaign_form()
    
    except Exception as e:
        st.error(f"Error loading your campaigns: {str(e)}")

def show_create_campaign_form():
    """Display form to create a new campaign."""
    with st.form("create_campaign"):
        st.subheader("Create New Campaign")
        
        title = st.text_input("Campaign Title")
        description = st.text_area("Description")
        
        col1, col2 = st.columns(2)
        with col1:
            target_amount = st.number_input("Funding Goal ($)", min_value=100, step=100)
        with col2:
            end_date = st.date_input("End Date", min_value=datetime.now().date())
        
        category = st.selectbox(
            "Category",
            ["Education", "Health", "Community", "Environment", "Other"]
        )
        
        if st.form_submit_button("Create Campaign"):
            if not all([title, description, target_amount, end_date]):
                st.error("Please fill in all required fields.")
            else:
                try:
                    # In a real app, this would call the API
                    # result = api.create_campaign(
                    #     title=title,
                    #     description=description,
                    #     target_amount=target_amount,
                    #     end_date=end_date.isoformat(),
                    #     category=category
                    # )
                    st.success("Campaign created successfully!")
                    st.session_state.show_create_campaign = False
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error creating campaign: {str(e)}")

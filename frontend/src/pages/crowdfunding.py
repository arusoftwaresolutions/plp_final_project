from datetime import datetime, timedelta
import random

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import get_auth_headers, format_currency, format_date, API_BASE_URL

def get_campaigns():
    """Fetch crowdfunding campaigns from the backend."""
    # In a real app, this would call your backend API
    # For now, we'll use mock data
    campaigns = [
        {
            "id": 1,
            "title": "Clean Water for Mtwara",
            "description": "Help us provide clean drinking water to 500 families in Mtwara region by building a new well.",
            "goal": 10000,
            "raised": 7250,
            "backers": 189,
            "days_left": 15,
            "image": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1476&q=80",
            "category": "Community",
            "location": "Mtwara, Tanzania"
        },
        {
            "id": 2,
            "title": "School Supplies for Rural Students",
            "description": "Provide school supplies and uniforms for 200 students in rural Kenya to support their education.",
            "goal": 5000,
            "raised": 3200,
            "backers": 142,
            "days_left": 8,
            "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80",
            "category": "Education",
            "location": "Kisumu, Kenya"
        },
        {
            "id": 3,
            "title": "Women's Entrepreneurship Program",
            "description": "Empower 50 women with business training and microloans to start their own small businesses.",
            "goal": 15000,
            "raised": 8900,
            "backers": 256,
            "days_left": 22,
            "image": "https://images.unsplash.com/photo-1521791136064-7986c2920216?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80",
            "category": "Women Empowerment",
            "location": "Kampala, Uganda"
        },
        {
            "id": 4,
            "title": "Solar Power for Health Clinic",
            "description": "Install solar panels to provide reliable electricity for a rural health clinic serving 5,000 people.",
            "goal": 20000,
            "raised": 15400,
            "backers": 321,
            "days_left": 5,
            "image": "https://images.unsplash.com/photo-1581056771107-24ca5f033842?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80",
            "category": "Healthcare",
            "location": "Arusha, Tanzania"
        },
        {
            "id": 5,
            "title": "Sustainable Farming Initiative",
            "description": "Train 100 farmers in sustainable agricultural practices to improve food security and income.",
            "goal": 12000,
            "raised": 4500,
            "backers": 98,
            "days_left": 30,
            "image": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1632&q=80",
            "category": "Agriculture",
            "location": "Nakuru, Kenya"
        },
        {
            "id": 6,
            "title": "Youth Coding Bootcamp",
            "description": "Provide coding education and mentorship to underprivileged youth in Nairobi's informal settlements.",
            "goal": 8000,
            "raised": 6200,
            "backers": 176,
            "days_left": 12,
            "image": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80",
            "category": "Education",
            "location": "Nairobi, Kenya"
        }
    ]
    
    # Add some variation to the mock data
    for campaign in campaigns:
        campaign['progress'] = (campaign['raised'] / campaign['goal']) * 100
        campaign['days_ago'] = random.randint(1, 30)
        campaign['start_date'] = (datetime.now() - timedelta(days=campaign['days_ago'])).strftime('%b %d, %Y')
        campaign['end_date'] = (datetime.now() + timedelta(days=campaign['days_left'])).strftime('%b %d, %Y')
    
    return campaigns

def show():
    """Show the crowdfunding page."""
    st.title("Crowdfunding")
    st.markdown("Support community projects and make a difference in people's lives.")
    
    # Add tabs for different views
    tab1, tab2 = st.tabs(["Browse Campaigns", "Start a Campaign"])
    
    with tab1:
        # Search and filter
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input("Search campaigns", "", placeholder="Search by title, description, or location")
        
        with col2:
            categories = ["All"] + sorted(list(set([campaign['category'] for campaign in get_campaigns()])))
            selected_category = st.selectbox("Filter by category", categories)
        
        # Get and filter campaigns
        campaigns = get_campaigns()
        
        if search_query:
            search_query = search_query.lower()
            campaigns = [c for c in campaigns if 
                        search_query in c['title'].lower() or 
                        search_query in c['description'].lower() or
                        search_query in c['location'].lower()]
        
        if selected_category != "All":
            campaigns = [c for c in campaigns if c['category'] == selected_category]
        
        # Display campaigns
        if not campaigns:
            st.info("No campaigns found matching your criteria. Try adjusting your search or filters.")
        else:
            for campaign in campaigns:
                with st.container():
                    st.markdown(f"""
                        <div style="
                            background: white;
                            border-radius: 10px;
                            overflow: hidden;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                            margin-bottom: 2rem;
                        ">
                            <div style="
                                height: 200px;
                                background: url('{campaign['image']}');
                                background-size: cover;
                                background-position: center;
                                position: relative;
                            ">
                                <div style="
                                    position: absolute;
                                    top: 1rem;
                                    right: 1rem;
                                    background: rgba(0,0,0,0.7);
                                    color: white;
                                    padding: 0.25rem 0.75rem;
                                    border-radius: 1rem;
                                    font-size: 0.8rem;
                                    font-weight: 500;
                                ">
                                    {campaign['category']}
                                </div>
                            </div>
                            
                            <div style="padding: 1.5rem;">
                                <div style="
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: flex-start;
                                    margin-bottom: 1rem;
                                ">
                                    <h3 style="margin: 0 0 0.5rem 0;">{campaign['title']}</h3>
                                    <div style="
                                        background: #f0fdf4;
                                        color: #166534;
                                        padding: 0.25rem 0.75rem;
                                        border-radius: 1rem;
                                        font-size: 0.8rem;
                                        font-weight: 500;
                                        white-space: nowrap;
                                        margin-left: 1rem;
                                    ">
                                        {campaign['location']}
                                    </div>
                                </div>
                                
                                <p style="
                                    color: #4b5563;
                                    margin: 0 0 1.5rem 0;
                                    display: -webkit-box;
                                    -webkit-line-clamp: 2;
                                    -webkit-box-orient: vertical;
                                    overflow: hidden;
                                    text-overflow: ellipsis;
                                ">
                                    {campaign['description']}
                                </p>
                                
                                <div style="margin-bottom: 1rem;">
                                    <div style="
                                        display: flex;
                                        justify-content: space-between;
                                        margin-bottom: 0.25rem;
                                        font-size: 0.9rem;
                                    ">
                                        <span>${campaign['raised']:,.0f} raised of ${campaign['goal']:,.0f}</span>
                                        <span>{campaign['progress']:.0f}%</span>
                                    </div>
                                    
                                    <div style="
                                        height: 8px;
                                        background: #e5e7eb;
                                        border-radius: 4px;
                                        overflow: hidden;
                                        margin-bottom: 0.5rem;
                                    ">
                                        <div style="
                                            width: {min(100, campaign['progress'])}%;
                                            height: 100%;
                                            background: #3b82f6;
                                            border-radius: 4px;
                                        "></div>
                                    </div>
                                    
                                    <div style="
                                        display: flex;
                                        justify-content: space-between;
                                        color: #6b7280;
                                        font-size: 0.8rem;
                                    ">
                                        <span>{campaign['backers']} backers</span>
                                        <span>{campaign['days_left']} days left</span>
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
                                    onclick="alert('This would open a contribution form in a real app.')">
                                        Donate Now
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
                                    onclick="alert('This would save the campaign to your favorites in a real app.')">
                                        Save
                                    </button>
                                </div>
                                
                                <div style="
                                    display: flex;
                                    justify-content: space-between;
                                    margin-top: 1rem;
                                    padding-top: 1rem;
                                    border-top: 1px solid #e5e7eb;
                                    color: #6b7280;
                                    font-size: 0.8rem;
                                ">
                                    <span>Started on {campaign['start_date']}</span>
                                    <span>Ends on {campaign['end_date']}</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Start a New Campaign")
        st.markdown("Create your own crowdfunding campaign to raise money for your community project.")
        
        with st.form("create_campaign"):
            col1, col2 = st.columns(2)
            
            with col1:
                campaign_title = st.text_input("Campaign Title*")
                campaign_goal = st.number_input(
                    "Funding Goal (USD)*",
                    min_value=100,
                    step=100,
                    format="%d"
                )
                campaign_category = st.selectbox(
                    "Category*",
                    ["Education", "Healthcare", "Community", "Women Empowerment", "Agriculture", "Environment", "Other"]
                )
                campaign_location = st.text_input("Location (City, Country)*")
            
            with col2:
                campaign_image = st.file_uploader("Campaign Image*", type=["jpg", "jpeg", "png"])
                campaign_end_date = st.date_input(
                    "Campaign End Date*",
                    min_value=datetime.now().date() + timedelta(days=1),
                    value=datetime.now().date() + timedelta(days=30)
                )
            
            campaign_description = st.text_area(
                "Campaign Description*",
                height=200,
                help="Tell your story and explain how the funds will be used."
            )
            
            # Campaign rewards
            st.subheader("Add Rewards (Optional)")
            st.markdown("Offer rewards to encourage people to contribute to your campaign.")
            
            rewards = []
            for i in range(3):
                with st.expander(f"Reward Tier {i+1}", expanded=i==0):
                    reward_amount = st.number_input(
                        f"Contribution Amount {i+1} (USD)*",
                        min_value=1,
                        step=10,
                        key=f"reward_amount_{i}"
                    )
                    reward_title = st.text_input(f"Reward Title {i+1}*", key=f"reward_title_{i}")
                    reward_description = st.text_area(
                        f"Reward Description {i+1}*",
                        help="Describe what backers will receive at this tier.",
                        key=f"reward_desc_{i}"
                    )
                    
                    if reward_title and reward_description:
                        rewards.append({
                            "amount": reward_amount,
                            "title": reward_title,
                            "description": reward_description
                        })
            
            # Terms and conditions
            st.markdown("### Terms & Conditions")
            terms_accepted = st.checkbox(
                "I agree to the Terms of Service and Privacy Policy*"
            )
            
            # Submit button
            submit_button = st.form_submit_button("Submit Campaign for Review")
            
            if submit_button:
                # Basic validation
                required_fields = [
                    (campaign_title, "Campaign Title"),
                    (campaign_goal, "Funding Goal"),
                    (campaign_description, "Campaign Description"),
                    (campaign_location, "Location"),
                    (campaign_image, "Campaign Image")
                ]
                
                missing_fields = [field_name for field, field_name in required_fields if not field]
                
                if missing_fields:
                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
                elif not terms_accepted:
                    st.error("Please accept the Terms of Service and Privacy Policy")
                else:
                    # In a real app, this would submit to your backend
                    st.success("✅ Your campaign has been submitted for review!")
                    st.balloons()
                    
                    # Show a preview
                    st.subheader("Campaign Preview")
                    st.markdown(f"**Title:** {campaign_title}")
                    st.markdown(f"**Goal:** ${campaign_goal:,.2f}")
                    st.markdown(f"**Category:** {campaign_category}")
                    st.markdown(f"**Location:** {campaign_location}")
                    st.markdown(f"**End Date:** {campaign_end_date.strftime('%B %d, %Y')}")
                    st.markdown("**Description:**")
                    st.markdown(campaign_description)
                    
                    if rewards:
                        st.markdown("**Rewards:**")
                        for reward in rewards:
                            st.markdown(f"- **${reward['amount']}:** {reward['title']} - {reward['description']}")
                    
                    # Reset form
                    st.session_state.create_campaign = False
    
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
        </style>
    """, unsafe_allow_html=True)

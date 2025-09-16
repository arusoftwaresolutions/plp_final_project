import streamlit as st
from datetime import datetime
from ..services import api

def show():
    """Display the settings page."""
    st.title("Settings")
    
    # Tabs for different settings sections
    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Notifications", "Security", "Preferences"])
    
    with tab1:
        show_profile_settings()
    
    with tab2:
        show_notification_settings()
    
    with tab3:
        show_security_settings()
    
    with tab4:
        show_preferences()

def show_profile_settings():
    """Display and edit user profile settings."""
    try:
        # In a real app, this would fetch from the API
        # user_data = api.get_user_profile()
        
        # Mock data for demonstration
        user_data = {
            'username': 'johndoe',
            'email': 'john.doe@example.com',
            'full_name': 'John Doe',
            'bio': 'Financial inclusion advocate and micro-entrepreneur',
            'location': 'Nairobi, Kenya',
            'phone': '+254 700 123456',
            'date_joined': '2023-01-15',
            'last_login': '2023-10-16T08:30:00'
        }
        
        with st.form("profile_form"):
            st.subheader("Profile Information")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", value=user_data.get('full_name', '').split(' ')[0])
            with col2:
                last_name = st.text_input("Last Name", value=' '.join(user_data.get('full_name', '').split(' ')[1:]) if ' ' in user_data.get('full_name', '') else '')
            
            email = st.text_input("Email", value=user_data.get('email', ''))
            phone = st.text_input("Phone Number", value=user_data.get('phone', ''))
            location = st.text_input("Location", value=user_data.get('location', ''))
            
            bio = st.text_area("Bio", value=user_data.get('bio', ''), 
                             help="Tell us a bit about yourself and your goals.")
            
            if st.form_submit_button("Save Changes"):
                # In a real app, this would call the API
                # api.update_profile({
                #     'first_name': first_name,
                #     'last_name': last_name,
                #     'email': email,
                #     'phone': phone,
                #     'location': location,
                #     'bio': bio
                # })
                st.success("Profile updated successfully!")
        
        # Account information (read-only)
        st.subheader("Account Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Username", user_data['username'])
            st.metric("Member Since", datetime.strptime(user_data['date_joined'], '%Y-%m-%d').strftime('%B %d, %Y'))
        with col2:
            st.metric("Last Login", datetime.strptime(user_data['last_login'].split('T')[0], '%Y-%m-%d').strftime('%B %d, %Y'))
    
    except Exception as e:
        st.error(f"Error loading profile settings: {str(e)}")

def show_notification_settings():
    """Display and edit notification preferences."""
    try:
        # In a real app, this would fetch from the API
        # notification_prefs = api.get_notification_preferences()
        
        # Mock data for demonstration
        notification_prefs = {
            'email_notifications': True,
            'push_notifications': True,
            'sms_notifications': False,
            'transaction_alerts': True,
            'payment_reminders': True,
            'campaign_updates': True,
            'newsletter': True,
            'promotional_offers': False
        }
        
        st.subheader("Notification Preferences")
        
        with st.form("notification_form"):
            st.write("### Notification Methods")
            email_notifications = st.toggle(
                "Email Notifications", 
                value=notification_prefs['email_notifications'],
                help="Receive notifications via email"
            )
            
            push_notifications = st.toggle(
                "Push Notifications", 
                value=notification_prefs['push_notifications'],
                help="Receive push notifications on your device"
            )
            
            sms_notifications = st.toggle(
                "SMS Notifications", 
                value=notification_prefs['sms_notifications'],
                help="Receive text message notifications"
            )
            
            st.write("### Notification Types")
            
            col1, col2 = st.columns(2)
            with col1:
                transaction_alerts = st.toggle(
                    "Transaction Alerts", 
                    value=notification_prefs['transaction_alerts'],
                    help="Get notified for all transactions"
                )
                
                payment_reminders = st.toggle(
                    "Payment Reminders", 
                    value=notification_prefs['payment_reminders'],
                    help="Reminders for upcoming payments"
                )
            
            with col2:
                campaign_updates = st.toggle(
                    "Campaign Updates", 
                    value=notification_prefs['campaign_updates'],
                    help="Updates on campaigns you've supported"
                )
                
                newsletter = st.toggle(
                    "Newsletter", 
                    value=notification_prefs['newsletter'],
                    help="Weekly newsletter with platform updates"
                )
                
                promotional_offers = st.toggle(
                    "Promotional Offers", 
                    value=notification_prefs['promotional_offers'],
                    help="Special offers and promotions"
                )
            
            if st.form_submit_button("Save Preferences"):
                # In a real app, this would call the API
                # api.update_notification_preferences({
                #     'email_notifications': email_notifications,
                #     'push_notifications': push_notifications,
                #     'sms_notifications': sms_notifications,
                #     'transaction_alerts': transaction_alerts,
                #     'payment_reminders': payment_reminders,
                #     'campaign_updates': campaign_updates,
                #     'newsletter': newsletter,
                #     'promotional_offers': promotional_offers
                # })
                st.success("Notification preferences updated successfully!")
    
    except Exception as e:
        st.error(f"Error loading notification settings: {str(e)}")

def show_security_settings():
    """Display and manage security settings."""
    st.subheader("Security Settings")
    
    # Change password
    with st.expander("Change Password", expanded=True):
        with st.form("password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password", 
                                       help="Password must be at least 8 characters long and include a number and a special character.")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if not all([current_password, new_password, confirm_password]):
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("New passwords do not match.")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters long.")
                else:
                    # In a real app, this would call the API
                    # api.change_password(current_password, new_password)
                    st.success("Password updated successfully!")
    
    # Two-factor authentication
    with st.expander("Two-Factor Authentication", expanded=True):
        two_fa_enabled = st.toggle(
            "Enable Two-Factor Authentication",
            value=False,
            help="Add an extra layer of security to your account"
        )
        
        if two_fa_enabled:
            st.info("Two-factor authentication will be enabled after you verify your identity.")
            
            # In a real app, this would show the QR code and verification input
            # st.image("path_to_qr_code.png", caption="Scan this QR code with your authenticator app")
            # verification_code = st.text_input("Enter verification code")
            
            if st.button("Set Up 2FA"):
                # In a real app, this would verify the code and enable 2FA
                # api.enable_two_factor(verification_code)
                st.success("Two-factor authentication has been enabled for your account.")
    
    # Active sessions
    with st.expander("Active Sessions", expanded=True):
        # In a real app, this would fetch from the API
        # sessions = api.get_active_sessions()
        
        # Mock data for demonstration
        sessions = [
            {
                'id': 'session_123',
                'device': 'Chrome on Windows',
                'location': 'Nairobi, Kenya',
                'last_activity': '2023-10-16T08:30:00',
                'current': True
            },
            {
                'id': 'session_456',
                'device': 'Safari on iPhone',
                'location': 'Mombasa, Kenya',
                'last_activity': '2023-10-15T14:20:00',
                'current': False
            }
        ]
        
        st.write("These are the devices that are currently or were recently logged into your account.")
        
        for session in sessions:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{session['device']}**")
                st.caption(f"Last active: {session['last_activity'].replace('T', ' ').split('.')[0]}")
            with col2:
                st.caption(session['location'])
            with col3:
                if session['current']:
                    st.success("Current session")
                else:
                    if st.button("Sign out", key=f"sign_out_{session['id']}"):
                        # In a real app, this would call the API
                        # api.revoke_session(session['id'])
                        st.success(f"Signed out of {session['device']}")
                        st.experimental_rerun()
            
            st.divider()

def show_preferences():
    """Display and manage user preferences."""
    st.subheader("Preferences")
    
    # In a real app, this would fetch from the API
    # preferences = api.get_user_preferences()
    
    # Mock data for demonstration
    preferences = {
        'language': 'en',
        'timezone': 'Africa/Nairobi',
        'currency': 'KES',
        'theme': 'light',
        'dashboard_view': 'overview',
        'transactions_per_page': 20
    }
    
    with st.form("preferences_form"):
        st.write("### Display Preferences")
        
        col1, col2 = st.columns(2)
        with col1:
            language = st.selectbox(
                "Language",
                ["English (en)", "Swahili (sw)", "French (fr)", "Spanish (es)"],
                index=["en", "sw", "fr", "es"].index(preferences['language'])
            )
            
            theme = st.selectbox(
                "Theme",
                ["Light", "Dark", "System"],
                index=["light", "dark", "system"].index(preferences['theme'])
            )
        
        with col2:
            timezone = st.selectbox(
                "Timezone",
                ["Africa/Nairobi", "Africa/Kampala", "Africa/Dar_es_Salaam", "UTC"],
                index=["Africa/Nairobi", "Africa/Kampala", "Africa/Dar_es_Salaam", "UTC"].index(preferences['timezone'])
            )
            
            currency = st.selectbox(
                "Currency",
                ["KES - Kenyan Shilling", "UGX - Ugandan Shilling", "TZS - Tanzanian Shilling", "USD - US Dollar"],
                index=["KES", "UGX", "TZS", "USD"].index(preferences['currency'])
            )
        
        st.write("### Transaction Preferences")
        
        transactions_per_page = st.slider(
            "Transactions per page",
            min_value=10,
            max_value=100,
            step=10,
            value=preferences['transactions_per_page']
        )
        
        default_dashboard_view = st.selectbox(
            "Default Dashboard View",
            ["Overview", "Transactions", "Budgets", "Investments"],
            index=["overview", "transactions", "budgets", "investments"].index(preferences['dashboard_view'])
        )
        
        if st.form_submit_button("Save Preferences"):
            # In a real app, this would call the API
            # api.update_preferences({
            #     'language': language.split('(')[1][:-1],
            #     'timezone': timezone,
            #     'currency': currency.split(' ')[0],
            #     'theme': theme.lower(),
            #     'dashboard_view': default_dashboard_view.lower(),
            #     'transactions_per_page': transactions_per_page
            # })
            st.success("Preferences updated successfully!")

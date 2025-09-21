import streamlit as st

# Set page config at the very top
st.set_page_config(
    page_title="SDG Finance Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed
)

# Global CSS to hide sidebar during login
st.markdown("""
<style>
/* Hide sidebar completely during login */
[data-testid="stSidebar"] {
    display: none !important;
}

/* Login page styling */
.login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: 0;
    padding: 0;
}

.login-box {
    background: white;
    padding: 3rem;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    max-width: 500px;
    width: 90%;
    margin: 0 auto;
}

.login-header h1 {
    color: #2c3e50;
    margin-bottom: 0.5rem;
    font-size: 2.5rem;
    text-align: center;
}

.login-header p {
    color: #666;
    font-size: 1.1rem;
    margin: 0;
    text-align: center;
}

/* Main app styling */
.main-header {
    background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
    color: white;
    padding: 1rem 2rem;
    border-radius: 0 0 20px 20px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.main-header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 600;
}

.main-header p {
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    font-size: 1rem;
}

.footer {
    text-align: center;
    color: #666;
    font-size: 0.8rem;
    padding: 1rem 0;
    border-top: 1px solid #e0e0e0;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function - simplified"""
    # Check authentication FIRST
    if not st.session_state.get('authenticated', False):
        # Show login page - NO SIDEBAR
        st.markdown("""
        <div class="login-container">
            <div class="login-box">
                <div class="login-header">
                    <h1>🌍 SDG Finance Platform</h1>
                    <p>Empowering communities through financial inclusion</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Simple login form
        st.markdown("---")
        st.subheader("🔑 Login to Continue")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button("Login", use_container_width=True)
            with col2:
                st.form_submit_button("Forgot Password?", use_container_width=True)

        if login_button:
            if username and password:
                if username == "admin" and password == "password":
                    st.session_state.authenticated = True
                    st.session_state.is_admin = True
                    st.session_state.current_user = {"username": username}
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                elif username == "user" and password == "password":
                    st.session_state.authenticated = True
                    st.session_state.is_admin = False
                    st.session_state.current_user = {"username": username}
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")

        st.markdown("---")
        st.markdown("**Demo Accounts:**")
        st.markdown("- Username: `admin`, Password: `password` (Admin access)")
        st.markdown("- Username: `user`, Password: `password` (User access)")

        return  # Stop here if not authenticated

    # User is authenticated - show main app WITH sidebar
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🌍 SDG Finance Platform Dashboard</h1>
        <p>Welcome back, {st.session_state.current_user.get('username', 'User')}!</p>
    </div>
    """, unsafe_allow_html=True)

    # Create layout with sidebar
    col1, col2 = st.columns([1, 3])

    # Sidebar in first column
    with col1:
        st.markdown("""
        <div style="padding: 1rem; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: #2c3e50; margin-bottom: 1rem; text-align: center;">🌍 SDG Finance Platform</h3>
            <p style="color: #666; font-size: 0.9rem; text-align: center; margin-bottom: 1rem;">Empowering communities through financial inclusion</p>
        </div>
        """, unsafe_allow_html=True)

        # Simple navigation
        pages = ["Dashboard", "AI Recommendations", "Transactions", "Crowdfunding", "Microloans", "Poverty Map", "Profile"]
        current_page = st.session_state.get('current_page', 'Dashboard')

        for page in pages:
            if st.button(f"📊 {page}", key=page, use_container_width=True):
                st.session_state.current_page = page
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.is_admin = False
            st.session_state.current_user = None
            st.success("Logged out successfully!")
            st.rerun()

    # Main content in second column
    with col2:
        current_page = st.session_state.get('current_page', 'Dashboard')

        st.markdown(f"## 📊 {current_page}")
        st.write(f"Welcome to the {current_page.lower()} page!")

        if current_page == "Dashboard":
            st.write("📈 **Key Metrics:**")
            st.write("- Total Users: 1,234")
            st.write("- Active Loans: 567")
            st.write("- Total Crowdfunding: $89,012")

        elif current_page == "AI Recommendations":
            st.write("🤖 **AI-powered insights for financial decisions**")
            st.write("Coming soon...")

        elif current_page == "Transactions":
            st.write("💳 **Transaction History**")
            st.write("Your recent transactions will appear here.")

        elif current_page == "Crowdfunding":
            st.write("🤝 **Community Crowdfunding Projects**")
            st.write("Support projects that matter to your community.")

        elif current_page == "Microloans":
            st.write("📈 **Microloan Opportunities**")
            st.write("Small loans for big impact.")

        elif current_page == "Poverty Map":
            st.write("🗺️ **Interactive Poverty Map**")
            st.write("Visualize areas that need financial support.")

        elif current_page == "Profile":
            st.write("👤 **Your Profile**")
            st.write(f"Username: {st.session_state.current_user.get('username', 'User')}")
            st.write(f"Role: {'Admin' if st.session_state.get('is_admin', False) else 'User'}")

        st.info("This is a simplified version. Full functionality coming soon!")

    # Footer
    st.markdown("""
    <div class="footer">
        2023 SDG Finance Platform | Version 1.0.0 |
        <a href="#" style="color: #4b6cb7; text-decoration: none;">Help</a> |
        <a href="#" style="color: #4b6cb7; text-decoration: none;">Terms</a> |
        <a href="#" style="color: #4b6cb7; text-decoration: none;">Privacy</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

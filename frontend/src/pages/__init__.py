"""
This module imports all page modules to make them available for the main app.
"""

# Import all page modules
from .dashboard import show as show_dashboard
from .ai_recommendations import show as show_ai_recommendations
from .transactions import show as show_transactions
from .crowdfunding import show as show_crowdfunding
from .microloans import show as show_microloans
from .poverty_map import show as show_poverty_map
from .profile import show as show_profile
from .admin_panel import show as show_admin_panel

# Re-export the show functions for easier access in app.py
dashboard = show_dashboard
ai_recommendations = show_ai_recommendations
transactions = show_transactions
crowdfunding = show_crowdfunding
microloans = show_microloans
poverty_map = show_poverty_map
profile = show_profile
admin_panel = show_admin_panel

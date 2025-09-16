import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from ..services import api

def show():
    """Display the insights page with poverty data and recommendations."""
    st.title("Poverty Insights")
    
    # Tabs for different insights
    tab1, tab2, tab3 = st.tabs(["Poverty Overview", "AI Recommendations", "Impact Analysis"])
    
    with tab1:
        show_poverty_overview()
    
    with tab2:
        show_ai_recommendations()
    
    with tab3:
        show_impact_analysis()

def show_poverty_overview():
    """Display overview of poverty statistics and trends."""
    try:
        # In a real app, this would fetch from the API
        # poverty_data = api.get_poverty_insights()
        
        # Mock data for demonstration
        poverty_data = {
            'global_poverty_rate': 9.2,
            'people_in_poverty': 689000000,
            'regions': [
                {'name': 'Sub-Saharan Africa', 'poverty_rate': 40.2, 'population': 1150000000},
                {'name': 'South Asia', 'poverty_rate': 12.4, 'population': 1900000000},
                {'name': 'East Asia & Pacific', 'poverty_rate': 1.7, 'population': 2300000000},
                {'name': 'Latin America', 'poverty_rate': 24.1, 'population': 650000000},
                {'name': 'Middle East', 'poverty_rate': 7.2, 'population': 450000000},
            ],
            'trends': [
                {'year': 2015, 'rate': 10.1},
                {'year': 2016, 'rate': 9.8},
                {'year': 2017, 'rate': 9.5},
                {'year': 2018, 'rate': 9.3},
                {'year': 2019, 'rate': 9.2},
                {'year': 2020, 'rate': 9.5},
                {'year': 2021, 'rate': 9.2},
            ]
        }
        
        # Key metrics
        st.subheader("Global Poverty at a Glance")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Global Poverty Rate", f"{poverty_data['global_poverty_rate']}%")
        with col2:
            st.metric("People Living in Poverty", f"{poverty_data['people_in_poverty']:,}")
        
        # Poverty trends over time
        st.subheader("Poverty Rate Trends (2015-2021)")
        
        df_trends = pd.DataFrame(poverty_data['trends'])
        fig1 = px.line(
            df_trends,
            x='year',
            y='rate',
            markers=True,
            labels={'year': 'Year', 'rate': 'Poverty Rate (%)'},
            title='Global Poverty Rate Over Time'
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Regional poverty rates
        st.subheader("Poverty by Region")
        
        df_regions = pd.DataFrame(poverty_data['regions'])
        df_regions['people_in_poverty'] = (df_regions['poverty_rate'] / 100) * df_regions['population']
        
        # Sort by poverty rate (descending)
        df_regions = df_regions.sort_values('poverty_rate', ascending=False)
        
        # Bar chart for regional poverty rates
        fig2 = px.bar(
            df_regions,
            x='poverty_rate',
            y='name',
            orientation='h',
            labels={'name': 'Region', 'poverty_rate': 'Poverty Rate (%)'},
            title='Poverty Rate by Region',
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Regional data table
        st.subheader("Regional Poverty Data")
        
        # Format the data for display
        display_df = df_regions.copy()
        display_df['population'] = display_df['population'].apply(lambda x: f"{x:,}")
        display_df['people_in_poverty'] = display_df['people_in_poverty'].apply(lambda x: f"{int(x):,}")
        
        st.dataframe(
            display_df[['name', 'poverty_rate', 'population', 'people_in_poverty']],
            column_config={
                'name': 'Region',
                'poverty_rate': st.column_config.NumberColumn('Poverty Rate', format='%.1f%%'),
                'population': 'Population',
                'people_in_poverty': 'People in Poverty'
            },
            hide_index=True,
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Error loading poverty data: {str(e)}")

def show_ai_recommendations():
    """Display AI-powered recommendations for poverty alleviation."""
    try:
        # In a real app, this would fetch from the API
        # recommendations = api.get_ai_recommendations()
        
        # Mock data for demonstration
        recommendations = {
            'personalized_recommendations': [
                {
                    'title': 'Microsavings Program',
                    'description': 'Based on your transaction history, you could save an additional 10% of your income by reducing discretionary spending.',
                    'impact': 'High',
                    'effort': 'Low',
                    'category': 'Financial Planning'
                },
                {
                    'title': 'Education Investment',
                    'description': 'Investing in vocational training could increase your earning potential by up to 25% within 2 years.',
                    'impact': 'Very High',
                    'effort': 'Medium',
                    'category': 'Education'
                },
                {
                    'title': 'Community Support',
                    'description': 'Join a local savings group to build financial resilience and access to credit.',
                    'impact': 'Medium',
                    'effort': 'Low',
                    'category': 'Community'
                }
            ],
            'community_recommendations': [
                {
                    'title': 'Agricultural Co-op',
                    'description': 'Forming a farmers cooperative could increase income by 15-20% through bulk purchasing and collective bargaining.',
                    'beneficiaries': 'Small-scale farmers',
                    'cost_estimate': 'Low to Medium',
                    'timeframe': '6-12 months'
                },
                {
                    'title': 'Digital Literacy Program',
                    'description': 'Implementing digital skills training can open up remote work opportunities for community members.',
                    'beneficiaries': 'Youth and unemployed',
                    'cost_estimate': 'Medium',
                    'timeframe': '3-6 months'
                }
            ]
        }
        
        st.subheader("Personalized Recommendations")
        
        # Display personalized recommendations
        for idx, rec in enumerate(recommendations['personalized_recommendations'], 1):
            with st.expander(f"{idx}. {rec['title']}"):
                st.write(rec['description'])
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Impact", rec['impact'])
                with col2:
                    st.metric("Effort Required", rec['effort'])
                st.caption(f"Category: {rec['category']}")
        
        st.subheader("Community-Level Recommendations")
        
        # Display community recommendations
        for idx, rec in enumerate(recommendations['community_recommendations'], 1):
            with st.expander(f"{idx}. {rec['title']}"):
                st.write(rec['description'])
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Beneficiaries", rec['beneficiaries'])
                    st.metric("Cost Estimate", rec['cost_estimate'])
                with col2:
                    st.metric("Timeframe", rec['timeframe'])
        
        # Action buttons
        st.markdown("### Take Action")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect with Local Organizations"):
                st.session_state.show_organizations = True
        with col2:
            if st.button("Learn More About These Programs"):
                st.session_state.show_learn_more = True
        
        # Additional information based on user interaction
        if st.session_state.get('show_organizations', False):
            st.info("""
            ### Local Organizations
            - **Microfinance Institution**: Contact local branches for microloans
            - **Community Center**: Visit for training programs and support
            - **Government Office**: Inquire about social welfare programs
            """)
        
        if st.session_state.get('show_learn_more', False):
            st.info("""
            ### Additional Resources
            - [Guide to Financial Inclusion](https://example.com/financial-inclusion)
            - [Vocational Training Programs](https://example.com/vocational-training)
            - [Community Development Resources](https://example.com/community-dev)
            """)
    
    except Exception as e:
        st.error(f"Error loading recommendations: {str(e)}")

def show_impact_analysis():
    """Display impact analysis of poverty alleviation programs."""
    try:
        # In a real app, this would fetch from the API
        # impact_data = api.get_impact_analysis()
        
        # Mock data for demonstration
        impact_data = {
            'programs': [
                {
                    'name': 'Microfinance Initiative',
                    'year_started': 2018,
                    'participants': 1250,
                    'income_increase': 35.5,
                    'poverty_reduction': 18.2,
                    'success_rate': 82.5
                },
                {
                    'name': 'Education Grants',
                    'year_started': 2019,
                    'participants': 850,
                    'income_increase': 42.3,
                    'poverty_reduction': 22.7,
                    'success_rate': 78.9
                },
                {
                    'name': 'Agricultural Training',
                    'year_started': 2020,
                    'participants': 620,
                    'income_increase': 28.7,
                    'poverty_reduction': 15.4,
                    'success_rate': 75.2
                },
                {
                    'name': 'Healthcare Access',
                    'year_started': 2021,
                    'participants': 1500,
                    'income_increase': 12.8,
                    'poverty_reduction': 8.9,
                    'success_rate': 65.3
                }
            ]
        }
        
        st.subheader("Program Impact Analysis")
        
        # Convert to DataFrame for visualization
        df = pd.DataFrame(impact_data['programs'])
        
        # Sort by poverty reduction (descending)
        df = df.sort_values('poverty_reduction', ascending=False)
        
        # Impact comparison chart
        st.subheader("Program Impact Comparison")
        
        fig1 = go.Figure()
        
        # Add bars for income increase
        fig1.add_trace(go.Bar(
            x=df['name'],
            y=df['income_increase'],
            name='Income Increase (%)',
            marker_color='#1f77b4'
        ))
        
        # Add bars for poverty reduction
        fig1.add_trace(go.Bar(
            x=df['name'],
            y=df['poverty_reduction'],
            name='Poverty Reduction (%)',
            marker_color='#ff7f0e'
        ))
        
        # Update layout
        fig1.update_layout(
            barmode='group',
            xaxis_title='Program',
            yaxis_title='Percentage (%)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Success rate vs participants scatter plot
        st.subheader("Success Rate vs Number of Participants")
        
        fig2 = px.scatter(
            df,
            x='participants',
            y='success_rate',
            size='poverty_reduction',
            color='name',
            hover_name='name',
            size_max=50,
            labels={
                'participants': 'Number of Participants',
                'success_rate': 'Success Rate (%)',
                'name': 'Program',
                'poverty_reduction': 'Poverty Reduction (%)'
            },
            title='Program Effectiveness'
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Program details table
        st.subheader("Program Details")
        
        # Format the data for display
        display_df = df.copy()
        display_df['participants'] = display_df['participants'].apply(lambda x: f"{x:,}")
        display_df['income_increase'] = display_df['income_increase'].apply(lambda x: f"{x:.1f}%")
        display_df['poverty_reduction'] = display_df['poverty_reduction'].apply(lambda x: f"{x:.1f}%")
        display_df['success_rate'] = display_df['success_rate'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(
            display_df,
            column_config={
                'name': 'Program Name',
                'year_started': 'Year Started',
                'participants': 'Participants',
                'income_increase': 'Income Increase',
                'poverty_reduction': 'Poverty Reduction',
                'success_rate': 'Success Rate'
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Key takeaways
        st.subheader("Key Takeaways")
        
        st.markdown("""
        1. **Education Grants** show the highest income increase (42.3%) and second-highest poverty reduction (22.7%).
        2. **Microfinance Initiative** has the highest success rate (82.5%) and serves the most participants.
        3. **Healthcare Access** has the broadest reach but shows more modest impact metrics.
        4. Programs with more focused interventions (e.g., Agricultural Training) show strong results with smaller participant groups.
        """)
        
    except Exception as e:
        st.error(f"Error loading impact analysis: {str(e)}")

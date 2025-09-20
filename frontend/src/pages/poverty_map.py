import json
from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import get_auth_headers, format_currency, format_date, API_BASE_URL

def load_geojson_data(country_code):
    """Load GeoJSON data for the specified country."""
    # In a real app, this would load actual GeoJSON data for the country
    # For now, we'll return a simplified example for demonstration
    
    if country_code == 'TZ':  # Tanzania
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Dar es Salaam",
                        "poverty_rate": 28.4,
                        "population": 4364541,
                        "region": "Dar es Salaam"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [39.2083, -6.8161]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Mwanza",
                        "poverty_rate": 32.1,
                        "population": 706453,
                        "region": "Mwanza"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [32.8986, -2.5167]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Arusha",
                        "poverty_rate": 24.7,
                        "population": 416442,
                        "region": "Arusha"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [36.6833, -3.3667]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Dodoma",
                        "poverty_rate": 35.2,
                        "population": 410956,
                        "region": "Dodoma"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [35.7389, -6.1630]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Mbeya",
                        "poverty_rate": 38.6,
                        "population": 385279,
                        "region": "Mbeya"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [33.4500, -8.9000]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Morogoro",
                        "poverty_rate": 41.3,
                        "population": 315866,
                        "region": "Morogoro"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [37.6611, -6.8200]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Tanga",
                        "poverty_rate": 29.8,
                        "population": 273332,
                        "region": "Tanga"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [39.1000, -5.0667]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Kahama",
                        "poverty_rate": 45.7,
                        "population": 242208,
                        "region": "Shinyanga"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [32.6000, -3.8333]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Tabora",
                        "poverty_rate": 43.9,
                        "population": 226999,
                        "region": "Tabora"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [32.8000, -5.0167]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Zanzibar City",
                        "poverty_rate": 26.5,
                        "population": 205870,
                        "region": "Zanzibar"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [39.2000, -6.1667]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Sumbawanga",
                        "poverty_rate": 47.2,
                        "population": 209793,
                        "region": "Rukwa"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [31.6200, -7.9667]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Kigoma",
                        "poverty_rate": 42.8,
                        "population": 215458,
                        "region": "Kigoma"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [29.6167, -4.8833]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Moshi",
                        "poverty_rate": 22.4,
                        "population": 184292,
                        "region": "Kilimanjaro"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [37.3333, -3.3500]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Songea",
                        "poverty_rate": 39.5,
                        "population": 203309,
                        "region": "Ruvuma"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [35.6500, -10.6833]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Musoma",
                        "poverty_rate": 36.7,
                        "population": 134327,
                        "region": "Mara"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [33.8000, -1.5000]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Iringa",
                        "poverty_rate": 34.2,
                        "population": 151345,
                        "region": "Iringa"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [35.7000, -7.7667]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Singida",
                        "poverty_rate": 40.1,
                        "population": 150379,
                        "region": "Singida"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [34.7500, -4.8167]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Shinyanga",
                        "poverty_rate": 44.3,
                        "population": 161391,
                        "region": "Shinyanga"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [33.4167, -3.6667]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Bukoba",
                        "poverty_rate": 31.9,
                        "population": 128796,
                        "region": "Kagera"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [31.8167, -1.3333]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Mtwara",
                        "poverty_rate": 37.5,
                        "population": 108299,
                        "region": "Mtwara"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [40.1833, -10.2667]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Lindi",
                        "poverty_rate": 39.8,
                        "population": 41587,
                        "region": "Lindi"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [39.7000, -10.0000]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Sengerema",
                        "poverty_rate": 46.2,
                        "population": 58526,
                        "region": "Mwanza"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [32.5500, -2.6500]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Mpanda",
                        "poverty_rate": 43.7,
                        "population": 102900,
                        "region": "Katavi"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [31.0500, -6.3500]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Bariadi",
                        "poverty_rate": 42.9,
                        "population": 50315,
                        "region": "Simiyu"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [33.9833, -2.8000]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Njombe",
                        "poverty_rate": 35.8,
                        "population": 130223,
                        "region": "Njombe"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [34.7667, -9.3333]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Geita",
                        "poverty_rate": 41.5,
                        "population": 104939,
                        "region": "Geita"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [32.2333, -2.8667]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Babati",
                        "poverty_rate": 38.2,
                        "population": 93508,
                        "region": "Manyara"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [35.7500, -4.2167]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Sikonge",
                        "poverty_rate": 47.6,
                        "population": 42683,
                        "region": "Tabora"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [32.7667, -5.6333]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Kibaha",
                        "poverty_rate": 33.4,
                        "population": 128488,
                        "region": "Pwani"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [38.9167, -6.7667]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Kasulu",
                        "poverty_rate": 44.1,
                        "population": 208244,
                        "region": "Kigoma"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [30.1000, -4.5667]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Tunduma",
                        "poverty_rate": 36.9,
                        "population": 97614,
                        "region": "Mbeya"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [32.7667, -9.3000]
                    }
                }
            ]
        }
    else:
        # Return a default feature collection if country not found
        return {
            "type": "FeatureCollection",
            "features": []
        }

def get_poverty_indicators(country_code):
    """Get poverty indicators for the specified country."""
    # In a real app, this would fetch data from an API or database
    # For now, we'll return mock data
    
    if country_code == 'TZ':  # Tanzania
        return {
            "country": "Tanzania",
            "population": 59734218,
            "poverty_rate": 26.4,
            "extreme_poverty_rate": 15.7,
            "gini_index": 40.5,
            "rural_poverty_rate": 34.8,
            "urban_poverty_rate": 14.8,
            "year": 2022,
            "indicators": [
                {"name": "Population below poverty line", "value": "26.4%"},
                {"name": "Population in extreme poverty", "value": "15.7%"},
                {"name": "Gini coefficient", "value": "40.5"},
                {"name": "Rural poverty rate", "value": "34.8%"},
                {"name": "Urban poverty rate", "value": "14.8%"},
                {"name": "Human Development Index (HDI)", "value": "0.529"},
                {"name": "Life expectancy at birth", "value": "65.5 years"},
                {"name": "Mean years of schooling", "value": "6.2 years"},
                {"name": "Gross national income per capita", "value": "$2,780"}
            ]
        }
    else:
        # Return empty data if country not found
        return {
            "country": "",
            "population": 0,
            "poverty_rate": 0,
            "extreme_poverty_rate": 0,
            "gini_index": 0,
            "rural_poverty_rate": 0,
            "urban_poverty_rate": 0,
            "year": 2023,
            "indicators": []
        }

def get_poverty_trends(country_code):
    """Get poverty trends data for the specified country."""
    # In a real app, this would fetch data from an API or database
    # For now, we'll return mock data
    
    if country_code == 'TZ':  # Tanzania
        return {
            "country": "Tanzania",
            "years": [2007, 2012, 2018, 2022],
            "poverty_rate": [34.4, 28.2, 26.8, 26.4],
            "extreme_poverty_rate": [28.2, 19.3, 16.6, 15.7],
            "rural_poverty_rate": [37.6, 33.3, 35.5, 34.8],
            "urban_poverty_rate": [17.0, 12.3, 15.2, 14.8]
        }
    else:
        # Return empty data if country not found
        return {
            "country": "",
            "years": [],
            "poverty_rate": [],
            "extreme_poverty_rate": [],
            "rural_poverty_rate": [],
            "urban_poverty_rate": []
        }

def get_region_details(region_name):
    """Get details for a specific region."""
    # In a real app, this would fetch data from an API or database
    # For now, we'll return mock data
    
    region_data = {
        "Dar es Salaam": {
            "population": 4364541,
            "poverty_rate": 28.4,
            "main_industries": ["Trade", "Manufacturing", "Services", "Transportation"],
            "interventions": [
                "Urban poverty reduction program",
                "Skills development for youth",
                "Small business support"
            ],
            "challenges": [
                "High cost of living",
                "Unemployment",
                "Informal settlements"
            ]
        },
        "Mwanza": {
            "population": 706453,
            "poverty_rate": 32.1,
            "main_industries": ["Fishing", "Mining", "Agriculture", "Trade"],
            "interventions": [
                "Fishing industry support",
                "Agricultural extension services",
                "Small-scale mining regulation"
            ],
            "challenges": [
                "Climate change impacts",
                "Limited access to markets",
                "Youth unemployment"
            ]
        },
        "Arusha": {
            "population": 416442,
            "poverty_rate": 24.7,
            "main_industries": ["Tourism", "Agriculture", "Trade"],
            "interventions": [
                "Tourism development",
                "Agricultural value chain support",
                "Community-based conservation"
            ],
            "challenges": [
                "Seasonal employment",
                "Land use conflicts",
                "Climate variability"
            ]
        },
        "Dodoma": {
            "population": 410956,
            "poverty_rate": 35.2,
            "main_industries": ["Agriculture", "Government", "Trade"],
            "interventions": [
                "Irrigation development",
                "Government employment programs",
                "Infrastructure development"
            ],
            "challenges": [
                "Drought",
                "Limited economic diversification",
                "Rural-urban migration"
            ]
        },
        "Mbeya": {
            "population": 385279,
            "poverty_rate": 38.6,
            "main_industries": ["Agriculture", "Mining", "Trade"],
            "interventions": [
                "Agricultural productivity programs",
                "Mining sector formalization",
                "Cross-border trade facilitation"
            ],
            "challenges": [
                "Soil degradation",
                "Limited value addition",
                "Market access"
            ]
        },
        "Morogoro": {
            "population": 315866,
            "poverty_rate": 41.3,
            "main_industries": ["Agriculture", "Education", "Manufacturing"],
            "interventions": [
                "Agricultural research and extension",
                "Education and skills development",
                "Agro-processing support"
            ],
            "challenges": [
                "Land degradation",
                "Low agricultural productivity",
                "Limited access to finance"
            ]
        },
        "Tanga": {
            "population": 273332,
            "poverty_rate": 29.8,
            "main_industries": ["Agriculture", "Manufacturing", "Port Services"],
            "interventions": [
                "Port infrastructure development",
                "Sisal industry revitalization",
                "Tourism development"
            ],
            "challenges": [
                "Industrial decline",
                "Infrastructure gaps",
                "Youth unemployment"
            ]
        },
        "Kigoma": {
            "population": 215458,
            "poverty_rate": 42.8,
            "main_industries": ["Fishing", "Agriculture", "Trade"],
            "interventions": [
                "Refugee support programs",
                "Agricultural productivity initiatives",
                "Lake Tanganyika fisheries management"
            ],
            "challenges": [
                "Refugee influx",
                "Limited infrastructure",
                "Food insecurity"
            ]
        },
        "Moshi": {
            "population": 184292,
            "poverty_rate": 22.4,
            "main_industries": ["Tourism", "Coffee Production", "Education"],
            "interventions": [
                "Mountaineering tourism development",
                "Coffee value chain support",
                "Education and training programs"
            ],
            "challenges": [
                "Climate change impacts",
                "Seasonal employment",
                "Youth unemployment"
            ]
        },
        "Mtwara": {
            "population": 108299,
            "poverty_rate": 37.5,
            "main_industries": ["Agriculture", "Natural Gas", "Fishing"],
            "interventions": [
                "Natural gas industry development",
                "Agricultural modernization",
                "Infrastructure development"
            ],
            "challenges": [
                "Limited economic opportunities",
                "Infrastructure gaps",
                "Youth unemployment"
            ]
        }
    }
    
    return region_data.get(region_name, {
        "population": 0,
        "poverty_rate": 0,
        "main_industries": [],
        "interventions": [],
        "challenges": []
    })

def show():
    """Show the poverty map page."""
    st.title("Poverty Map")
    st.markdown("Visualize poverty data and explore regional insights.")
    
    # Country selection
    countries = {
        "Tanzania": "TZ",
        "Kenya": "KE",
        "Uganda": "UG",
        "Rwanda": "RW",
        "Burundi": "BI"
    }
    
    selected_country = st.selectbox(
        "Select Country",
        list(countries.keys()),
        index=0
    )
    
    country_code = countries[selected_country]
    
    # Load data for the selected country
    geojson_data = load_geojson_data(country_code)
    poverty_indicators = get_poverty_indicators(country_code)
    poverty_trends = get_poverty_trends(country_code)
    
    # Create a DataFrame from the GeoJSON features
    features = geojson_data.get("features", [])
    df = pd.DataFrame([{
        "name": f["properties"]["name"],
        "poverty_rate": f["properties"]["poverty_rate"],
        "population": f["properties"]["population"],
        "region": f["properties"]["region"],
        "lon": f["geometry"]["coordinates"][0],
        "lat": f["geometry"]["coordinates"][1]
    } for f in features])
    
    # Display the map
    st.subheader(f"Poverty Rate by Region in {selected_country}")
    
    if not df.empty:
        # Create a scatter mapbox figure
        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            color="poverty_rate",
            size="population",
            hover_name="name",
            hover_data={
                "poverty_rate": ":.1f%",
                "population": ",",
                "region": True,
                "lat": False,
                "lon": False
            },
            color_continuous_scale=px.colors.sequential.Reds,
            zoom=5,
            height=600,
            title=f"Poverty Rate by Region in {selected_country}"
        )
        
        # Update layout
        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            coloraxis_colorbar={
                "title": "Poverty Rate",
                "tickformat": ".0%"
            },
            hoverlabel={
                "bgcolor": "white",
                "font_size": 14,
                "font_family": "Arial"
            }
        )
        
        # Display the map
        st.plotly_chart(fig, use_container_width=True)
        
        # Add region selection
        selected_region = st.selectbox(
            "Select a region to view details",
            [""] + sorted(df["region"].unique().tolist()),
            index=0
        )
        
        if selected_region:
            # Display region details
            region_data = df[df["region"] == selected_region].iloc[0]
            region_details = get_region_details(selected_region)
            
            st.subheader(f"{selected_region} Region Details")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Population", f"{region_data['population']:,}")
            
            with col2:
                st.metric("Poverty Rate", f"{region_data['poverty_rate']:.1f}%")
            
            with col3:
                st.metric("Main City", region_data["name"])
            
            # Display additional region information
            st.markdown("#### Key Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Main Industries**")
                for industry in region_details["main_industries"]:
                    st.markdown(f"- {industry}")
                
                st.markdown("\n**Ongoing Interventions**")
                for intervention in region_details["interventions"]:
                    st.markdown(f"- {intervention}")
            
            with col2:
                st.markdown("**Key Challenges**")
                for challenge in region_details["challenges"]:
                    st.markdown(f"- {challenge}")
                
                # Add a button to view more details or take action
                if st.button("View Development Projects", key=f"projects_{selected_region}"):
                    st.session_state.view_projects = selected_region
    else:
        st.warning("No data available for the selected country.")
    
    # Display country-level poverty indicators
    st.subheader(f"Poverty Indicators for {selected_country}")
    
    if poverty_indicators["indicators"]:
        # Create a grid of indicator cards
        cols = st.columns(3)
        
        for i, indicator in enumerate(poverty_indicators["indicators"]):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style="
                        background: white;
                        border-radius: 8px;
                        padding: 1rem;
                        margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    ">
                        <div style="
                            color: #4b5563;
                            font-size: 0.9rem;
                            margin-bottom: 0.5rem;
                        ">
                            {indicator['name']}
                        </div>
                        <div style="
                            font-size: 1.25rem;
                            font-weight: 600;
                            color: #1f2937;
                        ">
                            {indicator['value']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No poverty indicators available for the selected country.")
    
    # Display poverty trends over time
    st.subheader("Poverty Trends")
    
    if poverty_trends["years"]:
        # Create a DataFrame for the trends
        trends_df = pd.DataFrame({
            "Year": poverty_trends["years"],
            "Poverty Rate": poverty_trends["poverty_rate"],
            "Extreme Poverty Rate": poverty_trends["extreme_poverty_rate"],
            "Rural Poverty Rate": poverty_trends["rural_poverty_rate"],
            "Urban Poverty Rate": poverty_trends["urban_poverty_rate"]
        })
        
        # Create a line chart
        fig = px.line(
            trends_df.melt(id_vars=["Year"], var_name="Indicator", value_name="Rate"),
            x="Year",
            y="Rate",
            color="Indicator",
            title=f"Poverty Trends in {selected_country} ({poverty_trends['years'][0]}-{poverty_trends['years'][-1]})",
            labels={"Rate": "Poverty Rate (%)"},
            markers=True
        )
        
        # Update layout
        fig.update_layout(
            legend_title="",
            hovermode="x",
            yaxis={"tickformat": ".1f"}
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trend data available for the selected country.")
    
    # Add a section for data sources and methodology
    with st.expander("Data Sources and Methodology"):
        st.markdown("""
        ### Data Sources
        - Poverty rate estimates are based on national household surveys and World Bank data
        - Population data comes from national statistical offices and UN population estimates
        - Regional boundaries are from the GADM database
        
        ### Methodology
        - Poverty rates are calculated based on national poverty lines
        - Urban and rural classifications follow national definitions
        - Trends are adjusted for comparability over time
        
        ### Notes
        - Data availability varies by country and year
        - Some estimates are based on modeling and may be revised
        - Regional data may have larger margins of error than national estimates
        """)
    
    # Add custom styles
    st.markdown("""
        <style>
            /* Style the select boxes */
            .stSelectbox > div > div > div {
                border-radius: 8px;
                padding: 0.5rem 0.75rem;
                border: 1px solid #e2e8f0;
            }
            
            /* Style the expander */
            .stExpander > div > div > div {
                background: #f8fafc;
                border-radius: 8px;
                padding: 1.5rem;
                border: 1px solid #e2e8f0;
            }
            
            /* Style the map container */n            .stPlotlyChart {
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            /* Style the indicator cards */
            .stMarkdown > div > div > div {
                margin-bottom: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)

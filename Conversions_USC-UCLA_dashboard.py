
import streamlit as st
import pandas as pd
import numpy as np
import ipaddress
import requests
import math
import time
import random
import pickle
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
import folium
import plotly.express as px
from streamlit_folium import st_folium
import sys


def intro():
 # Title shown in the app
    st.markdown("<h1 style='text-align: center;'>AnswersAi</h1>", unsafe_allow_html=True)
    st.sidebar.success("Select Dashboard above")

    st.image("answersai.png")

    st.write(sys.executable)

def tiktok_instagram_demo ():
    st.markdown("<h1 style='text-align: center;'>TikTok and Instagram Conversion Rates</h1>", unsafe_allow_html=True)

    #IMPORTANT VARIABLES
    #Tiktok
    TikTok_total_interactions = 76827
    Tiktok_total_coversions = 16285
    print(Tiktok_total_coversions)

    #Intagram
    Instagram_total_interactions = 94877

    #Organics
    organic_searches = 189152

    #Customer data

    #st.markdown(
     #   '''
      #  #### New customers since the last month
      #  '''
    #)
    #st.markdown(f"Total Number of New Customers: 246340 customers")
    new_customers = pd.read_csv("new_customers_8:27-9:30.csv")
    #st.dataframe(new_customers)


    #Tiktok ads manager data
    
    #st.markdown(
     #   '''
      #  #### Promotion data from TikTok Ads Manager
      #  '''
    #)
    
    app_promotion_tik_tok = pd.read_csv("Updated_tiktok_data.csv")
    #st.dataframe(app_promotion_tik_tok)

    #Total number of clicks generated by Tiktok Ads
    tiktok_ad_clicks = app_promotion_tik_tok['Clicks (destination)'].sum()

    #Total number of clicks generated from Tiktok Organics
    tiktok_organic_clicks = TikTok_total_interactions - tiktok_ad_clicks

    #Total number of Ad conversions based on TikTok Ads Manager Website
    tiktok_conversions_SKAN = app_promotion_tik_tok['Conversions (SKAN)'].sum()

    #Estimate number of Organic conversios
    tiktok_organic_conversion = Tiktok_total_coversions - tiktok_conversions_SKAN

    #Total number of Ad views
    tiktok_ad_views = app_promotion_tik_tok['Video views'].sum()

    #Total number of Organic views
    tiktok_organic_views = 56711563 - tiktok_ad_views # Manually recorded from tiktok account

    #Total number of impressions (number of times ads were shown)
    tiktok_impressions = app_promotion_tik_tok['Impressions'].sum()

    ### KPI Cards for Key Metrics
    st.markdown("### Key Performance Indicators (KPIs)")
    st.metric(label="Total TikTok Interactions", value=TikTok_total_interactions)
    st.metric(label="Total TikTok Conversions", value=Tiktok_total_coversions)
    st.metric(label="Total Instagram Interactions", value=Instagram_total_interactions)

    color_map = {'Ads': '#aec6cf', 'Organic': '#fdfd96'}

    st.markdown(
        '''
        ### Tiktok Ad vs. Organic Conversion Rates
        ''')
    conversion_data = {
        "Source": ["Ads", "Organic"],
        "Conversions": [tiktok_conversions_SKAN, tiktok_organic_conversion]
    }
    df_conversion = pd.DataFrame(conversion_data)
    fig_conversion = px.bar(df_conversion, x='Source', y='Conversions', title='TikTok Ad vs. Organic Conversion Rates',
                            labels={'Conversions': 'Total Conversions'}, text='Conversions', color='Source', color_discrete_map=color_map)
    st.plotly_chart(fig_conversion)

  

    #View to Click Conversion Rate
    st.markdown(
        '''
        ### **View-to-Click Conversion Rate**

        * **Ad Click-Through Rate (CTR):**  1.05%
        * **Organic Click-Through Rate (CTR):**  0.04%

        ''')

    #Visualizations for View-to-Click Conversion Rates below
    ctr_data = {
        "Source": ["Ads", "Organic"],
        "CTR (%)": [1.05, 0.04]
    }
    df_ctr = pd.DataFrame(ctr_data)

    fig_ctr = px.pie(df_ctr, names='Source', values='CTR (%)', title='View-to-Click CTR: Ads vs Organic', color='Source', color_discrete_map=color_map)
    st.plotly_chart(fig_ctr)

    
    #View-to-Conversion Rate
    st.markdown(
        '''  
        ### **View-to-Conversion Rate**

        * **Tiktok Ad View to Conversion Rate:** 0.19%
        * **Tiktok Ad View to Conversion Rate per 1 Million Views:** 0.0019%
        * **Tiktok Organic View to Conversion Rate:** 0.01%
        * **Tiktok Organic View to Conversion Rate per 1 Million Views:** 0.0001%   


        ''')

    #Visualizations for View-to-Conversion Rates below
    view_to_conversion_data = {
        "Source": ["Ad (Total)", "Ad (Per Million Views)", "Organic (Total)", "Organic (Per Million Views)"],
        "Conversion Rate (%)": [0.19, 0.0019, 0.01, 0.0001]
    }
    df_view_conversion = pd.DataFrame(view_to_conversion_data)

    # Define colors based on Ads and Organics
    color_map_extended = {'Ad (Total)': '#aec6cf', 'Ad (Per Million Views)': '#aec6cf', 
                          'Organic (Total)': '#fdfd96', 'Organic (Per Million Views)': '#fdfd96'}

    fig_view_conversion = px.bar(df_view_conversion, x='Source', y='Conversion Rate (%)', 
                                 title='View-to-Conversion Rates',
                                 labels={'Conversion Rate (%)': 'Conversion Rate'}, 
                                 text='Conversion Rate (%)', color='Source', color_discrete_map=color_map_extended)
    st.plotly_chart(fig_view_conversion)



    #Click-to-Conversion Rates
    st.markdown(
        '''
        ### **Click-to-Conversion Rates**

        * **Ad Click-to-Conversion Rate:** 18.06%
        * **Organic Click-to-Conversio Rate:** 31.49%

        '''
    )

    #Visualizations for Click-to-Conversion Rates below
    # Data for Click-to-Conversion Rate
    click_to_conversion_data = {
        "Source": ["Ads", "Organics"],
        "Click-to-Conversion Rate (%)": [18.06, 31.49]
    }
    df_click_conversion = pd.DataFrame(click_to_conversion_data)

    # Set the custom pastel colors for Ads (blue) and Organics (yellow)
    color_map = {'Ads': '#aec6cf', 'Organics': '#fdfd96'}

    # Plotting the bar chart with custom pastel colors
    fig_click_conversion = px.bar(df_click_conversion, 
                                  x='Source', 
                                  y='Click-to-Conversion Rate (%)',
                                  title='Click-to-Conversion Rates',
                                  labels={'Click-to-Conversion Rate (%)': 'Click-to-Conversion Rate'},
                                  text='Click-to-Conversion Rate (%)', 
                                  color='Source', 
                                  color_discrete_map=color_map)

    # Display the chart in Streamlit
    st.plotly_chart(fig_click_conversion)

    ### Line Plot: Engagement Over Time with Pastel Colors ###
    st.markdown("### Engagement Over Time (Line Plot)")
    
    # Adjusted time frame: August 30, 2024 to September 27, 2024
    time_data = {
        "Date": pd.date_range(start="2024-08-30", end="2024-09-27"),
        "Clicks": np.random.randint(1000, 5000, size=29),  # 29 days of data
        "Likes": np.random.randint(5000, 10000, size=29),
        "Comments": np.random.randint(200, 500, size=29)
    }
    df_time = pd.DataFrame(time_data)

    # Define pastel colors for each engagement metric
    line_color_map = {'Clicks': '#aec6cf', 'Likes': '#ffd1dc', 'Comments': '#fdfd96'}
    
    fig_line = px.line(df_time, x='Date', y=['Clicks', 'Likes', 'Comments'],
                       title="Daily Engagement Metrics Over Time (Aug 30 to Sep 27)",
                       labels={'value': 'Engagement Count', 'variable': 'Metric'},
                       color_discrete_map=line_color_map)
    
    st.plotly_chart(fig_line)

    ### Funnel Charts: TikTok Ads vs Organic with Pastel Colors ###
    st.markdown("### User Funnel: TikTok Ads vs Organic")
    
    # Funnel data for TikTok Ads
    tiktok_funnel_data = {
        "Stage": ["Impressions", "Clicks", "Conversions"],
        "TikTok Ads": [tiktok_impressions, tiktok_ad_clicks, tiktok_conversions_SKAN]
    }
    df_tiktok_funnel = pd.DataFrame(tiktok_funnel_data)

    # Funnel data for TikTok Organic
    tiktok_organic_funnel_data = {
        "Stage": ["Impressions", "Clicks", "Conversions"],
        "TikTok Organic": [tiktok_organic_views, tiktok_organic_clicks, tiktok_organic_conversion]
    }
    df_tiktok_organic_funnel = pd.DataFrame(tiktok_organic_funnel_data)

    # Define pastel colors for each funnel stage
    funnel_color_map = {'Impressions': '#c3b1e1', 'Clicks': '#b2fba5', 'Conversions': '#ffb347'}
    
    # Funnel chart for TikTok Ads
    fig_tiktok_funnel = px.funnel(df_tiktok_funnel, x='TikTok Ads', y='Stage', 
                                  title="TikTok Ads Funnel", color='Stage', 
                                  color_discrete_map=funnel_color_map)
    
    # Funnel chart for TikTok Organic
    fig_tiktok_organic_funnel = px.funnel(df_tiktok_organic_funnel, x='TikTok Organic', y='Stage', 
                                          title="TikTok Organic Funnel", color='Stage', 
                                          color_discrete_map=funnel_color_map)
    
    # Display both funnels side by side
    st.plotly_chart(fig_tiktok_funnel)
    st.plotly_chart(fig_tiktok_organic_funnel)



usc_coordinates = (34.022415, -118.285530)
ucla_coordinates = (34.0700 ,  -118.4398)

def haversine(coord1, coord2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance in kilometers

def nearest_university(lat, lon, threshold=8):
        if lat is None or lon is None:
            return 'OTHER', None, None

        ip_coords = (lat, lon)

        # Calculate distances to UCLA and USC
        dist_to_ucla = haversine(ip_coords, ucla_coordinates)
        dist_to_usc = haversine(ip_coords, usc_coordinates)

        # Determine if within the threshold
        if dist_to_ucla <= threshold:
            return 'UCLA', dist_to_ucla, dist_to_usc
        elif dist_to_usc <= threshold:
            return 'USC', dist_to_usc, dist_to_ucla
        else:
            return 'OTHER', dist_to_usc, dist_to_ucla

def usc_ucla_demo ():
    st.markdown("<h1 style='text-align: center;'>UCLA and USC User Analysis</h1>", unsafe_allow_html=True)

    # Load IP address data
    Ip_merged = pd.read_csv('IP_merged.csv')

    # University Assignment and Aggregation
    Ip_merged[['nearest_university', 'distance_to_nearest', 'distance_to_other']] = Ip_merged.apply(
        lambda row: pd.Series(nearest_university(row['latitude'], row['longitude'])), axis=1)

    # Calculate the total number of users for each university
    USC_users = Ip_merged[(Ip_merged['nearest_university'] == 'USC')]
    total_USC_users = USC_users["count"].sum()

    UCLA_users = Ip_merged[(Ip_merged['nearest_university'] == 'UCLA')]
    total_UCLA_users = UCLA_users["count"].sum()

    # Key highlights using Streamlit metrics
    st.markdown("### Key Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total USC Users", value=total_USC_users)
    with col2:
        st.metric(label="Total UCLA Users", value=total_UCLA_users)

    # Bar chart for USC vs UCLA users
    st.markdown("### Comparison of Users by University")
    university_counts = {
        'University': ['USC', 'UCLA'],
        'Users': [total_USC_users, total_UCLA_users]
    }
    df_counts = pd.DataFrame(university_counts)
    fig_bar = px.bar(df_counts, x='University', y='Users', title="USC vs UCLA Users", color='University',
                     color_discrete_map={'USC': '#990000', 'UCLA': '#2774AE'})
    st.plotly_chart(fig_bar)

    # Map visualization (using Folium) for users
    st.markdown("### Map of Users (USC and UCLA)")
    
    # Create a Folium map centered around LA
    m = folium.Map(location=[34.05, -118.25], zoom_start=10)

    # Add USC markers
    for _, row in USC_users.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            color='blue',
            fill=True,
            fill_color='#990000',
            fill_opacity=0.6,
        ).add_to(m)

    # Add UCLA markers
    for _, row in UCLA_users.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            color='green',
            fill=True,
            fill_color='#2774AE',
            fill_opacity=0.6,
        ).add_to(m)

    # Display the map in Streamlit
    st_folium(m, width=700, height=500)


def main():

    page_names_to_funcs = {
    "Intro": intro,
    "Tiktok/Instagram Conversion Rates": tiktok_instagram_demo,
    "UCLA/USC users": usc_ucla_demo,
}

    demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
    page_names_to_funcs[demo_name]()


if __name__ == "__main__":
    main()
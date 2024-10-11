
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
import altair as alt


def intro():
 # Title shown in the app
    st.markdown("<h1 style='text-align: center;'>AnswersAi Marketing Insights</h1>", unsafe_allow_html=True)
    st.sidebar.success("Select Dashboard above")

    st.image("answersai.png")


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
        ### Tiktok Ad vs. Organic Total Conversions
        ''')
    conversion_data = {
        "Source": ["Ads", "Organic"],
        "Conversions": [tiktok_conversions_SKAN, tiktok_organic_conversion]
    }
    df_conversion = pd.DataFrame(conversion_data)
    fig_conversion = px.bar(df_conversion, x='Source', y='Conversions', title='TikTok Ad vs. Organic Conversion Rates',
                            labels={'Conversions': 'Total Conversions'}, text='Conversions', color='Source', color_discrete_map=color_map)

    fig_conversion.update_traces(textposition='auto', textfont_size=16)  # Adjust text font size here
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

    fig_ctr.update_traces(textposition='auto', textfont_size=16)
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

    fig_view_conversion.update_traces(textposition='auto', textfont_size=16)
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

    fig_click_conversion.update_traces(textposition='auto', textfont_size=16)
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
    fig_tiktok_funnel.update_traces(textposition='auto', textfont_size=16)
    
    # Funnel chart for TikTok Organic
    fig_tiktok_organic_funnel = px.funnel(df_tiktok_organic_funnel, x='TikTok Organic', y='Stage', 
                                          title="TikTok Organic Funnel", color='Stage', 
                                          color_discrete_map=funnel_color_map)
    fig_tiktok_organic_funnel.update_traces(textposition='auto', textfont_size=16)

    # Display both funnels side by side
    st.plotly_chart(fig_tiktok_funnel)
    st.plotly_chart(fig_tiktok_organic_funnel)

#######################################################################################################################
# UCLA/USC
########################################################################################################################

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

    USC_UCLA = Ip_merged.value_counts('nearest_university').reset_index()
    usc_count = USC_UCLA.loc[USC_UCLA['nearest_university'] == 'USC', 'count'].values[0]
    ucla_count = USC_UCLA.loc[USC_UCLA['nearest_university'] == 'UCLA', 'count'].values[0]


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
        st.metric(label="Total USC Users", value=usc_count)
    with col2:
        st.metric(label="Total UCLA Users", value=ucla_count)

    # Bar chart for USC vs UCLA users
    st.markdown("### Comparison of Users by University")
    university_counts = {
        'University': ['USC', 'UCLA'],
        'Users': [usc_count, ucla_count]  # Use the counts here
    }
    df_counts = pd.DataFrame(university_counts)

    fig_bar = px.bar(df_counts, 
                    x='University', 
                    y='Users', 
                    title="USC vs UCLA Users", 
                    color='University', 
                    text="Users",
                    color_discrete_map={'USC': '#990000', 'UCLA': '#2774AE'})

    # Update the layout to ensure the text is displayed clearly and adjust font size
    fig_bar.update_traces(textposition='auto', textfont_size=16)  # Adjust text font size here

    # Display the bar chart
    st.plotly_chart(fig_bar)

    # Scatter plot on map using Plotly with custom legend
    st.markdown("### Scatter Plot of USC and UCLA Users on Map")

    # Combine the latitude and longitude for both USC and UCLA users and add labels
    usc_ucla_combined = pd.concat([USC_users[['latitude', 'longitude']], UCLA_users[['latitude', 'longitude']]])
    usc_ucla_combined['University'] = ['USC'] * len(USC_users) + ['UCLA'] * len(UCLA_users)

    # Remove rows with missing or invalid latitude or longitude values
    usc_ucla_combined = usc_ucla_combined.dropna(subset=['latitude', 'longitude'])

    # Plot using Plotly scatter_mapbox with larger marker size
    fig_map = px.scatter_mapbox(
        usc_ucla_combined,
        lat='latitude',
        lon='longitude',
        color='University',
        color_discrete_map={'USC': '#990000', 'UCLA': '#2774AE'},
        zoom=10,
        mapbox_style='open-street-map',
        title="USC and UCLA Users on Map",
    )

    # Explicitly increase marker size for the dots
    fig_map.update_traces(marker=dict(size=14))  # Increase dot size here (e.g., size=20)

    # Set the layout size for the map
    fig_map.update_layout(
        height=500,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend=dict(title="Legend", font=dict(size=10))
    )

    # Display the Plotly map in Streamlit
    st.plotly_chart(fig_map)

    # Create a density heatmap using Plotly
    fig_density = px.density_mapbox(
        usc_ucla_combined,
        lat='latitude',
        lon='longitude',
        z=None,  # If you don't have a "count" column, use None
        radius=10,  # Adjust radius for density smoothing
        center=dict(lat=34.05, lon=-118.25),  # Center around LA
        zoom=10,  # Adjust zoom level
        mapbox_style='open-street-map',  # Use 'open-street-map' instead of 'stamen-terrain'
        title="User Density Heatmap (USC and UCLA)"
    )

    # Display the density heatmap in Streamlit
    st.plotly_chart(fig_density)


#######################################################################################################################
# CHURN
#######################################################################################################################

def cancellations_demo():
    st.markdown("<h1 style='text-align: center;'>Cancellation Insights</h1>", unsafe_allow_html=True)

    ### KPI Cards for Key Metrics
    st.markdown("### Key Performance Indicators (KPIs)")

    Total_subscriptions =  21444 
    Total_cancellations = 10387
    Cancellation_rate = round(Total_cancellations /  Total_subscriptions, 2)

    st.metric(label="Total number of Subscriptions", value=Total_subscriptions)
    st.metric(label="Total cancellations", value=Total_cancellations)
    st.metric(label="Cancellation rate", value=f"{Cancellation_rate}%")

    # Data for the charts
    data = {
        'Category': ['Total Subscriptions', 'Total Cancellations'],
        'Count': [Total_subscriptions, Total_cancellations]
    }
    df = pd.DataFrame(data)

    # Bar Chart for Total Subscriptions and Cancellations using Plotly
    bar_fig = px.bar(df, x='Category', y='Count', title="Total Subscriptions vs Cancellations",
                     color='Category', color_discrete_sequence=px.colors.qualitative.Pastel,
                     text='Count', template='plotly_dark')

    # Adjust layout to fit better
    bar_fig.update_layout(
        title_font_size=20,
        xaxis_title=None,
        yaxis_title="Count",
        font=dict(size=14),
        showlegend=False,
        height=450,  # Adjust the height to fit better in the layout
        margin=dict(l=30, r=30, t=80, b=40),  # Adjust margins to fit the chart
        bargap=0.2,  # Reduce gap between bars
    )
    bar_fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')


    # Pie Chart for Cancellation Rate using Plotly
    pie_fig = px.pie(
        names=['Cancellations', 'Active Subscriptions'],
        values=[Total_cancellations, Total_subscriptions - Total_cancellations],
        title="Cancellation Rate",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    pie_fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.1, 0])

    # Display the charts in Streamlit
    st.plotly_chart(bar_fig, use_container_width=True)
    st.plotly_chart(pie_fig, use_container_width=True)

    
    #-------------------------------------------------------------------------------------------------------


    # Markdown header for the cancellation report
    st.markdown("## Reason Cancellation Report")
    st.markdown("""
    The following table provides insights into the reasons why users have canceled their subscriptions.
    The data is grouped by the cancellation reason, and the total count of cancellations is displayed for each reason.
    """)

    # Load and display the cancellation report table
    cancellation_reasons = pd.read_csv("cancellation_reasons.csv")

    # Display the DataFrame
    st.dataframe(cancellation_reasons)


        ## Visualization: Bar Chart for Cancellation Reasons
    st.markdown("### Top Cancellation Reasons")
    bar_fig_top10 = px.bar(cancellation_reasons, 
                        x='cancellation_reason',  
                        y='reason_count', 
                        title="Top Reasons for Cancellation",
                        color='cancellation_reason',  # Use cancellation reason for coloring
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        text='reason_count',
                        template='plotly_dark')

    # Customize the layout for better readability
    bar_fig_top10.update_layout(
        title_font_size=20,
        xaxis_title=None,
        yaxis_title="Cancellation Count",
        font=dict(size=14),
        showlegend=False,
        height=600,  # Adjust height as necessary
        margin=dict(l=30, r=30, t=80, b=200),  # Adjust margins to allow space for long text
    )

    bar_fig_top10.update_xaxes(tickangle=-45)  # Rotate x-axis labels for better fit
    bar_fig_top10.update_traces(texttemplate='%{text:.0f}', textposition='outside')

    # Display the chart
    st.plotly_chart(bar_fig_top10, use_container_width=True)


    


    #------------------------------------------------------------------------------------------------
    # Define the data from the query result
    tools_data = {
        "feature_used": [
            "highlight", 
            "snapshot", 
            "mobile ocr mode", 
            "auto mode", 
            "Summary"
        ],
        "usage_count": [16355, 10888, 2732, 1219, 411]
    }

    # Most Used Tools Before Cancellation
    st.markdown("## Most Used Tools Before Cancellation")
    most_used_tools = pd.read_csv("most_used_tools_before_cancellation_2.csv")
    st.dataframe(most_used_tools)

    # Bar Chart for Most Used Tools Before Cancellation
    bar_fig = px.bar(tools_data, 
                    x='feature_used', 
                    y='usage_count', 
                    title='Most Used Tools Before Cancellation',
                    color='feature_used',
                    text='usage_count',
                    color_discrete_sequence=px.colors.qualitative.Pastel)

    # Customize the layout
    bar_fig.update_layout(
        title_font_size=22,
        xaxis_title=None,
        yaxis_title="Usage Count",
        font=dict(size=16),  # Set font size to 16
        showlegend=False,
        height=600,  # Increased height for better readability
        margin=dict(l=30, r=30, t=80, b=150),
    )
    bar_fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')

    # Display the bar chart
    st.plotly_chart(bar_fig, use_container_width=True)


    #---------------------------------------------------------------------------------------------------------


    # Sample data for average daily subscribers
    avg_subscribers_data = {
        'day_of_month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                        11, 12, 13, 14, 15, 16, 17, 18,
                        19, 20, 21, 22, 23, 24, 25, 26,
                        27, 28, 29, 30, 31],
        'avg_daily_subscribers': [3221.0000, 3326.1667, 3630.0000, 2962.5000, 2725.3333,
                                3752.5000, 3580.1667, 3601.6667, 3575.8333, 3061.0000,
                                2335.7143, 2101.6667, 2655.6667, 2978.8333, 3072.8333,
                                2606.1667, 2287.8333, 2106.8333, 2058.5000, 1977.8333,
                                2090.6667, 2357.5000, 3655.1667, 4229.6667, 3859.8333,
                                4330.3333, 3475.0000, 3085.5000, 3238.8333, 3274.8333,
                                2242.0000],
        'avg_daily_cancellations': [7.0000, 22.0000, 5.0000, 9.0000, 15.0000,
                                 66.0000, 12.0000, 38.0000, 1.5000, 14.0000,
                                 13.0000, 10.0000, 27.0000, 15.0000, 13.0000,
                                 19.5000, 19.5000, 24.5000, 18.0000, 11.0000,
                                 24.0000, 24.5000, 18.5000, 19.0000, 20.0000,
                                 13.5000, 8.0000, 16.0000, 23.0000, 25.0000,
                                 27.0000]
    }
    # DAU Data
    st.markdown("## Cancellation Rate by day After Subscription")

    # Load the DAU data from the CSV
    dau_data = pd.read_csv("DAU_data.csv")
    avg_subscribers_df = pd.DataFrame(avg_subscribers_data)


    avg_subscribers_df["cancellation_rate"] = avg_subscribers_df['avg_daily_cancellations'] /  avg_subscribers_df['avg_daily_subscribers']

    # Display the dataframe
    st.dataframe(avg_subscribers_df)

    # Create a line plot for cancellation rates over days of use
    fig = px.line(avg_subscribers_df, 
                x='day_of_month',  # X-axis: days of use
                y='cancellation_rate',  # Y-axis: cancellation rate
                title="Cancellation Rates Over Time (First 30 Days)", 
                labels={'days_of_use': 'Days of Use', 'cancellation_rate': 'Cancellation Rate (%)'},
                template='plotly_dark')

    # Change the line color to a pastel color (e.g., light blue)
    fig.update_traces(mode='lines+markers', marker=dict(size=8, symbol='circle', color='#FFCAA4'), line=dict(color='#9EDCE1'))  # Pastel color

    # Customize the layout with grid lines and enhanced font size
    fig.update_layout(
        title_font_size=22,
        xaxis_title="Days of Use",
        yaxis_title="Cancellation Rate (%)",
        font=dict(size=16),
        height=600,
        xaxis=dict(showgrid=True),  # Add grid lines to x-axis
        yaxis=dict(showgrid=True),  # Add grid lines to y-axis
        hovermode="x unified",  # Unify hover information for both axes
    )

    # Optionally, you can smooth the line (if desired)
    # fig.update_traces(line_shape='spline')

    # Show the line chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


    #-------------------------------------------------------------------------------
    monthly_cancellation_data = {
    'month_date': ['2023-09-01', '2023-10-01', '2023-11-01', '2023-12-01', '2024-01-01', '2024-02-01', 
                   '2024-03-01', '2024-04-01', '2024-05-01', '2024-06-01', '2024-07-01', '2024-08-01', 
                   '2024-09-01'],
    'total_subscribers': [28894, 23182, 11088, 7141, 16803, 19885, 40542, 55185, 49927, 25413, 20768, 
                          142084, 209016],
    'total_cancellations': [591, 1880, 2981, 3218, 1068, 689, 980, 2302, 3535, 2408, 1663, 958, 1715],
    'cancellation_rate_percentage': [2.0454, 8.1097, 26.8849, 45.0637, 6.3560, 3.4649, 2.4172, 4.1714, 
                                     7.0803, 9.4755, 8.0075, 0.6742, 0.8205]
}

    # Create a DataFrame
    monthly_cancellation_df = pd.DataFrame(monthly_cancellation_data)

    # MAU Line Plot
    st.markdown("## Cancellation Rate by Months After Subscription")

    # Load the MAU data from the CSV
    mau_data = pd.read_csv("cancellation_rate_by_month.csv")

    # Display the dataframe
    st.dataframe(monthly_cancellation_df)

    # Create a line plot for cancellation rates over months of subscription (MAU)
    fig_mau = px.line(monthly_cancellation_df, 
                    x='month_date',  # X-axis: months after subscription
                    y='cancellation_rate_percentage',  # Y-axis: cancellation rate
                    title="Cancellation Rates Over Time (First 12 Months)", 
                    labels={'months_after_subscription': 'Months After Subscription', 'cancellation_rate': 'Cancellation Rate (%)'},
                    template='plotly_dark')

    # Customize the line and marker colors for contrast
    fig_mau.update_traces(mode='lines+markers', marker=dict(size=8, symbol='circle', color='#FFCAA4'), line=dict(color='#9EDCE1'))

    # Customize the layout with grid lines and enhanced font size
    fig_mau.update_layout(
        title_font_size=22,
        xaxis_title="Months After Subscription",
        yaxis_title="Cancellation Rate (%)",
        font=dict(size=16),
        height=600,
        xaxis=dict(showgrid=True),  # Add grid lines to x-axis
        yaxis=dict(showgrid=True),  # Add grid lines to y-axis
        hovermode="x unified",  # Unify hover information for both axes
    )

    # Show the MAU line chart in Streamlit
    st.plotly_chart(fig_mau, use_container_width=True)
    
#---------------------------------------------------------------------------------------------------------------------------------------


    ####CHURN RATE

        # Load the CSV file
    monthly_vs_lost_customers = pd.read_csv("churn_data.csv")
    st.markdown("### Monthly Churn Rate")

    # Calculate churn rate
    monthly_vs_lost_customers["churn_rate"] = (
        monthly_vs_lost_customers["monthly_cancellations"] / 
        monthly_vs_lost_customers["cumulative_subscribers"]
    ) * 100

    # Display the DataFrame
    st.dataframe(monthly_vs_lost_customers)

    # Create a line plot for churn rate over time
    fig = px.line(
        monthly_vs_lost_customers,
        x='month',  # X-axis: months
        y='churn_rate',  # Y-axis: churn rate
        title="Churn Rate Over Time",
        labels={'month_start': 'Month', 'churn_rate_2': 'Churn Rate (%)'},  # Custom labels
        template='plotly_dark'  # Dark theme
    )

    # Customize the plot
    fig.update_traces(
        mode='lines+markers',
        marker=dict(size=8, symbol='circle', color='#FFAA4D'),
        line=dict(color='#A1C181', width=3)
    )

    # Optional: Remove or adjust the vertical line if not needed
    # Removed the vertical line for simplicity

    # Enhance layout
    fig.update_layout(
        title_font_size=20,
        xaxis_title="Month",
        yaxis_title="Churn Rate (%)",
        font=dict(size=14),
        height=500,
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        hovermode="x unified"
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

        

def main():

    page_names_to_funcs = {
    "Intro": intro,
    "Tiktok/Instagram Conversion Rates": tiktok_instagram_demo,
    "UCLA/USC users": usc_ucla_demo,
    "Cancellation Insights": cancellations_demo
}

    demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
    page_names_to_funcs[demo_name]()


if __name__ == "__main__":
    main()
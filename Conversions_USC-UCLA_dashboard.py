
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
import os
from sshtunnel import SSHTunnelForwarder
import pymysql



#import re
#import phonenumbers
#from phonenumbers import geocoder
#from phonenumbers import region_code_for_number
#import pycountry
#import pycountry
#import langcodes



"""
##############################################################################################################################
##############################################################################################################################
SQL IMPLEMENTATION
##############################################################################################################################
##############################################################################################################################
"""""

# SSH and MySQL connection details
SSH_KEY_PATH = 'answerai.pem'  # Path to the SSH key file
SSH_HOST = '3.136.57.217'  # SSH server IP address (Ubuntu server)
SSH_USER = 'ubuntu'  # SSH username (Ubuntu)

MYSQL_HOST = 'answer-ai-read.ceyenxdmnayo.us-east-2.rds.amazonaws.com'  # MySQL RDS host
MYSQL_USER = 'admin'  # MySQL username
MYSQL_PASSWORD = 'XxK33vR7LlYKOVYGOZoC'  # MySQL password (you'll need to fill this in)
MYSQL_DB = 'answer-ai'  # MySQL database name
MYSQL_PORT = 3306  # MySQL default por


# Load sensitive info from Streamlit secrets management or environment variables
SSH_KEY_PATH = st.secrets["SSH_KEY_PATH"]
SSH_HOST = st.secrets["SSH_HOST"]
SSH_USER = st.secrets["SSH_USER"]
MYSQL_HOST = st.secrets["MYSQL_HOST"]
MYSQL_USER = st.secrets["MYSQL_USER"]
MYSQL_PASSWORD = st.secrets["MYSQL_PASSWORD"]
MYSQL_DB = st.secrets["MYSQL_DB"]
MYSQL_PORT = int(st.secrets["MYSQL_PORT"])


# Function to set up the SSH tunnel and database connection
def create_db_connection():
    try:
        server = SSHTunnelForwarder(
            (SSH_HOST, 22),
            ssh_username=SSH_USER,
            ssh_pkey=SSH_KEY_PATH,
            remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
        )
        server.start()
        
        connection = pymysql.connect(
            host='127.0.0.1',
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DB,
            port=server.local_bind_port
        )
        return server, connection
    except Exception as e:
        st.error("Error establishing SSH or database connection: {}".format(e))
        return None, None

# Cache query results to minimize repeated calls
@st.cache_data
def load_data(query):
    server, connection = create_db_connection()
    if connection is None:
        return pd.DataFrame()  # Return empty DataFrame if connection fails
    
    try:
        df = pd.read_sql(query, connection)
    except Exception as e:
        st.error("Error executing query: {}".format(e))
        df = pd.DataFrame()  # Return empty DataFrame if query fails
    finally:
        connection.close()
        server.stop()
    
    return df

subscribed_users_query = 'SELECT * FROM subscribed_users;'
subscribed_users = load_data(subscribed_users_query)


"""
##############################################################################################################################
##############################################################################################################################
AUTHENTICATION
##############################################################################################################################
##############################################################################################################################
"""""


# Simple authentication setup with a single password
def check_password(password):
    # Replace this with a more secure password storage method
    correct_password = "gobears"  # Set your password here
    return password == correct_password


# Function to handle the login screen
def login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # If user is already logged in, don't show the login prompt again
    if st.session_state["logged_in"]:
        return True

    # Display login form
    st.sidebar.title("Login")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if check_password(password):
            st.session_state["logged_in"] = True
            st.sidebar.success("Login successful!")
            return True
        else:
            st.sidebar.error("Invalid password")
            return False

    return False



def intro():
 # Title shown in the app
    st.markdown("<h1 style='text-align: center;'>AnswersAi Marketing Insights</h1>", unsafe_allow_html=True)
    st.sidebar.success("Select Dashboard above")

    st.image("answersai.png")

    st.dataframe(subscribed_users)


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
# CHURN/CANCELLATIONS
#######################################################################################################################

def cancellations_demo():
    st.markdown("<h1 style='text-align: center;'>Cancellation Insights</h1>", unsafe_allow_html=True)

    ### KPI Cards for Key Metrics
    st.markdown("### Cancellation Rate")

    # Load the CSV data
    monthly_cancellation_data = pd.read_csv("updated_subscrioptions_output.csv")
    monthly_cancellation_df = pd.DataFrame(monthly_cancellation_data)

    # Convert 'subscription_start_date' and 'cancellation_date' to datetime format
    monthly_cancellation_df['Subscription_Start'] = pd.to_datetime(monthly_cancellation_df['Subscription_Start'], errors='coerce')
    monthly_cancellation_df['Cancellation_Date'] = pd.to_datetime(monthly_cancellation_df['Cancellation_Date'], errors='coerce')

    # Step 1: Create 'subscription_month' and 'cancellation_month' columns
    monthly_cancellation_df['subscription_month'] = monthly_cancellation_df['Subscription_Start'].dt.to_period('M')
    monthly_cancellation_df['cancellation_month'] = monthly_cancellation_df['Cancellation_Date'].dt.to_period('M')

    # Step 2: Count new subscriptions per month (ignore cancellations here)
    subscriptions_per_month = monthly_cancellation_df.groupby('subscription_month')['customer_id'].count()

    # Step 3: Count new cancellations per month (ignoring NaT values in 'cancellation_month')
    cancellations_per_month = monthly_cancellation_df[~monthly_cancellation_df['cancellation_month'].isna()].groupby('cancellation_month')['customer_id'].count()

        # Step 1: Calculate cumulative subscriptions
    cumulative_subscriptions = subscriptions_per_month.cumsum()

    # Step 2: Calculate cumulative cancellations (shift by 1 to exclude current month's cancellations)
    cumulative_cancellations = cancellations_per_month.cumsum().shift(1, fill_value=0)

    # Step 3: Calculate active subscribers at the start of each month
    active_subscribers_per_month = cumulative_subscriptions - cumulative_cancellations
    active_subscribers_per_month = active_subscribers_per_month.clip(lower=0)  # Ensure no negative values

    # Step 4: Adjust cancellations per month to ensure cancellations do not exceed active subscribers
    adjusted_cancellations_per_month = cancellations_per_month.clip(upper=active_subscribers_per_month)

    # Step 1: Calculate cumulative subscriptions
    cumulative_subscriptions = subscriptions_per_month.cumsum()

    # Step 2: Calculate cumulative cancellations (shift by 1 to exclude current month's cancellations)
    cumulative_cancellations = cancellations_per_month.cumsum().shift(1, fill_value=0)

    # Step 3: Calculate active subscribers at the start of each month
    active_subscribers_per_month = cumulative_subscriptions - cumulative_cancellations
    active_subscribers_per_month = active_subscribers_per_month.clip(lower=0)  # Ensure no negative values

    # Step 4: Ensure cancellations in each month do not exceed the active subscribers at the start of the month
    adjusted_cancellations_per_month = cancellations_per_month.copy()

    for month in cancellations_per_month.index:
        if cancellations_per_month[month] > active_subscribers_per_month[month]:
            adjusted_cancellations_per_month[month] = active_subscribers_per_month[month]

    # Step 6: Calculate the cancellation rate (adjusted cancellations / active subscribers)
    cancellation_rate = (adjusted_cancellations_per_month / active_subscribers_per_month) * 100
    cancellation_rate = cancellation_rate.fillna(0)



    cancellation_rate_df = cancellation_rate.reset_index()
    cancellation_rate_df.columns = ['month', 'cancellation_rate']
    cancellation_rate_df['month'] = cancellation_rate_df['month'].astype(str)

    cancellations_monthly_df = pd.DataFrame({'Starting Active Subscribers': active_subscribers_per_month , 'Cancellations': adjusted_cancellations_per_month, 'Cancellation_Rate': cancellation_rate})

    st.dataframe(cancellations_monthly_df)

    # Create the line chart for cancellation rate with pastel tones and larger markers
    fig_cancellations = px.line(
        cancellation_rate_df,
        x='month',  # Make sure 'month' is the column representing your date
        y='cancellation_rate',  # Your y-axis data
        title="Monthly Cancellation Rate (%)",
        markers=True  # Adds dots to each data point
    )

    # Customize marker and line colors, marker size, and outline
    fig_cancellations.update_traces(
        marker=dict(size=10, color='lightskyblue', line=dict(width=2, color='black')),  # Larger markers with black outline
        line=dict(color='lightcoral')  # Pastel line color
    )

    # Customize the layout of the chart for better readability and pastel background
    fig_cancellations.update_layout(
        plot_bgcolor='whitesmoke',  # Light pastel background
        xaxis_title="Month",
        yaxis_title="Cancellation Rate (%)",
        title_font_size=20,
        font=dict(size=12),  # Adjust general font size
        hovermode="x unified",  # Show tooltip for the full x-axis
        width=1000,  # Set the width of the plot
        height=500,  # Set height for a balanced aspect ratio
        xaxis=dict(
            tickmode='linear',  # Ensure every month is shown
            dtick="M1",  # Tick every month
            tickformat="%b %Y",  # Format ticks as 'Jan 2024', etc.
            ticks="outside"
        )
    )

    # Display the figure in Streamlit
    st.plotly_chart(fig_cancellations, use_container_width=True)



    

#----------------------------------------------------------------------------------------------------------------------------
# CANCELLATION REASONS  
#----------------------------------------------------------------------------------------------------------------------------

    # Markdown header for the cancellation report
    st.markdown("## Cancellation Reason Insights")

    # Load and display the cancellation report table
    cancellation_reasons = pd.read_csv("Total_cancellations_by_reason.-2024-10-29-06-18-42.csv")
    monthly_cancellation_counts = pd.read_csv("Cancellation_Reasons_and_Total_Cancellations-2024-10-29-06-19-57.csv")

    
    # Rename "No Reason Recorded" to "No_Reason_Provided"
    cancellation_reasons['cancellation_reason'] = cancellation_reasons['cancellation_reason'].replace('No Reason Provided', 'No_Reason_Provided')
    monthly_cancellation_counts['cancellation_reason'] = monthly_cancellation_counts['cancellation_reason'].replace('No Reason Recorded', 'No_Reason_Provided')

    st.dataframe(cancellation_reasons)

    # Ensure total_cancellations is numeric
    monthly_cancellation_counts['total_cancellations'] = pd.to_numeric(monthly_cancellation_counts['total_cancellations'], errors='coerce')


     # Prepare the data for visualization
    cancellation_reason_trends = pd.pivot_table(monthly_cancellation_counts, 
                                                index='cancellation_month', 
                                                columns='cancellation_reason', 
                                                values='total_cancellations', 
                                                aggfunc='sum', 
                                                fill_value=0)

    # Reset index to bring 'cancellation_month' back as a column
    cancellation_reason_trends = cancellation_reason_trends.reset_index()

    cancellation_reasons = cancellation_reasons.rename(columns={"total_cancellations": "reason_count"})


    ## Visualization: Bar Chart for Cancellation Reasons

    #st.markdown("### Top Cancellation Reasons")

        # Define a consistent color mapping for "No_Reason_Provided"
    color_mapping = {
        'No_Reason_Provided': '#ff686b',  # Red color for "No_Reason_Provided"
        'unused': '#66c2a5',
        'low_quality': '#fc8d62',
        'too_expensive': '#e78ac3',
        'switched_service': '#a6d854',
        'other': '#ffd92f',
        'too_complex': '#8da0cb',
        'missing_features': '#e5c494',
        'customer_service': '#b3b3b3'
    }


    # First Bar Chart: Top Reasons for Cancellation
    bar_fig_top10 = px.bar(cancellation_reasons, 
                        x='cancellation_reason',  
                        y='reason_count', 
                        title="Top Reasons for Cancellation",
                        color='cancellation_reason',  # Use cancellation reason for coloring
                        color_discrete_map=color_mapping,  # Apply color mapping
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

    # Separate data for 'No Reason Recorded' and other reasons
    no_reason_data = monthly_cancellation_counts[monthly_cancellation_counts['cancellation_reason'] == 'No_Reason_Provided']
    other_reasons_data = monthly_cancellation_counts[monthly_cancellation_counts['cancellation_reason'] != 'No_Reason_Provided']

    # Line Plot for 'No Reason Recorded' cancellations
    fig_no_reason = px.line(
        no_reason_data,
        x='cancellation_month',
        y='total_cancellations',
        title="Monthly Cancellations - 'No_Reason_Provided'",
        markers=True,
        color_discrete_sequence=['#ff686b']  # Red color for consistency
    )

    fig_no_reason.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Cancellations",
        plot_bgcolor='whitesmoke',
        width=1000,
        height=500,
        title_font_size=20,
        xaxis=dict(tickangle=-45)
    )

    # Line Plot for other cancellation reasons
    fig_other_reasons = px.line(
        other_reasons_data,
        x='cancellation_month',
        y='total_cancellations',
        color='cancellation_reason',
        title="Monthly Cancellations by Reason (Excluding 'No_Reason_Provided)",
        markers=True,
        color_discrete_map=color_mapping  # Apply the same color mapping
    )

    fig_other_reasons.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Cancellations",
        plot_bgcolor='whitesmoke',
        width=1000,
        height=500,
        title_font_size=20,
        xaxis=dict(tickangle=-45)
    )

    # Display both plots in Streamlit
    st.plotly_chart(fig_no_reason, use_container_width=True)
    st.plotly_chart(fig_other_reasons, use_container_width=True)



#----------------------------------------------------------------------------------------------------------------------------
# TOOLS
#----------------------------------------------------------------------------------------------------------------------------
   
    # Define the data from the query result
    tools_data = {
        "feature_used": [
            "Mobile OCR Mode"
            "Snapshot", 
            "Highlight", 
            "Auto Mode", 
            "auto mode", 
            "Summarize"
        ],
        "usage_count": [199571, 5533, 4035, 600, 52]
    }

    # Most Used Tools Before Cancellation
    st.markdown("## Tool Insights")
    most_used_tools = pd.read_csv("most_used_tools_before_cancellation_2.csv")
    #st.dataframe(most_used_tools)
    monthly_cancellations_df = pd.read_csv("monthly_tool_cancellation.csv")

        # Define a color mapping for each tool used (using a variation of pastel colors)
    color_mapping = {
        'Mobile OCR Mode': '#a1dab4',  # Light Green
        'Snapshot': '#41b6c4',         # Cyan
        'Highlight': '#225ea8',        # Dark Blue
        'Auto Mode': '#ffeda0',        # Light Yellow
        'Summarize': '#f03b20'         # Red
    }
    # Most Used Tools Before Cancellation
    st.markdown("## Tool Insights")

    # Bar Chart for Most Used Tools Before Cancellation
    bar_fig = px.bar(
        tools_data, 
        x='feature_used', 
        y='usage_count', 
        title='Most Used Tools Before Cancellation',
        color='feature_used',
        text='usage_count',
        color_discrete_map=color_mapping
    )

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

    # Create a line plot to visualize the monthly changes for tool usage before cancellation
    line_fig = px.line(
        monthly_cancellations_df,
        x='usage_month',
        y='usage_count',
        color='feature_used',
        title='Monthly Tool Usage Before Cancellation',
        line_group='feature_used',
        markers=True,
        color_discrete_map=color_mapping
    )

    # Customize the layout for better readability
    line_fig.update_layout(
        title_font_size=20,
        xaxis_title='Month',
        yaxis_title='Usage Count',
        font=dict(size=14),
        height=600,
        margin=dict(l=30, r=30, t=80, b=150),
        plot_bgcolor='whitesmoke',
        hovermode='x unified'
    )

    # Customize traces for better visualization
    line_fig.update_traces(textposition='top center', textfont_size=10)

    # Display the line chart in Streamlit
    st.plotly_chart(line_fig, use_container_width=True)




#---------------------------------------------------------------------------------------------------------------------------
# CHURN RATE
#---------------------------------------------------------------------------------------------------------------------------------------

    st.markdown("## Churn Rate")

    # Creating a DataFrame with the data you provided
    new_churn = {
    'start_of_month': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01', '2024-05-01',
                       '2024-06-01', '2024-07-01', '2024-08-01', '2024-09-01', '2024-10-01'],
    'new_start_of_month_subscribers': [5618, 5855, 6091, 6814, 7521, 7573, 7708, 7749, 8621, 10239],
    'customers_lost': [1197, 749, 1174, 1430, 1462, 1192, 935, 1327, 2153, 1508],
    'new_churn_rate': [21.306515, 12.792485, 19.274339, 20.986205, 19.438904, 15.740129, 12.130254, 
                       17.124790, 24.973901, 14.728001]
}

    # Convert to DataFrame
    new_churn_df = pd.DataFrame(new_churn)

    # Convert 'start_of_month' to datetime for proper formatting
    new_churn_df['start_of_month'] = pd.to_datetime(new_churn_df['start_of_month'])

    # Display DataFrame
    st.dataframe(new_churn_df)

    # Create a Plotly line plot with pastel colors and dots
    churn_fig = px.line(new_churn_df, 
                x='start_of_month', 
                y='new_churn_rate', 
                title='Monthly Churn Rate (Jan to Oct 2024)',
                markers=True)

    # Customize the appearance (pastel colors, larger dots)
    churn_fig.update_traces(line_color='lightcoral', marker=dict(size=10, color='lightskyblue', line=dict(width=2, color='black')))
    churn_fig.update_layout(
        plot_bgcolor='whitesmoke',
        xaxis_title="Month",
        yaxis_title="Churn Rate (%)",
        title_font_size=20,
        font=dict(size=12),
        hovermode="x unified",
        width=1000,  # Set the plot width to make it wider
        height=500,  # Optionally, set height for a balanced aspect ratio
        xaxis=dict(
            tickmode='linear',  # Ensure every month is shown
            dtick="M1",         # One tick for each month
            tickformat="%b %Y",  # Format the ticks as 'Jan 2024', 'Feb 2024', etc.
            ticks="outside"
        )
    )

    # Display the plot in Streamlit
    st.plotly_chart(churn_fig)
   #---------------------------------------------------------------------------------------------------------------------------------------    

#    ### Retention Rates

        # Load the CSV file into a DataFrame
 #   retention_data = pd.read_csv('Retention_data.csv')
  #  retention_data = retention_data.rename(columns={"first_of_month": "month"})

    # Convert the 'first_of_month' column to datetime format if it's not already
 #   retention_data['month'] = pd.to_datetime(retention_data['month'])

    # Format the 'first_of_month' column to display only the year and month
#    retention_data['month'] = retention_data['month'].dt.to_period('M')

    # Check the column names to ensure they're correctly referenced
 #   st.write(retention_data.columns)

 #   retention_data['total_customers'] = pd.to_numeric(retention_data['total_customers'], errors='coerce')
 #   retention_data['active_after_7_days'] = pd.to_numeric(retention_data['active_after_7_days'], errors='coerce')
 #   retention_data['weekly_retention_rate'] = pd.to_numeric(retention_data['weekly_retention_rate'], errors='coerce')

    # Calculate retention rate
 #   retention_data['weekly_retention_rate'] = (retention_data['active_after_7_days'] / retention_data['total_customers']) * 100
 #   retention_data['monthly_retention_rate'] = (retention_data['active_after_30_days'] / retention_data['total_customers']) * 100
 #   retention_data['semesterly_retention_rate'] = (retention_data['active_after_6_months'] / retention_data['total_customers']) * 100

#    st.dataframe(retention_data)


    # Create line plot for retention rate
 #   st.markdown("### Weekly Retention Rates ")
 #   line_fig = px.line(
 #       retention_data, 
  #      x='month', 
 #       y='weekly_retention_rate', 
 #       title='Weekly Retention Rate',
 #       labels={'month': 'Month', 'retention_rate': 'Retention Rate (%)'},
 #       markers=True
 #   )
 #   st.plotly_chart(line_fig)

    # Create bar chart for new customers and active after 7 days with distinct colors
 #   st.markdown("### New Customers and Active Customers After 7 Days")
 #   bar_fig = px.bar(
 #       retention_data, 
 #       x='month', 
 #       y=['total_customers', 'active_after_7_days'], 
 #       title='New Customers and Active Customers After 7 Days',
 #       labels={'value': 'Count', 'variable': 'Customer Type'},
 #       barmode='group'
 #   )

    # Update colors for the bar chart
  #  bar_fig.update_traces(marker_color=['#1f77b4', '#ff7f0e'])

#    # Display the bar chart
#    st.plotly_chart(bar_fig)

    
def tools_demo():
    st.markdown("<h1 style='text-align: center;'>Tools Insights</h1>", unsafe_allow_html=True)

    st.markdown("## Most Used Tools")
    # Data from the SQL query result
    tools_data = {
        "feature_used_category": [
            "Mobile OCR Mode", 
            "Snapshot", 
            "Unrecorded", 
            "Highlight", 
            "Auto Mode", 
            "Summarize"
        ],
        "usage_count": [
            1321552, 
            525587, 
            508233, 
            199934, 
            81361, 
            9367
        ]
    }


    # Convert to DataFrame
    monthly_used_tools = pd.read_csv("monthly_tool_usage.csv")

    # Create the DataFrame
    tools_df = pd.DataFrame(tools_data)

    # Ensure total_tools_used is numeric (for monthly data)
    monthly_used_tools['monthly_usage_count'] = pd.to_numeric(monthly_used_tools['monthly_usage_count'], errors='coerce')
    # Standardize "summarize" to "Summarize" in the 'feature_used' column
    monthly_used_tools['feature_used'] = monthly_used_tools['feature_used'].replace('summarize', 'Summarize')

    # First Bar Chart: Top Tools Used
    color_mapping_tools = {
        'Mobile OCR Mode': '#66c2a5',       # Cyan
        'Snapshot': '#fc8d62',              # Yellow
        'No Tool Recorded': '#e78ac3',      # Orange
        'Highlight': '#a6d854',             # Light Purple
        'Auto Mode': '#ffd92f',             # Light Green
        'Summarize': '#a4b6dd'              # Light Blue
    }

    # First Bar Chart: Top Tools Used
    bar_fig_top_tools = px.bar(tools_data, 
                            x='feature_used_category',  
                            y='usage_count', 
                            title="Top Tools Used",
                            color='feature_used_category',  # Use tool category for coloring
                            color_discrete_map=color_mapping_tools,  # Apply color mapping
                            text='usage_count',
                            template='plotly_dark')

    # Customize the layout for better readability
    bar_fig_top_tools.update_layout(
        title_font_size=20,
        xaxis_title=None,
        yaxis_title="Usage Count",
        font=dict(size=14),
        showlegend=False,
        height=600,  # Adjust height as necessary
        margin=dict(l=30, r=30, t=80, b=200),  # Adjust margins to allow space for long text
    )

    bar_fig_top_tools.update_xaxes(tickangle=-45)  # Rotate x-axis labels for better fit
    bar_fig_top_tools.update_traces(texttemplate='%{text:.0f}', textposition='outside')

    # Display the chart
    st.plotly_chart(bar_fig_top_tools, use_container_width=True)

    # Line Plot for Monthly Tools Usage Breakdown
    fig_line_tools = px.line(
        monthly_used_tools,
        x='usage_month',
        y='monthly_usage_count',
        color='feature_used',
        title="Monthly Tools Usage Breakdown (Line Plot with Markers)",
        markers=True,  # Add markers to each point for better visualization
        color_discrete_map=color_mapping_tools  # Apply the same color mapping
    )

    # Customize the appearance of the line plot
    fig_line_tools.update_layout(
        plot_bgcolor='whitesmoke',
        xaxis_title="Month",
        yaxis_title="Usage Count",
        title_font_size=20,
        font=dict(size=12),
        hovermode="x unified",
        width=1000,
        height=600,
        xaxis=dict(tickangle=-45)  # Rotate x-axis labels for readability
    )

    # Display the line plot in Streamlit
    st.plotly_chart(fig_line_tools, use_container_width=True)




def main():

   # Check if the user is authenticated
    if login():
        # Page navigation after successful login
        page_names_to_funcs = {
            "Home": intro,
            "Tiktok/Instagram Conversion Rates": tiktok_instagram_demo,
            "UCLA/USC users": usc_ucla_demo,
            "Cancellation Insights": cancellations_demo,
            "Tool Insights": tools_demo
        }

        # Sidebar selectbox for demo navigation
        demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
        
        # Execute the function corresponding to the selected demo
        page_names_to_funcs[demo_name]()
    else:
        intro()
        # Display login screen if not authenticated
        st.write("Please enter the password to access the dashboard.")



if __name__ == "__main__":
    main()
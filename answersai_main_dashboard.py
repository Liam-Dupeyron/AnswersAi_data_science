import pandas as pd
import numpy as np
import requests
import math
import csv
import re
import seaborn as sns
import matplotlib.pyplot as plt
import os
import phonenumbers
from phonenumbers import geocoder
from phonenumbers import region_code_for_number
from phonenumbers import carrier
import pycountry
import langcodes
from langcodes import Language
from babel.core import Locale, get_global
import streamlit as st
import geopandas as gpd
import contextily as ctx
from streamlit_folium import st_folium
import sys
import altair as alt
import pymysql
from sshtunnel import SSHTunnelForwarder
import plotly.express as px
import folium




#################################################################################################################################
# INTRO
#################################################################################################################################


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

# Improved Home Page layout
def intro():
    # Title and branding
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 style="color: #4CAF50;">AnswersAi Marketing Insights</h1>
            
        """,
        
        unsafe_allow_html=True,
    )
    # Centered welcome text
    st.markdown(
        """
        <div style="text-align: center;">
            <h3>Welcome!</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Display logo
    logo = "answersai.png"  # Ensure this file is in the same directory
    try:
        st.image(logo)
    except Exception as e:
        st.warning("Logo not found. Please add 'answersai.png' to the working directory.")
    # Navigation prompt
    st.markdown(
        """
        <div style="text-align: center;">
            <p style="font-size: 14px; color: gray;">Use the navigation bar on the left to explore more.</p>
        </div>
        """,
        unsafe_allow_html=True,
        
    )


#################################################################################################################################
# SQL Connection
#################################################################################################################################



#################################################################################################################################
# Data Extraction
#################################################################################################################################

# Data cleaning subscribed_users dataframe
subscribed_users = pd.read_csv("/Users/liamdupeyron/Desktop/AnswersAi/main_data/subscribed_users_11-24.csv")

subscribed_users['created_at'] = pd.to_datetime(subscribed_users['created_at'], errors='coerce')
subscribed_users['updated_at'] = pd.to_datetime(subscribed_users['updated_at'], errors='coerce')

subscribed_users['canceled_at'] = pd.to_datetime(subscribed_users['canceled_at'], unit='s', errors='coerce')
subscribed_users['created_month'] = subscribed_users['created_at'].dt.to_period('M').dt.to_timestamp()
subscribed_users['cancellation_month'] = subscribed_users['canceled_at'].dt.to_period('M').dt.to_timestamp()

# Step 2: Define Hourly Cohorts
subscribed_users['creation_hour'] = subscribed_users['created_at'].dt.hour


# Calculate the time difference between 'created_at' and 'canceled_at' in hours
subscribed_users['time_to_cancel_hours'] = (
    (subscribed_users['canceled_at'] - subscribed_users['created_at']) / np.timedelta64(1, 'h')
)

# Calculate the time difference between 'created_at' and 'canceled_at' in hours
subscribed_users['time_to_cancel_minutes'] = (
    (subscribed_users['canceled_at'] - subscribed_users['created_at']) / np.timedelta64(1, 'm')
)

master_table = pd.read_csv("/Users/liamdupeyron/Desktop/AnswersAi/main_data/master_table.csv")

#################################################################################################################################
# Cancellation Rates
#################################################################################################################################

def cancellation_insights():
    # Title and branding
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Cancellation Insights</h1>
         </div>
            
        """, unsafe_allow_html=True,)

    st.markdown(
        "## Monthly Cancellation Rate"
    )
    # Assuming 'subscribed_users' is your DataFrame
    df = subscribed_users.copy()

    # Step 1: Calculate new subscriptions and cancellations per month
    new_subscriptions = df.groupby('created_month').size()
    cancellations = df.groupby('cancellation_month').size()

    # Step 2: Create a date range that includes all months
    all_months = pd.date_range(
        start=df['created_month'].min(),
        end=df['cancellation_month'].max(),
        freq='MS'
    )

    # Step 3: Reindex the Series to include all months
    new_subscriptions = new_subscriptions.reindex(all_months, fill_value=0)
    cancellations = cancellations.reindex(all_months, fill_value=0)

    # Step 4: Calculate cumulative totals
    cumulative_subscriptions = new_subscriptions.cumsum()
    cumulative_cancellations = cancellations.cumsum()

    # Step 5: Calculate active subscribers at end of each month
    active_subscribers_end = cumulative_subscriptions - cumulative_cancellations

    # Step 6: Calculate active subscribers at start of each month
    active_subscribers_start = active_subscribers_end.shift(1, fill_value=0)

    # Step 7: Calculate cancellation rate
    cancellation_rate = (cancellations / active_subscribers_end.replace(0, pd.NA)).round(2)
    cancellation_rate = cancellation_rate.fillna(0)

    # Step 8: Compile the results into a DataFrame
    results_df = pd.DataFrame({
        'Month': all_months,
        'New Subscriptions': new_subscriptions.values,
        'Cancellations': cancellations.values,
        'Active Subscribers at Start': active_subscribers_start.values,
        'Active Subscribers at End': active_subscribers_end.values,
        'Cancellation_Rate': cancellation_rate.values,
        'Same_Month_Cancellation_Rate': (cancellations / new_subscriptions).fillna(0).values
    })

    # Format the 'Month' column
    results_df['Month'] = results_df['Month'].dt.strftime('%Y-%m')

    # Create the line chart for cancellation rate with pastel tones and larger markers
    fig_cancellations = px.line(
        results_df,
        x='Month',  # Make sure 'month' is the column representing your date
        y='Cancellation_Rate',  # Your y-axis data
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
    st.plotly_chart(fig_cancellations, use_container_width=True)


    st.markdown(
        "## Hourly Cancellation Rate"
    )

    st.markdown(
        "## Daily Cancellation Rate"
    )


def questions_duplicates():
    # Title and branding
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Question Insights</h1>
         </div>
            
        """, unsafe_allow_html=True,)



def features():
    # Title and branding
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Feature Insights</h1>
         </div>
            
        """, unsafe_allow_html=True,)

def languages_countries():
    # Title and branding
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Country and Language Insights</h1>
         </div>
            
        """, unsafe_allow_html=True,)

# Main function with navigation
def main():
    # Check if the user is authenticated
    if login():
        # Define navigation layout
        st.sidebar.title("Navigation")
        st.sidebar.markdown("---")

        # Add navigation items (for now, only the home page)
        page_names_to_funcs = {
            "Home": intro,
            "Cancellation Insights": cancellation_insights,
            "Question Insights": questions_duplicates,
            "Feauture Insights": features,
            "Country and Language Insights": languages_countries

        }

        # Navigation via sidebar selectbox
        selected_page = st.sidebar.radio("Choose a page", list(page_names_to_funcs.keys()))
        
        # Render the selected page
        page_names_to_funcs[selected_page]()
    else:
        intro()
        st.write("Please enter the password to access the dashboard.")




if __name__ == "__main__":
    main()
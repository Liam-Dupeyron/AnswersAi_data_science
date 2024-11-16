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

def cancellation_rate():
    # Title and branding
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Cancellation rates</h1>
         </div>
            
        """, unsafe_allow_html=True,)


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
            "Cancellation Rates": cancellation_rate,
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
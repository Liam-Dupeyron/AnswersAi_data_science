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


def intro():
 # Title shown in the app
    st.markdown("<h1 style='text-align: center;'>AnswersAi Marketing Insights</h1>", unsafe_allow_html=True)
    st.sidebar.success("Select Dashboard above")

    st.image("answersai.png")


def main():

   # Check if the user is authenticated
    if login():
        # Page navigation after successful login
        page_names_to_funcs = {
            "Home": intro
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
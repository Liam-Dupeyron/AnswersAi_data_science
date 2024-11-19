import pandas as pd
import numpy as np
import requests
import math
import csv
import re
import matplotlib.pyplot as plt
import os
import phonenumbers
from phonenumbers import geocoder
from phonenumbers import region_code_for_number
from phonenumbers import carrier
import pycountry
import langcodes
from langcodes import Language
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
subscribed_users = pd.read_csv("subscribed_users_11-24.csv")

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

master_table = pd.read_csv("master_table.csv")

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

    # Monthly Cancellation Rate

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
        title="",
        markers=True  # Adds dots to each data point
    )

    # Customize marker and line colors, marker size, and outline
    fig_cancellations.update_traces(
        marker=dict(size=10, color='lightskyblue', line=dict(width=2, color='black')),  # Larger markers with black outline
        line=dict(color='lightcoral')  # Pastel line color
    )

    # Customize the layout of the chart for better readability and pastel background
    fig_cancellations.update_layout(
        title="",
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

    # Hourly and Daily Cancellation Rate

    # Calculate overall cancellation rates

    total_subscriptions = len(subscribed_users)
    total_cancellations = (subscribed_users['status'] == 'canceled').sum()

    # Cancellations within 1 hour
    cancellations_within_1_hour = subscribed_users[
        (subscribed_users['status'] == 'canceled') &
        (subscribed_users['time_to_cancel_hours'] <= 1)
    ].shape[0]

    # Cancellations within 24 hours
    cancellations_within_24_hours = subscribed_users[
        (subscribed_users['status'] == 'canceled') &
        (subscribed_users['time_to_cancel_hours'] <= 24)
    ].shape[0]

    # Calculate rates
    overall_cancellation_rate = total_cancellations / total_subscriptions
    overall_cancellation_rate_1h = cancellations_within_1_hour / total_subscriptions
    overall_cancellation_rate_24h = cancellations_within_24_hours / total_subscriptions


    # Aggregate cancellations within 1 hour
    df_one_hour = subscribed_users.groupby('created_month').apply(
        lambda x: pd.Series({
            'total_subscriptions': len(x),
            'cancellations_within_1_hour': x[
                (x['status'] == 'canceled') & (x['time_to_cancel_hours'] <= 1)
            ].shape[0],
            'cancellation_rate_within_one_hour': x[
                (x['status'] == 'canceled') & (x['time_to_cancel_hours'] <= 1)
            ].shape[0] / len(x)
        })
    ).reset_index()

    # Aggregate cancellations within 24 hours
    df_24_hours = subscribed_users.groupby('created_month').apply(
        lambda x: pd.Series({
            'total_subscriptions': len(x),
            'cancellations_within_24_hours': x[
                (x['status'] == 'canceled') & (x['time_to_cancel_hours'] <= 24)
            ].shape[0],
            'cancellation_rate_within_24_hours': x[
                (x['status'] == 'canceled') & (x['time_to_cancel_hours'] <= 24)
            ].shape[0] / len(x)
        })
    ).reset_index()


    st.markdown(
        "## 1 hour vs. 24 hour Cancellation Insights"
        )

    col1_hourly_daily, col2_proportion = st.columns(2)

    with col1_hourly_daily:
        # Data for overall cancellation rates
        data_hourly_daily = {
            "Cancellation Rate Type": ["1-Hour", "24-Hour"],  # Labels for the bar chart
            "Cancellation Rate (%)": [overall_cancellation_rate_1h * 100, overall_cancellation_rate_24h * 100]  # Convert to percentage
        }

        # Create a DataFrame
        overall_cancellation_df = pd.DataFrame(data_hourly_daily)

        # Plot the bar chart using Plotly Express
        fig = px.bar(
            overall_cancellation_df,
            x="Cancellation Rate Type",
            y="Cancellation Rate (%)",
            title="Cancellation Rates: 1 hr vs. 24 hr",
            text="Cancellation Rate (%)"  # Show values on the bars
        )

        # Customize the chart
        fig.update_traces(
            marker=dict(color=["lightskyblue", "lightcoral"], line=dict(width=2, color="black")),
            texttemplate='%{text:.2f}',  # Format the text values
            textposition='outside'  # Position text above the bars
        )
        fig.update_layout(
            title=dict(
                text="Cancellation Rates: 1 hr vs. 24 hr",
                font_size=15,
                x = 0.02# Center the title
            ),
            plot_bgcolor="whitesmoke",
            xaxis_title="Cancellation Rate Type",
            yaxis_title="Cancellation Rate (%)",
            title_font_size=20,
            font=dict(size=12),
            margin=dict(l=10, r=10, t=50, b=50),  # Adjust margins
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)  # Allow dynamic resizing
            

    with col2_proportion:
        # Calculate cancellations beyond 24 hours
        cancellations_beyond_24_hours = total_cancellations - cancellations_within_24_hours

        # Prepare data for the pie chart
        data_proportions = {
            "Cancellation Category": [
                "Within 1 Hour", 
                "Within 24 Hours", 
                "Beyond 24 Hours"
            ],
            "Count": [
                cancellations_within_1_hour, 
                cancellations_within_24_hours - cancellations_within_1_hour,  # Only the 1-24 hour range
                cancellations_beyond_24_hours
            ]
        }

        # Create a DataFrame
        cancellation_proportions_df = pd.DataFrame(data_proportions)

        # Create the pie chart using Plotly Express
        fig = px.pie(
            cancellation_proportions_df,
            names="Cancellation Category",
            values="Count",
            title="User Cancellation Breakdown"
        )

        # Customize the pie chart
        fig.update_traces(
            textinfo="percent",  # Show only percentages inside the slices
            textfont=dict(size=14),  # Adjust font size for percentages
            marker=dict(
                colors=["lightskyblue", "lightcoral", "lightgreen"],  # Pastel tones
                line=dict(width=2, color="black")  # Black outline for slices
            )
        )

        # Update layout for better positioning
        fig.update_layout(
            title=dict(
                text="User Cancellation Breakdown",
                font_size=18,  
                x = 0.05, # Center the title
            ),
            title_font_size=20,  # Decrease title font size for alignment
            font=dict(size=12),  # General font size
            margin=dict(l=10, r=10, t=50, b=50),  # Adjust margins
            plot_bgcolor="whitesmoke",  # Light pastel background
            showlegend=True,  # Keep legend visible
            legend=dict(
                orientation="h",  # Horizontal layout for legend
                x=0.5,  # Center legend horizontally
                xanchor="center",
                y=0.035,  # Move legend closer to the chart
                font=dict(size=12)  # Adjust legend font size
            )
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)  # Allow dynamic resizing
            

#################################################################################################################################
# Questions/Duplicate Insights
#################################################################################################################################


def questions_duplicates():
    # Title and branding
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Question Insights</h1>
         </div>
            
        """, unsafe_allow_html=True,)


    st.markdown(
        "## Duplicate Questions"
    )

    
#----------------------------------------------------------------------------------------------------------------------------
# Proportion of Duplicate Questions 
#----------------------------------------------------------------------------------------------------------------------------

    # Calculate total questions and total duplicate questions for each status
    total_questions_by_status = master_table.groupby('status')['questions_asked'].sum()
    total_duplicates_by_status = master_table.groupby('status')['duplicate_questions'].sum()

    # Calculate the proportion of duplicate questions for each status
    proportions_by_status = (total_duplicates_by_status / total_questions_by_status) * 100

    # Prepare data for the bar chart
    data_duplicate_proportions = {
        "User Status": proportions_by_status.index,
        "Proportion of Duplicate Questions (%)": proportions_by_status.values
    }
    df_duplicate_proportions = pd.DataFrame(data_duplicate_proportions)

    # Create a bar chart with Plotly Express
    fig_duplicate_proportions = px.bar(
        df_duplicate_proportions,
        x="User Status",
        y="Proportion of Duplicate Questions (%)",
        title="Proportion of Duplicate Questions by User Status",
        text="Proportion of Duplicate Questions (%)"  # Display percentages on the bars
    )

    # Customize the chart
    fig_duplicate_proportions.update_traces(
        texttemplate='%{text:.2f}%',  # Format text as percentages
        textposition="outside",  # Place text above the bars
        marker=dict(color=px.colors.qualitative.Pastel, line=dict(width=2, color="black"))  # Pastel tones with black outlines
    )
    fig_duplicate_proportions.update_layout(
        plot_bgcolor="whitesmoke",
        xaxis_title="User Status",
        yaxis_title="Proportion of Duplicate Questions (%)",
        title_font_size=20,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50),  # Adjust margins for clean spacing
        yaxis=dict(gridcolor="lightgray"),  # Add gridlines to y-axis
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.2
        )
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig_duplicate_proportions, use_container_width=True)

    
    # Proportion by User Type
    

    # Proportion of duplicate questions for cancelled users within 1 hour
    total_hourly_questions_cancelled = master_table[(master_table['status_code'] == 2) & (master_table['time_to_cancel_hours'] <= 1)]['questions_asked'].sum()
    total_hourly_duplicates_cancelled = master_table[(master_table['status_code'] == 2) & (master_table['time_to_cancel_hours'] <= 1)]['duplicate_questions'].sum()
    proportion_hourly_duplicates_cancelled = total_hourly_duplicates_cancelled / total_hourly_questions_cancelled if total_hourly_questions_cancelled > 0 else 0

    # Proportion of duplicate questions for active users within the first hour
    total_hourly_questions_active = master_table[(master_table['status_code'] == 0)]['questions_first_hour'].sum()
    total_hourly_duplicates_active = master_table[(master_table['status_code'] == 0)]['duplicate_questions_first_hour'].sum()
    proportion_hourly_duplicates_active = total_hourly_duplicates_active / total_hourly_questions_active if total_hourly_questions_active > 0 else 0
    
    # Proportion of duplicate questions for cancelled users within 1 hour
    total_daily_questions_cancelled = master_table[(master_table['status_code'] == 2) & (master_table['time_to_cancel_hours'] <= 24)]['questions_asked'].sum()
    total_daily_duplicates_cancelled = master_table[(master_table['status_code'] == 2) & (master_table['time_to_cancel_hours'] <= 24)]['duplicate_questions'].sum()
    proportion_daily_duplicates_cancelled = total_daily_duplicates_cancelled / total_daily_questions_cancelled if total_daily_questions_cancelled > 0 else 0

    # Proportion of duplicate questions for active users within the first hour
    total_daily_questions_active = master_table[(master_table['status_code'] == 0)]['questions_first_24_hours'].sum()
    total_daily_duplicates_active = master_table[(master_table['status_code'] == 0)]['duplicate_questions_first_24_hours'].sum()
    proportion_daily_duplicates_active = total_daily_duplicates_active / total_daily_questions_active if total_daily_questions_active > 0 else 0

        # Prepare the data for visualization
    data_duplicates = {
        "Time Interval": ["Within 1 Hour", "Within 1 Hour", "Within 24 Hours", "Within 24 Hours"],
        "User Type": ["Cancelled Users", "Active Users", "Cancelled Users", "Active Users"],
        "Proportion of Duplicate Questions": [
            proportion_hourly_duplicates_cancelled,  # Duplicate questions for cancelled users within 1 hour
            proportion_hourly_duplicates_active,  # Duplicate questions for active users within 1 hour
            proportion_daily_duplicates_cancelled,  # Duplicate questions for cancelled users within 24 hours
            proportion_daily_duplicates_active  # Duplicate questions for active users within 24 hours
        ]
    }


    # Create a DataFrame
    df_duplicates = pd.DataFrame(data_duplicates)

    # Create a grouped bar chart
    fig = px.bar(
        df_duplicates,
        x="Time Interval",
        y="Proportion of Duplicate Questions",
        color="User Type",  # Group by user type
        barmode="group",  # Place bars side by side
        title="Proportion of Duplicate Questions by User Type and Time Interval",
        text="Proportion of Duplicate Questions",
        color_discrete_map={
        "Cancelled Users": "#68c4af",
        "Active Users": "#1b85b8"
    }  # Show proportions as labels on the bars
    )

    # Customize the chart
    fig.update_traces(
        texttemplate='%{text:.2%}',  # Format text as percentages
        textposition="outside",  # Place labels above the bars
        marker=dict(line=dict(width=2, color="black")),  # Add black outlines to bars

    )
    fig.update_layout(
        plot_bgcolor="whitesmoke",
        xaxis_title="Time Interval",
        yaxis_title="Proportion of Duplicate Questions (%)",
        title_font_size=20,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=120, b=90),
        yaxis=dict(
        range=[0, 0.55],  # Set a fixed range with extra space at the top
        ),
        legend=dict(
            title="User Type",
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.2  # Move legend below the chart
        )
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

   
#----------------------------------------------------------------------------------------------------------------------------
# Feature Insights in Relation to Duplicates 
#----------------------------------------------------------------------------------------------------------------------------

    st.markdown(
        "## Feature Usage"
    )

    # Overall Feature Usage per Duplicate Questions
    
    # Calculate total questions and total duplicate questions for each feature
    total_questions_by_feature = master_table.groupby('feature_used')['questions_asked'].sum()
    total_duplicates_by_feature = master_table.groupby('feature_used')['duplicate_questions'].sum()

    # Calculate the proportion of duplicate questions for each feature
    proportions_by_feature = (total_duplicates_by_feature / total_questions_by_feature) * 100

    # Prepare data for the bar chart
    data_features_duplicates = {
        "Feature Used": proportions_by_feature.index,
        "Proportion of Duplicate Questions (%)": proportions_by_feature.values
    }
    df_features_duplicates = pd.DataFrame(data_features_duplicates)

    # Create a horizontal bar chart with Plotly Express
    fig_features_duplicates = px.bar(
        df_features_duplicates,
        y="Feature Used",  # Use 'y' for horizontal bars
        x="Proportion of Duplicate Questions (%)",
        color="Feature Used",  # Assign a different color to each feature
        title="Overall Proportion of Duplicate Questions by Feature Used",
        text="Proportion of Duplicate Questions (%)",
        color_discrete_sequence=px.colors.qualitative.Set2  # Display values on the bars
    )

    # Customize the chart
    fig_features_duplicates.update_traces(
        texttemplate='%{text:.2f}%',  # Format text as percentages
        textposition="outside",  # Place text to the right of the bars
        marker=dict(line=dict(width=1, color="black"))  # Add black outlines to bars
    )

    fig_features_duplicates.update_layout(
        plot_bgcolor="whitesmoke",
        xaxis_title="Proportion of Duplicate Questions (%)",
        yaxis_title="Feature Used",
        title_font_size=20,
        font=dict(size=12),
        margin=dict(l=120, r=50, t=80, b=50),
        xaxis=dict(
            range=[0, 70],  # Adjust x-axis range to fit all bars
            title_standoff=10  # Add space between axis title and labels
        ),  # Adjust margins for cleaner layout
        yaxis=dict(
            categoryorder="total ascending"  # Order features by their proportion
        ),
        coloraxis_showscale=False  # Remove the color scale legend for cleaner look
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig_features_duplicates, use_container_width=True)

    # 1 hr vs. 24 hr Feature Usage

    # Data Preparation

    if 'cancel_within_1h' not in master_table.columns:
        master_table['cancel_within_1h'] = ((master_table['status'] == 'canceled') & (master_table['time_to_cancel_hours'] <= 1)).astype(int)

    if 'cancel_within_24h' not in master_table.columns:
        master_table['cancel_within_24h'] = ((master_table['status'] == 'canceled') & (master_table['time_to_cancel_hours'] <= 24)).astype(int)

    # Filter users who canceled within 1 hour
    cancelled_within_1h = master_table[master_table['cancel_within_1h'] == 1]

    # Filter users who canceled within 24 hours
    cancelled_within_24h = master_table[master_table['cancel_within_24h'] == 1]

    # Group by feature_used and calculate total duplicate questions and total users
    duplicates_cancel_1h_feature = cancelled_within_1h.groupby('feature_used').agg(
        total_duplicate_questions=('duplicate_questions', 'sum'),
        total_users=('user_id', 'nunique')
    ).reset_index()

    # Calculate proportion of duplicate questions
    duplicates_cancel_1h_feature['proportion_duplicates'] = duplicates_cancel_1h_feature['total_duplicate_questions'] / duplicates_cancel_1h_feature['total_duplicate_questions'].sum()

    # Handle division by zero and fill NaN values
    duplicates_cancel_1h_feature['proportion_duplicates'].fillna(0, inplace=True)

    # Group by feature_used and calculate total duplicate questions and total users
    duplicates_cancel_24h_feature = cancelled_within_24h.groupby('feature_used').agg(
        total_duplicate_questions=('duplicate_questions', 'sum'),
        total_users=('user_id', 'nunique')
    ).reset_index()

    # Calculate proportion of duplicate questions
    duplicates_cancel_24h_feature['proportion_duplicates'] = duplicates_cancel_24h_feature['total_duplicate_questions'] / duplicates_cancel_24h_feature['total_duplicate_questions'].sum()

    # Handle division by zero and fill NaN values
    duplicates_cancel_24h_feature['proportion_duplicates'].fillna(0, inplace=True)

    # Add a 'cancellation_window' column to the dataframes
    duplicates_cancel_1h_feature['cancellation_window'] = 'Within 1 Hour'
    duplicates_cancel_24h_feature['cancellation_window'] = 'Within 24 Hours'

    # Combine the data
    combined_duplicates_feature = pd.concat([duplicates_cancel_1h_feature, duplicates_cancel_24h_feature], ignore_index=True)

    # Sort the data by proportion_duplicates
    combined_duplicates_feature = combined_duplicates_feature.sort_values('proportion_duplicates', ascending=False)

        # Calculate percentages for annotations
    combined_duplicates_feature['percentage_text'] = (
        combined_duplicates_feature['proportion_duplicates'] * 100
    ).round(2).astype(str) + "%"

    # Create the bar plot using Plotly Express
    fig_combined_duplicates_feature = px.bar(
        combined_duplicates_feature,
        x="proportion_duplicates",
        y="feature_used",
        color="cancellation_window",
        orientation="h",  # Horizontal bar plot
        barmode="group",
        title="Proportion of Duplicate Questions by Feature and Cancellation Window",
        text="percentage_text",  # Display percentages as text
        labels={
            "proportion_duplicates": "Proportion of Duplicate Questions",
            "feature_used": "Feature Used",
        },
        color_discrete_sequence=["lightcoral", "lightskyblue"],  # Custom pastel color scheme
    )

    # Customize the chart
    fig_combined_duplicates_feature.update_traces(
        textposition="outside",  # Place text outside the bars
        textfont=dict(size=10),  # Adjust text font size
        cliponaxis=False,  # Prevent text from being clipped
        marker=dict(line=dict(width=1, color="black")),  # Add black outlines to bars
    )

    # Customize layout
    fig_combined_duplicates_feature.update_layout(
        plot_bgcolor="whitesmoke",
        title_font_size=20,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50),  # Adjust margins
        legend=dict(
            title="Cancellation Window",
            orientation="h",
            y=1.05,
            x=0.5,
            xanchor="center",
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0.7)",
        ),
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig_combined_duplicates_feature, use_container_width=True)


#----------------------------------------------------------------------------------------------------------------------------
# Monthly Breakdown for Duplicate Questions
#----------------------------------------------------------------------------------------------------------------------------

    st.markdown(
        "## Monthly Breakdown"
    )

    # Overall Monthly Breakdown for Duplicate Questions

    # Group by subscription month to calculate total duplicate questions for active and canceled users
    total_duplicates_monthly_cancelled = master_table[master_table['status_code'] == 2].groupby('created_month')[
        'duplicate_questions'].sum().reset_index()
    total_duplicates_monthly_active = master_table[master_table['status_code'] == 0].groupby('created_month')[
        'duplicate_questions'].sum().reset_index()

    # Rename columns for clarity
    total_duplicates_monthly_cancelled.rename(columns={'duplicate_questions': 'total_duplicate_questions_cancelled'}, inplace=True)
    total_duplicates_monthly_active.rename(columns={'duplicate_questions': 'total_duplicate_questions_active'}, inplace=True)

    # Merge the dataframes
    total_duplicates_monthly = pd.merge(
        total_duplicates_monthly_cancelled,
        total_duplicates_monthly_active,
        on='created_month',
        how='outer'
    ).fillna(0)

    # Sort data by month
    total_duplicates_monthly = total_duplicates_monthly.sort_values("created_month")

    # Prepare data for Plotly
    data_total_duplicates = pd.melt(
        total_duplicates_monthly,
        id_vars=["created_month"],
        value_vars=["total_duplicate_questions_cancelled", "total_duplicate_questions_active"],
        var_name="User Status",
        value_name="Total Duplicate Questions"
    )

    data_total_duplicates["User Status"] = data_total_duplicates["User Status"].replace({
        "total_duplicate_questions_cancelled": "Cancelled Users",
        "total_duplicate_questions_active": "Active Users"
    })

    # Create the line plot
    fig_total_duplicates = px.line(
        data_total_duplicates,
        x="created_month",
        y="Total Duplicate Questions",
        color="User Status",
        title="Monthly Breakdown of Total Duplicate Questions by User Status",
        labels={"created_month": "Subscription Month"},
        markers=True
    )

    # Customize the plot
    fig_total_duplicates.update_traces(
        marker=dict(size=8, line=dict(width=1, color="black")),  # Markers with black outlines
        line=dict(width=2)  # Increase line width
    )

    # Update layout
    fig_total_duplicates.update_layout(
        plot_bgcolor="whitesmoke",
        xaxis_title="Subscription Month",
        yaxis_title="Total Duplicate Questions",
        title_font_size=20,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50),  # Adjust margins
        legend=dict(
            title=None,  # Remove legend title
            font=dict(size=12),
            orientation="h",  # Horizontal legend
            x=0.5,  # Center the legend
            xanchor="center",
            y=-0.2  # Position legend below the chart
        )
    )

    # Set consistent colors for the lines
    fig_total_duplicates.for_each_trace(
        lambda trace: trace.update(line_color="#68c4af") if trace.name == "Cancelled Users" else trace.update(line_color="#1b85b8")
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig_total_duplicates, use_container_width=True)


    
    # Filter data for canceled users within 1 hour
    cancelled_within_1_hour = master_table[
        (master_table['status_code'] == 2) & (master_table['time_to_cancel_hours'] <= 1)
    ]

    # Filter data for active users and count duplicate questions within the first hour
    active_within_1_hour = master_table[master_table['status_code'] == 0]

    # Group by subscription month and calculate averages
    avg_cancelled_monthly = cancelled_within_1_hour.groupby('created_month')['duplicate_questions'].mean().reset_index()
    avg_active_monthly = active_within_1_hour.groupby('created_month')['duplicate_questions_first_hour'].mean().reset_index()

    # Rename columns explicitly for clarity
    avg_cancelled_monthly.rename(columns={'duplicate_questions': 'avg_duplicate_questions_cancelled'}, inplace=True)
    avg_active_monthly.rename(columns={'duplicate_questions_first_hour': 'avg_duplicate_questions_active'}, inplace=True)

    # Merge the dataframes
    avg_duplicates_monthly = pd.merge(
        avg_cancelled_monthly, avg_active_monthly, on='created_month', how='outer'
    ).fillna(0)

    # Prepare the data for Plotly
    avg_duplicates_monthly = avg_duplicates_monthly.sort_values("created_month")  # Ensure proper order of months
    
    data_montly_hourly = pd.melt(
        avg_duplicates_monthly,
        id_vars=['created_month'],
        value_vars=['avg_duplicate_questions_cancelled', 'avg_duplicate_questions_active'],
        var_name='User Status',
        value_name='Average Duplicate Questions'
    )
    data_montly_hourly['User Status'] = data_montly_hourly['User Status'].replace({
        'avg_duplicate_questions_cancelled': 'Cancelled Users',
        'avg_duplicate_questions_active': 'Active Users'
    })

    # Create a line plot with Plotly Express
    fig_montly_hourly = px.line(
        data_montly_hourly,
        x="created_month",
        y="Average Duplicate Questions",
        color="User Status",
        title="Average Duplicate Questions Within 1 Hour - Monthly Breakdown",
        labels={"created_month": "Subscription Month"},
        markers=True  # Add markers to the lines
    )

        # Customize the line plot
    fig_montly_hourly.update_traces(
        marker=dict(size=8, line=dict(width=1, color="black")),  # Markers with black outlines
        line=dict(width=2)  # Increase line width for better visibility
    )

    # Update layout to fix month visibility and colors
    fig_montly_hourly.update_layout(
        plot_bgcolor="whitesmoke",
        xaxis_title="Subscription Month",
        yaxis_title="Average Duplicate Questions",
        title_font_size=20,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50),  # Adjust margins
        legend=dict(
            title=None,  # Remove legend title
            font=dict(size=12),
            orientation="h",  # Horizontal legend
            x=0.5,  # Center the legend
            xanchor="center",
            y=-0.2  # Position legend below the plot
        )
    )

    # Set colors matching the bar chart
    fig_montly_hourly.for_each_trace(
        lambda trace: trace.update(line_color="#68c4af") if trace.name == "Cancelled Users" else trace.update(line_color="#1b85b8")
    )


    # Display the chart in Streamlit
    st.plotly_chart(fig_montly_hourly, use_container_width=True)


    # Monthly Breakdown for duplicate questions within 24 hours
    # Filter data for canceled users within 24 hours
    cancelled_within_24_hours = master_table[
        (master_table['status_code'] == 2) & (master_table['time_to_cancel_hours'] <= 24)
    ]

    # Filter data for active users and count duplicate questions within the first 24 hours
    active_within_24_hours = master_table[master_table['status_code'] == 0]

    # Group by subscription month and calculate averages
    avg_cancelled_24h_monthly = cancelled_within_24_hours.groupby('created_month')['duplicate_questions'].mean().reset_index()
    avg_active_24h_monthly = active_within_24_hours.groupby('created_month')['duplicate_questions_first_24_hours'].mean().reset_index()

    # Rename columns explicitly for clarity
    avg_cancelled_24h_monthly.rename(columns={'duplicate_questions': 'avg_duplicate_questions_cancelled_24h'}, inplace=True)
    avg_active_24h_monthly.rename(columns={'duplicate_questions_first_24_hours': 'avg_duplicate_questions_active_24h'}, inplace=True)

    # Merge the dataframes
    avg_duplicates_24h_monthly = pd.merge(
        avg_cancelled_24h_monthly, avg_active_24h_monthly, on='created_month', how='outer'
    ).fillna(0)

    # Prepare the data
    avg_duplicates_24h_monthly = avg_duplicates_24h_monthly.sort_values("created_month")  # Ensure proper order of months
    data_24h = pd.melt(
        avg_duplicates_24h_monthly,
        id_vars=['created_month'],
        value_vars=['avg_duplicate_questions_cancelled_24h', 'avg_duplicate_questions_active_24h'],
        var_name='User Status',
        value_name='Average Duplicate Questions'
    )
    data_24h['User Status'] = data_24h['User Status'].replace({
        'avg_duplicate_questions_cancelled_24h': 'Cancelled Users',
        'avg_duplicate_questions_active_24h': 'Active Users'
    })

    # Create a line plot using Plotly Express
    fig_24h = px.line(
        data_24h,
        x="created_month",
        y="Average Duplicate Questions",
        color="User Status",
        title="Average Duplicate Questions Within 24 Hours - Monthly Breakdown",
        labels={"created_month": "Subscription Month"},
        markers=True  # Add markers to the lines
    )

    # Customize the line plot
    fig_24h.update_traces(
        marker=dict(size=8, line=dict(width=1, color="black")),  # Markers with black outlines
        line=dict(width=2)  # Increase line width for better visibility
    )

    # Update layout for consistent x-axis and colors
    fig_24h.update_layout(
        plot_bgcolor="whitesmoke",
        xaxis_title="Subscription Month",
        yaxis_title="Average Duplicate Questions",
        title_font_size=20,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50),  # Adjust margins
        legend=dict(
            title=None,  # Remove legend title
            font=dict(size=12),
            orientation="h",  # Horizontal legend
            x=0.5,  # Center the legend
            xanchor="center",
            y=-0.2  # Position legend below the plot
        )
    )

    # Set consistent colors for the lines
    fig_24h.for_each_trace(
        lambda trace: trace.update(line_color="#68c4af") if trace.name == "Cancelled Users" else trace.update(line_color="#1b85b8")
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig_24h, use_container_width=True)

#################################################################################################################################
#################################################################################################################################
# Questions/Duplicate Insights
#################################################################################################################################
#################################################################################################################################

def languages_countries():
    # Title and branding
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Country and Language Insights</h1>
         </div>
            
        """, unsafe_allow_html=True,)

    #----------------------------------------------------------------------------------------------------------------------------
    # Language Proportions
    #----------------------------------------------------------------------------------------------------------------------------
    melted_duplicates_lang = pd.read_csv("melted_duplicates_lang.csv")
    
    # Ensure consistent sorting by proportion of duplicate questions
    sorted_data_lang = melted_duplicates_lang.sort_values('Prop Duplicate Questions', ascending=False)

    # Create the bar chart using Plotly Express
    fig_lang = px.bar(
        sorted_data_lang,
        x='main_language',
        y='Prop Duplicate Questions',
        color='Cancellation Window',
        barmode='group',  # Set to side-by-side bars
        title='Proportion Duplicate Questions per Canceled User by Main Language',
        #text='Prop Duplicate Questions',
        color_discrete_map={
            "Within 1 Hour": "skyblue",
            "Within 24 Hours": "salmon"
        }
    )

    # Update traces for accurate percentage formatting and text position
    fig_lang.update_traces(
        marker=dict(line=dict(width=1, color="black"))
    )

    # Customize layout
    fig_lang.update_layout(
        title=dict(font=dict(size=20)),
        xaxis_title='Main Language',
        yaxis_title='Proportion of Duplicate Questions (%)',
        xaxis=dict(tickangle=45),  # Rotate x-axis labels for readability
        legend=dict(
            title="Cancellation Window",
            orientation="h",
            y=1.03,
            x=0.5,
            xanchor="center",
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0.7)"
        ),
        plot_bgcolor="whitesmoke",
        width=900,
        height=600
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig_lang, use_container_width=True)

    #----------------------------------------------------------------------------------------------------------------------------
    # Country Proportions
    #----------------------------------------------------------------------------------------------------------------------------

    melted_duplicates_country = pd.read_csv("melted_duplicates_country.csv")

    # Sort the data for better visualization
    sorted_data_country = melted_duplicates_country.sort_values('Prop Duplicate Questions', ascending=False)

    # Create the bar chart using Plotly Express
    fig_country = px.bar(
        sorted_data_country,
        x='country',
        y='Prop Duplicate Questions',
        color='Cancellation Window',
        barmode='group',
        title='Proportion of Duplicate Questions per Canceled User by Country',
        #text='Prop Duplicate Questions',
        color_discrete_map={
            "Within 1 Hour": "skyblue",
            "Within 24 Hours": "salmon"
        }
    )

    # Update traces for percentage formatting and text position
    fig_country.update_traces(
        marker=dict(line=dict(width=1, color="black"))
    )

    # Customize the layout
    fig_country.update_layout(
        title=dict(font=dict(size=20)),
        xaxis_title='Country',
        yaxis_title='Proportion of Duplicate Questions (%)',
        xaxis=dict(tickangle=45),  # Rotate country labels for readability
        legend=dict(
            title="Cancellation Window",
            orientation="h",
            y=1.03,
            x=0.5,
            xanchor="center",
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0.7)"
        ),
        plot_bgcolor="whitesmoke",
        width=900,
        height=600
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig_country, use_container_width=True)


#################################################################################################################################
#################################################################################################################################
# Reactivations
#################################################################################################################################
#################################################################################################################################


def reactivations():
    # Title and branding
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Reactivation Insights</h1>
         </div>
            
        """, unsafe_allow_html=True,)

    reactivated_users = pd.read_csv("reactivated_users.csv")


    #----------------------------------------------------------------------------------------------------------------------------
    # Country Proportions
    #----------------------------------------------------------------------------------------------------------------------------

    # Calculate reactivation counts by time window
    reactivation_counts = reactivated_users['reactivation_window'].value_counts()

    # Convert the counts into a DataFrame for Plotly
    reactivation_df = pd.DataFrame({
        'Time Window': reactivation_counts.index,
        'Count': reactivation_counts.values
    })

    # Create the pie chart using Plotly Express
    fig_reactivation_prop = px.pie(
        reactivation_df,
        names='Time Window',
        values='Count',
        title='Proportion of Reactivations by Time Window',
        color_discrete_sequence=px.colors.qualitative.Pastel  # Pastel tones for better aesthetics
    )

    # Customize the layout
    fig_reactivation_prop.update_traces(
        textinfo='percent+label',  # Show percentages and labels
        textfont_size=14,  # Adjust font size
        marker=dict(line=dict(color='black', width=1))  # Add a border to slices
    )
    fig_reactivation_prop.update_layout(
        title=dict(font=dict(size=20), y=.95),  # Center the title
        showlegend=True,
        legend=dict(
            orientation="h",
            y=-0.2,  # Position the legend below the chart
            x=0.5,
            xanchor="center",
            font=dict(size=12)
        ),
        plot_bgcolor="whitesmoke",  # Light background
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig_reactivation_prop, use_container_width=True)

    #----------------------------------------------------------------------------------------------------------------------------
    # Last Used feature before reactivating
    #----------------------------------------------------------------------------------------------------------------------------

    # Pivot the data for easier plotting
    reactivation_feature = reactivated_users.groupby(['reactivation_window', 'feature_used'])['user_id'].nunique().reset_index(name='reactivated_users')

    reactivation_pivot = reactivation_feature.pivot(index='reactivation_window', columns='feature_used', values='reactivated_users').fillna(0)

    # Separate the data for each time window
    within_1_hour = reactivation_pivot.loc['Within 1 Hour']
    between_1_and_24_hours = reactivation_pivot.loc['1 to 24 Hours']
    after_24_hours = reactivation_pivot.loc['After 24 Hours']

    # Streamlit layout for displaying charts
    st.markdown("## Last Feature Used Before Reactivation")

    # Function to create a bar chart for a given time window with clearer y-axis labels
    def create_bar_chart(data, title):
        # Convert pivoted DataFrame into a long-form DataFrame
        data_long = data.reset_index().melt(id_vars='feature_used', value_name='reactivated_users')
        # Remove NaN values (if any) for clean plotting
        data_long = data_long.dropna(subset=['reactivated_users'])

        # Plotly bar chart
        chart = px.bar(
            data_frame=data_long,
            x='feature_used',
            y='reactivated_users',
            title=title,
            color='feature_used',  # Assign colors by feature
            color_discrete_sequence=px.colors.qualitative.Set3,  # Use Set3 color palette
        )


        chart.update_layout(
            title=dict(x=0.2, font=dict(size=20)),
            xaxis_title="Feature Used",
            yaxis_title="Number of Reactivated Users",  # Add clear label for y-axis
            yaxis=dict(
                tickformat=",",  # Add commas to large numbers for readability
                title_font=dict(size=14),  # Increase y-axis title font size
                tickfont=dict(size=12),  # Increase y-axis tick font size
            ),
            plot_bgcolor="whitesmoke",
            legend_title_text="Feature Used",
            xaxis=dict(tickangle=45),  # Rotate x-axis labels for readability
        )
        return chart

    # Plot for "Within 1 Hour"
    st.plotly_chart(create_bar_chart(within_1_hour.reset_index(), "Reactivations Within 1 Hour"))

    # Plot for "1 to 24 Hours"
    st.plotly_chart(create_bar_chart(between_1_and_24_hours.reset_index(), "Reactivations Between 1 and 24 Hours"))

    # Plot for "After 24 Hours"
    st.plotly_chart(create_bar_chart(after_24_hours.reset_index(), "Reactivations After 24 Hours"))

    #----------------------------------------------------------------------------------------------------------------------------
    # Monthly Breakdown Reactivations
    #----------------------------------------------------------------------------------------------------------------------------
    
        # Group by 'reactivation_month' and count unique reactivated users
    # Group by 'reactivation_month' and count unique reactivated users
    monthly_reactivations = reactivated_users.groupby('reactivation_month')['user_id'].nunique().reset_index(name='reactivated_accounts')

    # Ensure 'reactivation_month' is a datetime type
    monthly_reactivations['reactivation_month'] = pd.to_datetime(monthly_reactivations['reactivation_month'], errors='coerce')

    # Sort the DataFrame by 'reactivation_month'
    monthly_reactivations = monthly_reactivations.sort_values('reactivation_month')

    # Create the line chart using Plotly Express
    line_chart = px.line(
        data_frame=monthly_reactivations,
        x='reactivation_month',
        y='reactivated_accounts',
        title="Monthly Reactivated Accounts",
        markers=True  # Add markers to emphasize data points
    )

    # Customize the chart
    line_chart.update_traces(
        line=dict(width=2, color="lightcoral"),  # Line color and thickness
        marker=dict(size=10, color="lightskyblue", line=dict(width=2, color="black"))  # Larger markers for better visibility
    )

    # Update layout for better readability
    line_chart.update_layout(
        title=dict(x=0.2, font=dict(size=20)),  # Center the title and adjust font size
        xaxis=dict(
            title="Month",
            title_font=dict(size=14),  # X-axis title font size
            tickangle=45,  # Rotate x-axis labels for readability
            tickfont=dict(size=12),  # X-axis tick font size
            tickformat="%b %Y"  # Format x-axis labels as "Month Year"
        ),
        yaxis=dict(
            title="Number of Reactivated Accounts",
            title_font=dict(size=14),  # Y-axis title font size
            tickfont=dict(size=12),  # Y-axis tick font size
            tickformat=","  # Add commas to numbers for readability
        ),
        plot_bgcolor="whitesmoke",  # Set a light background color
    )

    # Display the chart in Streamlit
    st.plotly_chart(line_chart)

def signups():
    # Title and branding
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Sign Up Insights</h1>
         </div>
            
        """, unsafe_allow_html=True,)

    
    #----------------------------------------------------------------------------------------------------------------------------
    # Hourly Sign Up Times
    #----------------------------------------------------------------------------------------------------------------------------

    st.markdown(
        "## Cancellations Within 1 hour"
    )

    hourly_signups = pd.read_csv("hourly_signups.csv")

    # Ensure 'account_creation_time' is in datetime format
    hourly_signups['account_creation_time'] = pd.to_datetime(hourly_signups['account_creation_time'], errors='coerce')

    # Remove rows where datetime conversion failed (if any)
    hourly_signups = hourly_signups.dropna(subset=['account_creation_time'])

    # Create bins for the specified time intervals
    bins = [0, 1, 5, 30, 60]
    labels = ["<=1 min", "1-5 min", "5-30 min", "30-60 min"]
    hourly_signups['time_interval'] = pd.cut(
        hourly_signups['time_diff_in_minutes'],
        bins=bins,
        labels=labels,
        right=True  # Includes the right endpoint in the interval
    )

    # Calculate proportions for each time interval
    proportions = hourly_signups['time_interval'].value_counts(normalize=True).sort_index() * 100

    # Convert proportions to a DataFrame for visualization
    proportions_df = proportions.reset_index()
    proportions_df.columns = ['Time Interval', 'Proportion']

    # Visualization: Bar Chart
    bar_chart = px.bar(
        proportions_df,
        x='Time Interval',
        y='Proportion',
        title="Proportion of Users by Time to First Payment (1 hour span)",
        text='Proportion',  # Display proportions as text on bars
        labels={'Proportion': 'Proportion (%)', 'Time Interval': 'Time to First Payment'},
        color='Time Interval',  # Use different colors for each bar
        color_discrete_sequence=px.colors.qualitative.Pastel1  # Custom color palette
    )

    # Customize the chart
    bar_chart.update_traces(
        texttemplate='%{text:.2f}%',  # Format text as percentages
        textposition="outside",  # Place labels outside the bars
        marker=dict(line=dict(width=2, color="black"))  # Add black outlines to bars
    )

    bar_chart.update_layout(
        title=dict(x=0.17, font=dict(size=20)),  # Center and enlarge title
        xaxis=dict(
            title="Time to First Payment",
            title_font=dict(size=16),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title="Proportion (%)",
            title_font=dict(size=16),
            tickfont=dict(size=12),
            range=[0, 50],  # Set a fixed range with extra space at the top
        ),
        
        plot_bgcolor="whitesmoke"  # Background color
    )

    # Display the chart in Streamlit
    st.plotly_chart(bar_chart)

    # Ensure 'account_creation_time' is in datetime format
    hourly_signups['account_creation_time'] = pd.to_datetime(hourly_signups['account_creation_time'])

    # Format 'month_year' to show month names and year explicitly (e.g., "Sep 2024")
    hourly_signups['month_year'] = hourly_signups['account_creation_time'].dt.strftime('%b %Y')

    # Create time bins for signups
    hourly_signups['time_bins'] = pd.cut(
        hourly_signups['time_diff_in_minutes'], 
        bins=[0, 1, 5, 30, 60], 
        labels=['<1 min', '1-5 min', '5-30 min', '30-60 min'], 
        right=False
    )

    # Group and calculate proportions
    hourly_proportions = hourly_signups.groupby(['month_year', 'time_bins']).size().reset_index(name='count')
    hourly_proportions['proportion'] = hourly_proportions.groupby('month_year')['count'].transform(lambda x: x / x.sum() * 100)

    # Filter for the months of interest (Sep, Oct, Nov 2024)
    selected_months = ['Sep 2024', 'Oct 2024', 'Nov 2024']
    hourly_proportions_filtered = hourly_proportions[hourly_proportions['month_year'].isin(selected_months)]

    # Create a grouped bar chart with horizontal bars
    fig = px.bar(
        hourly_proportions_filtered,
        x='proportion',
        y='month_year',
        color='time_bins',
        color_discrete_sequence=px.colors.qualitative.Pastel2,
        title="Hourly Signups Proportions by Month (Sep, Oct, Nov)",
        labels={'proportion': 'Proportion (%)', 'month_year': 'Month-Year', 'time_bins': 'Time Bin'},
        barmode='group',  # Grouped layout
        orientation='h'  # Horizontal orientation
    )

    # Customize the chart
    fig.update_traces(
        texttemplate='%{x:.1f}%',  # Show percentages on bars
        textposition='outside',  # Position text outside the bars
        marker=dict(line=dict(width=1, color="black"))  # Add black outline
    )

    fig.update_layout(
        title=dict(x=0.5, font=dict(size=20)),  # Center and enlarge the title
        xaxis=dict(
            title="Proportion (%)",
            title_font=dict(size=14),
            tickfont=dict(size=12),
            range=[0, 73]  # Adjust the range for better visualization
        ),
        yaxis=dict(
            title="Month-Year",
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        legend=dict(
            title="Time Bin",
            font=dict(size=12),
            orientation="h",  # Horizontal legend
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        plot_bgcolor="whitesmoke",  # Set background color
    )

    # Show the visualization
    st.plotly_chart(fig)

    #----------------------------------------------------------------------------------------------------------------------------
    # Daily Sign Up Times
    #----------------------------------------------------------------------------------------------------------------------------

    st.markdown(
        "## Cancellations Within 24 hours"
    )

    # Load the dialy_signups CSV
    dialy_signups = pd.read_csv("/Users/liamdupeyron/Desktop/AnswersAi/main_data/dialy_signups.csv")

    # Ensure 'account_creation_time' is in datetime format
    dialy_signups['account_creation_time'] = pd.to_datetime(dialy_signups['account_creation_time'])

    # Define new bins for Time to First Payment
    bins = [0, 1, 6, 12, 24]  # Adjusted bins
    labels = ['<1 hour', '1-6 hours', '6-12 hours', '12-24 hours']  # Updated labels
    dialy_signups['time_bins'] = pd.cut(
        dialy_signups['time_diff_in_hours'], bins=bins, labels=labels, right=False
    )

    # Group and calculate proportions for the entire dataset
    time_bin_proportions = dialy_signups.groupby('time_bins').size().reset_index(name='Sign-ups')
    time_bin_proportions['Proportion'] = (time_bin_proportions['Sign-ups'] / time_bin_proportions['Sign-ups'].sum()) * 100

    # Visualization: Bar Chart for Overall Time Bins
    bar_chart = px.bar(
        time_bin_proportions,
        x='time_bins',
        y='Proportion',
        title="Proportion of Users by Time to First Payment (24 hour span)",
        text='Proportion',  # Show percentages on bars
        labels={'Proportion': 'Proportion (%)', 'time_bins': 'Time to First Payment'},
        color='time_bins',  # Use distinct colors for each bar
        color_discrete_sequence=px.colors.qualitative.Set3  # Custom color palette
    )

    # Customize the chart
    bar_chart.update_traces(
        texttemplate='%{text:.2f}%',  # Format text as percentages
        textposition="outside",  # Place text labels outside the bars
        marker=dict(line=dict(width=1, color="black"))  # Add black outlines to bars
    )

    bar_chart.update_layout(
        title=dict(x=0.17, font=dict(size=20)),  # Center and enlarge the title
        xaxis=dict(
            title="Time to First Payment",
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title="Proportion (%)",
            title_font=dict(size=14),
            tickfont=dict(size=12),
            range=[0, 105]
        ),
        plot_bgcolor="whitesmoke",  # Set background color
        showlegend=False  # Hide legend for simplicity
    )

    # Display the chart in Streamlit
    st.plotly_chart(bar_chart)

    # Add month-year formatting for the stacked bar chart
    dialy_signups['month_year'] = dialy_signups['account_creation_time'].dt.strftime('%b %Y')

    # Group and calculate proportions for each month
    daily_proportions = dialy_signups.groupby(['month_year', 'time_bins']).size().reset_index(name='count')
    daily_proportions['proportion'] = daily_proportions.groupby('month_year')['count'].transform(lambda x: x / x.sum() * 100)

    # Filter for the months of interest (Sep, Oct, Nov 2024)
    selected_months = ['Sep 2024', 'Oct 2024', 'Nov 2024']
    daily_proportions_filtered = daily_proportions[daily_proportions['month_year'].isin(selected_months)]

    # Create a stacked bar chart for proportions by month
    fig = px.bar(
        daily_proportions_filtered,
        x='proportion',
        y='month_year',
        color='time_bins',
        color_discrete_sequence=px.colors.qualitative.Pastel1,
        title="Daily Signups Proportions by Month (Sep, Oct, Nov)",
        labels={'proportion': 'Proportion (%)', 'month_year': 'Month-Year', 'time_bins': 'Time Bin'},
        barmode='group',  # Stacked layout
        orientation='h'  # Horizontal orientation
    )

    # Customize the chart
    fig.update_traces(
        texttemplate='%{x:.1f}%',  # Show percentages on bars
        textposition='inside',  # Position text inside the bars for better clarity
        marker=dict(line=dict(width=0.5, color="black"))  # Add black outline
    )

    fig.update_layout(
        title=dict(x=0.2, font=dict(size=20)),  # Center and enlarge the title
        xaxis=dict(
            title="Proportion (%)",
            title_font=dict(size=14),
            tickfont=dict(size=12),
            range=[0, 100]  # Adjust the range for clearer visualization
        ),
        yaxis=dict(
            title="Month-Year",
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        legend=dict(
            title="Time Bin",
            font=dict(size=12),
            orientation="v",  # Vertical legend
            yanchor="top",
            y=1,
            xanchor="right",
            x=1.2
        ),
        plot_bgcolor="whitesmoke",  # Set background color
    )

    # Show the visualization in Streamlit
    st.plotly_chart(fig)

    



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
            "Country and Language Insights": languages_countries,
            "Reactivation Insights": reactivations,
            "Sign Up Insights": signups



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
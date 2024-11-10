#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Function to fetch data from the claims table
def fetch_claims_data():
    try:
        # Load data from CSV for now
        df = pd.read_csv('Claims.csv')
        
        # Ensure date columns are in the correct format
        date_columns = [
            'claim_received_date', 'claim_loss_date', 'claim_finalised_date',
            'original_verified_date_of_loss_time', 'last_verified_date_of_loss_time',
            'catastrophe_valid_from_date_time', 'catastrophe_valid_to_date_time', 'update_date'
        ]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        df = pd.DataFrame()  # Return empty DataFrame on failure
    return df

# Streamlit app for the report with independent filters and charts
def main():
    st.title("Claims Report Dashboard")

    # Fetch data from the database
    data = fetch_claims_data()

    if not data.empty:
        filtered_data = data.copy()  # Start with a copy for independent filtering

        # Text-based filters for each relevant column
        text_columns = [
            'source_system', 'general_nature_of_loss', 'line_of_business', 'claim_status', 
            'fault_rating', 'fault_categorisation'
        ]
        for col in text_columns:
            unique_values = data[col].dropna().unique()
            selected_values = st.multiselect(f"Filter by {col}", options=unique_values, default=unique_values)
            if selected_values:
                filtered_data = filtered_data[filtered_data[col].isin(selected_values)]

        # Independent Date range filters
        date_columns = [
            'claim_received_date', 'claim_loss_date', 'claim_finalised_date', 
            'original_verified_date_of_loss_time', 'last_verified_date_of_loss_time', 
            'catastrophe_valid_from_date_time', 'catastrophe_valid_to_date_time'
        ]
        for col in date_columns:
            min_date, max_date = data[col].min(), data[col].max()
            if pd.notnull(min_date) and pd.notnull(max_date):
                date_range = st.date_input(f"{col} Range", value=(min_date, max_date))
                if date_range:
                    filtered_data = filtered_data[filtered_data[col].between(date_range[0], date_range[1])]

        # Independent Numeric filters
#         numeric_columns = [
#             'claim_number', 'policy_number', 'total_open_recovery_reserve', 
#             'total_open_remaining_reserve', 'total_open_future_payment', 
#             'total_recovery', 'total_net_incurred', 'total_paid'
#         ]
#         for col in numeric_columns:
#             min_val, max_val = data[col].min(), data[col].max()
#             if pd.notnull(min_val) and pd.notnull(max_val):
#                 value_range = st.slider(f"Filter by {col} range", min_val, max_val, (min_val, max_val))
#                 if value_range:
#                     filtered_data = filtered_data[(filtered_data[col] >= value_range[0]) & (filtered_data[col] <= value_range[1])]

        # Display filtered statistics
        st.subheader("Filtered Claims Statistics")
        st.write("Total Claims:", filtered_data["claim_number"].nunique())

        # Display interactive bar chart for claims by status
        st.subheader("Claims by Status")
        status_counts = filtered_data['claim_status'].value_counts().reset_index()
        status_counts.columns = ['claim_status', 'count']
        fig_status = px.bar(status_counts, x='claim_status', y='count', title="Claims by Status", color='claim_status')
        st.plotly_chart(fig_status)

        # Display line chart for claims over time (number of claims per day)
        st.subheader("Claims Over Time")
        claims_over_time = filtered_data.groupby('claim_received_date').size().reset_index(name='claim_count')
        fig_time = px.line(claims_over_time, x='claim_received_date', y='claim_count', title="Claims Over Time")
        st.plotly_chart(fig_time)

        # Display bar chart for claims by city (loss location)
        st.subheader("Claims by Loss Location (City)")
        city_counts = filtered_data['loss_location_city'].value_counts().reset_index()
        city_counts.columns = ['loss_location_city', 'count']
        fig_city = px.bar(city_counts, x='loss_location_city', y='count', title="Claims by Loss Location (City)", color='loss_location_city')
        st.plotly_chart(fig_city)

        # Display bar chart for claims by claim owner
        st.subheader("Claims by Claim Owner")
        owner_counts = filtered_data.groupby(['claim_owner_first_name', 'claim_owner_last_name']).size().reset_index(name='claim_count')
        fig_owner = px.bar(owner_counts, x='claim_owner_first_name', y='claim_count', title="Claims by Claim Owner", color='claim_owner_first_name')
        st.plotly_chart(fig_owner)

        # Display filtered claims data and download option
        st.subheader("Filtered Claims Data")
        st.dataframe(filtered_data)

        # Option to download the filtered data
        csv = filtered_data.to_csv(index=False)
        st.download_button("Download as CSV", csv, "filtered_claims.csv", "text/csv")
        
    else:
        st.warning("No data available.")

if __name__ == "__main__":
    main()


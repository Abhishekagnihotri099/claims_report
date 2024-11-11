import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(
    page_title="Claim Leakage Dashboard Testing",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

st.markdown("""
    <style>
        /* General body background color */
        body {
            background-color: #f0f0f0;
        }

        /* Sidebar custom styling */
        .sidebar .sidebar-content {
            background-color: #ffffff;
        }

        /* Input fields in sidebar */
        .css-1to6prn input {
            border: 2px solid #5d3a9b;
            background-color: #f8f8f8;
            color: #333333;
            padding: 10px;
        }

        /* Sidebar header styling */
        .css-1to6prn label {
            color: #5d3a9b;
        }

        /* Title and Subheader text color */
        .css-ffhzg2 {
            color: #5d3a9b;
        }

        /* Button Styling */
        .css-1v3fvcr button {
            background-color: #5d3a9b;
            color: white;
            border-radius: 5px;
        }

        

        /* Styling for Metric Cards */
        .css-1v3fvcr {
            background-color: #5d3a9b;
            color: white;
            border-radius: 5px;
        }

        /* Change background of the filters */
        .stTextInput {
            background-color: #e0e0e0;
            border-radius: 8px;
            padding: 10px;
            border: 2px solid #5d3a9b;
        }
        
        /* Metric card styling */
        .stMetric {
            background-color: #ffffff;
            border: 2px solid #5d3a9b;
            padding: 15px;
            border-radius: 8px;
        }
        /* Styling for the multiselect input */
        .stMultiSelect {
            background-color: #e0e0e0;
            border-radius: 8px;
            padding: 10px;
            border: 2px solid #5d3a9b;
        }

        /* Change text color and border of selected items */
        .stMultiSelect input {
            color: #5d3a9b;
            background-color: #f8f8f8;
            padding: 8px;
        }
        /* Styling for the dropdown options */
        div[role="listbox"] {
            background-color: #f8f8f8; /* Background color of the dropdown */
            border: 2px solid #5d3a9b; /* Border color of the dropdown */
            border-radius: 8px;
            padding: 8px;
        }

        /* Change selected option in the dropdown */
        div[role="option"][aria-selected="true"] {
            background-color: #5d3a9b; /* Background color when an option is selected */
            color: white; /* Text color of the selected option */
        }

        /* Optional: Change unselected options background color */
        div[role="option"]:not([aria-selected="true"]) {
            background-color: #e0e0e0; /* Light gray for unselected options */
            color: #5d3a9b; /* Border color for unselected options */
        }

        /* Styling for the multiselect input */
        .stDateInput {
            background-color: #e0e0e0;
            border-radius: 8px;
            padding: 10px;
            border: 2px solid #5d3a9b;
        }

        /* Change text color, background color, and border of the selected item */
        .stDateInput input {
            color: #5d3a9b; /* Text color same as border color */
            background-color: #f8f8f8;
            padding: 8px;
        }
        .stDateInput input::placeholder {
            color: #5d3a9b; /* Match placeholder text color with the border */
        }

        

    </style>
""", unsafe_allow_html=True)



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
    # Display logo
    st.image("exl.png", width=150)  # Replace 'logo.png' with the path to your logo image file
    st.title("Claim Report Dashboard Testing")

    # Fetch data from the database
    data = fetch_claims_data()

    if not data.empty:
        # Sidebar for filters
        st.sidebar.header("Filter Options")

        filtered_data = data.copy()  # Start with a copy for independent filtering
#         st.markdown("""
#             <style>
#                 /* Style the input field in the sidebar */
#                 .css-1to6prn {  /* Class for the text input field */
#                     border: 2px solid #5d3a9b;  /* Set border color */
#                     background-color: #f0f0f0;  /* Set background color */
#                     border-radius: 8px;  /* Border radius for rounded corners */
#                     padding: 10px;  /* Add padding inside the input field */
#                 }
#             </style>
#         """, unsafe_allow_html=True)
        # Claim number filter (text input)
        claim_numbers = st.sidebar.text_input("Filter by Claim Number (comma-separated)")
        if claim_numbers:
            claim_numbers = [num.strip() for num in claim_numbers.split(",") if num.strip()]
            filtered_data = filtered_data[filtered_data['claim_number'].astype(str).isin(claim_numbers)]

        # Text-based filters with an "All" option for each relevant column
        text_columns = [
            'source_system', 'general_nature_of_loss', 'line_of_business', 'claim_status', 
            'fault_rating', 'fault_categorisation'
        ]
        for col in text_columns:
            unique_values = data[col].dropna().unique().tolist()
            unique_values.insert(0, "All")  # Add "All" option
            selected_values = st.sidebar.multiselect(f"Filter by {col}", options=unique_values, default="All")
            
            # Apply filter only if "All" is not selected
            if "All" not in selected_values:
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
                date_range = st.sidebar.date_input(f"{col} Range", value=(min_date, max_date))
                if date_range:
                    filtered_data = filtered_data[filtered_data[col].between(date_range[0], date_range[1])]

        # Display filtered statistics
        st.markdown("""
            <style>
                h3 {
                    color: #5d3a9b !important;
                }
            </style>
        """, unsafe_allow_html=True)
        st.subheader("Filtered Claims Statistics")
        st.write("Total Claims:", filtered_data["claim_number"].nunique())
        def display_custom_metric(title, value, background_color="#f0f0f0"):
            card_style = f"""
            <style>
            .metric-card {{
                border: 2px solid #5d3a9b;
                border-radius: 8px;
                background-color: {background_color};
                padding: 20px;
                margin: 10px;
                height: 200px;  
                width: 160px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .metric-card h3 {{
                color: #5d3a9b;
                font-size: 18px;
                margin-bottom: 10px;
            }}
            .metric-card .value {{
                font-size: 36px;
                font-weight: bold;
                color: #333;
                margin-bottom: 0px;
            }}
            </style>
            """

            # HTML for the metric card
            card_html = f"""
            <div class="metric-card">
                <h3>{title}</h3>
                <div class="value">{value}</div>
            </div>
            """

            # Render the card with custom styling
            st.markdown(card_style + card_html, unsafe_allow_html=True)
        
        st.subheader("Metrics Overview")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            display_custom_metric("Claims Monitored", "3,071")
#             st.metric("**Claims Monitored**", "3,071")
        with col2:
            display_custom_metric("Claims with Leakage Opportunity", "1,854")

        with col3:
            # Function to display a styled card with a gauge chart inside
            def display_gauge_in_metric_card(title, gauge_value, background_color="#f0f0f0"):
                # Ensure that gauge_value is a number (int or float)
                if not isinstance(gauge_value, (int, float)):
                    raise ValueError("gauge_value must be a numeric type.")

                # Custom CSS for the card-style around the gauge chart
                card_style = f"""
                <style>
                .gauge-card {{
                    border: 2px solid #5d3a9b;
                    border-radius: 8px;
                    background-color: {background_color};
                    padding: 20px;
                    margin: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    height: 400px;  /* Fixed height for all cards */
                    width: 300px;   /* Fixed width for all cards */
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                    justify-content: space-between;
                }}
                .gauge-card h3 {{
                    color: #5d3a9b;
                    font-size: 18px;
                    margin-bottom: 10px;
                }}
                </style>
                """

                # Create the gauge chart using Plotly
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=gauge_value,
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#5d3a9b"}},
                    title={'text': f"{title} (%)", 'font': {'size': 16, 'color': 'black'}},
                    domain={'x': [0, 1], 'y': [0, 1]}
                ))
                fig.update_layout(height=170, margin=dict(t=0, b=0, l=0, r=0))

                # Display the card content in Streamlit within the column layout
                with st.container():
                    st.markdown(card_style, unsafe_allow_html=True)
                    st.markdown(f"<div class='gauge-card'><h3>{title}</h3></div>", unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True)

            display_custom_metric("Leakage Opportunity %", 60)

        with col4:
            display_custom_metric("Potential Leakage $", "$51.2M")
            
            

        # Optionally, add more detailed visualizations (e.g., charts) below the metrics

        # Horizontal gauge charts display for percentage metrics
#         col5, col6 = st.columns(2)

        with col5:
            display_custom_metric("Leakage Rate %", 100)
#             def gauge_chart(value, title):
#                 fig = go.Figure(go.Indicator(
#                     mode="gauge+number",
#                     value=value,
#                     gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#5d3a9b"}},
#                     title={'text': title, 'font': {'size': 12, 'weight': 'bold', 'color': 'black'}},
#                     domain={'x': [0, 1], 'y': [0, 1]}
#                 ))
#                 fig.update_layout(height=175, margin=dict(t=1, b=1, l=1, r=1))
#                 st.plotly_chart(fig, use_container_width=True)

#             gauge_chart(60, "Leakage Opportunity %")

        with col6:
            display_custom_metric("Opportunities Not Actioned", "3,063")
            
        
        st.markdown("<br><br>", unsafe_allow_html=True)
#         def styled_plotly_chart(fig, background_color="#f0f0f0", border_color="#5d3a9b"):
#             fig.update_layout(
#                 paper_bgcolor=background_color,  # Background for the full chart area
#                 plot_bgcolor=background_color,   # Background for the plot area inside axes
#                 margin=dict(t=10, b=10, l=10, r=10),  # Tighten margins to help fit the border
#                 autosize=False,
#                 height=250,  # Set consistent height
#                 width=300,   # Set consistent width
#                 title=dict(
#                     x=0.5,  # Center the title
#                     font=dict(size=16, color=border_color)
#                 ),
#                 shapes=[
#                     # Add a border around the entire chart area
#                     dict(
#                         type="rect",
#                         xref="paper", yref="paper",
#                         x0=0, y0=0, x1=1, y1=1,
#                         line=dict(color=border_color, width=2),
#                     )
#                 ]
#             )
#             st.plotly_chart(fig, use_container_width=False)
        # Create columns for charts to appear side by side with a thin dividing line
        col1, col2 = st.columns(2, gap="small")

        # Claims by Status chart with customized colors
        with col1:
            st.subheader("Claims by Status")
            status_counts = filtered_data['claim_status'].value_counts().reset_index()
            status_counts.columns = ['claim_status', 'count']
            fig_status = px.bar(
                status_counts, x='claim_status', y='count', title="Claims by Status", 
                color='claim_status', color_discrete_sequence=px.colors.sequential.Plasma
            )
            fig_status.update_layout(
                plot_bgcolor="#ffffff",
                paper_bgcolor="#f0f2f6",
            )
#             st.markdown('<div class="graph-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_status)

#         # Divider between charts
#         with col2:
#             st.markdown('<hr style="border:1px solid #e0e0e0; margin-top: 20px; margin-bottom: 20px;">', unsafe_allow_html=True)

        # Claims Over Time chart
        with col2:
            st.subheader("Claims Over Time")
            claims_over_time = filtered_data.groupby('claim_received_date').size().reset_index(name='claim_count')
            fig_time = px.line(
                claims_over_time, x='claim_received_date', y='claim_count', 
                title="Claims Over Time", color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig_time.update_layout(
                plot_bgcolor="#ffffff",
                paper_bgcolor="#f0f2f6",
            )
            st.plotly_chart(fig_time)

#         # New side-by-side charts for Claim Status (Pie) and Line of Business (Horizontal Bar)
        col3, col4 = st.columns(2, gap="small")

        # Pie chart for Claim Status
        with col3:
            st.subheader("Claim Status Distribution")
            fig_pie = px.pie(filtered_data, names='claim_status', title="Claim Status Distribution", hole=0.3)
            fig_pie.update_layout(
                plot_bgcolor="#ffffff",
                paper_bgcolor="#f0f2f6",
            )
            st.plotly_chart(fig_pie)

#         # Divider line
#         with col4:
#             st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

        # Horizontal bar chart for Line of Business
        with col4:
            st.subheader("Claims by Line of Business")
            line_of_business_counts = filtered_data['line_of_business'].value_counts().reset_index()
            line_of_business_counts.columns = ['line_of_business', 'count']
            fig_line_of_business = px.bar(
                line_of_business_counts, 
                y='line_of_business', 
                x='count', 
                orientation='h', 
                title="Claims by Line of Business", 
                color='line_of_business'
            )
            fig_line_of_business.update_layout(
                plot_bgcolor="#ffffff",
                paper_bgcolor="#f0f2f6",
                showlegend=False,
            )
            fig_line_of_business.update_xaxes(title="Count")
            fig_line_of_business.update_yaxes(title="Line of Business")
            st.plotly_chart(fig_line_of_business)
            
         
        # Trend graph for Claim Status (Open and Closed) by Year
        # Trend graph for Claim Status (Open and Closed) by Month
        st.subheader("Claim Status Trend Over Months")

        # Extract month and year from claim_received_date
        filtered_data['claim_received_date'] = pd.to_datetime(filtered_data['claim_received_date'], errors='coerce')
        filtered_data['month_year'] = filtered_data['claim_received_date'].dt.to_period('M').astype(str)
        monthly_status_counts = (
            filtered_data.groupby(['month_year', 'claim_status'])
            .size()
            .reset_index(name='count')
        )

        # Create bar chart with a line trend for total claims per month
        fig_trend_monthly = px.bar(
            monthly_status_counts, 
            x='month_year', 
            y='count', 
            color='claim_status', 
            title="Monthly Claim Status Trend (Open vs Closed)",
            barmode='group'
        )

        # Add a line to show the overall trend of claims per month
        monthly_totals = monthly_status_counts.groupby('month_year')['count'].sum().reset_index()
        fig_trend_monthly.add_scatter(
            x=monthly_totals['month_year'], 
            y=monthly_totals['count'], 
            mode='lines+markers', 
            name='Total Claims Trend',
            line=dict(color='blue', width=2)
        )

        # Update layout and background
        fig_trend_monthly.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#f0f2f6",
            xaxis_title="Month-Year",
            yaxis_title="Number of Claims",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_trend_monthly)
        
#         # Dropdowns for selecting column and chart type
#         st.sidebar.header("Custom Graph Options")
#         column_options = filtered_data.columns.tolist()
#         selected_column = st.sidebar.selectbox("Select Column for Visualization", options=column_options)
#         chart_type = st.sidebar.selectbox("Select Chart Type", options=["Bar Chart", "Line Chart", "Pie Chart"])

#         # Generate the selected chart based on user input
#         st.subheader(f"{chart_type} of {selected_column}")

#         # Prepare data for chart
#         column_data = filtered_data[selected_column].value_counts().reset_index()
#         column_data.columns = [selected_column, 'count']

#         # Display the selected chart type
#         if chart_type == "Bar Chart":
#             fig = px.bar(column_data, x=selected_column, y='count', title=f"{chart_type} of {selected_column}", color=selected_column)
#             fig.update_layout(plot_bgcolor="#f0f2f6", paper_bgcolor="#f0f2f6")
#             st.plotly_chart(fig)

#         elif chart_type == "Line Chart":
#             # For a line chart, ensure the column represents a temporal or sequential aspect.
#             # If the column is a datetime, sort by date; otherwise, this will show counts in order of unique values.
#             if pd.api.types.is_datetime64_any_dtype(filtered_data[selected_column]):
#                 filtered_data['date'] = pd.to_datetime(filtered_data[selected_column], errors='coerce')
#                 line_data = filtered_data.groupby('date').size().reset_index(name='count')
#                 fig = px.line(line_data, x='date', y='count', title=f"{chart_type} of {selected_column}")
#             else:
#                 fig = px.line(column_data, x=selected_column, y='count', title=f"{chart_type} of {selected_column}")
#             fig.update_layout(plot_bgcolor="#f0f2f6", paper_bgcolor="#f0f2f6")
#             st.plotly_chart(fig)

#         elif chart_type == "Pie Chart":
#             fig = px.pie(column_data, names=selected_column, values='count', title=f"{chart_type} of {selected_column}")
#             fig.update_layout(plot_bgcolor="#f0f2f6", paper_bgcolor="#f0f2f6")
#             st.plotly_chart(fig)
        # Custom CSS for styling metric cards and setting the right sidebar with a fixed width and border
# CSS to create a fixed right panel
        # Create two columns with a blank left side and a right "sidebar" for metrics
# Toggle for metrics sidebar visibility
        # Horizontal metrics display at the top
        
        
        # Display filtered claims data and download option
#         st.subheader("Filtered Claims Data")
#         pd.set_option("styler.render.max_elements", 1080000)
#         filtered_data = filtered_data.head()
#         styled_data = filtered_data.style.set_table_styles([
#             {'selector': 'thead th', 'props': [('background-color', '#5d3a9b'), ('color', 'white')]},  # Column header styling
#             {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', '#f2f2f2')]},  # Odd rows background color
#             {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#ffffff')]},  # Even rows background color
#         ])

#         # Display the styled dataframe with a subheader
        st.subheader("Filtered Claims Data")
        filtered_data = filtered_data.head(20)
#         st.dataframe(styled_data)
        def style_alternate_rows(x):
            # Create an empty style object
            style = pd.DataFrame('', index=x.index, columns=x.columns)
#             style = style.applymap(lambda v: 'border: 2px solid #5d3a9b')
            # Apply background color for even rows
            style.iloc[::2] = 'background-color: #f9f9f9'  # Light gray for even rows
            style.iloc[1::2] = 'background-color: #e6e6e6'  # Slightly darker gray for odd rows
            
            
            return style

        # Apply the styling to the dataframe
        styled_df = filtered_data.style.apply(style_alternate_rows, axis=None)
#         filtered_data = filtered_data.head(20)
        st.dataframe(styled_df)

        # Option to download the filtered data
        csv = filtered_data.to_csv(index=False)
        st.download_button("Download as CSV", csv, "filtered_claims.csv", "text/csv")
        
    else:
        st.warning("No data available.")

if __name__ == "__main__":
    main()

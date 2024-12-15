"""Class: CS230--Section 1
Name: Nick Kane
Description: Final Project
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student. """

import os
import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt

# Load and clean data
file_path = "volcanoes.csv"

# Check if file exists
if not os.path.exists(file_path):
    st.error(f"File not found: {file_path}")
else:
    volcanoes_data = pd.read_csv(file_path, encoding="latin1")
    volcanoes_data.columns = volcanoes_data.iloc[0]
    volcanoes_data = volcanoes_data[1:]

    # Select and rename relevant columns
    relevant_columns = {
        'Volcano Number': 'Volcano_ID',
        'Volcano Name': 'Name',
        'Country': 'Country',
        'Volcanic Region': 'Region',
        'Volcanic Province': 'Province',
        'Volcano Landform': 'Landform',
        'Primary Volcano Type': 'Type',
        'Activity Evidence': 'Activity_Evidence',
        'Last Known Eruption': 'Last_Eruption',
        'Latitude': 'Latitude',
        'Longitude': 'Longitude',
        'Elevation (m)': 'Elevation',
        'Tectonic Setting': 'Tectonic_Setting',
        'Dominant Rock Type': 'Rock_Type'
    }

    cleaned_data = volcanoes_data[list(relevant_columns.keys())].rename(columns=relevant_columns)
    cleaned_data['Elevation'] = pd.to_numeric(cleaned_data['Elevation'], errors='coerce')
    cleaned_data['Latitude'] = pd.to_numeric(cleaned_data['Latitude'], errors='coerce')
    cleaned_data['Longitude'] = pd.to_numeric(cleaned_data['Longitude'], errors='coerce')

    # Extract year from the 'Last Known Eruption' column
    cleaned_data['Eruption_Year'] = cleaned_data['Last_Eruption'].str.extract(r'(\d{4})', expand=False)
    cleaned_data['Eruption_Year'] = pd.to_numeric(cleaned_data['Eruption_Year'], errors='coerce')

    # Filter out illogical eruption years
    current_year = pd.Timestamp.now().year
    cleaned_data = cleaned_data[(cleaned_data['Eruption_Year'] <= current_year) & (cleaned_data['Eruption_Year'] >= 0)]

    # Drop rows with missing or invalid coordinates
    cleaned_data = cleaned_data.dropna(subset=['Latitude', 'Longitude'])

    # Streamlit App
    st.title("Volcanoes of the World")
    st.sidebar.title("Exhibits")

    # Sidebar tabs
    tab = st.sidebar.radio("Choose an exhibit:", ["Filtered Data", "Charts", "Map"])

    # Filters
    if tab == "Filtered Data" or tab == "Charts" or tab == "Map":
        country_filter = st.sidebar.multiselect("Select Country:", cleaned_data['Country'].unique())
        elevation_filter = st.sidebar.slider("Select Elevation Range (m):",
                                             int(cleaned_data['Elevation'].min()),
                                             int(cleaned_data['Elevation'].max()),
                                             (int(cleaned_data['Elevation'].min()), int(cleaned_data['Elevation'].max())))

        volcano_type_filter = st.sidebar.multiselect("Select Volcano Type:", cleaned_data['Type'].unique())

        # Filter data
        filtered_data = cleaned_data.copy()
        if country_filter:
            filtered_data = filtered_data[filtered_data['Country'].isin(country_filter)]

        filtered_data = filtered_data[(filtered_data['Elevation'] >= elevation_filter[0]) &
                                      (filtered_data['Elevation'] <= elevation_filter[1])]

        if volcano_type_filter:
            filtered_data = filtered_data[filtered_data['Type'].isin(volcano_type_filter)]

    # Filtered Data Exhibit
    if tab == "Filtered Data":
        st.subheader("Filtered Volcanoes Data")
        search_query = st.text_input("Search for a Volcano:")
        if search_query:
            filtered_data = filtered_data[filtered_data['Name'].str.contains(search_query, case=False, na=False)]
        st.dataframe(filtered_data)

    # Charts Exhibit
    elif tab == "Charts":
        # 1. Bar Chart: Top 10 Tallest Volcanoes
        st.subheader("Top 10 Tallest Volcanoes")
        top_volcanoes = filtered_data.nlargest(10, 'Elevation')
        plt.figure(figsize=(10, 6))
        plt.bar(top_volcanoes['Name'], top_volcanoes['Elevation'], color='orange')
        plt.xlabel("Volcano Name")
        plt.ylabel("Elevation (m)")
        plt.title("Top 10 Tallest Volcanoes")
        plt.xticks(rotation=45, ha='right')  # Fix overlapping names
        st.pyplot(plt)

        # 2. Pie Chart: Distribution by Volcano Type
        st.subheader("Volcano Types Distribution")
        volcano_type_distribution = filtered_data['Type'].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(volcano_type_distribution, labels=volcano_type_distribution.index, autopct='%1.1f%%', startangle=140)
        plt.title("Distribution of Volcano Types")
        plt.tight_layout()  # Adjust layout to prevent overlap
        st.pyplot(plt)

        # 3. Line Chart: Volcano Eruptions by Year
        st.subheader("Volcano Eruptions by Year")
        eruption_counts = filtered_data['Eruption_Year'].dropna().value_counts().sort_index()
        plt.figure(figsize=(10, 6))
        plt.plot(eruption_counts.index, eruption_counts.values, marker='o', linestyle='-', color='purple')
        plt.xlabel("Year")
        plt.ylabel("Number of Eruptions")
        plt.title("Volcano Eruptions Over Time")
        st.pyplot(plt)

    # Map Exhibit
    elif tab == "Map":
        st.subheader("Interactive Map")
        map_data = filtered_data[['Latitude', 'Longitude', 'Name']].dropna()
        map_data = map_data.rename(columns={"Latitude": "lat", "Longitude": "lon"})

        if not map_data.empty:
            layer = pdk.Layer(
                'ScatterplotLayer',
                data=map_data,
                get_position='[lon, lat]',
                get_radius=800,  # Adjusted radius for better balance
                get_color='[200, 30, 0, 160]',
                pickable=True,
                radius_scale=2**8,  # Scaling based on zoom level
                radius_min_pixels=3,  # Minimum size
                radius_max_pixels=30  # Maximum size
            )
            view_state = pdk.ViewState(latitude=map_data['lat'].mean(), longitude=map_data['lon'].mean(), zoom=3)
            r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Name}"})
            st.pydeck_chart(r)
        else:
            st.write("No data available for the selected filters.")

    st.write("Explore and analyze the dataset using the interactive filters and visualizations above!")




import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Global Water Consumption Dashboard", layout="wide", page_icon="💧")

# Header
st.markdown(
    "<h1 style='text-align: center; color: #2A7F62;'>Global Water Consumption Dashboard</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# Load fixed dataset
data = pd.read_csv("data/cleaned_global_water_consumption.csv")

# Normalize data types for stable metrics and plots
numeric_columns = [
    "Year",
    "Total Water Consumption (Billion Cubic Meters)",
    "Per Capita Water Use (Liters per Day)",
    "Agricultural Water Use (%)",
    "Industrial Water Use (%)",
    "Household Water Use (%)",
    "Rainfall Impact (Annual Precipitation in mm)",
    "Groundwater Depletion Rate (%)",
]
for column in numeric_columns:
    if column in data.columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

data = data.dropna(subset=["Country", "Year", "Total Water Consumption (Billion Cubic Meters)"])

# Sidebar filters
st.sidebar.header("Filters")
countries = sorted(data["Country"].dropna().unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=countries,
    default=countries[:5] if len(countries) >= 5 else countries,
)

year_min = int(data["Year"].min())
year_max = int(data["Year"].max())
selected_year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
)

filtered_data = data[
    data["Year"].between(selected_year_range[0], selected_year_range[1])
]

if selected_countries:
    filtered_data = filtered_data[filtered_data["Country"].isin(selected_countries)]

if filtered_data.empty:
    st.warning("No data available for the selected filters. Please adjust country or year range.")
    st.stop()

st.subheader("Filtered Data")
st.dataframe(filtered_data, use_container_width=True)

# KPIs
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", len(filtered_data))
col2.metric(
    "Avg Total Consumption (BCM)",
    round(filtered_data["Total Water Consumption (Billion Cubic Meters)"].mean(), 2),
)
col3.metric(
    "Avg Per Capita Use (L/day)",
    round(filtered_data["Per Capita Water Use (Liters per Day)"].mean(), 2),
)
scarcity_mode = (
    filtered_data["Water Scarcity Level"].mode().iat[0]
    if not filtered_data["Water Scarcity Level"].mode().empty
    else "N/A"
)
col4.metric("Most Common Scarcity Level", scarcity_mode)

st.markdown("---")

# Trend Chart
st.subheader("Total Water Consumption Trend")
trend_data = (
    filtered_data.groupby(["Year", "Country"], as_index=False)[
        "Total Water Consumption (Billion Cubic Meters)"
    ].mean()
)
fig_trend = px.line(
    trend_data,
    x="Year",
    y="Total Water Consumption (Billion Cubic Meters)",
    color="Country",
    markers=True,
)
st.plotly_chart(fig_trend, use_container_width=True)

# Bar Chart
st.subheader("Average Water Use by Sector")
sector_avg = filtered_data[
    [
        "Agricultural Water Use (%)",
        "Industrial Water Use (%)",
        "Household Water Use (%)",
    ]
].mean().reset_index()
sector_avg.columns = ["Sector", "Average Usage (%)"]
fig_bar = px.bar(
    sector_avg,
    x="Sector",
    y="Average Usage (%)",
    color="Average Usage (%)",
    color_continuous_scale="Teal",
)
st.plotly_chart(fig_bar, use_container_width=True)

# Pie Chart
st.subheader("Water Scarcity Level Distribution")
scarcity_data = filtered_data["Water Scarcity Level"].value_counts().reset_index()
scarcity_data.columns = ["Water Scarcity Level", "Count"]
fig_pie = px.pie(
    scarcity_data,
    names="Water Scarcity Level",
    values="Count",
    color_discrete_sequence=px.colors.sequential.Tealgrn,
)
st.plotly_chart(fig_pie, use_container_width=True)

# Additional Charts
st.subheader("Rainfall vs Water Consumption")
fig_scatter = px.scatter(
    filtered_data,
    x="Rainfall Impact (Annual Precipitation in mm)",
    y="Total Water Consumption (Billion Cubic Meters)",
    color="Water Scarcity Level",
    size="Groundwater Depletion Rate (%)",
    hover_data=["Country", "Year", "Per Capita Water Use (Liters per Day)"],
    title="Rainfall Impact and Total Consumption",
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Top 10 Countries by Average Water Consumption")
top_countries = (
    filtered_data.groupby("Country", as_index=False)[
        "Total Water Consumption (Billion Cubic Meters)"
    ]
    .mean()
    .sort_values("Total Water Consumption (Billion Cubic Meters)", ascending=False)
    .head(10)
)
fig_top_countries = px.bar(
    top_countries,
    x="Country",
    y="Total Water Consumption (Billion Cubic Meters)",
    color="Total Water Consumption (Billion Cubic Meters)",
    color_continuous_scale="Tealgrn",
)
st.plotly_chart(fig_top_countries, use_container_width=True)

st.subheader("Average Consumption by Country (World Map)")
country_map_data = filtered_data.groupby("Country", as_index=False)[
    "Total Water Consumption (Billion Cubic Meters)"
].mean()
fig_map = px.choropleth(
    country_map_data,
    locations="Country",
    locationmode="country names",
    color="Total Water Consumption (Billion Cubic Meters)",
    color_continuous_scale="Teal",
)
st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Correlation Heatmap")
correlation_columns = [
    "Total Water Consumption (Billion Cubic Meters)",
    "Per Capita Water Use (Liters per Day)",
    "Agricultural Water Use (%)",
    "Industrial Water Use (%)",
    "Household Water Use (%)",
    "Rainfall Impact (Annual Precipitation in mm)",
    "Groundwater Depletion Rate (%)",
]
correlation_data = filtered_data[correlation_columns].corr()
fig_heatmap = px.imshow(
    correlation_data,
    text_auto=True,
    color_continuous_scale="Tealgrn",
    title="Correlation Between Key Water Metrics",
)
st.plotly_chart(fig_heatmap, use_container_width=True)
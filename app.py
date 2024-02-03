import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plost


st.set_page_config(layout="wide")
# Function to fetch data from API
def fetch_data():
    url = "https://fakestoreapi.com/products/"
    query_params = {
        "limit": 20
    }
    response = requests.get(url, params=query_params)
    data_response = response.json()
    title = []
    price = []
    category = []
    rating = []
    count = []
    for item in data_response:
        title.append(item['title'])
        price.append(item['price'])
        category.append(item['category'])
        rating.append(item['rating']['rate'])
        count.append(item['rating']['count'])
    data_dict = {'Title': title,
                 'Price': price,
                 'category': category,
                 'rating': rating,
                 'count': count}
    df = pd.DataFrame(data_dict)
    return df

# Cache data for 6 hours
@st.cache_data(ttl=60 * 60 * 6, show_spinner="Fetching data from API...")
def get_data():
    return fetch_data()

# Get the cached data or fetch new data if cache expired
df = get_data()

# Function to calculate total revenue
def calculate_revenue(row):
    return row["Price"] * row["count"]


# Add revenue column
df["revenue"] = df.apply(calculate_revenue, axis=1)

average_rating = df["rating"].mean()
total_revenue = df["revenue"].sum()

target_average_rating = 4.5
target_average_profit = 1000000

# Calculate the differences
rating_delta = average_rating - target_average_rating
profit_delta = total_revenue - target_average_profit
# Dashboard layout


st.title("Francis Store Performance Tracker🚀")

col_average, col_total = st.columns(2)

with col_average:
    st.metric(label="Average Rating", value=f"{average_rating:.2f}", delta=rating_delta)

with col_total:
    st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}", delta=profit_delta)
# Split the layout into two columns and two rows using st.columns and st.containers
col1, col2 = st.columns(2)

# First row
with col1:
    st.header("Category Ratings📊")
    category_ratings = df.groupby("category")["rating"].mean().reset_index()
    st.bar_chart(category_ratings, x="category", y="rating")

with col2:
    st.header("Top Products🔝")
    top_products = df.groupby("Title")["count"].sum().sort_values(ascending=False).head(10).reset_index()
    st.bar_chart(top_products, x="Title", y="count")

# Second row
col3, col4 = st.columns(2)

with col3:
    st.header("Category Revenue💰")
    category_revenue = df.groupby("category")["revenue"].sum().reset_index()
    plost.donut_chart(data=category_revenue,theta="revenue",color='category',legend='bottom',use_container_width=True)

with col4:
    st.header("Top Revenue Products🚀")
    top_revenue_products = df.groupby("Title")["revenue"].sum().sort_values(ascending=False).head(10).reset_index()
    st.bar_chart(top_revenue_products, x="Title", y="revenue")
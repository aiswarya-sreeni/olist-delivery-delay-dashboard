import pandas as pd
import streamlit as st

# 1. Page Title (The header of our dashboard website)
st.title("🚚 Supply Chain Delivery Delay Dashboard")
st.write("Let's look at why shipments get delayed!")

# 2. Load our raw ingredients (The CSV files)
@st.cache_data # This keeps the app running super fast
def load_and_clean_data():
    # Read the data files from our data folder
    orders = pd.read_csv('data/olist_orders_dataset.csv')
    reviews = pd.read_csv('data/olist_order_reviews_dataset.csv')
    
    # Convert text dates into real calendar times
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
    orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])
    
    # Only look at completed deliveries
    orders = orders.dropna(subset=['order_delivered_customer_date'])
    
    # Calculate delay days: Actual delivery day minus Estimated delivery day
    orders['delay_days'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']).dt.days
    
    # Create a true/false marker for delays
    orders['is_delayed'] = orders['delay_days'] > 0
    
    # Merge orders together with customer review scores
    combined_data = pd.merge(orders, reviews, on='order_id', how='inner')
    return combined_data

# Run our cleaning function
df = load_and_clean_data()

# 3. Display our findings on our dashboard screen
st.header("📊 Key Metrics")

# Count delayed packages
total_packages = len(df)
delayed_packages = df['is_delayed'].sum()
delay_percent = (delayed_packages / total_packages) * 100

# Show scorecards on the website
col1, col2 = st.columns(2)
col1.metric("Total Shipments Analyzed", f"{total_packages:,}")
col2.metric("Delayed Shipments", f"{delayed_packages:,} ({delay_percent:.1f}%)")

# Answer Question: Does delay affect scores?
st.header("⭐ Do delays make customers unhappy?")
avg_scores = df.groupby('is_delayed')['review_score'].mean()

st.write(f"🟢 **On-Time Deliveries** get an average score of: **{avg_scores[False]:.2f} / 5 stars**")
st.write(f"🔴 **Delayed Deliveries** drop all the way down to: **{avg_scores[True]:.2f} / 5 stars**")

# Answer Question: Which product categories are slowest?
st.header("🐢 Slowest Product Categories")
st.write("These categories experience the longest delivery delays:")

# We need to load the product classification sheet to get names
products = pd.read_csv('data/olist_products_dataset.csv')
items = pd.read_csv('data/olist_order_items_dataset.csv')

# Combine them with our main delay data frame
df_items = pd.merge(items, products, on='product_id', how='inner')
df_full = pd.merge(df_items, df, on='order_id', how='inner')

# Calculate the average true delay days for each category
# If delay is negative (early), change to 0 for tracking true delays
df_full['true_delay'] = df_full['delay_days'].apply(lambda x: x if x > 0 else 0)
category_delays = df_full.groupby('product_category_name')['true_delay'].mean().sort_values(ascending=False).head(10)

# Render a beautiful interactive bar chart directly on the dashboard page!
st.bar_chart(category_delays)

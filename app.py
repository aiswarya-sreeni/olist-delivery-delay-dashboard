import pandas as pd
import streamlit as st

# 1. 🌟 Make the layout wide to fill empty spaces on the sides!
st.set_page_config(layout="wide")

st.title("🚚 Supply Chain Delivery Delay Dashboard")
st.write("An interactive analytics layout exploring regional bottlenecks and satisfaction trends.")
st.markdown("---")

# 2. Load and Clean Core Datasets
@st.cache_data
def load_and_clean_data():
    orders = pd.read_csv('data/olist_orders_dataset.csv')
    reviews = pd.read_csv('data/olist_order_reviews_dataset.csv')
    sellers = pd.read_csv('data/olist_sellers_dataset.csv')
    items = pd.read_csv('data/olist_order_items_dataset.csv')
    
    # Convert text dates into real calendar times
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
    orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])
    
    # Drop missing delivery records
    orders = orders.dropna(subset=['order_delivered_customer_date'])
    
    # Calculate delay metrics
    orders['delay_days'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']).dt.days
    orders['is_delayed'] = orders['delay_days'] > 0
    orders['true_delay_days'] = orders['delay_days'].apply(lambda x: x if x > 0 else 0)
    
    # Combine order tracking data with reviews and seller hubs
    df_merged = pd.merge(orders, reviews, on='order_id', how='inner')
    df_items = pd.merge(items, sellers, on='seller_id', how='inner')
    final_df = pd.merge(df_merged, df_items, on='order_id', how='inner')
    
    return final_df

df = load_and_clean_data()

# 3. 📈 Stretch Metrics across 4 columns to fill space
st.header("📊 Key Operational Parameters")
total_packages = len(df['order_id'].unique())
delayed_packages = df[df['is_delayed'] == True]['order_id'].nunique()
delay_percent = (delayed_packages / total_packages) * 100
avg_delay_overall = df[df['is_delayed'] == True]['true_delay_days'].mean()
avg_review = df['review_score'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total Shipments", f"{total_packages:,}")
col2.metric("⚠️ Delayed Shipments", f"{delayed_packages:,} ({delay_percent:.1f}%)")
col3.metric("⏳ Avg Delay Duration", f"{avg_delay_overall:.1f} Days")
col4.metric("⭐ Overall Rating Baseline", f"{avg_review:.2f} / 5.0")

st.markdown("---")

# 4. 🗺️ Interactive Delay Map Layout (Filling out the middle tier)
st.header("📍 Regional Supply Chain Delay Map (Brazil)")
st.write("Discover which geographic hubs face the longest logisitical backlogs.")

# Map coordinates for Brazilian State capitals to render visual pinpoints
geo_data = {
    'seller_state': ['SP', 'RJ', 'MG', 'PR', 'SC', 'RS', 'BA', 'GO', 'DF', 'PE'],
    'latitude': [-23.5505, -22.9068, -19.9167, -25.4284, -27.5954, -30.0346, -12.9777, -16.6869, -15.7942, -8.0578],
    'longitude': [-46.6333, -43.1729, -43.9345, -49.2733, -48.5480, -51.2177, -38.5016, -49.2648, -47.8822, -34.8778]
}
coords_df = pd.DataFrame(geo_data)

# Compute delay averages by seller region
state_delays = df.groupby('seller_state')['true_delay_days'].mean().reset_index()
map_df = pd.merge(state_delays, coords_df, on='seller_state', how='inner')

# Allow the user to toggle circle sizes on the map view layout
map_scale = st.slider("Adjust Map Scale Pinpoint Size:", min_value=10, max_value=200, value=50)
map_df['size'] = map_df['true_delay_days'] * map_scale

# Render the interactive map visualization
st.map(map_df, latitude='latitude', longitude='longitude', size='size')
st.caption("💡 Larger circles identify states where sellers generate higher average delivery delays.")

st.markdown("---")

# 5. Bottom Layer Layout: Unhappiness Insights & Product Backlogs
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("⭐ Customer Satisfaction Divergence")
    avg_scores = df.groupby('is_delayed')['review_score'].mean()
    st.write(f"🟢 **On-Time Deliveries:** **{avg_scores[False]:.2f} stars**")
    st.write(f"🔴 **Delayed Deliveries:** **{avg_scores[True]:.2f} stars**")
    
    # Review Score Dropdown Distribution Filter
    delivery_filter = st.selectbox(
        "Filter Review Score Distribution Chart:",
        options=["Show All Shipments", "On-Time Deliveries Only", "Delayed Deliveries Only"]
    )
    if delivery_filter == "On-Time Deliveries Only":
        f_df = df[df['is_delayed'] == False]
    elif delivery_filter == "Delayed Deliveries Only":
        f_df = df[df['is_delayed'] == True]
    else:
        f_df = df
    st.bar_chart(f_df['review_score'].value_counts().sort_index())

with right_col:
    st.subheader("🐢 Top 10 Slowest Product Categories")
    products = pd.read_csv('data/olist_products_dataset.csv')
    df_prod = pd.merge(df, products, on='product_id', how='inner')
    cat_delays = df_prod.groupby('product_category_name')['true_delay_days'].mean().sort_values(ascending=False).head(10)
    st.bar_chart(cat_delays)

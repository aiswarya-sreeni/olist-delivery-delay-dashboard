import pandas as pd
import streamlit as st

# 1. 🌟 Make the layout wide to fill empty spaces on the sides!
st.set_page_config(layout="wide")

st.title("🚚 Supply Chain Delivery Delay Dashboard")
st.write("An interactive executive analytics layout exploring regional bottlenecks, fulfillment metrics, and satisfaction trends.")
st.markdown("---")

# 2. Load and Clean Core Datasets
@st.cache_data
def load_and_clean_data():
    orders = pd.read_csv('data/olist_orders_dataset.csv')
    reviews = pd.read_csv('data/olist_order_reviews_dataset.csv')
    sellers = pd.read_csv('data/olist_sellers_dataset.csv')
    items = pd.read_csv('data/olist_order_items_dataset.csv')
    products = pd.read_csv('data/olist_products_dataset.csv')
    translations = pd.read_csv('data/product_category_name_translation.csv')
    
    # Convert text dates into real calendar times
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    orders['order_delivered_carrier_date'] = pd.to_datetime(orders['order_delivered_carrier_date'])
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
    orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])
    
    # Drop missing delivery records
    orders = orders.dropna(subset=['order_delivered_customer_date'])
    
    # Calculate core delay metrics
    orders['delay_days'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']).dt.days
    orders['is_delayed'] = orders['delay_days'] > 0
    orders['true_delay_days'] = orders['delay_days'].apply(lambda x: x if x > 0 else 0)
    
    # Calculate Advanced Supply Chain Metrics
    orders['is_on_time'] = orders['delay_days'] <= 0
    orders['fulfillment_cycle_days'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days
    orders['seller_handling_days'] = (orders['order_delivered_carrier_date'] - orders['order_purchase_timestamp']).dt.days
    
    # Translate product categories to English
    products_translated = pd.merge(products, translations, on='product_category_name', how='left')
    # Use English name if available, fallback to Portuguese if missing
    products_translated['product_category_name_english'] = products_translated['product_category_name_english'].fillna(products_translated['product_category_name'])
    
    # Combine everything together into a clean master file
    df_merged = pd.merge(orders, reviews, on='order_id', how='inner')
    df_items = pd.merge(items, sellers, on='seller_id', how='inner')
    df_prod = pd.merge(df_items, products_translated, on='product_id', how='inner')
    final_df = pd.merge(df_merged, df_prod, on='order_id', how='inner')
    
    return final_df

df = load_and_clean_data()

# 3. 📈 Executive Operational Command Center (2 Rows of 4 Cards)
st.header("📊 Executive Operational Command Center")

total_packages = len(df['order_id'].unique())
delayed_packages = df[df['is_delayed'] == True]['order_id'].nunique()
delay_percent = (delayed_packages / total_packages) * 100

unique_orders = df.drop_duplicates(subset=['order_id'])
otd_rate = (unique_orders['is_on_time'].sum() / len(unique_orders)) * 100
avg_cycle_time = unique_orders['fulfillment_cycle_days'].mean()
avg_handling_time = unique_orders['seller_handling_days'].mean()
avg_delay_overall = unique_orders[unique_orders['is_delayed'] == True]['true_delay_days'].mean()
avg_review = df['review_score'].mean()
revenue_at_risk = df[df['is_delayed'] == True]['price'].sum()

# Row 1: High-Level Service Standards & Volume
row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
row1_col1.metric("🎯 On-Time Delivery (OTD) Rate", f"{otd_rate:.1f}%", help="Percentage of orders arriving on or before the promised delivery date.")
row1_col2.metric("📦 Total Shipments", f"{total_packages:,}")
row1_col3.metric("⚠️ Delayed Shipments", f"{delayed_packages:,} ({delay_percent:.1f}%)")
row1_col4.metric("🚨 Revenue at Risk", f"${revenue_at_risk:,.2f}", delta="- Risk Exposure", delta_color="inverse")

st.markdown(" ") 

# Row 2: Velocity & Satisfaction Parameters
row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
row2_col1.metric("🏁 Avg Fulfillment Cycle", f"{avg_cycle_time:.1f} Days")
row2_col2.metric("🏭 Avg Seller Handling Time", f"{avg_handling_time:.1f} Days")
row2_col3.metric("🐢 Avg Delay Severity", f"{avg_delay_overall:.1f} Days")
row2_col4.metric("⭐ Overall Rating Baseline", f"{avg_review:.2f} / 5.0")

st.markdown("---")

# 4. 🗺️ Interactive Delay Map Layout
st.header("📍 Regional Supply Chain Delay Map (Brazil)")
st.write("Discover which geographic seller hubs generate the longest logistical backlogs.")

geo_data = {
    'seller_state': ['SP', 'RJ', 'MG', 'PR', 'SC', 'RS', 'BA', 'GO', 'DF', 'PE'],
    'latitude': [-23.5505, -22.9068, -19.9167, -25.4284, -27.5954, -30.0346, -12.9777, -16.6869, -15.7942, -8.0578],
    'longitude': [-46.6333, -43.1729, -43.9345, -49.2733, -48.5480, -51.2177, -38.5016, -49.2648, -47.8822, -34.8778]
}
coords_df = pd.DataFrame(geo_data)
state_delays = df.groupby('seller_state')['true_delay_days'].mean().reset_index()
map_df = pd.merge(state_delays, coords_df, on='seller_state', how='inner')

map_scale = st.slider("Adjust Map Scale Pinpoint Size:", min_value=10, max_value=200, value=50)
map_df['size'] = map_df['true_delay_days'] * map_scale
st.map(map_df, latitude='latitude', longitude='longitude', size='size')

st.markdown("---")

# 5. Bottom Layer Layout: Unhappiness Insights & Product Backlogs
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("⭐ Customer Satisfaction Divergence")
    avg_scores = df.groupby('is_delayed')['review_score'].mean()
    st.write(f"🟢 **On-Time Deliveries:** **{avg_scores[False]:.2f} stars**")
    st.write(f"🔴 **Delayed Deliveries:** **{avg_scores[True]:.2f} stars**")
    
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
        
    review_sort = st.selectbox(
        "Sort Review Scores By:",
        options=["Star Rating Axis (1 to 5)", "Highest Count First (Descending)", "Lowest Count First (Ascending)"]
    )
    
    review_counts = f_df['review_score'].value_counts()
    if review_sort == "Highest Count First (Descending)":
        review_counts = review_counts.sort_values(ascending=False)
    elif review_sort == "Lowest Count First (Ascending)":
        review_counts = review_counts.sort_values(ascending=True)
    else:
        review_counts = review_counts.sort_index()
        
    st.bar_chart(review_counts)

with right_col:
    st.subheader("⏱️ Product Category Delivery Speed")
    
    # Calculate the total end-to-end fulfillment days using our translated column
    cat_speeds = df.groupby('product_category_name_english')['fulfillment_cycle_days'].mean()
    
    product_sort = st.selectbox(
        "Sort Product Categories By:",
        options=["Slowest Categories (Longest Wait Time)", "Fastest Categories (Shortest Wait Time)"]
    )
    
    if product_sort == "Fastest Categories (Shortest Wait Time)":
        sorted_cats = cat_speeds.sort_values(ascending=True).head(10)
    else:
        sorted_cats = cat_speeds.sort_values(ascending=False).head(10)
        
    # Convert the series to a clean data frame and rename the axis index for the graph label
    sorted_cats_df = sorted_cats.to_frame(name="Average Days")
    sorted_cats_df.index.name = "Product Category"
    
    # Render the polished chart
    st.bar_chart(sorted_cats_df)
    st.caption("📊 Shows the average total days taken from customer order placement to physical home delivery.")


# ==========================================================
# 📊 NEW INTERACTIVE PIE CHART & RIBBON CHART ADDITIONS
# ==========================================================
st.markdown("---")
st.header("🎛️ Operational Breakdown & Monthly Trends")

# Ensure required libraries are imported at the top or here locally
import plotly.express as px

# 1. Process data for categories dynamically
def assign_delivery_tier(days):
    if days <= 0:
        return 'On-Time Delivery'
    elif days <= 7:
        return 'Minor Delay (1-7 Days)'
    else:
        return 'Severe Delay (>7 Days)'

# Safety copy of unique orders for timeline building
df_unique = df.drop_duplicates(subset=['order_id']).copy()
df_unique['fulfillment_status'] = df_unique['delay_days'].apply(assign_delivery_tier)

# Create two layout columns to seat the charts side-by-side cleanly
mid_col1, mid_col2 = st.columns([1, 2]) # 1/3rd width to Pie, 2/3rd width to Ribbon

with mid_col1:
    st.subheader("🍰 Shipment Fulfillment Share")
    status_counts = df_unique['fulfillment_status'].value_counts().reset_index()
    status_counts.columns = ['Fulfillment Status', 'Orders']
    
    # Render an interactive, compact Plotly Pie Chart
    fig_pie = px.pie(
        status_counts, 
        values='Orders', 
        names='Fulfillment Status',
        color='Fulfillment Status',
        color_discrete_map={
            'On-Time Delivery': '#2ca02c', 
            'Minor Delay (1-7 Days)': '#ff7f0e', 
            'Severe Delay (>7 Days)': '#d62728'
        },
        hole=0.3 # Turns it into a clean, modern donut configuration
    )
    
    # Configure smaller sizing layout constraints
    fig_pie.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=320,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with mid_col2:
    st.subheader("🎀 Monthly Fulfillment Ribbon Trend")
    
    # Extract Year-Month periods for tracking historical distribution
    df_unique['Period'] = df_unique['order_purchase_timestamp'].dt.to_period('M').astype(str)
    
    # Group and pivot data to align columns for a stacked ribbon format
    trend_data = df_unique.groupby(['Period', 'fulfillment_status']).size().unstack(fill_value=0)
    
    # Ensure correct ordering of the stacked layers
    columns_order = [c for c in ['On-Time Delivery', 'Minor Delay (1-7 Days)', 'Severe Delay (>7 Days)'] if c in trend_data.columns]
    trend_data = trend_data[columns_order]
    
    # Render an elegant, interactive ribbon area chart using Streamlit's native stack engine
    st.area_chart(trend_data, height=320)
    st.caption("📅 Hover across the ribbon blocks to audit service performance spikes across operational timelines.")

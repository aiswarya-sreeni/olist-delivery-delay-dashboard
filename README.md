# Supply Chain Delivery Delay Dashboard

An end-to-end data analytics project exploring the operational bottlenecks causing e-commerce delivery delays in Brazil, and how those delays directly impact customer review scores.

## 📊 Key Findings
* **Total Volume:** Analyzed **96,359 completed shipments**, identifying a **6.7% baseline delay rate** (6,410 delayed orders) across the supply chain network.
* **Customer Impact:** Deliveries that arrived on time scored a strong average of **4.29 / 5 stars**. However, once an order was delayed, customer satisfaction plummeted down to **2.27 / 5 stars**.
* **Slowest Categories:** Home comfort items (`casa_conforto_2`) and furniture mattresses (`moveis_colchao_estofados`) experienced the highest average operational delays, tracking over 2 days late.

## 🏗️ Project Structure
* `data/`: Raw Brazilian E-Commerce datasets (Olist).
* `app.py`: Streamlit dashboard calculation logic and interactive bar charts.
* `requirements.txt`: Python package dependencies (`pandas`, `streamlit`).

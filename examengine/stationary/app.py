import streamlit as st
from google.cloud import bigquery
import pandas as pd
import datetime
import time

st.set_page_config(page_title="Stationary Store Uploader", page_icon="📦")

st.title("📦 Stationary Store Sales Uploader")

# Sales form
with st.form("sales_form"):
    item_id = st.text_input("Item ID")
    quantity_sold = st.number_input("Quantity Sold", min_value=1, step=1)
    submitted = st.form_submit_button("Submit Sale")

if submitted:
    if item_id:
        client = bigquery.Client()
        table_id = "exam-engine-462520.store_data.sales_staging"
        rows = [{"item_id": item_id, "quantity_sold": quantity_sold}]
        errors = client.insert_rows_json(table_id, rows)
        if not errors:
            st.success("Sale recorded!")
        else:
            st.error(f"Error: {errors}")
    else:
        st.error("Item ID is required.")

# Countdown to 9:00 PM
st.markdown("### ⚠️ Time left until scheduled update (9:00 PM)")
now = datetime.datetime.now()
target_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
if now > target_time:
    target_time += datetime.timedelta(days=1)
remaining = target_time - now
st.info(f"{remaining.seconds // 3600} hours and {(remaining.seconds // 60) % 60} minutes left.")

# Manual Update Section
st.markdown("### ⚙️ Manual Inventory Update")
if st.button("🛠️ Force Update Now"):
    client = bigquery.Client()

    # Run MERGE query
    merge_query = """
    MERGE `store_data.inventory` AS inv
    USING (
      SELECT item_id, SUM(quantity_sold) AS quantity_sold
      FROM `store_data.sales_staging`
      GROUP BY item_id
    ) AS sales
    ON inv.item_id = sales.item_id
    WHEN MATCHED THEN
      UPDATE SET inv.quantity_available = inv.quantity_available - sales.quantity_sold;
    """
    client.query(merge_query).result()

    # Clear staging safely
    clear_query = """
    CREATE OR REPLACE TABLE `store_data.sales_staging` (
      item_id STRING,
      quantity_sold INT64
    )
    """
    client.query(clear_query).result()

    st.success("✅ Inventory manually updated and staging table cleared.")

# Show live data
st.markdown("### 📊 Current Inventory Table")
client = bigquery.Client()
inv_df = client.query("SELECT * FROM `store_data.inventory`").to_dataframe()
st.dataframe(inv_df)

st.markdown("### 🧾 Sales Staging Table")
stage_df = client.query("SELECT * FROM `store_data.sales_staging`").to_dataframe()
st.dataframe(stage_df)




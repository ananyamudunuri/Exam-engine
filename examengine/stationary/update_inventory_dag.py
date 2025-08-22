from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
}

with DAG(
    dag_id='daily_inventory_update',
    default_args=default_args,
    start_date=datetime(2025, 6, 18),
    schedule_interval='0 21 * * *',  # Runs daily at 9:00 PM UTC
    catchup=False,
    description='Updates inventory by merging with sales_staging table',
) as dag:

    run_merge_query = BashOperator(
        task_id='run_merge_query',
        bash_command="""
        bq query --use_legacy_sql=false '
        MERGE `exam-engine-462520.store_data.inventory` AS inv
        USING (
          SELECT item_id, SUM(quantity_sold) AS quantity_sold
          FROM `exam-engine-462520.store_data.sales_staging`
          GROUP BY item_id
        ) AS sales
        ON inv.item_id = sales.item_id
        WHEN MATCHED THEN
          UPDATE SET inv.quantity_available = inv.quantity_available - sales.quantity_sold;
        '
        """
    )

    clear_sales_staging = BashOperator(
        task_id='clear_sales_staging',
        bash_command="bq query --use_legacy_sql=false 'DELETE FROM `exam-engine-462520.store_data.sales_staging` WHERE TRUE;'"
    )

    run_merge_query >> clear_sales_staging

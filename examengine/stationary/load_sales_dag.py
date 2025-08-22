from airflow import models
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Define default args
default_args = {
    "start_date": datetime(2025, 6, 19),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
with models.DAG(
    "load_sales_staging_dag",
    default_args=default_args,
    schedule_interval="0 21 * * *",  # Run daily at 9:00 PM
    catchup=False,
    tags=["inventory", "sales"],
) as dag:

    load_sales_to_staging = BashOperator(
        task_id="run_load_to_staging_script",
        bash_command=(
            "python /home/airflow/gcs/data/load_scripts/load_to_staging.py"
        ),
    )

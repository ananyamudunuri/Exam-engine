from google.cloud import bigquery

def main():
    client = bigquery.Client()

    # Replace with the correct GCS path to your CSV file
    gcs_uri = "gs://us-central1-inventory-pipel-867089cb-bucket/data/sales_2025-06-18.csv"

    table_id = "exam-engine-462520.store_data.sales_staging"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition="WRITE_APPEND"
    )

    load_job = client.load_table_from_uri(
        gcs_uri, table_id, job_config=job_config
    )

    print("Starting CSV load...")
    load_job.result()
    print("✅ Load complete.")

    table = client.get_table(table_id)
    print(f"✅ {table.num_rows} rows now in sales_staging.")

if __name__ == "__main__":
    main()

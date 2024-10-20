from shopify_dlt_pipeline import load_all_resources, incremental_load_with_backloading, load_partner_api_transactions
import logging

# Initialize logger
logger = logging.getLogger("loop_case")

if __name__ == "__main__":
    resources = ["orders", "products", "customers"]

    try:
        load_all_resources(resources, start_date="2024-10-14")
        # Uncomment to run incremental loading
        # incremental_load_with_backloading(resources)
        # Uncomment to run partner API transaction loading
        # load_partner_api_transactions()
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")

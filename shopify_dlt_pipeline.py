import dlt
from dlt.common import pendulum
from typing import List, Tuple
from shopify_dlt import shopify_source, TAnyDateTime, shopify_partner_query
import logging
import time


# Function to configure logging
def setup_logging() -> None:
    """Sets up the logging configuration for the pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("loop_case")
    return logger


# Initialize the logger
logger = setup_logging()


def log_execution_time(func):
    """Decorator to log execution time for functions."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error during {func.__name__}: {e}")
            raise
        else:
            duration = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {duration:.2f} seconds")
        return result

    return wrapper


def create_pipeline(pipeline_name: str, dataset_name: str):
    """Helper function to create a DLT pipeline."""
    logger.info(f"Creating pipeline {pipeline_name}")
    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination='bigquery',
        dataset_name=dataset_name
    )


def execute_pipeline(pipeline, data):
    """Helper function to execute a pipeline and handle logging."""
    try:
        load_info = pipeline.run(data)
        logger.info(f"Load completed successfully: {load_info}")
        return load_info
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise


@log_execution_time
def load_all_resources(resources, start_date: TAnyDateTime) -> None:
    """Execute a pipeline that will load the given Shopify resources incrementally starting at the given start date.
    Subsequent runs will load only items updated since the previous run.
    """
    logger.info(f"Loading resources: {resources}, starting from {start_date}")

    pipeline = create_pipeline(pipeline_name="shopify", dataset_name="shopify_raw_data")
    data = shopify_source(start_date=start_date).with_resources(*resources)

    execute_pipeline(pipeline, data)


@log_execution_time
def incremental_load_with_backloading(resources) -> None:
    """Load past orders from Shopify in chunks of 1 week each using the start_date and end_date parameters.
    This can reduce the potential failure window when loading large amounts of historic data.
    Chunks and incremental load can also be run in parallel to speed up the initial load.
    """
    logger.info("Starting incremental backloading process.")

    pipeline = create_pipeline(pipeline_name="shopify", dataset_name="shopify_raw_data_historical")

    # Load all orders from a start date to now
    min_start_date = current_start_date = pendulum.datetime(2024, 10, 1)
    max_end_date = pendulum.now()

    # Create a list of time ranges of 1 week each
    ranges: List[Tuple[pendulum.DateTime, pendulum.DateTime]] = []
    while current_start_date < max_end_date:
        end_date = min(current_start_date.add(weeks=1), max_end_date)
        ranges.append((current_start_date, end_date))
        current_start_date = end_date

    # Run the pipeline for each time range
    for start_date, end_date in ranges:
        logger.info(f"Loading orders between {start_date} and {end_date}")
        data = shopify_source(
            start_date=start_date,
            end_date=end_date,
            created_at_min=min_start_date).with_resources(*resources)

        execute_pipeline(pipeline, data)

    # Continue loading new data incrementally starting at the end of the last range
    data = shopify_source(
        start_date=max_end_date,
        created_at_min=min_start_date).with_resources(*resources)

    execute_pipeline(pipeline, data)


@log_execution_time
def load_partner_api_transactions() -> None:
    """Load transactions from the Shopify Partner API.
    The partner API uses GraphQL and this example loads all transactions from the beginning paginated.
    """
    logger.info("Starting Shopify Partner API transaction load.")

    pipeline = create_pipeline(pipeline_name="shopify_partner", dataset_name="shopify_partner_api_transactions")

    # Construct query to load transactions 100 per page
    query = """query Transactions($after: String, first: 100) {
        transactions(after: $after) {
            edges {
                cursor
                node {
                    id
                }
            }
        }
    }
    """

    # Configure the resource with the query and json paths to extract the data and pagination cursor
    resource = shopify_partner_query(
        query,
        data_items_path="data.transactions.edges[*].node",
        pagination_cursor_path="data.transactions.edges[-1].cursor",
        pagination_variable_name="after",
    )

    execute_pipeline(pipeline, resource)

"""
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
"""
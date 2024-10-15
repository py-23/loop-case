"""Pipeline to load shopify data into BigQuery.
"""

import dlt
from dlt.common import pendulum
from typing import List, Tuple
from shopify_dlt import shopify_source, TAnyDateTime, shopify_partner_query
import logging
# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("loop_case")


def load_all_resources(resources, start_date: TAnyDateTime) -> None:
    """Execute a pipeline that will load the given Shopify resources incrementally beginning at the given start date.
    Subsequent runs will load only items updated since the previous run.
    """

    pipeline = dlt.pipeline(
        pipeline_name="shopify",
        destination='bigquery',
        dataset_name="shopify_raw_data"
    )
    logger.info("Starting pipeline")
    load_info = pipeline.run(
        shopify_source(start_date=start_date).with_resources(*resources)
    )
    logger.info(load_info)


def incremental_load_with_backloading(resources) -> None:
    """Load past orders from Shopify in chunks of 1 week each using the start_date and end_date parameters.
    This can useful to reduce the potiential failure window when loading large amounts of historic data.
    Chunks and incremental load can also be run in parallel to speed up the initial load.
    """

    pipeline = dlt.pipeline(
        pipeline_name="shopify",
        destination='bigquery',
        dataset_name="shopify_raw_data_historical"
    )

    # Load all orders from a start date to now
    min_start_date = current_start_date = pendulum.datetime(2024, 10, 1)
    max_end_date = pendulum.now()

    # Create a list of time ranges of 1 week each, we'll use this to load the data in chunks
    ranges: List[Tuple[pendulum.DateTime, pendulum.DateTime]] = []
    while current_start_date < max_end_date:
        end_date = min(current_start_date.add(weeks=1), max_end_date)
        ranges.append((current_start_date, end_date))
        current_start_date = end_date

    # Run the pipeline for each time range created above
    for start_date, end_date in ranges:
        logger.info(f"Load orders between {start_date} and {end_date}")
        # Create the source with start and end date set according to the current time range to filter
        # created_at_min lets us set a cutoff to exclude orders created before the initial date of (2023-01-01)
        # even if they were updated after that date
        data = shopify_source(
            start_date=start_date,
            end_date=end_date,
            created_at_min=min_start_date).with_resources(*resources)

        load_info = pipeline.run(data)
        logger.info(load_info)

    # Continue loading new data incrementally starting at the end of the last range
    # created_at_min still filters out items created before 2023-01-01
    load_info = pipeline.run(
        shopify_source(
            start_date=max_end_date,
            created_at_min=min_start_date).with_resources(*resources)
    )
    logger.info(load_info)


def load_partner_api_transactions() -> None:
    """Load transactions from the Shopify Partner API.
    The partner API uses GraphQL and this example loads all transactions from the beginning paginated.

    The `shopify_partner_query` resource can be used to run custom GraphQL queries to load paginated data.
    """

    pipeline = dlt.pipeline(
        pipeline_name="shopify_partner",
        destination='bigquery',
        dataset_name="shopify_partner_api_transactions",
    )

    # Construct query to load transactions 100 per page, the `$after` variable is used to paginate
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
        # JSON path pointing to the data item in the results
        data_items_path="data.transactions.edges[*].node",
        # JSON path pointing to the highest page cursor in the results
        pagination_cursor_path="data.transactions.edges[-1].cursor",
        # The variable name used for pagination
        pagination_variable_name="after",
    )

    load_info = pipeline.run(resource)
    logger.info(load_info)


if __name__ == "__main__":
    resources = ["orders", "products", "customers"]

    load_all_resources(resources, start_date="2024-10-14")

    # incremental_load_with_backloading(resources)

    # load_partner_api_transactions()

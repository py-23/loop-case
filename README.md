<h1>Business Case</h1>

<p>This repo contains the code for the business case where a dataflow and data model is required to provide sales data from Shopify. The ingestion and transformation of data from the Shopify API is achieved using dlthub and dbt.</p>

<h2>Ingestion</h2>
<p>The ingestion from the Shopify API is done using dlthub's built in package for Shopify as a source and Bigquery as the destination.</p>

<h3>Getting started with dlthub</h3>
<b><p>Link: </b>https://dlthub.com/docs/dlt-ecosystem/verified-sources/shopify</p>

<p>The endpoints used are: orders, products and customers which provides the data from which we can get the sales information needed</p>

<p>To start, install the dlt cli and run:</p>
<code>dlt init shopify bigquery</code>

<b><p>Docs: </b>https://dlthub.com/docs/reference/command-line-interface</p>

<p>There are 3 ways to ingest data using this repo:</p>
<p>1. Incrementally loading the data from the 3 resources (orders, products, customers)</p>
<p>2. Incrementally loading the data for specific date ranges for back-filling or ingesting the data in chunks</p>
<p>3. Using GraphQL to create a custom query to ingest the data from the partner API of Shopify which would be highly efficient if only certain nodes are required to be ingested</p>

<h3>Cloud run</h3>

<p>The shopify_dlt_pipeline.py script is dockerized and the image is pushed via github actions to Google container registry. Cloud run then runs the latest image as it is serverless compute and can scale horizontally as needed. The workflow orchestrator used is Airflow (cloud composer) that has the cloud run job operator and triggers it based on a cron schedule.</p>

<p>Batch ingestion was chosen because it is well suited for the analytics use case of analysing data in a data warehouse and visualizing it as this process does not happen on real-time data but rather on data from a specific interval (weekly sales/monthly sales etc.)</p>

<h4>Improvements in ingestion</h4>
<p>Micro-batch, real-time or event based ingestion may be a better fit over the longer term as the amount of data increases and the number of sources. This can be achieved by using Google pub/sub and topics so that the data is pushed to the topic and then automatically ingested into bigquery when available. Consideration needs to be taken into account for the frequency of API calls and the impact this has on the Shopify API.</p>

<h2>Transformation</h2>

<p>dbt is used to transform the raw Shopify data after it lands in BigQuery. The data is transformed in the staging layer, intermediate layer and is exposed to the data analysts in a dimensional model in the mart layer so that a sales fact table is available.</p>
<p>Cloud run is used again to run the dbt code as a job and this is also orchestrated using Airflow.</p>
<h4>Explaining the data model to an analyst</h4>
<p>The sales fact table in the Shopify data mart contains the quantifiable or numerical data involved in a sale of <b>an item</b> such as quantity of items sold, sales price, discounts etc. This is the table that has fields which change more often since sales are happening constantly.</p> 
<p>The customer and product data are stored in dimension tables which have more descriptive attributes such as the type of product, the customer name and address. This information changes much slower this it is stored separately for efficiency and because it can then easily be used to aggregate the fact sales data.</p>
<p>For example: Sales per product type (in the case of loop this could be the loop quiet, enhance or switch earplugs) so we can see the sales values attributed to each type of earplug. There is also a date dimension table which is computed to provide various dates that we can use to aggregate the sales data such as sales per week or quarter. There is an orders fact table which contains the numerical data related to an overall order (which may contain multiple items sold and is thus a higher aggregation).</p>

<h2>Solution architecture principles</h2>

<p>Scalability of the solution: Cloud run allows for horizontal scaling since it is serverless. BigQuery allows for petabyte scale storage and scales as the data size increases. Incremental loading is used in dlthub and dbt which is highly effective and scalable for ingesting data from shopify.</p>

<p>Cost efficiency: Batch ingestion minimizes the API calls made. Using dlthub and dbt minimizes costs as they are open source or have free tiers. Incremental loading ensures that cpu and storage is charged only for new or updated records.</p>

<p>Flexibility: the architecture is flexible, supporting new data sources as needed. dbt models are modular and easily extendable, allowing for incremental improvements in the transformation process.</p>

<p>Modularity:
The pipeline is designed to be modular, with ingestion, transformation, and reporting decoupled from each other.
Each layer of transformation in dbt builds upon the previous one, ensuring reusability and ease of extension.
</p>

<p>Performance:
BigQuery is partitioned by date and clustering by customer id, product type and other commonly used aggregations is in place to improve performance when accessing the data. BigQuery is a columnar storage option meaning it is efficient at retrieving column level data which is well suited to analytics cases as most often only some columns are used. Incremental loading makes the data flow performant as only upserts are taken intp account post initial load.</p>

<h2>Data quality</h2>

Data quality is maintained throughout the pipeline by enforcing schema validation when ingestion data from the Shopify API. dbt tests are also run in CI in github actions to ensure data quality is not compromised as changes are made.
Data profiling is enabled via Dataplex in Bigquery which gives a summary of each table's data quality and the columns and allows for tracking/monitoring of this over time.

<h3>What is still to be implemented</h3>
<p>1. Schema validation on ingestion</p>
<p>2. Completed workflows in Github actions</p>
<p>3. dbt model contracts and tests in CI</p>
<p>4. Airflow cloud run operator and workflow</p>
<p>5. Observability with Montecarlo/orchestra</p>

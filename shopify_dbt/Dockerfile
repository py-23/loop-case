# Use a Python base image, which is sufficient for DBT
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install any required packages listed in your requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the DBT project files into the working directory
COPY . .

# Set environment variable for Google Cloud credentials (can be passed at runtime)
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/gcp_credentials.json"

# Define the command to run DBT (e.g., run the `dbt run` command)
CMD ["dbt", "run", "--select", "stg_shopify_orders"]

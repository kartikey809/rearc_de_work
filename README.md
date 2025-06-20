
# Please find Readme file
This quest leverages the AWS Cloud Development Kit (CDK) to deploy a scalable, serverless data pipeline for ingesting, processing, and analyzing labor and population datasets. It features Lambda functions that automate the extraction of data from public sources like the Bureau of Labor Statistics (BLS) and the Data USA API, storing raw data in Amazon S3. Additionally, it performs exploratory data analysis (EDA) to generate  reports
Folder Structure here  :

## Google Colab NB  - to preview notebook

```react_asn/
├── app.py
├── react_asn/
│ ├── init.py
│ ├── react_asn_stack.py
│ └── lambdas/
│ ├── bls_and_population_ingest/
│ │ ├── ingest.py
│ │ └── lambda_function.py
│ └── eda_report/
│ └── lambda_function.py```


Functions :

1& 2 .Data Ingestion and Staging in S3 bucket
BLS & Population Data Ingestion: Daily Lambda function scrapes BLS time series data and fetches JSON data from the DataUSA API.
S3 Storage: All data is stored in a versioned and organized structure.

3.Performing Exploratory Data Analysis + Report Gen

4.AWS Deployment Setup (CDK+SQS_Lambda)  
SQS Integration: S3 notifications trigger SQS events.

EDA Lambda: A downstream Lambda listens to SQS and performs analytics/report generation.

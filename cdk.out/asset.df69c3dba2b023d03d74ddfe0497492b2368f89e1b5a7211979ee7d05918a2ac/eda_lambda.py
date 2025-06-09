import boto3
import pandas as pd
import io
import json
import os

s3 = boto3.client('s3')
bucket = os.environ['BUCKET_NAME']

bls_S3 = "bls-data/pr.data.0.Current"
pop_S3 = "datausa/us_population.json"

def lambda_handler(event, context):
    # Load BLS CSV
    bls_obj = s3.get_object(Bucket=bucket, Key=bls_S3)
    bls_df = pd.read_csv(io.BytesIO(bls_obj['Body'].read()), sep='\t')
    print("BLS Data Loaded:", bls_df.shape)

    # Load Population JSON
    pop_obj = s3.get_object(Bucket=bucket, Key=pop_S3)
    pop_json = json.loads(pop_obj['Body'].read())
    pop_df = pd.DataFrame(pop_json['data'])
    print("Population Data Loaded:", pop_df.shape)

    # Standardize formatting
    for df in [bls_df, pop_df]:
        df.columns = df.columns.str.strip().str.lower()
        str_cols = df.select_dtypes(include='object').columns
        df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())
        df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')

    bls_df['value'] = pd.to_numeric(bls_df['value'], errors='coerce')
    pop_df['population'] = pd.to_numeric(pop_df['population'], errors='coerce')

    # Question 1: Mean and Std Dev of Population 2013–2018
    pop_13_18 = pop_df[(pop_df['year'] >= 2013) & (pop_df['year'] <= 2018)]
    mean_population = round(pop_13_18['population'].mean())
    std_population = round(pop_13_18['population'].std())
    print("Mean USA Population (2013-2018):", mean_population)
    print("Std Dev USA Population (2013-2018):", std_population)

    # Question 2: Best year by value sum for each series_id
    grouped = bls_df.groupby(['series_id', 'year'], as_index=False)['value'].sum()
    grouped = grouped.dropna(subset=['value'])
    grouped_sorted = grouped.sort_values(['series_id', 'value'], ascending=[True, False])
    best_years = grouped_sorted.drop_duplicates(subset=['series_id'], keep='first').reset_index(drop=True)
    print("Best Years Computed:", best_years.shape)

    # Question 3: Join filtered data on population
    filtered_bls_df = bls_df[(bls_df['series_id'] == 'PRS30006032') & (bls_df['period'] == 'Q01')]
    report = pd.merge(filtered_bls_df, pop_df, on='year', how='left')
    final_report = report[['series_id', 'year', 'period', 'value', 'population']]
    print("Final Merged Report:", final_report.shape)

    # Save report to S3
    output_key = "eda/eda_report.csv"
    csv_buffer = io.StringIO()
    final_report.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=bucket, Key=output_key, Body=csv_buffer.getvalue())

    return {
        "statusCode": 200,
        "body": json.dumps({
            "mean_population_2013_2018": mean_population,
            "std_population_2013_2018": std_population,
            "best_years_count": len(best_years),
            "report_key": output_key
        })
    }

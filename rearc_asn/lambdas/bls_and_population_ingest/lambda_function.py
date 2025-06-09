from rearc_asn.lambdas.bls_and_population_ingest.ingest import sync_files, fetch_population_data, upload_to_s3

def lambda_handler(event, context):
    print("Running BLS ingest...")
    sync_files()

    print("Running Population API fetch...")
    try:
        data = fetch_population_data()
        if data:
            upload_to_s3(data)
    except Exception as e:
        print("Error fetching/uploading population data:", e)

    return {
        "status": "Ingest completed"
    }
import logging
from rearc_asn.lambdas.bls_and_population_ingest.ingest import sync_files, fetch_population_data, upload_to_s3

# logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Starting BLS and Population ingest process...")

    try:
        logger.info("Running BLS file sync...")
        sync_files()
        logger.info("BLS file sync completed.")
    except Exception as e:
        logger.exception("Error during BLS file sync")

    try:
        logger.info("Fetching population data...")
        data = fetch_population_data()
        if data:
            logger.info("Population data fetched successfully. Uploading to S3...")
            upload_to_s3(data)
            logger.info("Upload to S3 completed.")
        else:
            logger.warning("No population data fetched.")
    except Exception as e:
        logger.exception("Error fetching or uploading population data")

    logger.info("Ingest process completed.")
    return {
        "status": "Ingest completed"
    }

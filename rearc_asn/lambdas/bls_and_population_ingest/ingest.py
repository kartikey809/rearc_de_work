import boto3
import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os


SOURCE_BASE_URL = "https://download.bls.gov"
SOURCE_PATH = "/pub/time.series/pr/"
BUCKET_NAME = "bucket-staging-s3" 

BLS_PREFIX = "bls-data/"
POP_JSON_KEY = "datausa/us_population.json"
POP_API_ENDPOINT = "https://datausa.io/api/data?drilldowns=Nation&measures=Population"

# -------------------------
# AWS Creds Secrets Here
# -------------------------
# -------------------------
# Using Boto3 lib to interact with S3 
# -------------------------

s3 = boto3.client("s3")

# -------------------------
# BLS Headers - for 403 issues
# -------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; krgconnect88@gmail.com)"  # BLS requires contact info in User-Agent
}

# -------------------------
# Function: List files on BLS website
# -------------------------

def list_files():
    url = SOURCE_BASE_URL + SOURCE_PATH
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    files = []
    for a in soup.find_all('a'):
        href = a.get('href')
        if href and href.startswith(SOURCE_PATH) and not href.endswith('/'):
            filename = href.split('/')[-1]
            files.append(filename)
    return files

# -------------------------
# Function: Generate content hash
# -------------------------

def hash_content(content):
    return hashlib.md5(content).hexdigest()  # also checking for file content changes

# -------------------------
# Function: Check if file exists in S3 with same content hash
# -------------------------

def existing_file_in_s3(filename, content_hash):
    key = f"{BLS_PREFIX}{filename}"
    try:
        response = s3.head_object(Bucket=BUCKET_NAME, Key=key)
        if response['Metadata'].get('hash') == content_hash:
            return True
    except s3.exceptions.ClientError:
        return False
    return False

# -------------------------
# Function: Sync BLS Files to S3
# -------------------------

def sync_files():
    files = list_files()
    print(f"Available files: {files}")
    for filename in files:
        file_url = f"{SOURCE_BASE_URL}{SOURCE_PATH}{filename}"
        print(f"Downloading {file_url}")
        res = requests.get(file_url, headers=HEADERS)
        content = res.content
        content_hash = hash_content(content)
        if existing_file_in_s3(filename, content_hash):
            print(f"{filename} is already up-to-date.")
        else:
            print(f"Uploading {filename} to S3...")
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=f"{BLS_PREFIX}{filename}",
                Body=content,
                Metadata={'hash': content_hash},
                ContentType='text/plain'
            )
    print("BLS data sync complete.")

# -------------------------
# Function: Fetch US Population JSON
# -------------------------

def fetch_population_data():
    response = requests.get(POP_API_ENDPOINT)
    if response.status_code != 200:
        print("Failed to fetch population data:", response.status_code)
        return None
    return response.json()

# -------------------------
# Function: Upload JSON to S3
# -------------------------

def upload_to_s3(data):
    json_str = json.dumps(data, indent=2)
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=POP_JSON_KEY,
        Body=json_str,
        ContentType='application/json'
    )
    print(f"Population JSON uploaded to s3://{BUCKET_NAME}/{POP_JSON_KEY}")


if __name__ == "__main__":
    try:
        print("Starting BLS sync fetch")
        sync_files()
        print("Fetching and uploading population data")
        data = fetch_population_data()
        if data:
            upload_to_s3(data)
    except Exception as e:
        print("Exception occurred:", e)

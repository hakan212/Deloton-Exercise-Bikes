"""Script for uploading generated pdf reports to an s3 bucket, for backup purposes"""
import os
from datetime import date

import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


FILE_PATH = "/tmp/deloton_daily_report.pdf"


def upload_to_s3(file_path):
    s3 = boto3.resource("s3")

    data = open(file_path, "rb")
    try:
        s3.Bucket(BUCKET_NAME).put_object(Key=f"{date.today()}", Body=data)
        print("Upload Successful")
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")


if __name__ == "__main__":
    upload_to_s3(FILE_PATH)

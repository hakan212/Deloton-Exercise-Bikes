import os
from datetime import date
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from report_generator import generate_report
from visualisation_generator import (get_dataframe, plot_age_rides_bar,
                                     plot_gender_rides_pie)

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
SENDER = os.getenv("SENDER")
CEO_RECIPIENT = os.getenv("CEO_RECIPIENT")

CHARSET = "UTF-8"
EMAIL_SUBJECT = f"Deloton Daily Report - {date.today()}"
BODY_TEXT = (
    "Dear Sir or Madame,"
    + "\n "
    + f"\nPlease find the attached daily report of analytics for {date.today()}."
    + "\n "
    + "\nKind Regards,"
    + "\nDeloton Exercise Co."
)
ATTACHMENT_PATH = "./assets/tmp/deloton_daily_report.pdf"


def send_email(
    aws_region,
    sender,
    recipient,
    email_body_text,
    email_subject,
    attachment_path,
):
    """
    Creates an email using email.mime and then
    connects to AWS SES using boto3 to send an email
    """

    # boto3 client for AWS SES
    client = boto3.client("ses", region_name=aws_region)

    # Email contents
    msg = MIMEMultipart("mixed")
    msg["Subject"] = email_subject
    msg["From"] = sender
    msg["To"] = recipient

    # Email text
    msg_body = MIMEMultipart("alternative")
    text_part = MIMEText(email_body_text.encode(CHARSET), "plain", CHARSET)
    msg_body.attach(text_part)
    msg.attach(msg_body)

    # Email attachment
    attachment = MIMEApplication(open(attachment_path, "rb").read())
    attachment.add_header(
        "Content-Disposition", "attachment", filename="deloton_daily_report.pdf"
    )
    msg.attach(attachment)

    try:
        response = client.send_raw_email(
            Source=msg["From"],
            Destinations=[msg["To"]],
            RawMessage={"Data": msg.as_string()},
        )
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])


def handler(event, context):
    """Handler function for AWS Lambda"""
    df_rides = get_dataframe()

    plot_age_rides_bar(df_rides)

    plot_gender_rides_pie(df_rides)

    generate_report(df_rides)

    send_email(
        AWS_REGION,
        "Deloton Exercise Co. <trainee.jordan.pacho@sigmalabs.co.uk>",
        "trainee.jordan.pacho@sigmalabs.co.uk",
        BODY_TEXT,
        EMAIL_SUBJECT,
        ATTACHMENT_PATH,
    )

    return "Function Execute"

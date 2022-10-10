import boto3
from botocore.exceptions import ClientError

def send_email(
    aws_region: str,
    send_email_from: str,
    recipient: str,
    email_body_html: str,
    email_body_text: str,
    email_subject: str,
    charset: str = "UTF-8",
) -> None:
    ## Sends email using AWS SES
    client = boto3.client("ses", region_name=aws_region)

    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    recipient,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": charset,
                        "Data": email_body_html,
                    },
                    "Text": {
                        "Charset": charset,
                        "Data": email_body_text,
                    },
                },
                "Subject": {
                    "Charset": charset,
                    "Data": email_subject,
                },
            },
            Source=send_email_from,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])

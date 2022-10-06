import boto3
from botocore.exceptions import ClientError
from heart_rate_calculator import heart_rate_high, heart_rate_low


def get_email_subject(heart_rate: int, age: int) -> str:
    ## Returns appropriate subject given age and heart rate
    if heart_rate_high(heart_rate, age):
        return "WARNING: Heart rate very high."
    if heart_rate_low(heart_rate, age):
        return "Heart rate low during Deloton session."


def get_email_HTML_body(heart_rate: int, age: int) -> str:
    ## Returns appropriate HTML body given age and heart rate
    if heart_rate_high(heart_rate, age):
        email_body_header = "WARNING: Heart rate dangerously fast!"
        email_body_content = "Your Deloton exercise bike recorded your heart rate to be very high, perhaps you should take a break."
    if heart_rate_low(heart_rate, age):
        email_body_header = "Heart rate very low, increase intensity!"
        email_body_content = "Your Deloton exercise bike recorded your heart rate to be very low, increase the intensity of exercise."

    return f"""<html>
    <head></head>
    <body>
        <h1>{email_body_header}</h1>
        <p>{email_body_content}</p>
    </body>
    </html>
    """


def get_email_text_body(heart_rate: int, age: int) -> str:
    ## Returns appropriate text body given age and heart rate
    if heart_rate_high(heart_rate, age):
        email_body_header = "WARNING: Heart rate dangerously fast!"
        email_body_content = "Your Deloton exercise bike recorded your heart rate to be very high, perhaps you should take a break."
    if heart_rate_low(heart_rate, age):
        email_body_header = "Heart rate very low, increase intensity!"
        email_body_content = "Your Deloton exercise bike recorded your heart rate to be very low, increase the intensity of exercise."

    return f"""{email_body_header}\r\n
    {email_body_content}
    """


def send_email(
    aws_region: str,
    send_email_from: str,
    recipient: str,
    email_body_html: str,
    email_body_text: str,
    email_subject: str,
    charset: str = "UTF-8",
):
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

import boto3
from botocore.exceptions import ClientError

SENDER = 'Deloton Exercise Co. <trainee.hakan.bas@sigmalabs.co.uk>'

RECIPIENT = 'trainee.noah.ryan@sigmalabs.co.uk'

AWS_REGION = 'eu-west-2'

SUBJECT = 'WARNING: abnormal heart rate'

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ('Warning heart rate too fast/slow\r\n'
             'Your heart rate has been recorded to be abnormal during exercise on your Deloton ecercise machine.'
            )
            
# The HTML body of the email.
BODY_HTML = '''<html>
<head></head>
<body>
  <h1>WARNING: Heart rate too fast/slow </h1>
  <p>Your heart rate has been recorded to be abnormal during exercise on your Deloton ecercise machine.</p>
</body>
</html>
'''            

CHARSET = "UTF-8"

# Create a new SES resource and specify a region.
client = boto3.client('ses',region_name=AWS_REGION)

def send_email(boto_3_ses_client, send_email_from:str ,recipient:str, email_body_html: str, email_body_text: str, email_subject: str ,charset: str = "UTF-8"):
    try:
        #Provide the contents of the email.
        response = boto_3_ses_client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': email_body_html,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': email_body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': email_subject,
                },
            },
            Source= send_email_from,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


send_email(client, SENDER, RECIPIENT, BODY_HTML, BODY_TEXT, SUBJECT, CHARSET)
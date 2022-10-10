FROM --platform=linux/x86-64 python

ADD heart_rate_email_requirements.txt .
RUN pip install -r heart_rate_email_requirements.txt

COPY . .

CMD python email_sender.py
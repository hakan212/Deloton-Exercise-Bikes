FROM --platform=linux/x86-64 python

ADD requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD python email_sender.py
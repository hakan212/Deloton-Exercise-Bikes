FROM --platform=linux/x86-64 python

ADD api_reqs.txt ./
RUN pip install -r api_reqs.txt

COPY . .

CMD python app.py
FROM --platform=linux/x86-64 python

ADD dash_reqs.txt ./
RUN pip install -r dash_reqs.txt

COPY . .

CMD python app.py

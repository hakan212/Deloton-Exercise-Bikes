FROM --platform=linux/x86-64 python

ADD batch_reqs.txt ./
RUN pip install -r batch_reqs.txt

COPY . .

CMD python main.py

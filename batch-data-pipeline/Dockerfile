FROM --platform=linux/x86-64 python
ENV APP_HOME /app
WORKDIR $APP_HOME

ADD batch_reqs.txt ./
RUN pip install -r batch_reqs.txt

COPY . .

ENV PYTHONUNBUFFERED True

CMD python main.py

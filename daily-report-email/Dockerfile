FROM public.ecr.aws/lambda/python:3.8

COPY . .
COPY email_sender.py ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip
RUN pip install -r daily_report_reqs.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["email_sender.handler"]
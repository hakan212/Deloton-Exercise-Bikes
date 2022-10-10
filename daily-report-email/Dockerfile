FROM public.ecr.aws/lambda/python:3.8

COPY email_sender.py ${LAMBDA_TASK_ROOT}

COPY transfer_data_reqs.txt .

RUN pip install --upgrade pip
RUN pip install -r transfer_data_reqs.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["email_sender.handler"]
FROM codingforentrepreneurs/python:3.9-webapp-cassandra

COPY .env /app/.env

COPY ./app ./app/app
COPY requirements.txt /app/requirements.txt


COPY ./pipelines /app/pipelines

WORKDIR /app

RUN python3 -m venv /opt/venv && /opt/venv/bin/python -m pip install -r requirements.txt

RUN apt-get update && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*


RUN /opt/venv/bin/python -m pypyr /app/pipelines/model_download

CMD ["uvicorn", "main:app", "--port", "8000"]
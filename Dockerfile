FROM codingforentrepreneurs/python:3.9-webapp-cassandra

COPY .env /app/.env
COPY ./entrypoint.sh ./app/entrypoint.sh
COPY ./app ./app/app
COPY requirements.txt /app/requirements.txt
COPY ./static ./app/static


COPY ./pipeline /app/pipelines

WORKDIR /app

RUN chmod +x entrypoint.sh

RUN python3 -m venv /opt/venv && /opt/venv/bin/python -m pip install -r requirements.txt

RUN apt-get update && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN /opt/venv/bin/python -m pypyr /app/pipelines/model_download
EXPOSE 8000/tcp
CMD [ "./entrypoint.sh" ]

#CMD ["/opt/venv/bin/uvicorn", "app.main:app","--host", "0.0.0.0", "--port", "8000"]
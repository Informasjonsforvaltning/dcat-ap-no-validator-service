FROM python:3.10

RUN mkdir -p /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install "poetry==1.7.1"
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-interaction --no-ansi

ADD dcat_ap_no_validator_service /app/dcat_ap_no_validator_service

EXPOSE 8080

CMD gunicorn "dcat_ap_no_validator_service:create_app"  --config=dcat_ap_no_validator_service/gunicorn_config.py --worker-class aiohttp.GunicornWebWorker

FROM python:3.9

RUN mkdir -p /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install "poetry==1.1.4"
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

ADD src /app/src

EXPOSE 8080

CMD gunicorn  --chdir src "dcat_ap_no_validator_service:create_app"  --config=src/dcat_ap_no_validator_service/gunicorn_config.py --worker-class aiohttp.GunicornWebWorker

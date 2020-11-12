# dcat-ap-no-validator-service
A shacl based validator backend  service for validating catalogs against dcat-ap-no specification

## Develop and run locally
### Requirements
- [pyenv](https://github.com/pyenv/pyenv) (recommended)
- [poetry](https://python-poetry.org/)
- [nox](https://nox.thea.codes/en/stable/)
- [nox-poetry](https://pypi.org/project/nox-poetry/)

### Install software:
```
% git clone https://github.com/Informasjonsforvaltning/dcat-ap-no-validator-service.git
% cd dcat-ap-no-validator-service
% pyenv install 3.9.0
% pyenv local 3.9.0
% python get-poetry.py
% pipx install nox
% pipx inject nox nox-poetry
% poetry install
```
### Running the API locally
 Start the endpoint:
```
% poetry shell
% FLASK_APP=dcat_ap_no_validator_service FLASK_ENV=development flask run --port=8080
```
## Running the API in a wsgi-server (gunicorn)
```
% poetry shell
% gunicorn  --chdir src "dcat_ap_no_validator_service:create_app()"  --config=src/dcat_ap_no_validator_service/gunicorn_config.py
```
## Running the wsgi-server in Docker
To build and run the api in a Docker container:
```
% docker build -t digdir/dcat-ap-no-validator-service:latest .
% docker run --env-file .env -p 8080:8080 -d digdir/dcat-ap-no-validator-service:latest
```
The easier way would be with docker-compose:
```
docker-compose up --build
```
## Running tests
We use [pytest](https://docs.pytest.org/en/latest/) for contract testing.

To run linters, checkers and tests:
```
% nox
```

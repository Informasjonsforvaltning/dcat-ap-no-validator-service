# dcat-ap-no-validator-service
A shacl based validator backend service for validating catalogs against dcat-ap-no specification

Input should be one of the following
 - a file containing your graph as turtle, or
 - a url pointing to resource on the internet containing your graph as turtle, or
 - a string containing your graph as turtle

 In addition you can input what version of dcat-ap-no you want your graph to be validated against.
 Today we support the following versions:
 - dcat-ap-no v1.1: 1.1
 - dcat-ap-no v2: 2

Response will be a RDF graph consisting of
 - the report as a graph according to a SHACL (validation report)[https://www.w3.org/TR/shacl/#validation-report]

## Usage by curl examples
### Validate file
```
% curl -i \
 -H "Accept: text/turtle" \
 -H "Content-Type: multipart/form-data" \
 -F "version=2" \
 -F "file=@tests/files/catalog_1.ttl;type=text/turtle" \
 -X POST http://localhost:8000/validator
```
### Validate endpoint(url) (Not implemented yet)
```
% curl -i \
 -H "Accept: text/turtle" \
 -H "Content-Type: multipart/form-data" \
 -F "url=https://example.com/mygraph" \
 -X POST http://localhost:8000/validator
```
### List all available shacl shapes (Not implemented yet)
```
% curl -i \
 -H "Accept: text/turtle" \
 -X GET http://localhost:8000/validator/shapes
 ```
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
Start the server locally:
```
% poetry shell
% adev runserver src/dcat_ap_no_validator_service
```
 TBD
## Running the API in a wsgi-server (gunicorn)
```
% poetry shell
% gunicorn dcat_ap_no_validator_service:create_app --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker
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

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
 - the report as a graph according to a SHACL [validation report](https://www.w3.org/TR/shacl/#validation-report)

## Usage by curl examples
### Validate file
```
% curl -i \
 -H "Accept: text/turtle" \
 -H "Content-Type: multipart/form-data" \
 -F "data-graph-file=@tests/files/valid_catalog.ttl;type=text/turtle" \
 -F "shapes-graph-file=@dcat-ap-no-shacl_shapes_2.00.ttl" \
 -X POST http://localhost:8000/validator
```
### Validate endpoint(url)
```
% curl -i \
 -H "Accept: text/turtle" \
 -H "Content-Type: multipart/form-data" \
 -F "data-graph-url=https://example.com/mygraph" \
 -F "shapes-graph-file=@dcat-ap-no-shacl_shapes_2.00.ttl" \
 -X POST http://localhost:8000/validator
```
### With config parameters:
```
% curl -i \
 -H "Accept: text/turtle" \
 -H "Content-Type: multipart/form-data" \
 -F "data-graph-file=@tests/files/valid_catalog.ttl;type=text/turtle" \
 -F "shapes-graph-file=@dcat-ap-no-shacl_shapes_2.00.ttl" \
 -F "config=@tests/files/config.json;type=application/json" \
-X POST http://localhost:8000/validator
```
Where `config.json` file may have the following properties, ref [the openAPI specification](./dcat_ap_no_validator_service.yaml) :
```
{
  "expand": "true",
  "includeExpandedTriples": "true"
}
```
### List all available shacl shapes
```
% curl -i \
 -H "Accept: application/json" \
 -X GET http://localhost:8000/shapes
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
% poetry run adev runserver src/dcat_ap_no_validator_service
```
 TBD
## Running the API in a wsgi-server (gunicorn)
```
% poetry run gunicorn dcat_ap_no_validator_service:create_app --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker
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
To run tests with logging, do:
```
% nox -s integration_tests -- --log-cli-level=DEBUG
```

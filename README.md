# dcat-ap-no-validator-service
A shacl based validator backend service for validating catalogs against dcat-ap-no specification

The validator need the following input graphs:
## A data graph
The RDF graph containing the data to be validated

## A shapes graph
The RDF graph containing the [SHACL shapes](https://www.w3.org/TR/shacl/) to validate with

## An ontology graph (optional)
The RDF graph containing extra ontological information. The validator will try to import
ontologies referenced in [owl:imports](https://www.w3.org/TR/owl-ref/#imports-def) statements

Input graphs should be supplied in of the following ways:
 - a file containing your graph, or
 - a url pointing to a resource on the internet containing your graph, or

Response will be a RDF graph consisting of
 - the input data graph
 - the report as a graph according to a SHACL [validation report](https://www.w3.org/TR/shacl/#validation-report)
 - the additional triples added to the data graph (if `includeExpandedTriples` is True)
 - the ontology graph (if `includeExpandedTriples` is True)

## Usage by curl examples
### Validate file
```
% curl -i \
 -H "Accept: text/turtle" \
 -H "Content-Type: multipart/form-data" \
 -F "data-graph-file=@tests/files/valid_catalog.ttl;type=text/turtle" \
 -F "shapes-graph-file=@tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl" \
 -F "ontology-graph-file=@tests/files/ontologies.ttl" \
 -X POST http://localhost:8000/validator
```
### Validate endpoint(url)
```
% curl -i \
 -H "Accept: text/turtle" \
 -H "Content-Type: multipart/form-data" \
 -F "data-graph-url=https://example.com/mygraph" \
 -F "shapes-graph-file=@tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl" \
 -F "ontology-graph-file=@tests/files/ontologies.ttl" \
 -X POST http://localhost:8000/validator
```
### With config parameters:
```
% curl -i \
 -H "Accept: text/turtle" \
 -H "Content-Type: multipart/form-data" \
 -F "data-graph-file=@tests/files/valid_catalog.ttl;type=text/turtle" \
 -F "shapes-graph-file=@tests/files/mock_dcat-ap-no-shacl_shapes_2.00.ttl" \
 -F "ontology-graph-file=@tests/files/ontologies.ttl" \
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
## Running the API locally
Start the server locally:
```
% poetry run adev runserver src/dcat_ap_no_validator_service
```
## Running the API in a wsgi-server (gunicorn)
```
% poetry run gunicorn dcat_ap_no_validator_service:create_app --bind localhost:8000 --worker-class aiohttp.GunicornWebWorker
```
## Running the wsgi-server in Docker
To build and run the api in a Docker container:
```
% docker build -t digdir/dcat-ap-no-validator-service:latest .
% docker run --env-file .env -p 8000:8080 -d digdir/dcat-ap-no-validator-service:latest
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
## Environment variables
### `LOGGING_LEVEL`
One of the supporte levels found [here](https://docs.python.org/3/library/logging.html#levels), given as string, eg.`DEBUG`
### `CONFIG`
One of
- `dev`: will not use cache backend
- `test`: will not use cache backend
- `production`: will require and use a redis backend, cf docker-compose.yml

An example .env file:
```
LOGGING_LEVEL=DEBUG
CONFIG=dev
```

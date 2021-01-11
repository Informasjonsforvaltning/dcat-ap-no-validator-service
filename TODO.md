TODO:
- [ ] Get SHACL from official sources, e.g. DCAT-AP-NO
- [x] Support validation based on both v1.1 and v2
- [x] Should accept multipart/form-data, ref https://stackoverflow.com/a/57264428/767586
- [x] Implement endpoint for shapes
- [ ] Get triples at the end of predicates and add to graph to be validated
- [x] Support content-negotiation on all known rdf serializations.
- [x] Create and raise relevant exceptions in service-layer.
- [x] Investigate why the following is failing, and give proper error message to user
```
curl -vi  --request POST 'http://localhost:8000/validator' \
--form 'version=2' \
--form 'file="@/home/stigbd/src/informasjonsforvaltning/dcat-ap-no-validator-service/tests/files/catalog_1.ttl;type=text/turtle"'
```

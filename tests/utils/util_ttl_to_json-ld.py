"""Simple util to serialize turtle to json-ld."""

from rdflib import Graph

g = Graph().parse("../files/valid_catalog.ttl", format="turtle")
context = {
    "dct": "http://purl.org/dc/terms/",
    "dcat": "http://www.w3.org/ns/dcat#",
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "rov": "http://www.w3.org/ns/regorg#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
}
g.serialize("../files/valid_catalog.json", format="json-ld", context=context)

"""Simple util to serialize turtle to json-ld."""
from rdflib import Graph

g = Graph().parse("../files/valid_catalog.ttl", format="turtle")
g.serialize("../files/valid_catalog.xml", format="xml")

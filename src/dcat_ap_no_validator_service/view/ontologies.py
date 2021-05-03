"""Resource module for ontology resources."""
from aiohttp import web

from dcat_ap_no_validator_service.adapter import OntologyGraphAdapter


class Ontologies(web.View):
    """Class representing a collecion of ontolgoy resource."""

    async def get(self) -> web.Response:
        """Ontologies route function."""
        response = dict()
        ontologies = [x.to_dict() for x in await OntologyGraphAdapter.get_all()]  # type: ignore
        response["ontologies"] = ontologies

        return web.json_response(response)


class Ontology(web.View):
    """Class representing a single ontology resource."""

    async def get(self) -> web.Response:
        """Ontology route function."""
        id = self.request.match_info["id"]
        ontology = await OntologyGraphAdapter.get_by_id(id)

        if ontology:
            return web.json_response(ontology.to_dict())  # type: ignore
        raise web.HTTPNotFound

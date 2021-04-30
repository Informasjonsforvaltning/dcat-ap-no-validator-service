"""Resource module for ontologies resources."""

from aiohttp import web

from dcat_ap_no_validator_service.service import OntologiesService


class Ontologies(web.View):
    """Class representing a collecion of ontology resources."""

    async def get(self) -> web.Response:
        """Ontologies route function."""
        ontologies = await OntologiesService().get_all_ontologies()
        return web.json_response(ontologies)


class Ontology(web.View):
    """Class representing a single ontology resource."""

    async def get(self) -> web.Response:
        """Ontology route function."""
        id = self.request.match_info["id"]
        ontology = await OntologiesService().get_ontology_by_id(id)

        if ontology:
            return web.json_response(ontology)
        raise web.HTTPNotFound

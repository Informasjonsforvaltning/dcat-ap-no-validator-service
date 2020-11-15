"""Resource module for liveness resources."""
from typing import Any

from aiohttp import web

from dcat_ap_no_validator_service.service import ValidatorService


class Validator(web.View):
    """Class representing validator resource."""

    async def post(self) -> Any:
        """Ready route function."""
        data = await self.request.text()
        try:
            service = ValidatorService(data)
            conforms, results_graph, results_text = await service.validate()
            return web.Response(text=results_text)
        except Exception as e:
            print(f"Exception: {e}")
            return web.Response(status=400, text="Bad request")

"""Resource module for liveness resources."""
import logging
from typing import Any

from aiohttp import MultipartWriter, web

from dcat_ap_no_validator_service.service import ValidatorService


class Validator(web.View):
    """Class representing validator resource."""

    # async def post(self) -> Any:
    #     """Ready route function."""
    #     data = await self.request.text()
    #     try:
    #         service = ValidatorService(data)
    #         conforms, results_graph, results_text = await service.validate()
    #         print(self.request.headers)
    #         if "Accept" in self.request.headers:
    #             print(self.request.headers["Accept"])
    #             if self.request.headers["Accept"] == "text/turtle":
    #                 body = results_graph.serialize(format="turtle", encoding="utf-8")
    #                 return web.Response(text=body.decode(), content_type="text/turtle")
    #         return web.Response(text=results_text, content_type="text/plain")
    #     except Exception as e:
    #         print(f"Exception: {e}")
    #         return web.Response(status=400, text="Bad request")

    async def post(self) -> Any:
        """Validate route function."""
        # Iterate through each field of MultipartReader
        data = str()
        filename = None
        async for field in (await self.request.multipart()):
            logging.debug(f"field.name {field.name}")
            if field.name == "url":
                # Do something about token
                url = (await field.read()).decode()
                logging.debug(f"Got url: {url}")
                return web.Response(status=501, text="Not Implemented")
                pass

            if field.name == "text":
                # Do something about key
                data = (await field.read()).decode()
                logging.debug(f"Got text: {data}")
                pass

            if field.name == "file":
                # Process any files you uploaded
                filename = field.filename
                logging.debug(f"got filename: {filename}")
                # In your example, filename should be "2C80...jpg"
                data = (await field.read()).decode()
                logging.debug(f"content of {filename}: {data}")
        # We have got data, now validate:
        try:
            service = ValidatorService(data)
            conforms, results_graph, results_text = await service.validate()

        except Exception as e:
            logging.error(f"Exception: {e}")
            return web.Response(status=400, text="Bad request")

        # TODO Build Response as Multipart. Should consist of:
        # - the data sent in for validation,
        # - the actual graph that was validated (incl any added triples)
        # - the shacl shapes used in validation
        # - the report as a graph
        # - the report as text
        with MultipartWriter("mixed") as mpwriter:
            p = mpwriter.append(data)
            if filename:
                p.set_content_disposition("attachment", name="data", filename=filename)
            else:
                p.set_content_disposition("attachment", name="data")
            p = mpwriter.append(results_text)
            p.set_content_disposition("attachment", name="results_text")
            p = mpwriter.append(
                results_graph.serialize(format="turtle"),
                {"CONTENT-TYPE": "text/turtle"},
            )
            p.set_content_disposition("attachment", name="results_graph")

        # Reply ok, all fields processed successfully
        return web.Response(body=mpwriter)

"""Resource module for liveness resources."""
import logging
import traceback

from aiohttp import MultipartWriter, web

from dcat_ap_no_validator_service.service import ValidatorService


class Validator(web.View):
    """Class representing validator resource."""

    async def post(self) -> web.Response:
        """Validate route function."""
        # Iterate through each field of MultipartReader
        data = ""
        version = ""
        filename = None
        async for field in (await self.request.multipart()):
            logging.debug(f"field.name {field.name}")
            if field.name == "version":
                # Do something about token
                version = (await field.read()).decode()
                logging.debug(f"Got version: {version}")
                pass

            if field.name == "url":
                # Do something about token
                url = (await field.read()).decode()
                logging.debug(f"Got url: {url}")
                raise web.HTTPNotImplemented
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
            service = ValidatorService(data, version)
            conforms, data_graph, results_graph, results_text = await service.validate()

        except ValueError:
            logging.error(traceback.format_exc())
            raise web.HTTPBadRequest(reason="Input is empty.")

        except SyntaxError:
            logging.error(traceback.format_exc())
            raise web.HTTPBadRequest(reason="Bad syntax in input.")

        # TODO Build Response as Multipart. Should consist of:
        # - "data_graph": the actual graph that was validated (incl any added triples)
        # - "result_graph": the report as a rdf (based on accept header), or
        # - "result_text": the report as text (based on accept header)
        # - the shacl shapes used in validation
        with MultipartWriter("mixed") as mpwriter:
            # data_graph:
            p = mpwriter.append(
                data_graph.serialize(format="turtle"),
                {"CONTENT-TYPE": "text/turtle"},
            )
            p.set_content_disposition("inline", name="data_graph")
            # result_text:
            # TODO: should return serialization based on content-negotiation
            p = mpwriter.append(results_text)
            p.set_content_disposition("inline", name="results_text")
            # result_graph:
            p = mpwriter.append(
                results_graph.serialize(format="turtle"),
                {"CONTENT-TYPE": "text/turtle"},
            )
            p.set_content_disposition("inline", name="results_graph")

        # Reply ok, all fields processed successfully
        return web.Response(body=mpwriter)

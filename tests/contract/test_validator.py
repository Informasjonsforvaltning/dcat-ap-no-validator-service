"""Contract test cases for ready."""
from typing import Any

import pytest
import requests


@pytest.mark.contract
def test_validator(http_service: Any) -> None:
    """Should return OK."""
    url = f"{http_service}/validator"
    with open("./tests/files/catalog_1.ttl") as ttl_file:
        data = ttl_file.read()
    headers = {
        "Content-Type": "text/turtle",
    }
    response = requests.post(url, headers=headers, data=data)
    assert response.status_code == 200
    text = response.text
    assert "Conforms: True" in text

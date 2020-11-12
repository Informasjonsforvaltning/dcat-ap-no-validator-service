"""Contract test cases for ping."""
from typing import Any

import pytest
import requests


@pytest.mark.contract
def test_ping(http_service: Any) -> None:
    """Should return OK."""
    url = f"{http_service}/ping"
    response = requests.get(url)

    assert response.status_code == 200
    assert response.text == "OK"

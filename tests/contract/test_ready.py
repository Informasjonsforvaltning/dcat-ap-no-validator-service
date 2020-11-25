"""Contract test cases for ready."""
from typing import Any

import pytest
import requests


@pytest.mark.contract
def test_ready(http_service: Any) -> None:
    """Should return OK."""
    url = f"{http_service}/ready"
    response = requests.get(url)

    assert response.status_code == 200
    assert response.text == "OK"

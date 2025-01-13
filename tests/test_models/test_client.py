import pytest
from unittest.mock import patch, MagicMock
from src.models.client import Client


def test_client_fetch_success():
    client = Client(
        base_url="https://fakeapi.io",
        auth_header="X-FAKE-KEY",
        api_key="dummy_key",
    )

    # success response
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = "hello world"
        mock_get.return_value = mock_response

        resp = client.fetch("/endpoint", params={"test": "ok"})
        assert resp.text == "hello world"
        mock_get.assert_called_once_with(
            "https://fakeapi.io/endpoint",
            headers={"X-FAKE-KEY": "dummy_key"},
            params={"test": "ok"},
        )


def test_client_fetch_http_error():
    client = Client("https://fakeapi.io", "X-FAKE-KEY", "dummy_key")

    # HTTPError
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error!")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="HTTP Error!"):
            client.fetch("/endpoint", params={})

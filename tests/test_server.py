"""Tests for the demo producer server. The tests mock all outbound HTTP calls."""

from unittest import mock

import pytest

import server


@pytest.fixture
def client():
    server.app.config.update(TESTING=True)
    return server.app.test_client()


def test_index_returns_hello_world(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "<p>Hello, World!</p>"


def test_data_returns_upstream_json_as_text(client):
    upstream = mock.Mock()
    upstream.json.return_value = [{"state": "NY", "confirmed": 10}]

    with mock.patch.object(server.requests, "get", return_value=upstream) as get:
        response = client.get("/data")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "[{'state': 'NY', 'confirmed': 10}]"
    get.assert_called_once()
    assert get.call_args.args[0].startswith("https://webhooks.mongodb-stitch.com/")


def test_unknown_route_returns_404(client):
    assert client.get("/missing").status_code == 404

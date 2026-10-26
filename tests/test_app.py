import pytest
from typing import Iterator
from flask.testing import FlaskClient

from hgnc_app.app import app


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------
# Test-client fixture pattern adapted from the Flask testing docs:
# https://flask.palletsprojects.com/en/stable/testing/
#
# These are end-to-end tests: importing hgnc_app.app builds the app with
# the real HGNC dataset, so data/hgnc_complete_set.txt must be present and
# the search tests exercise the same data users see.

@pytest.fixture
def client() -> Iterator[FlaskClient]:
    """
    Create a Flask test client for the application.

    Yields
    ------
    FlaskClient
        Configured test client for sending requests.
    """
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# ------------------------------------------------------------------
# Home route tests
# ------------------------------------------------------------------

def test_home_page_status(client: FlaskClient) -> None:
    """
    Test that the home page returns HTTP 200.

    Parameters
    ----------
    client : FlaskClient
        Flask test client.
    """
    response = client.get("/")
    assert response.status_code == 200


def test_home_page_contains_html(client: FlaskClient) -> None:
    """
    Test homepage returns HTML content.

    Checks that basic HTML structure is present.

    Parameters
    ----------
    client : FlaskClient
    """
    response = client.get("/")
    html = response.data.decode()

    assert "<html" in html.lower()
    assert "</html>" in html.lower()


# ------------------------------------------------------------------
# Search route tests (happy path)
# ------------------------------------------------------------------

def test_search_valid_gene(client: FlaskClient) -> None:
    """
    Test submitting a valid gene returns expected output.

    Parameters
    ----------
    client : FlaskClient
    """
    response = client.post(
        "/search",
        data={"gene": "BRCA2"}
    )

    assert response.status_code == 200

    html = response.data.decode()

    # Check expected response structure
    assert "Gene Information" in html
    assert "HGNC ID" in html
    assert "HGNC gene symbol" in html


# ------------------------------------------------------------------
# Search route tests (edge cases)
# ------------------------------------------------------------------

def test_search_missing_gene(client: FlaskClient) -> None:
    """
    Test submitting empty gene returns error message.

    Parameters
    ----------
    client : FlaskClient
    """
    response = client.post("/search", data={"gene": ""})

    assert response.status_code == 200

    html = response.data.decode()
    assert "error" in html.lower() or "no gene" in html.lower()


def test_search_no_form_data(client: FlaskClient) -> None:
    """
    Test POST with no form data does not crash.

    Parameters
    ----------
    client : FlaskClient
    """
    response = client.post("/search", data={})

    assert response.status_code == 200

    html = response.data.decode()
    assert "error" in html.lower()


# ------------------------------------------------------------------
# Error handling tests
# ------------------------------------------------------------------

def test_search_invalid_gene(client: FlaskClient) -> None:
    """
    Test searching for non-existent gene.

    Should not crash and should return gracefully.

    Parameters
    ----------
    client : FlaskClient
    """
    response = client.post(
        "/search",
        data={"gene": "THIS_DOES_NOT_EXIST"}
    )

    assert response.status_code == 200

    html = response.data.decode()

    # Either error or empty result is acceptable
    assert "error" in html.lower() or "Gene Information" not in html


# ------------------------------------------------------------------
# HTML content sanity test
# ------------------------------------------------------------------

def test_response_is_html(client: FlaskClient) -> None:
    """
    Ensure response content type is HTML.

    Parameters
    ----------
    client : FlaskClient
    """
    response = client.get("/")

    assert "text/html" in response.content_type
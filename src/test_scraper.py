from scraper import get_inspection_page
import pytest


@pytest.fixture(scope='function')
def empty_request():
    """Create an empty request."""
    return {}


@pytest.fixture(scope='function')
def seattle_request():
    """Create a request for every seattle restruant."""
    return {"City": "Seattle"}

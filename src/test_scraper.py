from scraper import (
    update_vals,
    SCRAPE_VARS,
    get_inspection_page,
    send_request,
)
import pytest


@pytest.fixture(scope='function')
def empty_request():
    """Create an empty request."""
    return {}


@pytest.fixture(scope='function')
def seattle_request():
    """Create a request for every seattle restraunt."""
    return {"City": "Seattle", "Inspection_End": "3/22/2016", "Inspection_Start": "3/1/2016"}


def test_update_null(empty_request):
    """Test that we create a blank search properly."""
    result = update_vals(**empty_request)
    expected = SCRAPE_VARS['PARAMS']
    assert result == expected


def test_update_seattle(seattle_request):
    """Test that we create a proper seattle search."""
    result = update_vals(**seattle_request)
    expected = {
        'Output': 'W',
        'Business_Name': '',
        'Business_Address': '',
        'Longitude': '',
        'Latitude': '',
        'City': 'Seattle',
        'Zip_Code': '',
        'Inspection_Type': 'All',
        'Inspection_Start': '',
        'Inspection_End': '',
        'Inspection_Closed_Business': 'A',
        'Violation_Points': '',
        'Violation_Red_Points': '',
        'Violation_Descr': '',
        'Fuzzy_Search': 'N',
        'Sort': 'H'
    }
    assert result == expected


def test_send_request_dummy():
    response = send_request(, {})

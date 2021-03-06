from scraper import (
    update_vals,
    SCRAPE_VARS,
    get_inspection_page,
    load_inspection_page,
    format_get_request,
    send_request,
    parse_broken_html,
    save_html,
)
import pytest


@pytest.fixture(scope='function')
def empty_request():
    """Create an empty request."""
    return {}


@pytest.fixture(scope='function')
def seattle_request():
    """Create a request for every seattle restraunt."""
    return {
            "City": "Seattle",
            "Inspection_End": "3/22/2016",
            "Inspection_Start": "3/1/2016"
            }


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
        'Inspection_Start': '3/1/2016',
        'Inspection_End': '3/22/2016',
        'Inspection_Closed_Business': 'A',
        'Violation_Points': '',
        'Violation_Red_Points': '',
        'Violation_Descr': '',
        'Fuzzy_Search': 'N',
        'Sort': 'H'
    }
    assert result == expected


def test_seattle_to_get(seattle_request):
    full = update_vals(**seattle_request)
    get_req = format_get_request(full)
    expected = ("Output=W&Business_Name=&Business_Address=&Longitude=&Latitud"
                "e=&City=Seattle&Zip_Code=&Inspection_Type=All&"
                "Inspection_Start=3/1/2016&Inspection_End=3/22/2016&"
                "Inspection_Closed_Business=A&Violation_Points=&Violation_Red"
                "_Points=&Violation_Descr=&Fuzzy_Search=N&Sort=H")

    for part in expected.split("&"):
        assert part in get_req
    assert get_req.startswith('?')
    assert not get_req.endswith('&')


def test_send_request_dummy(seattle_request):
    params = update_vals(**seattle_request)
    get_request = format_get_request(params)
    url = SCRAPE_VARS['DOMAIN'] + SCRAPE_VARS['PATH'] + get_request
    response = send_request(url)
    assert response.status_code == 200


def test_get_inspection_page(seattle_request):
    params = update_vals(**seattle_request)
    get_request = format_get_request(params)
    url = SCRAPE_VARS['DOMAIN'] + SCRAPE_VARS['PATH'] + get_request
    response = send_request(url)
    test_text, test_encoding = get_inspection_page(**seattle_request)
    assert test_text[:200] == response.text[:200], response.encoding  # NOQA

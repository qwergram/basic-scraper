# coding=utf-8
"""Scrape foodsafety data from kingcounty."""
import requests
from bs4 import BeautifulSoup

SCRAPE_VARS = {
    "DOMAIN": 'http://info.kingcounty.gov/',
    "PATH": 'health/ehs/foodsafety/inspections/Results.aspx',
    "PARAMS": {
        'Output': 'W',
        'Business_Name': '',
        'Business_Address': '',
        'Longitude': '',
        'Latitude': '',
        'City': '',
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
}


def update_vals(**kwargs):
    """Take all the kwargs and compile them into a proper request."""
    params = SCRAPE_VARS['PARAMS'].copy()
    for key, val in kwargs.items():
        if key in SCRAPE_VARS['PARAMS']:
            params[key] = val
        else:
            raise KeyError("Illegal key '{}':'{}' passed in".format(key, val))
    return params


def format_get_request(params):
    if not params:
        return ""
    request = "?"
    for key, value in params.items():
        request += "{}={}&".format(key, value)
    return request[:-1]


def send_request(endpoint):
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
    except requests.exceptions.ReadTimeout:
        raise ValueError("Invalid URL")
    return response


def parse_broken_html(raw_text, encoding="utf-8"):
    parsed = BeautifulSoup(raw_text, 'html5lib', from_encoding=encoding)
    return parsed


def get_inspection_page(**kwargs):
    """Create a get request to the API endpoint."""
    endpoint = SCRAPE_VARS['DOMAIN'] + SCRAPE_VARS['PATH']
    params = update_vals(**kwargs)
    response = send_request(endpoint, params)
    return response.content, response.encoding


if __name__ == "__main__":
    get_inspection_page()

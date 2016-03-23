# coding=utf-8
"""Scrape foodsafety data from kingcounty."""
import requests
import io
from bs4 import BeautifulSoup
import sys

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


def save_html(html):
    if isinstance(html, bytes):
        html = html.decode()
    with io.open("inspection_page.html", 'w') as save:
        save.write(html)


def get_inspection_page(**kwargs):
    """Create a get request to the API endpoint."""
    endpoint = SCRAPE_VARS['DOMAIN'] + SCRAPE_VARS['PATH']
    params = update_vals(**kwargs)
    get = format_get_request(params)
    response = send_request(endpoint + get)
    save_html(response.content)
    return response.content, response.encoding


def load_inspection_page():
    """Load the cached inspection page."""
    with io.open("inspection_page.html") as response:
        response = response.read()
    return response, "utf-8"

if __name__ == "__main__":
    seattle = {
               "City": "Seattle",
               "Inspection_End": "3/22/2016",
               "Inspection_Start": "3/1/2016"
              }
    try:
        if sys.argv[1] == "get":
            content, encoding = get_inspection_page(**seattle)
        elif sys.argv[1] == "load":
            content, encoding = load_inspection_page()
        else:
            raise IndexError
    except IndexError:
        raise ValueError("Please specify a 'load' or 'get' keyword")
    parse_broken_html(content, encoding)

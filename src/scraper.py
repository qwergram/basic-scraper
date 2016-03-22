# coding=utf-8
"""Scrape foodsafety data from kingcounty."""
import requests

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


def get_inspection_page(**kwargs):
    """Create a get request to the API endpoint.


    """
    endpoint = SCRAPE_VARS['DOMAIN'] + SCRAPE_VARS['PATH']
    params = update_vals(**kwargs)
    resp = requests.get(endpoint, params=params)
    resp.raise_for_status()
    return resp.content, resp.encoding


def main():
    response = get_inspection_page()
    return response

if __name__ == "__main__":
    main()

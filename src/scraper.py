# coding=utf-8
"""Scrape foodsafety data from kingcounty."""
import requests
import io
from bs4 import BeautifulSoup
import sys
import re
import json
import geocoder

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


def get_divs(soup):
    id_finder = re.compile(r"PR[\d]+~")
    return soup.find_all('div', id=id_finder)


def has_two_tds(elem):
    if elem.name == 'tr':
        td_children = elem.find_all('td', recursive=False)
        return len(td_children) == 2
    return False


def get_meta_data(divs):
    meta_data = []
    for div in divs:
        rows = div.find('tbody').find_all(
            has_two_tds, recursive=False
        )
        inspection_data = div.find_all(is_inspection_row)
        meta_data.append([rows, inspection_data])
    return meta_data


def extract_useful_data(meta_data):
    parsed_meta_data = {}
    for data_set, inspection_data in meta_data:
        try:
            name = data_set[0].find_all('td')[1].string.strip()
            parsed_meta_data[name] = {"name": name}
        except (AttributeError, TypeError):
            continue
        parsed_meta_data[name]['inspection'] = extract_inspection_data(inspection_data)
        for i, column in enumerate("name category address1"
                                   " address2 phone latitude "
                                   "longitude".split()):
            try:
                target = data_set[i].find_all('td')[1].string.strip()
                parsed_meta_data[name][column] = target
            except AttributeError:
                pass
        parsed_meta_data[name]['geo'] = get_more_geo_data(parsed_meta_data[name])
        del parsed_meta_data[name]['address1']
        del parsed_meta_data[name]['address2']
        del parsed_meta_data[name]['latitude']
        del parsed_meta_data[name]['longitude']

    return parsed_meta_data



def is_inspection_row(elem):
    if elem.name == 'tr':
        td_children = elem.find_all('td', recursive=False)
        has_four = len(td_children) == 4
        if td_children[0].string:
            contains_word = 'inspection' in td_children[0].string.lower()
            return has_four and contains_word
        else:
            return False
    else:
        return False


def extract_inspection_data(inspection_data):
    result = {'history': []}
    for inspection in inspection_data[1:]:
        parsed = {}
        focus = inspection.find_all('td')
        parsed['type'] = focus[0].string.strip()
        parsed['date'] = focus[1].string.strip()
        parsed['score'] = focus[2].string.strip()
        parsed['result'] = focus[3].string.strip()
        result['history'].append(parsed)
    high_score, average_score, inspections = get_mean_high_sum(result['history'])
    result['high'] = high_score
    result['avg'] = average_score
    result['inpsection_count'] = inspections
    return result


def get_mean_high_sum(parsed_inspection_data):
    high_score = 0
    score_history = []
    if not len(parsed_inspection_data):
        return 0, 0, 0
    for inspection in parsed_inspection_data:
        score = int(inspection['score'])
        score_history.append(score)
        if score > high_score:
            high_score = score
    average = sum(score_history) / len(score_history)
    return high_score, average, len(score_history)

def parse_broken_html(raw_text, encoding="utf-8"):
    soup = BeautifulSoup(raw_text, 'html5lib', from_encoding=encoding)
    divs = get_divs(soup)
    meta_data = get_meta_data(divs)
    py_dict = extract_useful_data(meta_data)

    return py_dict

def get_more_geo_data(data_set):
    address = ""
    address1 = data_set.get('address1')
    address2 = data_set.get('address2')
    if address1:
        address += address1.strip()
    if address2:
        address += ' ' + address2.strip()
    more = geocoder.google(address).json
    if more.ok:
        return more
    else:
        return {"address": address}
    import pdb; pdb.set_trace()


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
    return response.content.decode('utf-8'), response.encoding


def load_inspection_page():
    """Load the cached inspection page."""
    with io.open("inspection_page.html") as response:
        response = response.read()
    return response, "utf-8"


def save_json(py_dict):
    data = json.dumps(py_dict, indent=2)
    with io.open("result.json", 'w') as f:
        f.write(data)


if __name__ == "__main__":
    seattle = {
               "City": "Seattle",
               "Inspection_End": "3/22/2016",
               "Inspection_Start": "3/1/2016"
              }
    try:
        if len(sys.argv) > 2:
            params = json.loads(sys.argv[2])
        else:
            params = seattle
        if sys.argv[1] == "get":
            content, encoding = get_inspection_page(**params)
        elif sys.argv[1] == "load":
            content, encoding = load_inspection_page()
        else:
            raise IndexError
    except IndexError:
        raise ValueError("Please specify a 'load' or 'get' keyword")
    parsed = parse_broken_html(content.encode('utf-8'), encoding)
    save_json(parsed)
    print(parsed)

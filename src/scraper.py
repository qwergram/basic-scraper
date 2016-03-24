# coding=utf-8
"""Scrape foodsafety data from kingcounty."""
import requests
import io
from bs4 import BeautifulSoup
import sys
import re

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
        parsed_meta_data['inspection'] = extract_inspection_data(inspection_data)
        for i, column in enumerate("name category address1"
                                   " address2 phone latitude "
                                   "longitude".split()):
            try:
                target = data_set[i].find_all('td')[1].string.strip()
                parsed_meta_data[name][column] = target
            except AttributeError:
                pass

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
    inspection_history = []
    for inspection in inspection_data[1:]:
        parsed = {}
        focus = inspection.find_all('td')
        parsed['type'] = focus[0].string.strip()
        parsed['date'] = focus[1].string.strip()
        parsed['score'] = focus[2].string.strip()
        parsed['result'] = focus[3].string.strip()
        inspection_history.append(parsed)
    return inspection_history


def parse_broken_html(raw_text, encoding="utf-8"):
    soup = BeautifulSoup(raw_text, 'html5lib', from_encoding=encoding)
    divs = get_divs(soup)
    meta_data = get_meta_data(divs)
    py_dict = extract_useful_data(meta_data)
    import pdb; pdb.set_trace()
    return divs


def parse_broken_html_bad(raw_text, encoding="utf-8"):

    def has_two_tds(elem):
        if elem.name == 'tr':
            td_children = elem.find_all('td', recursive=False)
            return len(td_children) == 2
        return False

    def custom_filter(focus):
        isfull = this.get('name') and this.get('address')
        if not isfull:
            return False
        isnot_inspection = not this['name'].lower().startswith('inspection')
        isnot_business = not this['name'].lower().startswith('- business')
        isnot_description = not this['name'].lower().startswith('Inspection '
                                                                'violations '
                                                                'and points')
        return isnot_inspection and isnot_business and isnot_description

    parsed = BeautifulSoup(raw_text, 'html5lib', from_encoding=encoding)
    restruants = []
    results = {}
    for restruant in parsed.find_all('table')[2:]:
        restruants.append(restruant)

    for i, r in enumerate(restruants):
        this = {}
        if i % 4 == 0:
            this['name'] = (r.find("td").text.strip().replace("+ ", "", 1))
            this['address'] = (r.find_all("td")[-1].text.strip())

            if custom_filter(this):
                results[this['name']] = this

        elif (i - 1) % 4 == 0:
            keys = [
                ("category", "", 3),
                ("phone", "", 9),
                ("latitude", "", 11),
                ("longitude", "", 13),
                ("name", "- business name", 1),
                ("address", "address:", 5),
            ]
            for string, check, index in keys:
                try:
                    if check not in r.find_all('td')[index - 1].string.lower():
                        raise AttributeError("Check failed")
                    this[string] = r.find_all('td')[index].string.strip()
                except (IndexError, AttributeError):
                    pass

                inspection_details = {}
                keys = [
                    ("inspection type", 0, 4),
                    ("date", 1, 5),
                    ("score", 2, 6),
                    ("result", 3, 7),
                ]
                for check, check_index, actual_index in keys:
                    try:
                        value = r.table.find_all("td")[actual_index].string.strip()
                        inspection_details[check.replace(" ", "_")] = value
                    except (AttributeError, TypeError, IndexError):
                        pass

                if inspection_details:
                    this['inspection'] = inspection_details


                grades = []
                try:
                    for grade in r.find_all("table")[1].find_all("td")[1:]:
                        if grade.string:
                            grades.append(grade.string.strip())
                    if grades:
                        this['grades'] = grades
                except IndexError:
                    pass

            if custom_filter(this):
                results[this['name']].update(this)

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
    return response.content.decode('utf-8'), response.encoding


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
    parse_broken_html(content.encode('utf-8'), encoding)

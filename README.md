# basic-scraper

A webscraper for parsing data from http://info.kingcounty.gov/health/ehs/foodsafety/inspections/search.aspx and
creates a machine friendly JSON object.

## Running the program
`python scraper.py [option] [search parameters]`

`option` can either be `load` or `get`

`load` will search for a file named `inspection_page.html` and parse the html from there

`get` will download data from the servers and pour it into `inspection_page.html`.

Either option will create a JSON file called `result.json` which contains data from the query made.

```
{
  "CUTTING BOARD": {
    "phone": "(206) 329-3414",
    "latitude": "47.5531078958",
    "address2": "SEATTLE, WA 98108",
    "inspection": {
      "history": [
        {
          "score": "10",
          "result": "Satisfactory",
          "type": "Routine Inspection/Field Review",
          "date": "03/03/2016"
        }
      ],
      "high": 10,
      "inpsection_count": 1,
      "avg": 10.0
    },
    "name": "CUTTING BOARD",
    "longitude": "-122.3211959030",
    "category": "Seating 13-50 - Risk Category III",
    "address1": "5503 AIRPORT WAY S" ...
```

You can specify search parameters, for exampe: `'{"City": "Seattle", "Inspection_Start": "3/1/2016", "Inspection_End": "3/31/2016"}'`
will return all inspections made in Seattle this month.


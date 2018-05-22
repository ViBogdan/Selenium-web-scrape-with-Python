# Facebook Events Scraper

Scrape events from a given list of facebook pages using selenium

### Prerequisites

```
python3
pipenv
```

### Installing

Install:
```
git clone https://github.com/ViBogdan/Selenium-web-scrape-with-Python.git
cd Selenium-web-scrape-with-Python
pipenv install
```

## Running
```
pipenv run python scrape_events.py
```

## Interesting libraries to follow:
[requests-html](http://html.python-requests.org/)  
However it has some limitations (for now):
- scrolling is manual, doesn't scrollIntoView
- can't pass arguments (such as lang) to pyppeteer (chrome automation lib)

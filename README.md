# OpenAI API Key Scraper

This is a Python script to scrape OpenAI API keys that are exposed on public Replit projects. 

Inspired by [this article](https://www.vice.com/en/article/93kkky/people-pirating-gpt4-scraping-openai-api-keys).

## Installation and Usage:
1. Clone this repository by running the following commands:
```
git clone https://github.com/ading2210/openai-key-scraper
cd openai-key-scraper
```
2. Obtain your Replit cookie by going to the network tab of your browser's devtools while on replit.com, searching for `graphql`, and copying the value in the `Cookie` request header. You may need to reload the page for the requests to show up.
3. Run the script using the following command:
```
python3 main.py "TOKEN_HERE"
```

It is recommended that you set a custom search query. You can do that by passing another argument into the script, like in the following example:
```
python3 main.py "TOKEN" "chatgpt sk-"
```

## Copyright:
This program is licensed under the [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.txt).

```
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
```
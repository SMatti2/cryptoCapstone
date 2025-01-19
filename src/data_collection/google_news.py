import requests, time, random, urllib.parse, json, os

from datetime import datetime, timedelta
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36",
]

COOKIES = {
    "AEC": "AZ6Zc-W9vgU5oWIeK2trdWb7VX4mDnJLhNMf9pTL6WljvREKpAMX2lIhZw",
    "DV": "o8sxQVVjsUYVMLoqspk1c5H325XxRhk",
    "NID": (
        "520=TAMezii_Q7RhjsAVi3ucP8969AG0UnosdQGTiBvNAIaxkvXofCcnl"
        "r4YTaxM-o7a_qMAEZVBI_MX9wCyg6n3r2mOOkQzvGkoBRPWQhM2qaS0"
        "f5iDSorUl_dWTFyEWB8h8h2c5bU-eU1vyh6u3jG9NqNU8YDdKx4KPvVR"
        "6XlpYjXWNt5h9JNkFctymw1uK20Hani8sSAeOLvnvuh-ceRFEVAqV7QUB"
        "4JUB92-I0TBr3bGNuMsHZqQZPLgRZqh5zkKqmH35d-ByVVzX_H1iOIA_H"
        "Jx3Ius7Jx-"
    ),
    "SOCS": "CAISHAgBEhJnd3NfMjAyNTAxMTMtMF9SQzIaAml0IAEaBgiAmKG8Bg",
}


def get_google_news_url(query, start_date, end_date, preferred_domains=None):
    """
    Create a Google News search URL for the given query, date range,
    and optional preferred domains.
    """
    base_url = "https://www.google.com/search"

    # Handle comma-separated queries
    if "," in query:
        parts = [part.strip() for part in query.split(",")]
        modified_query = " OR ".join(f"({part})" for part in parts)
    else:
        modified_query = query

    # Convert single domain into list if necessary
    if isinstance(preferred_domains, str):
        preferred_domains = [preferred_domains]

    # Append site restrictions
    if preferred_domains:
        domain_query = " OR ".join(f"site:{domain}" for domain in preferred_domains)
        modified_query = f"{modified_query} ({domain_query})"

    # Construct query params
    params = {
        "q": modified_query,
        "tbm": "nws",
        "tbs": f"lr:lang_1en,cdr:1,cd_min:{start_date},cd_max:{end_date}",
        "lr": "lang_en",
        "hl": "en",
        "gl": "us",
    }

    return f"{base_url}?{urllib.parse.urlencode(params)}"


def fetch_page_source(session, url):
    """
    Fetch the HTML source code from a URL using a Requests session.
    """
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    response = session.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(
            f"Failed to retrieve the page. Status code: {response.status_code}"
        )


def extract_articles(html_content):
    """
    Parse Google News search results HTML and return a list of articles.
    Each article is a dict: {"title": "...", "description": "...", "link": "..."}
    """
    soup = BeautifulSoup(html_content, "html.parser")
    containers = soup.find_all("div", class_="SoaBEf")

    if not containers:
        print("No article containers found.")
        return []

    print(f"Found {len(containers)} article containers.")
    articles = []

    for article in containers:
        link_el = article.select_one("a.WlydOe")
        # in extract_articles:
        link = (
            link_el["href"]
            if (link_el and link_el.has_attr("href"))
            else "No link found"
        )

        title_el = article.select_one("div.n0jPhd.ynAwRc.MBeuO.nDgy9d")
        title = title_el.get_text(strip=True) if title_el else "No title found"

        desc_el = article.select_one("div.GI74Re.nDgy9d")
        description = (
            desc_el.get_text(strip=True) if desc_el else "No description found"
        )

        articles.append(
            {
                "title": title,
                "description": description,
                "link": link,
            }
        )

    return articles


def load_existing_json(filepath):
    """
    Load existing JSON data from `filepath` if it exists,
    otherwise return an empty dict.
    """
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}


def save_to_json(filepath, data):
    """
    Write the dictionary `data` to `filepath` in JSON format, with indentation.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def scrape_google_news(
    start_date,
    end_date,
    preferred_domains=None,
    queries=None,  # This is now expected to be a list of lists
    output_path="articles.json",
):
    """
    create a daily Google News search for each 'group' of terms in [start_date, end_date].
    Each 'group' in queries is combined with 'OR' to form a single query.

    Example queries structure:
      queries = [
        ["AI", "Machine Learning", "crypto"],
        ["Joe Biden", "White House"],
      ]

    This results in two searches:
      1) (AI) OR (Machine Learning) OR (crypto)
      2) (Joe Biden) OR (White House)

    Saves articles day by day to JSON in the format:
        {
          "YYYY-MM-DD": [
            {
              "title": "...",
              "subtitle": "...",
              "url": "...",
              "query": "..."    # The combined query
            },
            ...
          ],
          ...
        }
    :param output_path: The path where the JSON file will be saved (default: 'articles.json').
    """
    if queries is None:
        queries = []

    # Convert string dates to datetime objects
    start_dt = datetime.strptime(start_date, "%m/%d/%Y")
    end_dt = datetime.strptime(end_date, "%m/%d/%Y")

    # Initialize a session with pre-set cookies
    session = requests.Session()
    session.cookies.update(COOKIES)

    # Load existing data from JSON file (so we can append)
    daily_data = load_existing_json(output_path)

    base_wait = 60  # 1 minute
    max_wait = 900  # 15 minutes

    current_dt = start_dt
    while current_dt <= end_dt:
        # Use YYYY-MM-DD as the daily key
        day_key = current_dt.strftime("%Y-%m-%d")

        # We'll collect articles for this day in a temporary list
        day_articles = []

        # Instead of iterating over single 'query' strings, we iterate over each sub-list
        for group in queries:
            # Combine sub-list items with OR
            # e.g. ["AI", "Machine Learning", "crypto"] => (AI) OR (Machine Learning) OR (crypto)
            combined_query = " OR ".join(f"({term})" for term in group)

            backoff = base_wait
            retry = True

            while retry:
                try:
                    # Format current day as MM/DD/YYYY for Google
                    gnews_date_str = current_dt.strftime("%m/%d/%Y")

                    # Build the URL using the combined OR query
                    url = get_google_news_url(
                        combined_query,
                        gnews_date_str,
                        gnews_date_str,
                        preferred_domains,
                    )
                    print(f"[{day_key}] Query '{combined_query}' => {url}")

                    source_code = fetch_page_source(session, url)
                    print(
                        f"Source code fetched successfully for '{combined_query}' on {day_key}!"
                    )

                    articles = extract_articles(source_code)

                    # Limit to 10 articles per query per day
                    if len(articles) > 10:
                        articles = articles[:10]

                    # Convert the extracted fields to your final desired keys
                    # and add "query" as the combined OR string
                    for art in articles:
                        renamed = {
                            "title": art["title"],
                            "subtitle": art["description"],  # rename
                            "url": art["link"],  # rename
                            "query": combined_query,  # store the OR query
                        }
                        day_articles.append(renamed)

                    retry = False  # success => stop retrying
                except Exception as e:
                    err_msg = str(e)
                    if "429" in err_msg:
                        print(
                            f"429 for '{combined_query}' on {day_key}. Waiting {backoff}s, then retry..."
                        )
                        time.sleep(backoff)
                        backoff = min(backoff * 2, max_wait)
                    else:
                        print(f"Error on '{combined_query}' / {day_key}: {err_msg}")
                        retry = False

        # Merge the day's results into daily_data
        if day_key not in daily_data:
            daily_data[day_key] = []

        # Append newly scraped articles for the day
        daily_data[day_key].extend(day_articles)

        # **Save to JSON** after finishing this day
        save_to_json(output_path, daily_data)
        print(f"Saved {len(day_articles)} articles for {day_key} to '{output_path}'.")

        current_dt += timedelta(days=1)

    return daily_data


if __name__ == "__main__":
    start_date = "1/1/2024"
    end_date = "1/5/2024"
    preferred_domains = ["nytimes.com"]
    output_file = "my_articles.json"

    # Each sub-list will become one combined OR query
    queries = [["Joe Biden", "White House"]]

    scrape_google_news(
        start_date, end_date, preferred_domains, queries, output_path=output_file
    )

    print("Scraping completed! Saved to:", output_file)

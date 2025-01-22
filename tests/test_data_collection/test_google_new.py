import unittest
from unittest.mock import patch, Mock
import urllib.parse

from src.data_collection.google_news import (
    scrape_google_news,
    get_google_news_url,
    fetch_page_source,
    extract_articles,
)


class TestGoogleNewsScraper(unittest.TestCase):
    # tests for get_google_news_url
    def test_get_google_news_url_single_domain(self):
        """
        Test URL generation with a single preferred domain.
        """
        query = "AI, Machine Learning, crypto"
        start_date = "1/1/2024"
        end_date = "12/10/2024"
        preferred_domains = ["brookings.edu"]

        expected_query = "(AI) OR (Machine Learning) OR (crypto) (site:brookings.edu)"
        expected_params = {
            "q": expected_query,
            "tbm": "nws",
            "tbs": "lr:lang_1en,cdr:1,cd_min:1/1/2024,cd_max:12/10/2024",
            "lr": "lang_en",
            "hl": "en",
            "gl": "us",
        }

        generated_url = get_google_news_url(
            query, start_date, end_date, preferred_domains
        )
        expected_url = "https://www.google.com/search?" + urllib.parse.urlencode(
            expected_params
        )
        self.assertEqual(generated_url, expected_url)

    def test_get_google_news_url_multiple_domains(self):
        """
        Test URL generation with multiple preferred domains.
        """
        query = "AI, Machine Learning, crypto"
        start_date = "1/1/2024"
        end_date = "12/10/2024"
        preferred_domains = ["brookings.edu", "example.com"]

        expected_query = "(AI) OR (Machine Learning) OR (crypto) (site:brookings.edu OR site:example.com)"
        expected_params = {
            "q": expected_query,
            "tbm": "nws",
            "tbs": "lr:lang_1en,cdr:1,cd_min:1/1/2024,cd_max:12/10/2024",
            "lr": "lang_en",
            "hl": "en",
            "gl": "us",
        }

        generated_url = get_google_news_url(
            query, start_date, end_date, preferred_domains
        )
        expected_url = "https://www.google.com/search?" + urllib.parse.urlencode(
            expected_params
        )
        self.assertEqual(generated_url, expected_url)

    def test_get_google_news_url_no_preferred_domains(self):
        """
        Test URL generation without preferred domains.
        """
        query = "AI, Machine Learning, crypto"
        start_date = "1/1/2024"
        end_date = "12/10/2024"
        preferred_domains = None

        expected_query = "(AI) OR (Machine Learning) OR (crypto)"
        expected_params = {
            "q": expected_query,
            "tbm": "nws",
            "tbs": "lr:lang_1en,cdr:1,cd_min:1/1/2024,cd_max:12/10/2024",
            "lr": "lang_en",
            "hl": "en",
            "gl": "us",
        }

        generated_url = get_google_news_url(
            query, start_date, end_date, preferred_domains
        )
        expected_url = "https://www.google.com/search?" + urllib.parse.urlencode(
            expected_params
        )
        self.assertEqual(generated_url, expected_url)

    # tests for fetch_page_source (success/failure)
    def test_fetch_page_source_success(self):
        session_mock = Mock()
        mock_response = Mock(status_code=200, text="<html></html>")
        session_mock.get.return_value = mock_response

        content = fetch_page_source(
            session_mock, "https://www.google.com/search?q=test"
        )
        self.assertEqual(content, "<html></html>")

    @patch("src.data_collection.google_news.requests.Session")
    def test_fetch_page_source_failure(self, mock_session):
        """
        Test fetching page source with a failed HTTP response.
        """
        url = "https://www.google.com/search?q=test"

        # Mock the session and its response
        mock_response = Mock()
        mock_response.status_code = 404  # Ensure this is an integer
        mock_response.text = "Not Found"

        # Mock the session's get method
        mock_session_instance = mock_session.return_value
        mock_session_instance.get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            fetch_page_source(mock_session_instance, url)

        # Verify the exception message
        self.assertIn(
            "Failed to retrieve the page. Status code: 404", str(context.exception)
        )

    # tests for extract_articles
    def test_extract_articles_no_articles(self):
        """
        Test extracting articles when no articles are present in HTML.
        """
        html_content = "<html><body><div>No articles here!</div></body></html>"
        articles = extract_articles(html_content)
        self.assertEqual(len(articles), 0)
        self.assertEqual(articles, [])

    def test_extract_articles_with_articles(self):
        """
        Test extracting articles from valid HTML content.
        """
        html_content = """
        <html>
            <body>
                <div class="SoaBEf">
                    <a class="WlydOe" href="https://example.com/article1">
                        <div class="n0jPhd ynAwRc MBeuO nDgy9d">Title 1</div>
                        <div class="GI74Re nDgy9d">Description 1</div>
                    </a>
                </div>
                <div class="SoaBEf">
                    <a class="WlydOe" href="https://example.com/article2">
                        <div class="n0jPhd ynAwRc MBeuO nDgy9d">Title 2</div>
                        <div class="GI74Re nDgy9d">Description 2</div>
                    </a>
                </div>
            </body>
        </html>
        """
        articles = extract_articles(html_content)
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]["title"], "Title 1")
        self.assertEqual(articles[0]["description"], "Description 1")
        self.assertEqual(articles[0]["link"], "https://example.com/article1")
        self.assertEqual(articles[1]["title"], "Title 2")
        self.assertEqual(articles[1]["description"], "Description 2")
        self.assertEqual(articles[1]["link"], "https://example.com/article2")

    def test_extract_articles_partial_missing_fields(self):
        """
        Test extracting articles when some fields are missing.
        """
        html_content = """
        <html>
            <body>
                <div class="SoaBEf">
                    <a class="WlydOe" href="https://example.com/article1">
                        <!-- Missing title -->
                        <div class="GI74Re nDgy9d">Description 1</div>
                    </a>
                </div>
                <div class="SoaBEf">
                    <a class="WlydOe" href="https://example.com/article2">
                        <div class="n0jPhd ynAwRc MBeuO nDgy9d">Title 2</div>
                        <!-- Missing description -->
                    </a>
                </div>
                <div class="SoaBEf">
                    <!-- Missing link -->
                    <div class="n0jPhd ynAwRc MBeuO nDgy9d">Title 3</div>
                    <div class="GI74Re nDgy9d">Description 3</div>
                </div>
            </body>
        </html>
        """
        articles = extract_articles(html_content)
        self.assertEqual(len(articles), 3)
        self.assertEqual(articles[0]["title"], "No title found")
        self.assertEqual(articles[0]["description"], "Description 1")
        self.assertEqual(articles[0]["link"], "https://example.com/article1")

        self.assertEqual(articles[1]["title"], "Title 2")
        self.assertEqual(articles[1]["description"], "No description found")
        self.assertEqual(articles[1]["link"], "https://example.com/article2")

        self.assertEqual(articles[2]["title"], "Title 3")
        self.assertEqual(articles[2]["description"], "Description 3")
        self.assertEqual(articles[2]["link"], "No link found")

    # tests for scrape_google_news
    @patch("src.data_collection.google_news.save_to_json")
    @patch("src.data_collection.google_news.load_existing_json", return_value={})
    @patch("src.data_collection.google_news.fetch_page_source")
    @patch("src.data_collection.google_news.extract_articles")
    def test_scrape_google_news(
        self, mock_extract, mock_fetch, mock_loadjson, mock_savetojson
    ):
        """
        Test the scrape_google_news function to ensure it processes queries
        (list of lists) correctly over a date range.
        """
        # Mock the fetch_page_source and extract_articles
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = [
            {
                "title": "Test Article 1",
                "description": "This is a test article.",
                "link": "https://example.com/article1",
            }
        ]

        # 3 days range
        start_date = "1/1/2024"
        end_date = "1/3/2024"
        preferred_domains = ["brookings.edu"]

        # Each sub-list => one combined OR query
        queries = [
            ["AI", "Machine Learning"],  # => (AI) OR (Machine Learning)
            ["crypto"],  # => (crypto)
        ]

        articles_by_day = scrape_google_news(
            start_date,
            end_date,
            preferred_domains,
            queries,
            output_path="test_articles.json",  # we can remove or mock file writing in real usage
        )

        # Because it's 3 days × 2 queries = 6 total calls
        self.assertEqual(mock_fetch.call_count, 6)
        self.assertEqual(mock_extract.call_count, 6)

        # In total, each call returns 1 article, so 6 articles across 3 days × 2 queries
        # The function returns daily data, so let's check structure
        # e.g. articles_by_day => { "2024-01-01": [...], "2024-01-02": [...], "2024-01-03": [...] }
        self.assertEqual(len(articles_by_day), 3)  # 3 distinct date keys
        for day_key in ["2024-01-01", "2024-01-02", "2024-01-03"]:
            self.assertIn(day_key, articles_by_day)
            # Should have 2 articles each day
            day_articles = articles_by_day[day_key]
            self.assertEqual(len(day_articles), 2)
            for a in day_articles:
                # 'subtitle' => from 'description'
                self.assertEqual(a["title"], "Test Article 1")
                self.assertEqual(a["subtitle"], "This is a test article.")
                self.assertEqual(a["url"], "https://example.com/article1")


if __name__ == "__main__":
    unittest.main()

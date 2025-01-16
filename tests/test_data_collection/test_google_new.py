import unittest
import urllib.parse

from unittest.mock import patch, Mock

from src.data_collection.google_news import (
    get_google_news_url,
    fetch_page_source,
    extract_articles,
)


class TestGoogleNewsScraper(unittest.TestCase):

    def test_get_google_news_url_single_domain(self):
        """
        Test URL generation with a single preferred domain.
        """
        query = "AI, Machine Learning, crypto"
        start_date = "1/1/2024"
        end_date = "12/10/2024"
        preferred_domains = ["brookings.edu"]

        # Expected query format
        expected_query = (
            "(AI) OR (Machine Learning) OR (crypto) (site:brookings.edu OR *)"
        )
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

        expected_query = "(AI) OR (Machine Learning) OR (crypto) (site:brookings.edu OR site:example.com OR *)"
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

    @patch("src.data_collection.google_news.requests.get")
    def test_fetch_page_source_success(self, mock_get):
        """
        Test fetching page source successfully.
        """
        url = "https://www.google.com/search?q=test"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response

        content = fetch_page_source(url)
        mock_get.assert_called_once_with(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
            cookies={
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
            },
        )
        self.assertEqual(content, "<html></html>")

    @patch("src.data_collection.google_news.requests.get")
    def test_fetch_page_source_failure(self, mock_get):
        """
        Test fetching page source with a failed HTTP response.
        """
        url = "https://www.google.com/search?q=test"
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            fetch_page_source(url)
        self.assertIn(
            "Failed to retrieve the page. Status code: 404", str(context.exception)
        )

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
        # Sample HTML with two articles
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


if __name__ == "__main__":
    unittest.main()

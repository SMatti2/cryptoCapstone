import requests


class Client:
    def __init__(self, base_url: str, auth_header: str, api_key: str):
        self.base_url = base_url
        self.auth_header = auth_header
        self.api_key = api_key

    def fetch(self, endpoint: str, params: dict):
        headers = {self.auth_header: self.api_key}
        try:
            response = requests.get(
                self.base_url + endpoint, headers=headers, params=params
            )
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            raise

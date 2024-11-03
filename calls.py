import requests
import json


class GameAPIClient:
    def __init__(self, base_url="http://localhost:8081", api_key="7bcd6334-bc2e-4cbf-b9d4-61cb9e868869"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session_id = None
        self.endpoints = {
            "start_session": f"{self.base_url}/api/v1/session/start",
            "end_session": f"{self.base_url}/api/v1/session/end",
            "play_round": f"{self.base_url}/api/v1/play/round"
        }

    @property
    def base_headers(self):
        return {"API-KEY": self.api_key}

    @property
    def session_headers(self):
        headers = self.base_headers.copy()
        if self.session_id:
            headers["SESSION-ID"] = self.session_id
        return headers

    def start_session(self):
        """Start a new game session."""
        response = requests.post(
            self.endpoints["start_session"],
            headers=self.base_headers
        )

        if response.status_code == 200:
            print("Session started successfully")
            self.session_id = response.text
            return response.text
        elif response.status_code == 409:
            print("Connection already existed, ending session and retrying...")
            self.end_session()
            self.start_session()
        else:
            print(f"Error: {response.status_code}", response.text)

    def end_session(self):
        """End the current game session."""
        response = requests.post(
            self.endpoints["end_session"],
            headers=self.base_headers
        )

        if response.status_code == 200:
            print(f"Session <{self.session_id}> ended successfully")
            self.session_id = None
        else:
            print(f"Error: {response.status_code}", response.text)

    def play_round(self, day=0, movements=None):
        """Play a round with the given day and movements."""
        if not self.session_id:
            print("No active session. Can't play round")
            return

        round_data = {
            "day": day,
            "movements": movements or []
        }

        response = requests.post(
            self.endpoints["play_round"],
            headers=self.session_headers,
            json=round_data
        )

        if response.status_code == 200:
            print(f"Round {day} completed successfully")
            # print(response.text)
            return response.json()
            # print(json.dumps(response.json(), indent=4))
        else:
            print(f"Round {day} failed: {response.status_code}", response.text)
            return


def main():
    client = GameAPIClient()
    client.start_session()

    # try:
    for day in range(43):
        print(client.play_round(day=day))
    # finally:
        # client.end_session()


if __name__ == "__main__":
    main()

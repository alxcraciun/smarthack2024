import requests


class GameAPIClient:
    def __init__(self, base_url="http://localhost:8081", api_key="7bcd6334-bc2e-4cbf-b9d4-61cb9e868869"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session_id = None

    @property
    def base_headers(self):
        return {"API-KEY": self.api_key}

    @property
    def session_headers(self):
        headers = self.base_headers.copy()
        if self.session_id:
            headers["SESSION-ID"] = self.session_id
        return headers

    def _make_url(self, endpoint):
        return f"{self.base_url}/api/v1/{endpoint}"

    def _handle_response(self, response, success_message):
        if response.status_code == 200:
            print(f"{success_message}:")
            print(response.text, end="\n\n")
            return response.text
        elif response.status_code == 409:
            return None
        else:
            print(f"Error ({response.status_code}): {response.text}")
            return None

    def start_session(self):
        """Start a new game session."""
        response = requests.post(
            self._make_url("session/start"),
            headers=self.base_headers
        )

        if response.status_code == 409:
            print("Connection already existed, ending session and retrying...")
            self.end_session()
            return self.start_session()

        result = self._handle_response(response, "Session started successfully")
        if result:
            self.session_id = result
            return True
        return False

    def end_session(self):
        """End the current game session."""
        response = requests.post(
            self._make_url("session/end"),
            headers=self.base_headers
        )
        result = self._handle_response(response, "Session ended successfully")
        if result:
            self.session_id = None
            return True
        return False

    def play_round(self, day=0, movements=None):
        """Play a round with the given day and movements."""
        if not self.session_id:
            print("No active session. Starting new session...")
            if not self.start_session():
                return False

        round_data = {
            "day": day,
            "movements": movements or []
        }

        response = requests.post(
            self._make_url("play/round"),
            headers=self.session_headers,
            json=round_data
        )

        return self._handle_response(
            response,
            f"Round {day} completed successfully"
        )


def main():
    client = GameAPIClient()

    if client.start_session():
        try:
            for day in range(43):
                client.play_round(day=day)
        finally:
            client.end_session()


main()

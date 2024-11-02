import requests

# Constants
BASE_URL = "http://localhost:8081"
API_KEY = "7bcd6334-bc2e-4cbf-b9d4-61cb9e868869"
HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}
session_id = None


# 1. Start a New Session
def start_session():
    global session_id
    url = f"{BASE_URL}/api/v1/session/start"
    response = requests.post(url, headers=HEADERS)

    if response.status_code == 200:
        session_id = response.json().get("SESSION-ID")
        print("Session started:", session_id)
    else:
        print("Error starting session:", response.status_code, response.text)
        return None


# 2. Play a Round
def play_round(day, movements=None):
    url = f"{BASE_URL}/api/v1/play/round"
    round_headers = {**HEADERS, "SESSION-ID": session_id}  # Adding SESSION-ID to headers
    data = {
        "day": day,
        "movements": movements or []  # Empty list if no movements provided
    }

    response = requests.post(url, headers=round_headers, json=data)

    if response.status_code == 200:
        result = response.json()
        print(f"Day {day} Results:")
        print("  Demands:", result.get("demands"))
        print("  Penalties:", result.get("penalties"))
        print("  Daily KPIs - Cost:", result["kpis"]["daily_cost"], "CO2:", result["kpis"]["daily_co2"])
        print("  Session KPIs - Cost:", result["kpis"]["session_cost"], "CO2:", result["kpis"]["session_co2"])
    else:
        print(f"Error on day {day}:", response.status_code, response.text)


# 3. End the Session
def end_session():
    url = f"{BASE_URL}/api/v1/session/end"
    end_headers = {**HEADERS, "SESSION-ID": session_id}  # Adding SESSION-ID to headers

    response = requests.post(url, headers=end_headers)

    if response.status_code == 200:
        print("Session ended successfully.")
        print("Final session data:", response.json())
    else:
        print("Error ending session:", response.status_code, response.text)


# Example Usage
if __name__ == "__main__":
    start_session()  # Start the session
    if session_id:
        # Play rounds; for example, day 0 with no movements, and day 1 with example movements
        play_round(day=0, movements=[])  # Day 0 with no movements
        play_round(day=1, movements=[{"type": "move", "details": "example movement"}])  # Day 1 with movements
        end_session()  # End the session

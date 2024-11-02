import requests

# Constants
BASE_URL = "http://localhost:8081"
API_KEY = "7bcd6334-bc2e-4cbf-b9d4-61cb9e868869"

START_ENDPOINT = BASE_URL + "/api/v1/session/start"
END_ENDPOINT = BASE_URL + "/api/v1/session/end"
SESSION_HEADERS = {"API-KEY": API_KEY}

ROUND_ENDPOINT = BASE_URL + "/api/v1/play/round"
ROUND_HEADERS = {"API-KEY": API_KEY, "SESSION-ID": ""}

session_id = None


def update_round_headers(session_id):
    global ROUND_HEADERS
    ROUND_HEADERS = {"API-KEY": API_KEY, "SESSION-ID": session_id}


def start_session():
    global session_id
    response = requests.post(START_ENDPOINT, headers=SESSION_HEADERS)

    if response.status_code == 409:
        print("Connection already existed, now ending sesion\n")
        end_session()
        print("Trying to start session again...\n")
        start_session()
    elif response.status_code == 200:
        print("Session started successfully: ")
        session_id = response.text
        update_round_headers(session_id)
        print(session_id, end="\n\n")
    else:
        print("Error starting session:", response.status_code, response.text)


def end_session():
    global session_id
    response = requests.post(END_ENDPOINT, headers=SESSION_HEADERS)

    if response.status_code == 200:
        print("Session ended successfully")
        print(response.text, end="\n\n")
    elif response.status_code == 404:
        print("Session does not exist")
    else:
        print("Error ending session:", response.status_code, response.text)


def play_round(day=0, movements=None):
    round_data = {
        "day": day,
        "movements": movements or []
    }

    response = requests.post(ROUND_ENDPOINT, headers=ROUND_HEADERS, json=round_data)

    if response.status_code == 200:
        print("Round started succesfully")
        print(response.text, end="\n\n")
    else:
        print(f"Error on day {day}:", response.status_code, response.text)


# Code to test all endpoints
start_session()

for day in range(43):
    play_round(day=day)

end_session()

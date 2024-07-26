import requests
import json


base_url = "https://atapi.atomation.net/api/v1/s2s/v1_0"


def get_access_token(email, password):

    login_url = f"{base_url}/auth/login"


    login_payload = {
        "email": email,
        "password": password
    }


    login_headers = {
        "Content-Type": "application/json",
        "app_version": "1.8.5",
        "access_type": "5"
    }


    response = requests.post(login_url, headers=login_headers, data=json.dumps(login_payload))


    if response.status_code == 200:
        return response.json()["data"]["token"]
    else:
        raise Exception(f"Login failed: {response.json()}")




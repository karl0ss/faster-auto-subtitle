import requests
import os
token = os.getenv('bazarr_token')

def get_wanted_episodes():
    url = "http://192.168.4.23/api/episodes/wanted"

    payload={}
    headers = {
    'accept': 'application/json',
    'X-API-KEY': token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()


def get_episode_details(episode_id: str):
    url = f"http://192.168.4.23/api/episodes?episodeid%5B%5D={episode_id}"

    payload={}
    headers = {
    'accept': 'application/json',
    'X-API-KEY': token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()['data'][0]


def sync_series():
    url = f"http://192.168.4.23/api/system/tasks?taskid=update_series"

    payload={}
    headers = {
    'accept': 'application/json',
    'X-API-KEY': token
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()['data'][0]
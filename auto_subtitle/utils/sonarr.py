import requests
import json


def update_show_in_soarr(show_id):
    url = "http://192.168.4.9:8989/api/v3/command"

    payload = json.dumps({
    "name": "RefreshSeries",
    "seriesId": show_id
    })
    headers = {
  'Content-Type': 'application/json',
  'X-Api-Key': 'f6ea49a75a44469daec03969bdf6764d',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 404:
        print("Updated show in Sonarr")
import requests
import json
from .models import Wize

url = "https://srvc.tokenize.ee/01/events/audience"


def updateDB():
    payload = json.dumps(
        {
            "data": {"event": "d28ea5982b14436d98027b67f6b744b04", "items": 100},
            "user": "59d2b80833b94155bcd0a65b5346bb639",
        }
    )
    headers = {
        "Authorization": "59d2b80833b94155bcd0a65b5346bb639",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    r = response.json()
    print(r["data"]["count"])
    users = []
    for u in r["data"]["list"]:
        e = u["user"]["mail"]
        i = u["item"]
        users.append(
            {"emailId": e, "qrId": i, "eventId": "d28ea5982b14436d98027b67f6b744b04"}
        )
    print(users[:10])
    # json.dump(users, open('users.json', 'w'))
    # users = json.load(open('users.json', 'r'))
    # obj = [Wize(emailId=d['emailId'], qrId=d['qrId'], eventId=d['eventId']) for d in users]
    # Wize.objects.bulk_create(obj)

import requests
import json



def send_invoice(chat_id):
    method="sendInvoice"
    token = "token"
    url = f"https://api.telegram.org/bot{token}/{method}"
    chat_id = "@space_as_it_is"
    prices = json.dumps([{
        "label": "руб",
        "amount": 10000
    }])
    params = {
        "chat_id": chat_id,
        "title": "YourTitle",
        "description": "YourDescription",
        "payload": "YourPayload",
        "provider_token": "provider_token",
        "currency": "RUB",
        "start parameter": "test",
        "prices": prices
    }

    response = requests.post(url, params=params)
    response.raise_for_status()

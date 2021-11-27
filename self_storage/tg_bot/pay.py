import requests
import json
from environs import Env


def send_invoice(chat_id, token, provider_token):
    method="sendInvoice"
    url = f"https://api.telegram.org/bot{token}/{method}"
    prices = json.dumps([{
        "label": "руб",
        "amount": 10000
    }])
    params = {
        "chat_id": chat_id,
        "title": "YourTitle",
        "description": "YourDescription",
        "payload": "YourPayload",
        "provider_token": provider_token,
        "currency": "RUB",
        "start parameter": "Услуги аренды",
        "prices": prices
    }

    response = requests.post(url, params=params)
    response.raise_for_status()


if __name__ == "__main__":
    env = Env()
    env.read_env()
    provider_token = env.str('PROVIDER_TOKEN')
    token = env.str('TG_TOKEN')
    chat_id = env.str('BOT_ID')
    send_invoice(chat_id, token, provider_token)

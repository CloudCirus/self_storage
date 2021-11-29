# Self Storage Bot

Telegram bot for booking storage of things.   
The service allows customers to choose storage location, storage space, time interval, pay for the order and etc. 

## Enviroments

- create new bot in Telegram and get the token   
  (you can obtain bot from @BotFather in Telegram, [See example](https://telegra.ph/Awesome-Telegram-Bot-11-11))
- create the file .env and fill it with this data:
  - TG_TOKEN
  - DEBUG
  - SECRET_KEY
  - ALLOWED_HOSTS
- create file pd.pdf with personal data agreements for customers.

## Installing

- create virtualenv
```bash
python -m venv your_env_name
```

- clone github repository or download the code

- install packages

```bash
$pip install -r requirements.txt
```
- if you want to deploy bot to a server please proceed the manual of the selected service for settings. This project is adjusted for Heroku.
  
- set up Database as it described below

- for Admin access to create super user 

```bash
$python manage.py createsuperuser
```

- run the local server and pass to `http://127.0.0.1:8000/admin` to login to admin webpage
```bash
python manage.py runserver
```

- fill the fields according to the chapter "Models"

- run the bot with command below and pass to your bot chat in Telegram

```bash
$python manage.py bot
```

## Working with Database 
- Go to the app folder

```bash
$cd self_storage
```

- run the following commands to migrate models into DB:
```bash
python3 manage.py makemigrations
```

```bash
$python manage.py migrate 
```

## Authors

* [Rostwik](https://github.com/Rostwik)
* [Throughwind](https://github.com/throughwind)
* [CloudCirus](https://github.com/CloudCirus)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

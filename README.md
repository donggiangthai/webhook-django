# webhook-django
This is a simple bot using webhook with Django.

You need a https method to run webhook with facebook. In this project I'm using NgRok to host as a https server.

You need these environments to run this project:
```
PAGE_ACCESS_TOKEN = Generate with facebook developer page
VERIFY_TOKEN = Create by you
SECRET_KEY = a random string for Django secret key.
NGROK_HOST = using ngrok http 8000 to get https url
```
Reference document:

1. https://thecodespace.in/how-to-build-a-facebook-messenger-bot-using-django-ngrokfacebook-api/
2. https://github.com/rehabstudio/fbmessenger

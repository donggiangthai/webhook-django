import json
from abc import ABC
from decouple import config
from django.conf import settings
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from fbmessenger import BaseMessenger, MessengerClient
from fbmessenger.elements import Text

# Environment variable
PAGE_ACCESS_TOKEN = config('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = config('VERIFY_TOKEN')


# Create your views here.
class Messenger(BaseMessenger, ABC):
    def __init__(self, page_access_token, app_secret=None):
        self.page_access_token = page_access_token
        self.app_secret = app_secret
        self.client = MessengerClient(self.page_access_token, app_secret=self.app_secret)

    def message(self, message):
        action = process_message(message)
        res = self.send(action, 'RESPONSE')
        print(f"RESPONSE: {res}")


messenger = Messenger(PAGE_ACCESS_TOKEN)


def process_message(message):
    if 'text' in message['message']:
        msg = message['message']['text']
        response = Text(text=f"Sorry didn't understand that: {msg}")

        auto_message = settings.DATA

        if msg.lower() in auto_message:
            response = Text(text=auto_message[msg.lower()])
        return response.to_dict()
    else:
        response = Text(text=f"Sorry only text message, please!")
        return response.to_dict()


class BotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    # A POST method in Django need to be using with csrf token.
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # POST function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        payload = json.loads(self.request.body.decode('utf-8'))
        messenger.handle(payload)
        return HttpResponse()

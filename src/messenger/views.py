import json
import re
import requests
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

    def postback(self, message):
        pass


messenger = Messenger(PAGE_ACCESS_TOKEN)


def process_message(message):
    if 'text' in message['message']:
        msg = message['message']['text']
        response = Text(text=f"Sorry didn't understand that: {msg}")

        auto_message = settings.DATA

        if msg.lower() in auto_message:
            response = Text(text=auto_message[msg.lower()])
        # for key in auto_message.keys():
        #     if key in msg.lower():
        #         response = Text(text=auto_message[key])
        #         break
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

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        payload = json.loads(self.request.body.decode('utf-8'))
        messenger.handle(payload)
        return HttpResponse()


def post_facebook_message(sender_id, received_message):
    auto_message = {
        'hello': "Hello World!",
    }
    # Remove all punctuations, lower case the text and split it based on space
    # [^a-zA-Z0-9\s] is the pattern which match all character except a-z, A-Z, 0-9 and any whitespace
    # re.sub(pattern, repl, string)
    # pattern is a regular expression that you want to match.
    # repl is the replacement
    # string is the input string
    # => replace all matching pattern with the repl in the input string.
    tokens = re.sub(r"[^a-zA-Z0-9\s]", ' ', received_message).lower().split()
    response_text = ''
    for token in tokens:
        if token in auto_message:
            response_text = auto_message[token]
            break
    if not response_text:
        response_text = "I didn't understand!"
    post_message_url = f'https://graph.facebook.com/v2.6/me/messages?access_token={PAGE_ACCESS_TOKEN}'
    response_msg = json.dumps({"recipient": {"id": sender_id}, "message": {"text": response_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    print(status.json())




import json
import requests
import re
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.http.response import HttpResponse
from decouple import config


# Environment variable
PAGE_ACCESS_TOKEN = config('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = config('VERIFY_TOKEN')


# Create your views here.
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
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, opt-in, postback for other events
                if 'message' in message:
                    # Print the message to the terminal
                    print(message)
                    # Assuming the sender only sends text.
                    # Non-text messages like stickers, audio, pictures are sent as attachments
                    # and must be handled accordingly.
                    post_facebook_message(message['sender']['id'], message['message']['text'])
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




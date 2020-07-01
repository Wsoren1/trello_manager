from slack import WebClient
import json
from time import sleep


class Slackbot:
    def __init__(self):
        with open('data/slack_credentials.json', 'r') as f:
            slack_creds = json.load(f)

        self.server = slack_creds["api_key"]
        self.channel = slack_creds["active_channel"]

    def send_message(self, message):
        client = WebClient(token=self.server)
        response = client.chat_postMessage(
            channel=self.channel,
            text=message
        )

    def construct_text(self, message, kwargs=None):
        message_dict = {
            "due_passed":      "We observe mission `{0}` timeline parameters have expired.  We do not understand why.  "
                               "Your input is required for consensus. ```Ambitious Due Date``` ```Task Overload``` "
                               "```Forgot to Update``` ```Excused```",
            "set_due_date":    "Mission still critical.  How long have the mission parameters been extended, Commander?",
            "thank_for_data":  "Storing parameters.  Analyzing data.  Sorensen-Commander, we thank you."
        }
        return message_dict[message].format(kwargs)

    def get_last_user_message(self):
        client = WebClient(token=self.server)
        latest_message = client.channels_history(channel=self.channel).data['messages'][0]
        is_user = True
        try:
            latest_message['subtype']
            is_user = False
        except KeyError:
            pass

        if is_user:
            return latest_message['text']
        else:
            return ''




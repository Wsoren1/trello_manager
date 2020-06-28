from slack import WebClient
import json


class SlackbotPersonality:
    def __init__(self):
        with open('data/slack_credentials.json', 'r') as f:
            slack_creds = json.load(f)

        self.server = slack_creds["api_key"]
        self.channel = slack_creds["active_channel"]

    def _send_message(self, message):
        client = WebClient(token=self.server)
        response = client.chat_postMessage(
            channel=self.channel,
            text=message
        )


Sb = SlackbotPersonality()
Sb._send_message("Sorensen-Commander, this is a test.  We are Legion.")

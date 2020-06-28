import requests as req
import json


class TrelloBoard:
    def __init__(self):
        self.base_url = 'https://api.trello.com/1/'

        with open('data/trello/trello_credentials.json', 'r') as f:
            trello_creds = json.load(f)

            api_key = trello_creds['api_key']
            token = trello_creds['token']
            self.board_id = trello_creds['board_id']

            self.authentication = '?key={0}&token={1}'.format(api_key, token, self.board_id)

        self.labels = {}
        self.lists = {}

        self.heavy_update_self()

    def light_update_self(self):
        # Set
        self._extract_cards_data()

    def heavy_update_self(self):
        self.light_update_self()
        self._extract_lists_data()
        self._extract_labels_data()

        with open('data/trello/trello_lists.json', 'r') as f:
            j = json.load(f)
            for j_obj in j:
                self.lists[j_obj['name']] = j_obj['id']

        with open('data/trello/trello_labels.json', 'r') as f:
            j = json.load(f)
            for j_obj in j:
                self.labels[j_obj['name']] = j_obj['id']

    def _extract_labels_data(self):
        labels = req.request("GET", self.base_url + 'boards/{0}/labels'.format(self.board_id) + self.authentication)
        j = json.loads(labels.content)

        with open('data/trello/trello_labels.json', 'w') as f:
            json.dump(j, f)

    def _extract_lists_data(self):
        labels = req.request("GET", self.base_url + 'boards/{0}/lists'.format(self.board_id) + self.authentication)
        j = json.loads(labels.content)

        with open('data/trello/trello_lists.json', 'w') as f:
            json.dump(j, f)

    def _extract_cards_data(self):
        cards = req.request("GET", self.base_url + 'boards/{0}/cards'.format(self.board_id) + self.authentication)
        j = json.loads(cards.content)


TB = TrelloBoard()
print(TB.lists)
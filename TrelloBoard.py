import requests as req
import json
import datetime as dt
import re
import os


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
        self.label_names = []
        self.lists = {}
        self.lists_transposed = {}

        self.heavy_update_self()

    def light_update_self(self):
        os.remove('data/OverdueBufferCheck.txt')
        with open('data/OverdueBufferCheck.txt', 'w') as f:
            f.close()

        self._update_board()
        self._extract_cards_data()

    def heavy_update_self(self):
        self._extract_lists_data()
        self._extract_labels_data()

        with open('data/trello/trello_lists.json', 'r') as f:
            j = json.load(f)
            for j_obj in j:
                self.lists[j_obj['name']] = j_obj['id']
                self.lists_transposed[j_obj['id']] = j_obj['name']

        with open('data/trello/trello_labels.json', 'r') as f:
            j = json.load(f)
            for j_obj in j:
                self.labels[j_obj['name']] = j_obj['id']
                if j_obj['name'] not in self.label_names:
                    self.label_names += [j_obj['name']]

        self.light_update_self()

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
        log_time = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        with open('data/active.json', 'r') as f:
            j_prev = json.load(f)

        old_ids = [j_prev_obj['id'] for j_prev_obj in j_prev]
        new_cards = []

        for j_obj in j:
            if j_obj['id'] not in old_ids:
                new_cards += [j_obj]

        for j_obj in new_cards:
            j_obj["initialized_date"] = str(log_time)

        test = j_prev + new_cards
        with open('data/active.json', 'w') as f:
            json.dump(test, f)

    def _update_board(self):  # will need to be rewritten, but works for now
        cards = req.request("GET", self.base_url + 'boards/{0}/cards'.format(self.board_id) + self.authentication)
        j = json.loads(cards.content)

        for j_obj in j:
            url = self.base_url + 'cards/{0}'.format(j_obj['id']) + self.authentication
            querystring = {}

            list_name = self.lists_transposed[j_obj['idList']]
            if list_name in self.label_names:
                querystring["idLabels"] = [self.labels[list_name]] + j_obj["idLabels"]

            if j_obj['due'] is not None:
                re_due_date = re.search(r'^.*(?=(T))', j_obj['due'])
                card_due = dt.datetime.strptime(re_due_date.group(0), '%Y-%m-%d')
                days_since_due = (dt.datetime.today() - card_due).total_seconds() / 60 / 60 / 24

                if days_since_due > 3:
                    if j_obj['dueComplete']:
                        querystring['closed'] = "true"
                        file_to_write = 'data/IDsToArchive.txt'
                    else:
                        file_to_write = 'data/OverdueBufferCheck.txt'

                    with open(file_to_write, 'a') as f:
                        f.write(j_obj['id'] + '\n')

                elif days_since_due > -3:
                    querystring['idLabels'] = [self.labels["Priority"]] + j_obj["idLabels"]

                else:
                    if j_obj['dueComplete']:
                        querystring["idList"] = self.lists["Completed Today"]

                if days_since_due > -1:
                    querystring['idList'] = self.lists["Today"]

            req.request("PUT", url, params=querystring)

    def set_card_query(self, id, querystring):
        url = self.base_url + 'cards/{0}'.format(id) + self.authentication
        req.request("PUT", url, params=querystring)

    def push_recurring_cards(self):
        pass

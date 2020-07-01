import datetime
import json
import os


class DatabaseManager:
    def __init__(self):
        self.today = datetime.datetime.today()
        self.toMonthAbbrv = {
            1: "jan",
            2: "feb",
            3: "mar",
            4: "apr",
            5: "may",
            6: "jun",
            7: "jul",
            8: "aug",
            9: "sep",
            10: "oct",
            11: "nov",
            12: "dec"
        }
        self.archive_title = self.toMonthAbbrv[self.today.month] + str(self.today.year)
        self.toArchive = []

    def update_archive(self):
        with open('data/IDsToArchive.txt', 'r') as f:
            ids = [id[:-1] for id in f.readlines()]

        keep_obj = []
        with open('data/active.json', 'r') as f:
            j = json.load(f)
            for j_obj in j:
                if j_obj['id'] in ids:
                    j_obj['completed_date'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    self.toArchive += [j_obj]
                else:
                    keep_obj += [j_obj]
        with open('data/active.json', 'w') as f:
            json.dump(keep_obj, f)

        archive_file = 'data/archive/{0}.json'.format(self.archive_title)
        j_prev_archive = None

        if not os.path.exists(archive_file):
            open(archive_file, 'w')

        if os.stat(archive_file).st_size != 0:
            with open(archive_file, 'r') as f:
                j_prev_archive = json.load(f)

        if len(self.toArchive) != 0:
            with open(archive_file, 'w') as f:
                if j_prev_archive is not None:
                    json.dump(self.toArchive + j_prev_archive, f)
                else:
                    json.dump(self.toArchive, f)
        self.toArchive = []
        with open('data/IDsToArchive.txt', 'w') as f:
            f.close()

    def edit_object(self, id, key, value):
        with open('data/active.json', 'r') as f:
            j = json.load(f)

        for j_obj in j:
            if j_obj['id'] == id:
                if isinstance(value, list) and key in j_obj:
                    j_obj[key] = value + j_obj[key]
                else:
                    j_obj[key] = value
                break

        print(j[0][key])

        with open('data/active.json', 'w') as f:
            json.dump(j, f)

    def update_manager(self):
        self.today = datetime.datetime.today()
        self.archive_title = self.toMonthAbbrv[self.today.month] + str(self.today.year)


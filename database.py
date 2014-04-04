'''because dbm doesn't work'''

import random
import json

class DB(object):
    def __init__(self, filepath=None):
        self.d = {} if filepath is None else self.load(filepath)
        self.filepath = filepath

    def init_app(self, app):
        filepath = app.config['DB_PATH']
        self.__init__(filepath)

    def load(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save(self, filepath=None):
        if filepath is None:
            filepath = self.filepath

        if filepath is not None:
            with open(filepath, 'w') as f:
                json.dump(self.d, f, indent=2)

    def get(self,k):
        return self.d.get(k)

    def put(self,k,v):
        if v is None:
            return self.rm(k)
        self.d[k] = v
        self.save()

    def rm(self,k):
        del self.d[k]
        self.save()

    def next_id(self):
        for _ in range(5):
            x = repr(random.random())[2:]
            if x not in self.d:
                return x

    def items(self):
        return self.d.items()

    def __iter__(self):
        return self.d.__iter__()

db = DB()


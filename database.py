import random
import json

DB_PATH='db.json'

def load(filepath=DB_PATH):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return {}

def save(d,filepath=DB_PATH):
    with open(filepath, 'w') as f:
        json.dump(d, f, indent=2)

db = load()

def put(d,k,v):
    d[k] = v
    save(d)

def rm(d,k):
    del d[k]
    save(d)

def next_id():
    for _ in range(5):
        x = repr(random.random())[2:]
        if x not in db:
            return x

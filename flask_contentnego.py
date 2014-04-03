import json
import random

from flask import app, Flask, jsonify, request, render_template, redirect, url_for, g

DB_PATH='db.json'
app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'GET':
        for t,_ in request.accept_mimetypes:
            if t == 'text/html':
                return render_template('list.html', db=db)
            if t == 'application/json':
                return json.dumps(db),200,{'Content-Type': 'application/json'}
        return json.dumps(db),200,{'Content-Type': 'application/json'}

    # too lazy to do Content-Type check.
    form = request.get_json(silent=True)
    if not form:
        form = request.form

    val = form.get('val')
    if not val:
        msg = 'need val'
        for t,_ in request.accept_mimetypes:
            if t == 'text/html':
                return render_template('list.html', db=db, msg=msg),400
            if t == 'application/json':
                return jsonify(msg=msg),400
        return jsonify(msg=msg),400

    key = next_id()
    put(db,key,val)
    return redirect(url_for('detail',key=key))
    
    

@app.route('/<key>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def detail(key):
    if request.method == 'GET':
        val = db.get(key)
        if val is None:
            msg = 'cannot find '+key
            for t,_ in request.accept_mimetypes:
                if t == 'application/json':
                    return jsonify(msg=msg),404
                if t == 'text/html':
                    return render_template('base.html', msg=msg),404
            return jsonify(msg=msg),404

        for t,_ in request.accept_mimetypes:
            if t == 'application/json':
                return jsonify(key=key,val=val)
            if t == 'text/html':
                return render_template('detail.html', key=key, val=val)
        return jsonify(key=key,val=val)

    if request.method == 'POST':
        method = request.args.get('method', request.form.get('method'))
        if method:
            g.method = method.upper()
        else:
            msg = 'not supported: POST'
            for t,_ in request.accept_mimetypes:
                if t == 'application/json':
                    return jsonify(msg=msg),405
                if t == 'text/html':
                    return render_template('base.html', msg=msg),405
            return jsonify(msg=msg),405

    if request.method == 'PUT' or g.method == 'PUT':
        val = None
        if request.mimetype == 'application/json':
            d = request.get_json(force=True)
            val = d['val']
        if request.mimetype == 'application/x-www-form-urlencoded':
            val = request.form['val']

        put(db,key,val)

        for t,_ in request.accept_mimetypes:
            if t == 'application/json':
                return jsonify(key=key, val=val)
            if t == 'text/html':
                return render_template('detail.html', key=key, val=val)
        return jsonify(key=key, val=val)

    if request.method == 'DELETE' or g.method == 'DELETE':
        if key in db:
            rm(db,key)
            msg = 'deleted: '+key
            for t,_ in request.accept_mimetypes:
                if t == 'application/json':
                    return jsonify(msg=msg),200
                if t == 'text/html':
                    return render_template('base.html',msg=msg),200
            return jsonify(msg=msg),200
        for t,_ in request.accept_mimetypes:
            msg = 'not found: '+key
            if t == 'application/json':
                return jsonify(msg=msg),404
            if t == 'text/html':
                return render_template('base.html', msg=msg),404
        return jsonify(msg=msg),404


if __name__ == '__main__':
    app.run(debug=True)

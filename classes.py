import json

from flask import Blueprint, render_template, jsonify, request, url_for, g

from database import db

bp = Blueprint('classes', __name__)

class Renderable(object):
    def render_default(self):
        return self.render_json()

    def render_json(self):
        raise NotImplemented()

    def render_html(self):
        raise NotImplemented()

    def render(self):
        for t,_ in request.accept_mimetypes:
            if t == 'application/json':
                return self.render_json()
            if t == 'text/html':
                return self.render_html()
        return self.render_default()


class DetailRenderer(Renderable):
    def __init__(self, key, val):
        self.key = key
        self.val = val

    def render_json(self):
        return jsonify(key=self.key, val=self.val)

    def render_html(self):
        return render_template('detail.html', key=self.key, val=self.val)

class MessageRenderer(Renderable):
    def __init__(self, msg, status_code=200, headers=None):
        self.msg = msg
        self.status_code = status_code
        self.headers = headers

    def render_json(self):
        return jsonify(msg=self.msg),self.status_code,self.headers

    def render_html(self):
        return render_template('base.html', msg=self.msg),self.status_code,self.headers

class ListRenderer(Renderable):
    def __init__(self, db):
        self.db = db

    def render_json(self):
        return self.db.jsondumps(),200,{'Content-Type': 'application/json'}

    def render_html(self):
        return render_template('list.html', db=self.db)

@bp.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'GET':
        return ListRenderer(db).render()

    # too lazy to do Content-Type check.
    form = request.get_json(silent=True)
    if not form:
        form = request.form

    val = form.get('val')
    if not val:
        return MessageRenderer('need val',400).render()
    
    key = db.next_id()
    db.put(key,val)
    created_url = url_for('.detail', key=key)
    return MessageRenderer('created: '+created_url,201,{'Location': created_url, 'Content-Location':  created_url}).render()

@bp.route('/<key>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def detail(key):
    if request.method == 'GET':
        val = db.get(key)
        if val is None:
            return MessageRenderer('cannot find: '+key, 404).render()
        
        return DetailRenderer(key, val).render()

    if request.method == 'POST':
        method = request.args.get('method', request.form.get('method'))
        if method:
            g.method = method.upper()
        else:
            return MessageRenderer('not supported: POST', 405).render()

    if request.method == 'PUT' or g.method == 'PUT':
        val = None
        if request.mimetype == 'application/json':
            d = request.get_json(force=True)
            val = d['val']
        if request.mimetype == 'application/x-www-form-urlencoded':
            val = request.form['val']

        db.put(key,val)

        return DetailRenderer(key,val).render()

    if request.method == 'DELETE' or g.method == 'DELETE':
        if key in db:
            db.rm(key)
            return MessageRenderer('deleted: '+key).render()
        return MessageRenderer('not found: '+key,404).render()



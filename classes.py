import json

from flask import Blueprint, render_template, make_response, jsonify, request, url_for, g

from database import db

bp = Blueprint('classes', __name__)

class Renderable(object):
    '''subclass this and implement render_* methods.
    and call .render() method.
    '''
    def render_default(self):
        return self.render_json()

    def render_json(self):
        raise NotImplemented()

    def render_html(self):
        raise NotImplemented()

    def _render(self, ret_val, status_code=None, headers=None, status=None):
        resp = make_response(ret_val)
        if status_code is not None:
            resp.status_code = status_code
        if status is not None:
            resp.status = status
        if headers:
            resp.headers.extend(headers)
        return resp

    def render(self, status_code=None, headers=None, status=None):
        '''renders this renderable based on Accept header.
        you can override default status_code, headers, status.'''
        for t,_ in request.accept_mimetypes:
            if t == 'application/json':
                return self._render(self.render_json(), status_code, headers, status)
            if t == 'text/html':
                return self._render(self.render_html(), status_code, headers, status)
        return self._render(self.render_default(), status_code, headers, status)

def blitdict(key, **kwargs):
    '''if kwargs[key] is dict, blits kwargs into kwargs[key]. kwargs[key].update(kwargs)'''
    obj = kwargs.get(key)
    if obj and 'update' in dir(obj):
        del kwargs[key]
        obj.update(kwargs)
    else:
        obj = kwargs
    return obj

class Renderer(Renderable):
    '''renders objects.
    Renderer('base.html', 'x', x={'a':1}, foo='bar') renders {'a':1, 'foo':bar}
    Renderer('base.html', x={'a':1}, foo='bar') renders {'x': {'a':1}, 'foo':'bar} 
        because main_obj_key, 'obj', isn't found in **objects
    '''
    def __init__(self, template_name, main_obj_key='obj', status_code=200, **objects):
        self.main_obj_key = main_obj_key
        self.template_name = template_name
        self.status_code = status_code
        self.objects = objects

    def render_json(self):
        obj = blitdict(self.main_obj_key, **self.objects)
        return json.dumps(obj),self.status_code,{'Content-Type': 'application/json'}

    def render_html(self):
        return render_template(self.template_name, **self.objects),self.status_code

@bp.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'GET':
        return Renderer('list.html', 'db', db=db.d).render()

    # too lazy to do Content-Type check.
    form = request.get_json(silent=True)
    if not form:
        form = request.form

    val = form.get('val')
    if not val:
        return Renderer('base.html', 'msg', msg='need val').render(400)
    
    key = db.next_id()
    db.put(key,val)
    created_url = url_for('.detail', key=key)
    return Renderer('base.html', msg='created: '+created_url).render(
            201,{'Location': created_url, 'Content-Location':  created_url})

@bp.route('/<key>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def detail(key):
    if request.method == 'GET':
        val = db.get(key)
        if val is None:
            return Renderer('base.html',msg='cannot find: '+key).render(404)
        
        return Renderer('detail.html', key=key, val=val).render()

    if request.method == 'POST':
        method = request.args.get('method', request.form.get('method'))
        if method:
            g.method = method.upper()
        else:
            return Renderer('base.html',msg='not supported: POST').render(405)

    if request.method == 'PUT' or g.method == 'PUT':
        val = None
        if request.mimetype == 'application/json':
            d = request.get_json(force=True)
            val = d['val']
        if request.mimetype == 'application/x-www-form-urlencoded':
            val = request.form['val']

        db.put(key,val)

        return Renderer('base.html',key=key,val=val).render()

    if request.method == 'DELETE' or g.method == 'DELETE':
        if key in db:
            db.rm(key)
            return Renderer('base.html',msg='deleted: '+key).render()
        return Renderer('base.html',msg='not found: '+key).render(404)



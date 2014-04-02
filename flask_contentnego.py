from flask import app, Flask, jsonify, request, render_template

app = Flask(__name__)

db = {}

@app.route('/<key>', methods=['GET', 'DELETE', 'PUT'])
def detail(key):
    if request.method == 'GET':
        val = db.get(key)
        if val is None:
            msg = 'cannot find '+key
            for t,_ in request.accept_mimetypes:
                if t == 'application/json':
                    return jsonify(msg=msg),404
                if t == 'text/html':
                    return render_template('error.html', msg=msg),404
            return jsonify(msg=msg),404

        for t,_ in request.accept_mimetypes:
            if t == 'application/json':
                return jsonify(key=key,val=val)
            if t == 'text/html':
                return render_template('detail.html', key=key, val=val)
        return jsonify(key=key,val=val)


    if request.method == 'PUT':
        val = None
        if request.mimetype == 'application/json':
            d = request.get_json(force=True)
            val = d['val']
        if request.mimetype == 'application/x-www-form-urlencoded':
            val = request.form['val']

        db[key] = val

        for t,_ in request.accept_mimetypes:
            if t == 'application/json':
                return jsonify(key=key, val=val)
            if t == 'text/html':
                return render_template('detail.html', key=key, val=val)
        return jsonify(key=key, val=val)

    if request.method == 'DELETE':
        del db[key]


if __name__ == '__main__':
    app.run(debug=True)

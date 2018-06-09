from flask import render_template, request, redirect,url_for
from manifest_cultural import app, db
from manifest_cultural.models import Event


@app.route("/", methods=["POST", "GET"])
def index():
    events = db.session.query(Event)
    new_events = []

    if request.method == "POST":
        new_events = request.form.getlist('new_events')
        # return redirect(url_for('index', _anchor="services", new_events=new_events))

    return render_template('index.html', events=events, new_events=new_events)


if __name__ == "__main__":
    app.run(debug=True)

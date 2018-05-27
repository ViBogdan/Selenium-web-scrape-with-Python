from flask import render_template
from manifest_cultural import app, db
from manifest_cultural.models import Event


@app.route("/")
@app.route("/index")
def index():
    events = db.session.query(Event)
    return render_template('index.html', events=events)


if __name__ == "__main__":
    app.run(debug=True)

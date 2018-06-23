import datetime

from flask import render_template, jsonify, request
from sqlalchemy import func, or_

from manifest_cultural import app, db
from manifest_cultural.models import Event


@app.route("/")
def index():
    events = db.session.query(Event)
    return render_template('index.html', events=events)


@app.route('/ajax/events')
def get_events():
    when = request.args.get('when')
    if when == 'today':
        today = datetime.date.today()
        events = db.session.query(Event).filter(
            or_(
                func.DATE(Event.start_date) == today,
                func.DATE(Event.end_date) == today,
                func.DATE(Event.first_date) == today,
                func.DATE(Event.second_date) == today,
                )
        )
    elif when == 'tomorrow':
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        events = db.session.query(Event).filter(
            or_(
                func.DATE(Event.start_date) == tomorrow,
                func.DATE(Event.end_date) == tomorrow,
                func.DATE(Event.first_date) == tomorrow,
                func.DATE(Event.second_date) == tomorrow,
            )
        )
    else:
        events = db.session.query(Event)

    # serialize events as dict to be able to json encode them
    events = [event.as_dict() for event in events]
    return jsonify(events)


if __name__ == "__main__":
    app.run(debug=True)

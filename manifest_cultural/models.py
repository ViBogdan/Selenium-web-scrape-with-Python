from manifest_cultural import db


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    venue = db.Column(db.String)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    def __repr__(self):
        return "<Event(name='%s', venue='%s', start_date='%s', end_date='%s')>" % (
            self.name, self.venue, self.start_date, self.end_date
        )
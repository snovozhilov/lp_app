from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ParsedImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phash = db.Column(db.String, unique=True, nullable=False)
    chat_id = db.Column(db.BigInteger, nullable=True)
    chat_name = db.Column(db.String, nullable=True)
    full_filename = db.Column(db.String, nullable=False)
    filename = db.Column(db.String, nullable=False)
    published_ts = db.Column(db.DateTime, nullable=False)
    parsed_ts = db.Column(db.DateTime, nullable=False)
    dadd = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return '<ParsedImages {} {}>'.format(self.full_filename, self.published_ts, )


class UserRates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    image_id = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.SmallInteger, nullable=False)
    ts = db.Column(db.DateTime, nullable=False)
    dadd = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return '<UserRates {} {} {}>'.format(self.user_id, self.image_id, self.rate,)


class Recommendations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    image_id = db.Column(db.Integer, nullable=False)
    expected_rate = db.Column(db.Float, nullable=False)
    dadd = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return '<Recommendations {} {} {}>'.format(self.user_id, self.image_id, self.expected_rate,)
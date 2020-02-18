from app import db
from sqlalchemy.dialects.postgresql import JSON


class CssOrderDTO(db.Model):
    __tablename__ = 'css_orders'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)
    name = db.Column(db.String)
    service = db.Column(db.String)
    ordered_at: db.Column(db.String)
    items = db.Column(JSON)

    def __init__(self, name, service, result_no_stop_words):
        self.name = name
        self.service = service

    def __repr__(self):
        return '<id {}>'.format(self.id)

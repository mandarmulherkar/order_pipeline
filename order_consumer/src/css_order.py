from wsgi import db
from datetime import datetime
from css_constants import CssConstants


class CssOrder(db.Model):
    __tablename__ = 'received_order'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    service = db.Column(db.String())
    status = db.Column(db.String())
    items_in_order = db.Column(db.Integer())
    completed_items_in_order = db.Column(db.Integer())
    ordered_at = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, name, service, items_in_order, ordered_at, status=CssConstants.ORDER_RECEIVED,
                 completed_items_in_order=0):
        self.name = name
        self.service = service
        self.items_in_order = items_in_order
        self.ordered_at = datetime.strptime(ordered_at, "%Y-%m-%dT%H:%M:%S")
        self.status = status
        self.completed_items_in_order = completed_items_in_order

    def __repr__(self):
        return '<id {}>'.format(self.id)

from datetime import datetime
import sys

if hasattr(sys, '_called_from_test'):
    from .css_constants import CssConstants
    from .wsgi import db
else:
    from css_constants import CssConstants
    from wsgi import db


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
    completed_at = db.Column(db.DateTime(), default=None)

    def __init__(self, name, service, items_in_order, ordered_at, status=CssConstants.ORDER_RECEIVED,
                 completed_items_in_order=0):
        self.name = name
        self.service = service
        self.items_in_order = items_in_order
        try:
            self.ordered_at = datetime.strptime(ordered_at, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            try:
                self.ordered_at = datetime.strptime(ordered_at, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                self.ordered_at = datetime.utcnow()

        self.status = status
        self.completed_items_in_order = completed_items_in_order

    def __repr__(self):
        return '<id {}>'.format(self.id)

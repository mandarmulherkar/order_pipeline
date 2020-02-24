from wsgi import db
from datetime import datetime
from css_constants import CssConstants


class OrderItem(db.Model):
    __tablename__ = 'order_item'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('received_order.id'))
    name = db.Column(db.String())
    price_per_unit = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    status = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, order_id, name, price_per_unit, quantity, status=CssConstants.ORDER_RECEIVED):
        self.order_id = order_id
        self.name = name
        self.price_per_unit = price_per_unit
        self.quantity = quantity
        self.status = status

    def __repr__(self):
        return '<order_id: {}, id {}>'.format(self.order_id, self.id)

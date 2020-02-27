# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
from datetime import datetime
from app import db
from sqlalchemy.sql import text, func
import json


class CssConstants:
    ORDER_RECEIVED = "order_received"
    ORDER_COMPLETE = "order_complete"


class OrderItem(db.Model):
    __tablename__ = 'order_item'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('received_order.id'))
    name = db.Column(db.String())
    price_per_unit = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    status = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    completed_at = db.Column(db.DateTime(), default=None)

    def __init__(self, order_id, name, price_per_unit, quantity, status=CssConstants.ORDER_RECEIVED):
        self.order_id = order_id
        self.name = name
        self.price_per_unit = price_per_unit
        self.quantity = quantity
        self.status = status

    def __repr__(self):
        return '<order_id: {}, id {}>'.format(self.order_id, self.id)


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
        self.ordered_at = datetime.strptime(ordered_at, "%Y-%m-%dT%H:%M:%S")
        self.status = status
        self.completed_items_in_order = completed_items_in_order

    def __repr__(self):
        return '<id {}>'.format(self.id)


def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count


@blueprint.route('/index')
@login_required
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    # css_order = CssOrder.query.filter_by(id=2).with_for_update().first()
    # query(CssOrder.column, func.count(Table.column)).group_by(Table.column).all()
    # query = text(
    #     "select date_trunc('minute', completed_at), count(*) from received_order where status = 'order_complete' group by date_trunc('minute', completed_at) order by date_trunc('minute', completed_at) desc limit 10;")
    # query = query.columns(CssOrder.completed_at)

    css_order = CssOrder.query.with_entities(func.date_trunc('minute', CssOrder.created_at),
                                             func.count(CssOrder.name)).group_by(
        func.date_trunc('minute', CssOrder.created_at)).limit(10).all()

    data = []
    for order in css_order:
        data.append(order[1])
    print(data)
    print(str(data))
    # css_order = CssOrder.query.from_statement(query).all()

    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]

    # Top Stats
    received_count = get_count(CssOrder.query.filter())
    complete_count = get_count(CssOrder.query.filter(CssOrder.status == CssConstants.ORDER_COMPLETE))

    items_count_total = get_count(OrderItem.query.filter())
    items_cooked_count_total = get_count(OrderItem.query.filter(OrderItem.status == CssConstants.ORDER_COMPLETE))

    # Get last 4 orders as received
    #
    last_4_orders = CssOrder.query.order_by()
    #     CssOrder.status == 'order_complete').all()
    return render_template('index.html', chart_data={"values": values, "labels": labels, "legend": legend},
                           orders_complete=complete_count, orders_received=received_count,
                           items_total=items_count_total,
                           items_cooked=items_cooked_count_total)


@blueprint.route('/<template>')
def route_template(template):
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    try:

        return render_template(template + '.html')

    except TemplateNotFound:
        return render_template('error-404.html'), 404

    except:
        return render_template('error-500.html'), 500

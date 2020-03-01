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
from sqlalchemy.sql import text, func, desc
from sqlalchemy import or_
import json


class CssConstants:
    ORDER_RECEIVED = "order_received"
    ORDER_IN_PROGRESS = "in_progress"
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
                                             func.count(CssOrder.id)).group_by(
        func.date_trunc('minute', CssOrder.created_at)).order_by(
        func.date_trunc('minute', CssOrder.created_at)).limit(8).all()

    data = []
    labels = []
    for order in css_order:
        labels.append(order[0].strftime("%H:%M:%S"))
        data.append(order[1])

    #
    # if len(data) < 8:
    #     for i in range(len(data), 8):
    #         data.append(0)

    print(data)
    print(labels)
    # css_order = CssOrder.query.from_statement(query).all()

    legend = 'Orders per minute'
    labels = labels
    # ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = data
    # [10, 9, 8, 7, 6, 4, 7, 8]

    # Top Stats
    # Top Stats
    received_query = CssOrder.query.filter()
    received_count = get_count(received_query)

    complete_query = CssOrder.query.filter(CssOrder.status == CssConstants.ORDER_COMPLETE)
    complete_count = get_count(complete_query)

    items_count_query = OrderItem.query.filter()
    items_count = get_count(items_count_query)

    items_cooked_query = OrderItem.query.filter(OrderItem.status == CssConstants.ORDER_COMPLETE)
    items_cooked_count = get_count(items_cooked_query)

    in_progress_query_orders = CssOrder.query.filter(CssOrder.status == CssConstants.ORDER_IN_PROGRESS)
    in_progress_count_orders = get_count(in_progress_query_orders)

    in_progress_query_items = OrderItem.query.filter(OrderItem.status == CssConstants.ORDER_IN_PROGRESS)
    in_progress_count_items = get_count(in_progress_query_items)

    # Get last 4 orders as received
    last_few_orders = CssOrder.query.filter(or_(
        CssOrder.status == CssConstants.ORDER_IN_PROGRESS, CssOrder.status == CssConstants.ORDER_COMPLETE)).order_by(
        CssOrder.created_at.desc()).limit(4).all()

    last_few_orders_list = []
    for order in last_few_orders:
        percent_completion = round((order.completed_items_in_order / float(order.items_in_order)) * 100, 2)
        last_few_orders_list.append(
            {"id": order.id, "name": order.name, "status": order.status, "percent_completion": str(percent_completion),
             "service": order.service})

    #  Get most popular service
    most_popular_service = CssOrder.query.with_entities(CssOrder.service,
                                                        func.count(CssOrder.id).label('total')).group_by(
        CssOrder.service).order_by(desc('total')).limit(1).all()

    if len(most_popular_service) == 0:
        most_popular_service = 'Turning on the stove...'
    else:
        most_popular_service = most_popular_service[0].service + ", " + str(most_popular_service[0].total)

    #  Get most popular item
    most_popular_item = OrderItem.query.with_entities(OrderItem.name,
                                                      func.count(OrderItem.id).label('total')).group_by(
        OrderItem.name).order_by(desc('total')).limit(1).all()

    if len(most_popular_item) == 0:
        most_popular_item = 'Cutting onions...'
    else:
        most_popular_item = most_popular_item[0].name + ", " + str(most_popular_item[0].total)

    return render_template('index.html', chart_data={"values": values, "labels": labels, "legend": legend},
                           orders_complete=complete_count, orders_received=received_count,
                           items_total=items_count,
                           items_cooked=items_cooked_count,
                           orders_in_progress=in_progress_count_orders,
                           items_in_progress=in_progress_count_items,
                           last_few_orders_list=last_few_orders_list, length_last_few=len(last_few_orders_list),
                           most_popular_service=most_popular_service,
                           most_popular_item=most_popular_item)


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

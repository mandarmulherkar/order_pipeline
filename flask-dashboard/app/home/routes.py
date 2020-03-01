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
# @login_required
def index():
    # if not current_user.is_authenticated:
    #     return redirect(url_for('base_blueprint.login'))

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

    labels_orders_per_minute, legend_orders_per_minute, values_orders_per_minute = get_orders_per_minute()
    labels_orders_per_minute_complete, legend_orders_per_minute_complete, values_orders_per_minute_complete = get_orders_per_minute_complete()

    labels_items_per_minute, legend_items_per_minute, values_items_per_minute = get_items_per_minute()
    labels_items_per_minute_complete, legend_items_per_minute_complete, values_items_per_minute_complete = get_items_per_minute_complete()

    # Find waiting time / delays
    # select date_trunc('minute', created_at) as time_period, avg(completed_at - created_at) from order_item
    # group by time_period order by date_trunc('minute', created_at);
    labels_avg_time_to_completion, legend_avg_time_to_completion, values_avg_time_to_completion = get_avg_time_to_completion()

    # Orders per service, top 5
    labels_orders_per_service, legend_orders_per_service, values_orders_per_service = get_orders_per_service(5)

    # Count of items
    labels_items_ordered, legend_items_ordered, values_items_ordered = get_most_requested_items(3)

    # Get last (4) orders as received
    last_few_orders_list = get_last_few_orders(5)

    #  Get most popular service
    most_popular_service = get_popular_service()

    #  Get most popular item
    most_popular_item = get_popular_item()

    return render_template('index.html',
                           orders_per_minute={"values": values_orders_per_minute, "labels": labels_orders_per_minute,
                                              "legend": legend_orders_per_minute},
                           orders_per_minute_complete={"values": values_orders_per_minute_complete,
                                                       "labels": labels_orders_per_minute_complete,
                                                       "legend": legend_orders_per_minute_complete},
                           items_per_minute={"values": values_items_per_minute, "labels": labels_items_per_minute,
                                             "legend": legend_items_per_minute},
                           items_per_minute_complete={"values": values_items_per_minute_complete,
                                                      "labels": labels_items_per_minute_complete,
                                                      "legend": legend_items_per_minute_complete},
                           avg_time_to_completion={"values": values_avg_time_to_completion,
                                                   "labels": labels_avg_time_to_completion,
                                                   "legend": legend_avg_time_to_completion},
                           orders_per_service={"values": values_orders_per_service,
                                               "labels": labels_orders_per_service,
                                               "legend": legend_orders_per_service},
                           most_requested_items={"values": values_items_ordered,
                                                 "labels": labels_items_ordered,
                                                 "legend": legend_items_ordered},
                           orders_complete=complete_count, orders_received=received_count,
                           items_total=items_count,
                           items_cooked=items_cooked_count,
                           orders_in_progress=in_progress_count_orders,
                           items_in_progress=in_progress_count_items,
                           last_few_orders_list=last_few_orders_list, length_last_few=len(last_few_orders_list),
                           most_popular_service=most_popular_service,
                           most_popular_item=most_popular_item)


def get_orders_per_service(top_n):
    orders_per_service = CssOrder.query \
        .with_entities(CssOrder.service,
                       func.count(CssOrder.id).label('total')) \
        .group_by(CssOrder.service) \
        .order_by(desc('total')) \
        .limit(top_n) \
        .all()
    data_orders_per_service = []
    labels_orders_per_service = []
    for service in orders_per_service:
        labels_orders_per_service.append(service[0])
        data_orders_per_service.append(service[1])
    legend_orders_per_service = 'Orders Per Service'
    labels_orders_per_service = labels_orders_per_service
    values_orders_per_service = data_orders_per_service
    return labels_orders_per_service, legend_orders_per_service, values_orders_per_service


def get_most_requested_items(top_n):
    items_ordered = OrderItem.query \
        .with_entities(OrderItem.name,
                       func.count(OrderItem.id).label('total')) \
        .group_by(OrderItem.name) \
        .order_by(desc('total')) \
        .limit(top_n) \
        .all()
    data_items_ordered = []
    labels_items_ordered = []
    for item in items_ordered:
        labels_items_ordered.append(item[0])
        data_items_ordered.append(item[1])
    legend_items_ordered = 'Most Requested Items'
    labels_items_ordered = labels_items_ordered
    values_items_ordered = data_items_ordered
    return labels_items_ordered, legend_items_ordered, values_items_ordered


def get_avg_time_to_completion():
    avg_wait_times_per_minute = OrderItem.query \
        .with_entities(func.date_trunc('minute', OrderItem.created_at),
                       func.avg(OrderItem.completed_at - OrderItem.created_at).label('average')) \
        .filter(OrderItem.status == CssConstants.ORDER_COMPLETE) \
        .group_by(func.date_trunc('minute', OrderItem.created_at)) \
        .order_by(func.date_trunc('minute', OrderItem.created_at)) \
        .limit(15) \
        .all()
    data_avg_wait_times = []
    labels_avg_wait_times = []
    for wait_time in avg_wait_times_per_minute:
        seconds = wait_time[1].seconds % 60
        minutes = round((wait_time[1].seconds / 60) % 60, 2)
        hours = (wait_time[1].seconds // 3600) % 24
        days = wait_time[1].days

        labels_avg_wait_times.append(wait_time[0].strftime("%H:%M:%S"))
        data_avg_wait_times.append(minutes)
    legend_avg_wait_times = 'Avg. Time To Completion'
    labels_avg_wait_times = labels_avg_wait_times
    values_avg_wait_times = data_avg_wait_times
    return labels_avg_wait_times, legend_avg_wait_times, values_avg_wait_times


def get_popular_item():
    most_popular_item = OrderItem.query.with_entities(OrderItem.name,
                                                      func.count(OrderItem.id).label('total')).group_by(
        OrderItem.name).order_by(desc('total')).limit(1).all()
    if len(most_popular_item) == 0:
        most_popular_item = 'Chopping onions...'
    else:
        most_popular_item = most_popular_item[0].name
    return most_popular_item


def get_popular_service():
    most_popular_service = CssOrder.query.with_entities(CssOrder.service,
                                                        func.count(CssOrder.id).label('total')).group_by(
        CssOrder.service).order_by(desc('total')).limit(1).all()
    if len(most_popular_service) == 0:
        most_popular_service = 'Turning on the stove...'
    else:
        most_popular_service = most_popular_service[0].service
    return most_popular_service


def get_last_few_orders(last_orders):
    last_few_orders = CssOrder.query.filter(or_(
        CssOrder.status == CssConstants.ORDER_IN_PROGRESS, CssOrder.status == CssConstants.ORDER_COMPLETE)) \
        .order_by(CssOrder.created_at.desc()) \
        .limit(last_orders) \
        .all()
    last_few_orders_list = []
    for order in last_few_orders:
        percent_completion = round((order.completed_items_in_order / float(order.items_in_order)) * 100, 2)
        last_few_orders_list.append(
            {"id": order.id, "name": order.name, "status": order.status, "percent_completion": str(percent_completion),
             "service": order.service, "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S")})
    return last_few_orders_list


def get_items_per_minute():
    items_per_minute = OrderItem.query.with_entities(func.date_trunc('minute', OrderItem.created_at),
                                                     func.count(OrderItem.id)).group_by(
        func.date_trunc('minute', OrderItem.created_at)).order_by(
        func.date_trunc('minute', OrderItem.created_at)) \
        .limit(15) \
        .all()
    data_items_per_minute = []
    labels_items_per_minute = []
    for item in items_per_minute:
        labels_items_per_minute.append(item[0].strftime("%H:%M:%S"))
        data_items_per_minute.append(item[1])
    legend_items_per_minute = 'Total received'
    labels_items_per_minute = labels_items_per_minute
    values_items_per_minute = data_items_per_minute
    return labels_items_per_minute, legend_items_per_minute, values_items_per_minute


def get_items_per_minute_complete():
    items_per_minute_complete = OrderItem.query \
        .with_entities(func.date_trunc('minute', OrderItem.completed_at), func.count(OrderItem.id)) \
        .filter(OrderItem.status == CssConstants.ORDER_COMPLETE) \
        .group_by(func.date_trunc('minute', OrderItem.completed_at)) \
        .order_by(func.date_trunc('minute', OrderItem.completed_at)) \
        .limit(15) \
        .all()
    data_items_per_minute_complete = []
    labels_items_per_minute_complete = []
    for item in items_per_minute_complete:
        labels_items_per_minute_complete.append(item[0].strftime("%H:%M:%S"))
        data_items_per_minute_complete.append(item[1])
    legend_items_per_minute_complete = 'Completed'
    labels_items_per_minute_complete = labels_items_per_minute_complete
    values_items_per_minute_complete = data_items_per_minute_complete
    return labels_items_per_minute_complete, legend_items_per_minute_complete, values_items_per_minute_complete


def get_orders_per_minute():
    orders_per_minute = CssOrder.query.with_entities(func.date_trunc('minute', CssOrder.created_at),
                                                     func.count(CssOrder.id)).group_by(
        func.date_trunc('minute', CssOrder.created_at)).order_by(
        func.date_trunc('minute', CssOrder.created_at)) \
        .limit(15) \
        .all()
    data_orders_per_minute = []
    labels_orders_per_minute = []
    for order in orders_per_minute:
        labels_orders_per_minute.append(order[0].strftime("%H:%M:%S"))
        data_orders_per_minute.append(order[1])
    legend_orders_per_minute = 'Total received'
    labels_orders_per_minute = labels_orders_per_minute
    values_orders_per_minute = data_orders_per_minute
    return labels_orders_per_minute, legend_orders_per_minute, values_orders_per_minute


def get_orders_per_minute_complete():
    orders_per_minute_complete = CssOrder.query \
        .with_entities(func.date_trunc('minute', CssOrder.completed_at), func.count(CssOrder.id)) \
        .filter(CssOrder.status == CssConstants.ORDER_COMPLETE) \
        .group_by(func.date_trunc('minute', CssOrder.completed_at)) \
        .order_by(func.date_trunc('minute', CssOrder.completed_at)) \
        .limit(15) \
        .all()
    data_orders_per_minute_complete = []
    labels_orders_per_minute_complete = []
    for order in orders_per_minute_complete:
        labels_orders_per_minute_complete.append(order[0].strftime("%H:%M:%S"))
        data_orders_per_minute_complete.append(order[1])
    legend_orders_per_minute_complete = 'Completed'
    labels_orders_per_minute_complete = labels_orders_per_minute_complete
    values_orders_per_minute_complete = data_orders_per_minute_complete
    return labels_orders_per_minute_complete, legend_orders_per_minute_complete, values_orders_per_minute_complete


@blueprint.route('/<template>')
def route_template(template):
    # if not current_user.is_authenticated:
    #     return redirect(url_for('base_blueprint.login'))

    try:

        return render_template(template + '.html')

    except TemplateNotFound:
        return render_template('error-404.html'), 404

    except:
        return render_template('error-500.html'), 500

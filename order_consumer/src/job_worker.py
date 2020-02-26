from time import sleep
from datetime import datetime
from menu_item import MenuItem
from css_order import CssOrder
from order_item import OrderItem
from css_constants import CssConstants
from wsgi import db


class JobWorker:
    @classmethod
    def process(cls, order_id):
        print(">>>>>>>>>>>>>>> RQ Processing item {}".format(order_id))
        # menu_items = MenuItem.query.filter_by(id=order_id)
        # print(menu_items)

    @classmethod
    def process_item(cls, order_id, item_id, quantity, cook_time, name):
        # item.id, item['quantity'], menu_item.cook_time, menu_item.name
        print("<<<<<< Menu item {}: {}, {}, {}, ".format(item_id, name, quantity, cook_time))
        total_cook_time = int(quantity) * int(cook_time)
        print("Cooking for {}...".format(total_cook_time))
        sleep(total_cook_time / 100)
        print("{} x {} ready".format(quantity, name))

        # css_order = CssOrder.query.filter_by(id=order_id).first()
        order_item = OrderItem.query.filter_by(id=item_id).with_for_update().first()
        order_item.status = CssConstants.ORDER_COMPLETE
        order_item.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.add(order_item)
        db.session.commit()

        # css_order = CssOrder.query.filter_by(id=order_id).first()
        css_order = CssOrder.query.filter_by(id=order_id).with_for_update().first()
        css_order.completed_items_in_order = CssOrder.completed_items_in_order + quantity
        db.session.add(css_order)
        db.session.commit()

        css_order = CssOrder.query.filter_by(id=order_id).first()

        print("Completed orders are >>>>> {}".format(css_order.completed_items_in_order))
        print("Received orders were >>>>> {}".format(css_order.items_in_order))
        if css_order.completed_items_in_order == css_order.items_in_order:
            print("THIS ORDER IS COMPLETE YAY!".format(css_order.completed_items_in_order))
            print("This is ready for {}".format(css_order.name))
            css_order.status = CssConstants.ORDER_COMPLETE
            css_order.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.session.add(css_order)
            db.session.commit()

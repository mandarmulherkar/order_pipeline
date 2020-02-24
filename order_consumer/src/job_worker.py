from time import sleep
from menu_item import MenuItem
from css_order import CssOrder
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
        css_order = CssOrder.query.filter_by(id=order_id).with_for_update().first()
        css_order.completed_items_in_order = CssOrder.completed_items_in_order + 1
        db.session.add(css_order)
        db.session.commit()

        css_order = CssOrder.query.filter_by(id=order_id).with_for_update().first()

        print("Completed orders are >>>>> {}".format(css_order.completed_items_in_order))
        print("This is ready for {}".format(css_order.name))

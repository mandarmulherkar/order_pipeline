from time import sleep


class JobWorker:
    @classmethod
    def process(cls, order_id):
        print(">>>>>>>>>>>>>>> RQ Processing item {}".format(order_id))
        # menu_items = MenuItem.query.filter_by(id=order_id)
        # print(menu_items)

    @classmethod
    def process_item(cls, item_id, quantity, cook_time, name):
        # item.id, item['quantity'], menu_item.cook_time, menu_item.name
        print("<<<<<< Menu item {}: {}, {}, {}, ".format(item_id, name, quantity, cook_time))
        total_cook_time = int(quantity) * int(cook_time)
        print("Cooking for {}...".format(total_cook_time))
        sleep(total_cook_time / 100)
        print("{} x {} ready!".format(quantity, name))

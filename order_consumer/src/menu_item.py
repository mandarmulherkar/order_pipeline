from wsgi import db


class MenuItem(db.Model):
    __tablename__ = 'menu_item'

    id = db.Column(db.Integer, primary_key=True)
    cook_time = db.Column(db.Integer)
    name = db.Column(db.String())

    def __init__(self, name, cook_time):
        self.cook_time = cook_time
        self.name = name

    def __repr__(self):
        return '<name: {}, cook_time {}>'.format(self.name, self.cook_time)

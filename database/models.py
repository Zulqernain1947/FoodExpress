from .dbinitialization import db

class User(db.Document):
    userName=db.StringField(required=True)
    password = db.StringField(required=True)
    email = db.StringField(required=True)
    userType = db.StringField(required=True)

class MenuItem(db.EmbeddedDocument):
    itemName = db.StringField(required=True)
    price = db.FloatField(required=True)
    quantity = db.IntField(required=True)


class Restaurant(db.Document):
    ownerName = db.StringField(required=True)
    name = db.StringField(required=True)
    menu = db.ListField(db.EmbeddedDocumentField(MenuItem), required=True)
    speciality = db.StringField(required=True)
    contact = db.StringField(required=True)
    address = db.StringField(required=True)
    TotalIncome = db.FloatField()

class Order(db.Document):
    name = db.StringField(required=True)
    items = db.ListField(db.EmbeddedDocumentField(MenuItem), required=True)
    totalPrice = db.FloatField(required=True)
    discount = db.FloatField(required=True)
    deliveryTime = db.StringField(required=True)
    orderStatus = db.StringField(required=True)
    address = db.StringField(required=True)
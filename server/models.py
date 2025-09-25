from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# --------------------------
# Database Setup
# --------------------------
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# --------------------------
# Models
# --------------------------

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # relationships
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    # association proxy
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    # serialization rules
    serialize_rules = ("-restaurant_pizzas.restaurant",)

    def to_dict(self, only=None):
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "restaurant_pizzas": [rp.to_dict() for rp in self.restaurant_pizzas],
        }
        if only:
            return {k: data[k] for k in only if k in data}
        return data

    def __repr__(self):
        return f"<Restaurant {self.id}: {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # relationships
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan"
    )

    # association proxy
    restaurants = association_proxy("restaurant_pizzas", "restaurant")

    # serialization rules
    serialize_rules = ("-restaurant_pizzas.pizza",)

    def to_dict(self, only=None):
        data = {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients,
        }
        if only:
            return {k: data[k] for k in only if k in data}
        return data

    def __repr__(self):
        return f"<Pizza {self.id}: {self.name}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # foreign keys
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))

    # relationships
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    # serialization rules
    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")

    # validations
    @validates("price")
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30")
        return value

    def to_dict(self, only=None):
        data = {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id,
            "pizza": self.pizza.to_dict(only=("id", "name", "ingredients")) if self.pizza else None,
        }
        if only:
            return {k: data[k] for k in only if k in data}
        return data

    def __repr__(self):
        return f"<RestaurantPizza id={self.id}, price=${self.price}>"

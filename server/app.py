#!/usr/bin/env python3
import os
from flask import Flask, jsonify, request
from flask_restful import Api
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza

# --------------------------
# App & Database Setup
# --------------------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize the database
db.init_app(app)

# Setup migrations
migrate = Migrate(app, db)

# Setup Flask-RESTful API
api = Api(app)

# --------------------------
# Routes
# --------------------------

@app.route("/")
def index():
    return "<h1>Code Challenge</h1>"

# ✅ GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([r.to_dict(only=("id", "name", "address")) for r in restaurants])

# ✅ GET /restaurants/<id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    return jsonify(
        restaurant.to_dict(
            only=("id", "name", "address", "restaurant_pizzas")
        )
    )

# ✅ DELETE /restaurants/<id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()
    return "", 204

# ✅ GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([p.to_dict(only=("id", "name", "ingredients")) for p in pizzas])

# ✅ POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json() or {}

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if price is None or pizza_id is None or restaurant_id is None:
        return jsonify({"errors": ["Missing required fields"]}), 400

    if not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        return jsonify({"error": "Pizza or Restaurant not found"}), 404

    try:
        rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(rp)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400

    # ✅ Include both pizza and restaurant in response
    response_data = {
        "id": rp.id,
        "price": rp.price,
        "pizza_id": rp.pizza_id,
        "restaurant_id": rp.restaurant_id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients,
        },
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
        },
    }

    return jsonify(response_data), 201

# --------------------------
# Expose app for Flask CLI
# --------------------------
application = app

if __name__ == "__main__":
    app.run(port=5555, debug=True)

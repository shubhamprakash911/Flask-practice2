from flask import Flask, request, jsonify,render_template
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

import openai
from openai.error import RateLimitError


# Load environment variables from the .env file
load_dotenv()



app = Flask(__name__)

mongoUrl=os.environ.get("mongoUrl")
client = MongoClient(mongoUrl)
db = client['flaskDB']
menu_collection = db["menu"]
orders_collection = db["orders"]

# chatbot
openai.api_key = os.getenv("OPENAI_API_KEY")
print(os.getenv("OPENAI_API_KEY"))
@app.route('/chat')
def home():
    return render_template('chat.html')

@app.route('/gpt4', methods=['GET', 'POST'])
def gpt4():
    user_input = request.args.get('user_input') if request.method == 'GET' else request.form['user_input']
    messages = [{"role": "user", "content": user_input},
                {"role": "assistant", "content": 'take a role of online food delivery chatbot and resolve the query of customer'}]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        content = response.choices[0].message["content"]
    except RateLimitError:
        content = "The server is experiencing a high volume of requests. Please try again later."

    return jsonify(content=content)


# chatbot end


# Load menu data from MongoDB collection
def load_menu():
    return list(menu_collection.find({},{'_id':0}))

# Save menu data to MongoDB collection
def save_menu(menu):
    if not menu:
        return
    menu_collection.delete_many({})  # Clear existing data
    menu_collection.insert_many(menu)

# Load order data from MongoDB collection
def load_orders():
    return list(orders_collection.find({},{'_id':0}))

# Save order data to MongoDB collection
def save_orders(orders):
    orders_collection.delete_many({})  # Clear existing data
    orders_collection.insert_many(orders)



@app.route('/')
def index():
   return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


# Get all dishes from the menu
@app.route('/menu', methods=['GET'])
def get_menu():
    menu = load_menu()
    return jsonify(menu)

# Add a new dish to the menu
@app.route('/menu', methods=['POST'])
def add_dish():
    menu = load_menu()
    dish = request.json

    # Assign a new dish ID
    dish_id = len(menu) + 1
    dish['id'] = dish_id

    menu.append(dish)
    save_menu(menu)

    return jsonify({'message': 'Dish added successfully'})

# Update the availability of a dish
@app.route('/menu', methods=['PUT'])
def update_dish_availability():

    menu = load_menu()
    dish_id=int(request.json['id'])

    for dish in menu:
        if dish['id'] == dish_id:
            dish['availability'] = 'no' if dish['availability'] =='yes' else 'yes'
            print(dish)
            save_menu(menu)
            return jsonify({'message': 'Dish availability updated successfully'})

    return jsonify({'message': 'Dish not found'})

# Remove a dish from the menu
@app.route('/menu', methods=['DELETE'])
def remove_dish():
    menu = load_menu()
    dish_id=int(request.json['id'])

    for dish in menu:
        if dish['id'] == dish_id:
            menu.remove(dish)
            save_menu(menu)
            return jsonify({'message': 'Dish removed successfully'})

    return jsonify({'message': 'Dish not found'})

# Take a new order
@app.route('/orders', methods=['POST'])
def take_order():
    menu = load_menu()
    orders = load_orders()
    order = request.json

    # Assign a new order ID
    order_id = len(orders) + 1
    order['id'] = order_id

    # Check if each dish is available
    for dish_id in order['dishes']:
        dish_available = False
        for dish in menu:
            if dish['id'] == dish_id and dish['availability'] == 'yes':
                dish_available = True
                break
        if not dish_available:
            return jsonify({'message': 'One or more dishes are not available'})

    order['status'] = 'received'
    orders.append(order)
    save_orders(orders)

    return jsonify({'message': 'Order taken successfully'})

# Update the status of an order
@app.route('/orders', methods=['PUT'])
def update_order_status():
    orders = load_orders()
    order_id=int(request.json['order_id'])
    for order in orders:
        if order['id'] == order_id:
            order['status'] = request.json['status']
            save_orders(orders)
            return jsonify({'message': 'Order status updated successfully'})

    return jsonify({'message': 'Order not found'})

# Get all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = load_orders()
    return jsonify(orders)
    # return render_template("admin.html",orders=jsonify(orders))

if __name__ == '__main__':
    app.run(debug=True)

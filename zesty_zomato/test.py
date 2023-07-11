import pytest
from flask import json
from app import app, load_menu, save_menu, load_orders, save_orders,render_template


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode("utf-8") == render_template('index.html')



def test_admin_route(client):
    response = client.get('/admin')
    assert response.status_code == 200
    assert response.data.decode("utf-8") == render_template('admin.html')

def test_get_menu(client):
    # Add some dishes to the menu
    menu = [
        {'id': 1, 'name': 'Dish 1', 'availability': 'yes'},
        {'id': 2, 'name': 'Dish 2', 'availability': 'yes'}
    ]
    save_menu(menu)

    # Send a GET request to the /menu endpoint
    response = client.get('/menu')

    # Validate the response
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    response_data = json.loads(response.data)
    assert len(response_data) == len(menu)
    for i, dish in enumerate(response_data):
        assert dish['id'] == menu[i]['id']
        assert dish['name'] == menu[i]['name']
        assert dish['availability'] == menu[i]['availability']


def test_add_dish(client):
    # Send a POST request to the /menu endpoint to add a new dish
    response = client.post('/menu', json={'name': 'New Dish', 'availability': 'yes'})

    # Validate the response
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert json.loads(response.data) == {'message': 'Dish added successfully'}


def test_update_dish_availability(client):
    # Add a dish to the menu
    menu = [{'id': 1, 'name': 'Dish 1', 'availability': 'yes'}]
    save_menu(menu)

    # Send a PUT request to the /menu endpoint to update the availability of the dish
    response = client.put('/menu', json={'id': 1})

    # Validate the response
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert json.loads(response.data) == {'message': 'Dish availability updated successfully'}

    # Verify that the dish availability has been updated
    updated_menu = load_menu()
    assert updated_menu[0]['availability'] == 'no'


def test_remove_dish(client):
    # Add a dish to the menu
    menu = [{'id': 1, 'name': 'Dish 1', 'availability': 'yes'}]
    save_menu(menu)


    # Send a DELETE request to the /menu endpoint to remove the dish
    response = client.delete('/menu', json={'id': 1})

    # Validate the response
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert json.loads(response.data) == {'message': 'Dish removed successfully'}

    # Verify that the dish has been removed from the menu





def test_take_order(client):
    # Add some dishes to the menu
    menu = [
        {'id': 1, 'name': 'Dish 1', 'availability': 'yes'},
        {'id': 2, 'name': 'Dish 2', 'availability': 'yes'}
    ]
    save_menu(menu)

    # Send a POST request to the /orders endpoint to take a new order
    order = {'dishes': [1, 2], 'status': 'received'}
    response = client.post('/orders', json=order)

    # Validate the response
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert json.loads(response.data) == {'message': 'Order taken successfully'}


def test_update_order_status(client):
    # Add an order
    orders = [{'id': 1, 'dishes': [1, 2], 'status': 'received'}]
    save_orders(orders)

    # Send a PUT request to the /orders endpoint to update the status of the order
    response = client.put('/orders', json={'order_id': 1, 'status': 'completed'})

    # Validate the response
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert json.loads(response.data) == {'message': 'Order status updated successfully'}

    # Verify that the order status has been updated
    updated_orders = load_orders()
    assert updated_orders[0]['status'] == 'completed'


def test_get_orders(client):
    # Add some orders
    orders = [
        {'id': 1, 'dishes': [1, 2], 'status': 'received'},
        {'id': 2, 'dishes': [2, 3], 'status': 'completed'}
    ]
    save_orders(orders)

    # Send a GET request to the /orders endpoint
    response = client.get('/orders')

    # Validate the response
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    response_data = json.loads(response.data)
    assert len(response_data) == len(orders)
    for i, order in enumerate(response_data):
        assert order['id'] == orders[i]['id']
        assert order['dishes'] == orders[i]['dishes']
        assert order['status'] == orders[i]['status']



# Run the tests
if __name__ == '__main__':
    pytest.main()

import pytest
import json
from ..app import app, db

# Create a fixture for the app
@pytest.fixture
def client():
    # Create a test client
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
    app.secret_key = 'test_secret_key'  # Ensure a secret key is set for testing
    
    # Initialize the app and the database
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create database tables
        yield client  # Allow the test to run


# Test User Registration
def test_register(client):
    response = client.post('/register', json={
        "username": "testuser",
        "password": "testpassword"
    })
    json_data = json.loads(response.data)
    assert response.status_code == 201
    assert json_data['message'] == 'User is added'


# Test User Login
def test_login(client):
    # First, register a user
    client.post('/register', json={
        "username": "testuser",
        "password": "testpassword"
    })

    # Now login with the same user
    response = client.post('/login', json={
        "username": "testuser",
        "password": "testpassword"
    })
    json_data = json.loads(response.data)
    assert response.status_code == 200
    assert json_data['message'] == 'Logged in successfully.'


# Test Get Current User (requires login)
def test_get_current_user(client):
    # Register and login the user first
    client.post('/register', json={
        "username": "testuser",
        "password": "testpassword"
    })
    client.post('/login', json={
        "username": "testuser",
        "password": "testpassword"
    })

    response = client.get('/currentUser')
    json_data = json.loads(response.data)
    assert response.status_code == 200
    assert json_data['username'] == 'testuser'


# Test Adding Expense
def test_add_expense(client):
    # Register and login the user first
    client.post('/register', json={
        "username": "testuser",
        "password": "testpassword"
    })
    client.post('/login', json={
        "username": "testuser",
        "password": "testpassword"
    })

    response = client.post('/addExpense', json={
        "user": "1",   # Ensure this matches the user_id being tested
        "amount": 100,
        "currency": "USD",
        "date": "2023-01-01",
        "description": "Groceries"
        
        
    })
    json_data = json.loads(response.data)
    assert response.status_code == 201
    assert json_data['message'] == 'Expense added'


# Test Error Handling for Invalid Expense Request
def test_add_expense_invalid_currency(client):
    # Register and login the user first
    client.post('/register', json={
        "username": "testuser",
        "password": "testpassword"
    })
    client.post('/login', json={
        "username": "testuser",
        "password": "testpassword"
    })

    response = client.post('/addExpense', json={
        "user": "1",
        "amount": 100,
        "currency": "INVALID_CURRENCY",  # Test with an invalid currency
        "date": "2023-01-01",
        "description": "Groceries"
    })
    json_data = json.loads(response.data)
    assert response.status_code == 404  # Expecting a not found error due to currency check
    assert json_data['error'] == 'Selected currency not available'


# Test Error Handling for Missing User
def test_add_expense_missing_user(client):
    response = client.post('/addExpense', json={
        "amount": 100,
        "currency": "USD",
        "date": "2023-01-01",
        "description": "Groceries"
    })
    json_data = json.loads(response.data)
    assert response.status_code == 404
    assert json_data['error'] == 'User not found'

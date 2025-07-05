import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'DNS Update Service'

def test_update_dns_missing_data(client):
    """Test DNS update endpoint with missing data."""
    response = client.post('/update-dns')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'No IP address provided' in data['error']

def test_update_dns_invalid_content_type(client):
    """Test DNS update endpoint with invalid content type."""
    response = client.post('/update-dns', 
                          data=json.dumps({'ip': '192.168.1.100'}),
                          content_type='application/json')
    assert response.status_code == 400

def test_update_dns_valid_request(client):
    """Test DNS update endpoint with valid request."""
    # Mock the AWS client to avoid actual AWS calls during testing
    import app
    app.route53_client = None  # This will trigger the "not available" error
    
    response = client.post('/update-dns',
                          data='192.168.1.100',
                          content_type='text/plain')
    assert response.status_code == 500
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'AWS Route53 client not available' in data['error']

def test_invalid_endpoint(client):
    """Test invalid endpoint returns 404."""
    response = client.get('/invalid-endpoint')
    assert response.status_code == 404 
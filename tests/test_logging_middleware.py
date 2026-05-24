from fastapi.testclient import TestClient

from app.main import app



def test_request_id_header_is_returned() -> None:
    client = TestClient(app)

    response = client.get('/health', headers={'X-Request-ID': 'test-request-id'})

    assert response.status_code == 200
    assert response.headers['X-Request-ID'] == 'test-request-id'



def test_request_id_header_is_returned_on_server_error() -> None:
    test_path = '/__test-error'

    @app.get(test_path)
    def raise_test_error():
        raise RuntimeError('test error')

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get(test_path, headers={'X-Request-ID': 'error-request-id'})

    assert response.status_code == 500
    assert response.headers['X-Request-ID'] == 'error-request-id'
    assert response.json()['request_id'] == 'error-request-id'

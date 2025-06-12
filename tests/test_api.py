"""Tests for API endpoints"""

def test_get_alerts(client, db_init):
    """
    Test for GET /alerts endpoint
    """
    # GET request
    response = client.get('/alerts')

    # check that response code is 200 and response content is JSON
    assert response.status_code == 200
    assert response.content_type == 'application/json'

    # check format of data in response body
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2

    # check content of data in resposne body
    assert data[0]['user_id'] == 'test_user_2'
    assert data[0]['stress_score'] == 0.75
    assert '2025-06-11T13:00:00Z' in data[0]['timestamp']

    assert data[1]['user_id'] == 'test_user_1'
    assert data[1]['stress_score'] == 0.85
    assert '2025-06-11T12:00:00Z' in data[1]['timestamp']
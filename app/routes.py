from flask import Blueprint, jsonify, Response
from app.db import get_db
import json

# app blueprint
alerts_bp = Blueprint('api', __name__)

@alerts_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """
    Get high stress flagged users from DB
    """
    # connect to db
    conn = get_db()
    cur = conn.cursor()

    # get data from db(optional: sort by most recent timestamp)
    query = 'SELECT user_id, stress_score, "timestamp" FROM high_stress_users;'
    cur.execute(query)
    db_alerts = cur.fetchall()
    cur.close()

    # convert to json for api response body
    alerts_list = []
    for alert in db_alerts:
        user_id = alert[0]
        stress_score = int(alert[1])/100
        timestamp = alert[2].strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        alerts_list.append({
            "user_id": user_id,
            "stress_score": stress_score,
            "timestamp": timestamp
        })
    
    # format json body output(to match spec)
    json_str = json.dumps(alerts_list)
    return Response(json_str, content_type='application/json')

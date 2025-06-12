# ML Agentic Engineer(v1)
Python-based agentic pipeline that simulates live ingestion via Flask CLI and detects students with stress level above thresold(70 for this case) using heuristic rule and stores flagged users in a PostgreSQL database. Alerts can be accessed via a Flask API

## Project Features
- Python Agent: script triggered by Flask CLI that reads from university_mental_health_iot_dataset.csv and stores flagged users in a database
- PostgreSQL: alerts stored in local database within a Docker container
- Flask API: exposes endpoint (/alerts) to return flagged users
- Test Suite: unit and integration tests

## Project Structure
````bash
.
├── app/                   # Flask App
│   ├── __init__.py        # App factory setup
│   ├── db.py              # DB connection
│   ├── routes.py          # /alerts endpoint
│   └── stress_detector.py # Agent
├── data/                  # Csv files
├── db/                    # DB schema
│   └── init.sql
├── tests/                 # Unit and integration tests
├── config.py              # Config for app and testing
├── run.py                 # Starts local Flask server
├── requirements.txt    
└── README.md           
````

## Local Development Setup
**Prerequisites:**
- Python 3.11.*
- Docker and Docker Desktop

**Installation**
1. Clone repository
````bash
git clone https://github.com/igorstelnykh/MLAgenticEngineer.git
cd MLAgenticEngineer
````
2. Python virtual environment setup
- MacOS/Linux/WSL(I used WSL for dev)
````bash
python3.11 -m venv venv
source venv/bin/activate
````
- Windows(powershell)
````bash
\path_to_python311\python.exe -m venv venv
.\venv\Scripts\activate.ps1
````
3. Install Python packages(with venv activated)
````bash
pip install -r requirements.txt
````
4. Start PostgreSQL Docker container
````bash
docker run --name stress-db -e POSTGRES_PASSWORD=example -e POSTGRES_DB=stress_alerts -p 5432:5432 -d postgres
````
5. Create database schema
````bash
docker exec -i stress-db psql -U postgres -d stress_alerts < db/init.sql
````

## Run Instructions
Note: make sure venv is activated for all of these
1. Run agent(read from CSV and write to DB)
````bash
flask run-agent data/university_mental_health_iot_dataset.csv
````
2. Start Flask server
Note: check console for server host and port, it should be http://localhost:5001
````bash
python run.py
````
3. Query API endpoints
* GET /alerts : returns info about high-stress students
* GET /health : server health check

## Testing Instructions
Make sure that the Docker container is running(check docker ps -a and if stress-db container isn't running then run docker start stress-db). Exectute command below from project root(runs both unit and integration tests)
````bash
pytest
````

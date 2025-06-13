# ML Agentic Engineer(v1)
Serverless application designed with AWS SAM that implements a Python-based agent pipeline. The agent processes data from a CSV and detects students with stress level above threshold(70 for this case) using heuristic rule and stores flagged users in a PostgreSQL database. Alerts can be accessed via an API endpoint. This application is designed to be run and tested locally without needing an AWS account.

## Project Features
- Serverless Architecture: uses AWS Lambda amd API Gateway defined in an AWS SAM template file
- Python Agent: Lambda function(RunAgentFunction) that can be triggered using SAM CLI that reads from university_mental_health_iot_dataset.csv and stores flagged users in a database
- PostgreSQL: alerts stored in local database within a Docker container
- REST API: Lambda function(GetAlertsFunction) retrieves flagged users from DB by exposing GET /alerts endpoint
- Test Suite: unit tests for Lambda functions using pytest

## Project Structure
````bash
.
├── lambda_functions/           # Lambda functions with handlers and requirements
│   ├── get_alerts/             # get_alerts lambda triggered by /alerts
│   │   ├── app.py
│   │   └── requirements.txt
│   └── run_agent/              # run_agent lambda manually triggered
│       ├── app.py
|       ├── requirements.txt
│       └── university_mental_health_iot_dataset.csv
├── db/                         # DB schema      
│   └── init.sql
├── tests/                      # unit tests for lambda functions
│   ├── test_get_alerts.py
│   └── test_run_agent.py
├── event.json                  # event arg for run_agent lambda
├── pytest.ini                  # pytest config
├── README.md
├── requirements.txt
└── template.yaml               # SAM template
````

## AWS Overview
Project implementation consists of two AWS Lambda functions:
1. RunAgentFunction: contains Python agent logic. In a production environment it can be triggered in time intervals(cron) or another event like a file upload to an S3 bucket. For local testing, it is triggered manually via SAM CLI and given the path to a local CSV file(in the Lambda functions directory)
2. GetAlertsFunction: triggered by an HTTP GET request to /alerts from the AWS API Gateway. Function queries the PostgreSQL database and returns all flagged users

## Local Development Setup
**Prerequisites:**
- Python 3.11+
- Docker and Docker Desktop
- AWS CLI
- AWS SAM CLI
Note: no AWS account is required for locally using and testing this application with AWS CLI and AWS SAM CLI

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

If container doesn't exist
````bash
docker run --name stress-db -e POSTGRES_PASSWORD=example -e POSTGRES_DB=stress_alerts -p 5432:5432 -d postgres
````
If container exists
````bash
docker start stress-db
````
5. Create database schema
````bash
docker exec -i stress-db psql -U postgres -d stress_alerts < db/init.sql
````

## Run Instructions
Make sure virtual environment is activated!! Should say (venv) on the left side of the terminal line
1. Build application
````bash
sam build
````
2. Create event.json in lambda_functions/run_agent directory, paste name of CSV in the value for filepath, save
````bash
{
  "filepath": "university_mental_health_iot_dataset.csv"
}
````
3. Run Lambda Agent
````bash
sam local invoke RunAgentFunction --event event.json
````
4. Start local API server(for API gateway to trigger GetAlertsFunction)
````bash
sam local start-api
````
Check the terminal output for the URL

5. Query endpoint to see data
- GET /alerts

## Testing Instructions
Make sure that the Docker container is running(check docker ps -a and if stress-db container isn't running then run docker start stress-db). Make sure virtual environment is activated and run command below from project root
````bash
pytest
````

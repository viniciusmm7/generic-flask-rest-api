#!/usr/bin/env python3
from os import getenv
from flask import Flask, request, jsonify
import mysql.connector
import boto3
import logging
import time
from botocore.exceptions import ClientError, NoCredentialsError


def get_secret():
    secret_name = "api/mysql/credentials"
    region_name = "us-east-1"
    
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    
    return eval(get_secret_value_response['SecretString'])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

try:
    log_client = boto3.client('logs', region_name='us-east-1')
except NoCredentialsError:
    logger.error('AWS credentials not found. Please configure credentials.')
    
LOG_GROUP = '/flask-app-vmm/logs'
LOG_STREAM = getenv('INSTANCE_ID')

async def push_logs_to_cloudwatch(log_message):
    try:
        log_client.put_log_events(
            logGroupName=LOG_GROUP,
            logStreamName=LOG_STREAM,
            logEvents=[
                {
                    'timestamp': int(round(time.time() * 1000)),
                    'message': log_message
                },
            ],
        )
        
    except Exception as e:
        logger.error(f'Error sending logs to CloudWatch: {e}')

app = Flask(__name__)

secret = get_secret()

db_config = {
    "host": getenv("DB_HOST"),
    "user": secret['username'],
    "password": secret['password'],
    "database": secret['name'],
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

def create_users_table():
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255)
        )
        """
    )

def add_mock_data():
    cursor.execute(
        """
        INSERT INTO users (name, email) VALUES
            ("John Doe", "johndoe@email.com"),
            ("Jane Doe", "janedoe@email.com"),
            ("John Smith", "johnsmith@email.com")
        """
    )

@app.route("/", methods=["GET"])
def get_index():
    return jsonify({"message": "Connected successfully!"})

@app.route("/users", methods=["GET"])
def get_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify({"users": users})

@app.route("/users/<int:user_id>", methods=["GET"])
def get_users(user_id):
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return jsonify({"user": user})
    else:
        return jsonify({"message": "User not found"}), 404

@app.route("/users", methods=["POST"])
def create_user():
    new_user = request.json
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (new_user["name"], new_user["email"]))
    conn.commit()
    return jsonify({"message": "User created successfully"}), 201

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    updated_user = request.json
    cursor.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (updated_user["name"], updated_user["email"], user_id))
    conn.commit()
    return jsonify({"message": "User updated successfully"})

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    return jsonify({"message": "User deleted successfully"})

if __name__ == "__main__":
    create_users_table()
    add_mock_data()
    app.run(debug=True)
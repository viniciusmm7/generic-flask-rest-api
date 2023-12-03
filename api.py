#!/usr/bin/env python3
from os import getenv
from flask import Flask, request, jsonify
import mysql.connector


app = Flask(__name__)

db_config = {
    "host": getenv("DB_HOST"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
    "database": getenv("DB_NAME"),
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
#!/usr/bin/env python
from flask import Flask, request, jsonify
import mysql.connector


app = Flask(__name__)
db_config = {
    "host": "localhost",
    "user": "admin",
    "password": "12345678",
    "database": "vmm",
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

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
    app.run(debug=True)
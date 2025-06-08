import json
import os

DB_PATH = "db/users.json"

# Make sure the 'db' directory and JSON file exist
def initialize_json_db():
    if not os.path.exists("db"):
        os.makedirs("db")
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({}, f)

# Read all users
def load_users():
    with open(DB_PATH, "r") as f:
        return json.load(f)

# Write all users
def save_users(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

# Add new user
def add_user(username, password, email):
    users = load_users()
    if username in users:
        return False, "Username already exists!"

    users[username] = {
        "password": password,
        "email": email,
        "emergency_contact": "",
        "contacts": {
            "1": {"number": "", "code": ""},
            "2": {"number": "", "code": ""},
            "3": {"number": "", "code": ""}
        }
    }
    save_users(users)
    return True, "User created successfully!"

# Verify login
def verify_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return True, username
    return False, "Invalid credentials!"

# Update user profile
def update_user_profile(username, password=None, email=None, emergency_contact=None):
    users = load_users()
    if username in users:
        if password:
            users[username]["password"] = password
        if email:
            users[username]["email"] = email
        if emergency_contact:
            users[username]["emergency_contact"] = emergency_contact
        save_users(users)
        return True
    return False

# Update emergency contacts
def update_emergency_contacts(username, contacts):
    users = load_users()
    if username in users:
        users[username]["contacts"] = contacts
        save_users(users)
        return True
    return False

# Load contacts
def load_emergency_contacts(username):
    users = load_users()
    return users.get(username, {}).get("contacts", {})

# Initialize the DB on import
initialize_json_db()

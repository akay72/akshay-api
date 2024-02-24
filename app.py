from flask import Flask, request, jsonify
import threading
import main  # Import your scraping script
import uuid
from email_content import generate_outreach_email
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import json

app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
    "methods": ["GET", "POST", "PUT", "DELETE"]
}})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)  # Heroku DATABASE_URL fix
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    result = db.Column(db.Text, nullable=True)

    def __init__(self, task_id, status, result=None):
        self.task_id = task_id
        self.status = status
        self.result = result

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

def update_task_status_and_result(task_id, status, result=None):
    task = Task.query.filter_by(task_id=task_id).first()
    if task:
        task.status = status
        if result is not None:
            task.result = json.dumps(result)  # Serialize result to JSON string
        db.session.commit()

def scrape_yellow_pages_task(searchterm, location, leadid, task_id):
    try:
        result = []
        for progress_update in main.scrape_yellow_pages(searchterm, location, leadid):
            result.append(progress_update)
        update_task_status_and_result(task_id, 'success', result)
    except Exception as e:
        update_task_status_and_result(task_id, 'error', {'message': str(e)})

def find_contacts_task(website_url, task_id):
    try:
        result = []
        for progress_update in main.find_contacts(website_url):
            result.append(progress_update)
        update_task_status_and_result(task_id, 'success', result)
    except Exception as e:
        update_task_status_and_result(task_id, 'error', {'message': str(e)})

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters"}), 200

    task_id = str(uuid.uuid4())
    new_task = Task(task_id=task_id, status='in progress')
    db.session.add(new_task)
    db.session.commit()

    threading.Thread(target=scrape_yellow_pages_task, args=(searchterm, location, leadid, task_id)).start()
    return jsonify({"task_id": task_id, "message": "Scraping task started."}), 200

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL"}), 200

    task_id = str(uuid.uuid4())
    new_task = Task(task_id=task_id, status='in progress')
    db.session.add(new_task)
    db.session.commit()

    threading.Thread(target=find_contacts_task, args=(website_url, task_id)).start()
    return jsonify({"task_id": task_id, "message": "Contact finding task started."}), 200

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = Task.query.filter_by(task_id=task_id).first()
    if task:
        result = json.loads(task.result) if task.result else None  # Deserialize result from JSON string
        return jsonify({"task_id": task.task_id, "status": task.status, "result": result}), 200
    else:
        return jsonify({"error": "Task not found."}), 404

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
